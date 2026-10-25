"""Tests unitaires du pipeline image -> 3D (données synthétiques, sans poids de modèle ni réseau).

Lancement : npm run 3d:test   (ou python -m unittest discover -s scripts/3d_pipeline/tests)
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import trimesh
from PIL import Image

PIPELINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PIPELINE_DIR)

import catalog  # noqa: E402
import image_to_3d  # noqa: E402
import neural_reconstruct as nr  # noqa: E402
import revolve_solid  # noqa: E402

SIZE = 400


def vase_mask():
    """Silhouette de vase : col étroit, panse large, pied plus étroit."""
    mask = np.zeros((SIZE, SIZE), dtype=bool)
    for y in range(60, 340):
        if y < 130:
            r = 35.0                                            # col étroit
        elif y < 200:
            r = 35.0 + 75.0 * np.sin((y - 130) / 70.0 * np.pi / 2)  # épaule
        else:
            r = 110.0 - 25.0 * ((y - 200) / 140.0) ** 3         # panse puis pied légèrement rentré
        mask[y, int(SIZE / 2 - r):int(SIZE / 2 + r)] = True
    return mask


def box_mask():
    mask = np.zeros((SIZE, SIZE), dtype=bool)
    mask[100:300, 60:340] = True
    return mask


class IdAndQuality(unittest.TestCase):
    def test_safe_id_normalises(self):
        self.assertEqual(image_to_3d.safe_id("Art 009"), "art-009")
        self.assertEqual(image_to_3d.safe_id("sac_Cuir-Noir"), "sac_cuir-noir")

    def test_safe_id_rejects_path_traversal_and_empty(self):
        for bad in ("", "   ", "../.."):
            with self.assertRaises(ValueError):
                image_to_3d.safe_id(bad)

    def test_quality_reasons(self):
        good = {"watertight": True, "silhouette_iou_front": 0.8, "matte_coverage": 0.3, "faces": 40000}
        self.assertEqual(image_to_3d.quality_reasons(good), [])
        bad = {"watertight": False, "silhouette_iou_front": 0.2, "matte_coverage": 0.99, "faces": 900000}
        self.assertEqual(len(image_to_3d.quality_reasons(bad)), 4)
        two_shoes = {**good, "matte_objects": 2}
        self.assertEqual(len(image_to_3d.quality_reasons(two_shoes)), 1)

    def test_pick_background_lightens_only_dark_products(self):
        with tempfile.TemporaryDirectory() as tmp:
            for color, expected in (((15, 15, 18), image_to_3d.LIGHT_BACKGROUND), ((240, 220, 20), None)):
                rgba = np.zeros((40, 40, 4), np.uint8)
                rgba[10:30, 10:30] = (*color, 255)
                Image.fromarray(rgba, "RGBA").save(os.path.join(tmp, "cutout.png"))
                self.assertEqual(image_to_3d.pick_background(tmp), expected)

    def test_multiview_entry_is_not_flagged_monocular_and_carries_background(self):
        report = {"backend": "multiview", "silhouette_iou_front": 0.95, "faces": 60000, "monocular_estimate": False}
        entry = image_to_3d.manifest_entry("sac", report, [], "inputs/x.png", "#d9dce1")
        self.assertFalse(entry["monocular_estimate"])
        self.assertEqual(entry["background"], "#d9dce1")
        self.assertNotIn("background", image_to_3d.manifest_entry("sac", report, [], "inputs/x.png"))

    def test_inconsistent_views_are_sent_to_review(self):
        report = {"watertight": True, "silhouette_iou_front": 0.9, "matte_coverage": 0.4, "faces": 60000,
                  "view_ious": {"front": 0.95, "left": 0.5}}
        self.assertEqual(len(image_to_3d.quality_reasons(report)), 1)

    def test_unpublish_removes_only_that_models_files(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(image_to_3d, "PUBLIC_MODELS", tmp):
            for name in ("a.glb", "a-poster.png", "b.glb"):
                open(os.path.join(tmp, name), "wb").close()
            image_to_3d.unpublish("a")
            self.assertEqual(os.listdir(tmp), ["b.glb"])


class Catalog(unittest.TestCase):
    def test_parses_real_mock_data(self):
        with open(catalog.MOCK_DATA, encoding="utf-8") as f:
            articles = catalog.parse_mock_data(f.read())
        by_id = {a["id"]: a for a in articles}
        self.assertIn("art-009", by_id)
        self.assertEqual(by_id["art-009"]["categorie"], "sacs")
        self.assertTrue(by_id["art-009"]["has_model"])
        self.assertFalse(by_id["art-007"]["has_model"])
        self.assertTrue(by_id["art-009"]["photos"][0].startswith("https://"))

    def test_expands_unsplash_helper_and_dedupes(self):
        with open(catalog.MOCK_DATA, encoding="utf-8") as f:
            articles = catalog.parse_mock_data(f.read())
        ids = [a["id"] for a in articles]
        self.assertEqual(len(ids), len(set(ids)), "identifiants uniques")
        by_id = {a["id"]: a for a in articles}
        self.assertEqual(
            by_id["art-102"]["photos"][0],
            "https://images.unsplash.com/photo-1691480150204-66dd1eb77391?w=1600&auto=format&q=80&exp=6")
        for article in articles:
            self.assertTrue(all(p.startswith(("https://", "/images/")) for p in article["photos"]), article["id"])
        # planches multi-vues ajoutées en photo supplémentaire de galerie, la photo d'origine reste la première
        self.assertEqual(by_id["art-009"]["photos"][-1], "/images/planches/art-009-planche.jpg")
        self.assertTrue(by_id["art-009"]["photos"][0].startswith("https://"))

    def test_parse_handles_double_quoted_names_and_skips_incomplete(self):
        text = "{\n id: 'x1',\n nom: \"L'Élégante\",\n categorie: 'sacs',\n photos: ['https://a/b.jpg'],\n},\n{\n id: 'x2',\n}"
        parsed = catalog.parse_mock_data(text)
        self.assertEqual([a["id"] for a in parsed], ["x1"])
        self.assertEqual(parsed[0]["nom"], "L'Élégante")


class Manifest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        patcher = mock.patch.object(image_to_3d, "MANIFEST_PATH", os.path.join(self.tmp.name, "m.json"))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def test_roundtrip_is_atomic_and_sorted(self):
        image_to_3d.save_manifest({"b": {"status": "ok"}, "a": {"status": "review"}})
        self.assertFalse(os.path.exists(image_to_3d.MANIFEST_PATH + ".tmp"))
        self.assertEqual(list(image_to_3d.load_manifest()), ["a", "b"])

    def test_select_skips_published_unless_forced(self):
        image_to_3d.save_manifest({"art-1": {"status": "ok"}, "art-2": {"status": "review"}})
        arts = [{"id": f"art-{i}", "categorie": "sacs", "photos": ["p"]} for i in (1, 2, 3)]
        arts.append({"id": "art-4", "categorie": "robes", "photos": ["p"]})
        ids = lambda sel: [a["id"] for a in sel]  # noqa: E731
        self.assertEqual(ids(image_to_3d.select_articles(arts, {"sacs"})), ["art-2", "art-3"])
        self.assertEqual(ids(image_to_3d.select_articles(arts, {"sacs"}, force=True)), ["art-1", "art-2", "art-3"])
        self.assertEqual(ids(image_to_3d.select_articles(arts, {"sacs"}, only_id="art-4")), ["art-4"])
        arts.append({"id": "art-5", "categorie": "sacs", "photos": ["p"], "has_model": True})
        self.assertNotIn("art-5", ids(image_to_3d.select_articles(arts, {"sacs"})))
        self.assertIn("art-5", ids(image_to_3d.select_articles(arts, {"sacs"}, force=True)))


class Geometry(unittest.TestCase):
    def test_drop_tiny_components_keeps_main_body(self):
        big = trimesh.creation.icosphere(subdivisions=4)  # 5120 faces ; le fragment (20 faces) pèse < 1 %
        speck = trimesh.creation.icosphere(subdivisions=0, radius=0.01)
        speck.apply_translation([3, 0, 0])
        merged = trimesh.util.concatenate([big, speck])
        cleaned = nr._drop_tiny_components(merged)
        self.assertEqual(len(cleaned.split(only_watertight=False)), 1)
        self.assertEqual(len(cleaned.faces), len(big.faces))

    def test_revolution_detection(self):
        self.assertTrue(revolve_solid.looks_like_revolution(vase_mask())[0])
        self.assertFalse(revolve_solid.looks_like_revolution(box_mask())[0])

    def test_revolve_mesh_is_closed_and_matches_silhouette(self):
        mask = vase_mask()
        rgb = np.full((SIZE, SIZE, 3), (180, 90, 40), dtype=np.uint8)
        mesh = revolve_solid.build_revolve_mesh(mask, rgb, nr.CAMERA_DISTANCE, nr.CAMERA_FOVY)
        self.assertTrue(mesh.is_watertight)
        self.assertGreater(mesh.volume, 0)
        self.assertGreater(nr.silhouette_iou(mask, mesh), 0.9)
        self.assertTrue((np.asarray(mesh.visual.vertex_colors)[:, :3] == (180, 90, 40)).all())

    def test_photo_colors_reach_front_vertices_only(self):
        sphere = trimesh.creation.icosphere(subdivisions=4, radius=0.5)
        sphere.visual.vertex_colors = np.tile([128, 128, 128, 255], (len(sphere.vertices), 1)).astype(np.uint8)
        yy, xx = np.mgrid[:SIZE, :SIZE]
        disk = (xx - SIZE / 2) ** 2 + (yy - SIZE / 2) ** 2 < (0.7 * SIZE / 2) ** 2
        photo = Image.fromarray(np.full((SIZE, SIZE, 3), (220, 30, 30), dtype=np.uint8))
        nr._project_photo_colors(sphere, photo, disk)
        colors = np.asarray(sphere.visual.vertex_colors)[:, :3].astype(int)
        front = sphere.vertices[:, 2] > 0.45
        back = sphere.vertices[:, 2] < -0.45
        self.assertGreater(colors[front, 0].mean(), 200)   # face vers la caméra : rouge de la photo
        self.assertEqual(int(colors[back, 0].mean()), 128)  # dos : couleur estimée conservée


class Finish(unittest.TestCase):
    """Finition : lissage, décimation étanche, dépliage UV et texture cuite depuis la photo."""

    @staticmethod
    def noisy_sphere():
        sphere = trimesh.creation.icosphere(subdivisions=4, radius=0.5)
        rng = np.random.default_rng(1)
        radial = sphere.vertices / np.linalg.norm(sphere.vertices, axis=1, keepdims=True)
        sphere.vertices = sphere.vertices + radial * rng.normal(0, 0.01, (len(sphere.vertices), 1))
        return sphere

    def test_smoothing_removes_surface_noise_without_shrinking(self):
        import finish_mesh
        noisy = self.noisy_sphere()
        smooth = finish_mesh.smooth(noisy)
        spread = lambda m: np.linalg.norm(m.vertices, axis=1).std()  # noqa: E731
        self.assertLess(spread(smooth), 0.5 * spread(noisy))
        self.assertAlmostEqual(np.linalg.norm(smooth.vertices, axis=1).mean(), 0.5, delta=0.02)

    def test_decimation_reaches_target_and_stays_watertight(self):
        import finish_mesh
        sphere = trimesh.creation.icosphere(subdivisions=5)   # 20 480 faces, réduction x3,4 comme sur un vrai maillage
        reduced = finish_mesh.decimate(sphere, 6000)
        self.assertLessEqual(len(reduced.faces), 6600)
        self.assertTrue(reduced.is_watertight)
        small = trimesh.creation.icosphere(subdivisions=2)
        self.assertIs(finish_mesh.decimate(small, 6000), small, "déjà sous la cible : inchangé")

    def test_baked_texture_carries_photo_on_front_and_fill_on_back(self):
        import finish_mesh
        sphere = trimesh.creation.icosphere(subdivisions=3, radius=0.5)
        yy, xx = np.mgrid[:SIZE, :SIZE]
        disk = (xx - SIZE / 2) ** 2 + (yy - SIZE / 2) ** 2 < (0.7 * SIZE / 2) ** 2
        photo = Image.fromarray(np.full((SIZE, SIZE, 3), (210, 40, 40), dtype=np.uint8))
        textured, info = finish_mesh.finish(
            sphere, photo, disk, 256, None, 0, nr.CAMERA_DISTANCE, nr.CAMERA_FOVY)
        self.assertTrue(info["watertight"])
        self.assertEqual(info["faces"], len(textured.faces))
        texture = np.asarray(textured.visual.material.baseColorTexture.convert("RGB")).reshape(-1, 3)
        self.assertGreater(np.median(texture[:, 0]), 150)   # le rouge de la photo domine, dos compris (remplissage)
        self.assertLess(np.median(texture[:, 2]), 90)
        self.assertEqual(textured.visual.material.baseColorTexture.format, "JPEG")

    def test_uv_rasterization_covers_every_face(self):
        import finish_mesh
        sphere = trimesh.creation.icosphere(subdivisions=2)
        vertices, faces, uvs, normals = finish_mesh.unwrap(sphere)
        positions, _, covered = finish_mesh.rasterize_uv(faces, uvs, vertices, normals, 256)
        self.assertGreater(covered.mean(), 0.2)
        radii = np.linalg.norm(positions[covered], axis=1)
        self.assertAlmostEqual(radii.mean(), 1.0, delta=0.05)  # les texels retombent sur la surface


class Multiview(unittest.TestCase):
    """Planche multi-vues : découpe, nettoyage des silhouettes, enveloppe visuelle, orientation des vues."""

    DIMS = (0.56, 1.0, 0.4)

    @classmethod
    def silhouettes(cls, flips=None):
        """Silhouettes (nom -> masque) d'un corps + sangle arrière, rendues avec la même convention que carve."""
        import multiview as mv
        from scipy import ndimage

        flips = flips or {}
        w, h, d = cls.DIMS
        n = 70
        xs, ys, zs = ((np.arange(n) + 0.5) / n * s - o for s, o in ((w, w / 2), (h, 0), (d, d / 2)))
        x, y, z = np.meshgrid(xs, ys, zs, indexing="ij")
        body = (abs(x) < 0.28) & (z > -0.1) & (z < 0.2)
        # sangle étroite plaquée au dos : silhouettes dessus/dessous en « T », donc asymétriques en z
        strap = (z <= -0.1) & (z > -0.2) & (y > 0.25) & (y < 0.75) & (abs(x) < 0.15)
        occupied = body | strap
        views = {}
        for name in mv.HULL_VIEWS:
            u, v = mv.view_uv(name, x[occupied], y[occupied], z[occupied], cls.DIMS, *flips.get(name, (False, False)))
            mask = np.zeros((120, 120), bool)
            mask[np.clip((v * 119).round().astype(int), 0, 119), np.clip((u * 119).round().astype(int), 0, 119)] = True
            views[name] = {"mask": ndimage.binary_closing(mask, iterations=2)}
        return views

    def test_find_panels_ignores_labels(self):
        import multiview as mv
        sheet = np.full((500, 600), 255, np.uint8)
        for x0, x1 in ((20, 150), (200, 330), (380, 520)):
            sheet[10:200, x0:x1] = 30
            sheet[210:222, x0 + 40:x1 - 40] = 40   # étiquette fine sous le panneau
        for x0, x1 in ((30, 250), (300, 560)):
            sheet[260:440, x0:x1] = 30
            sheet[450:462, x0 + 50:x1 - 50] = 40
        rows = mv.find_panels(sheet, (3, 2))
        self.assertEqual([len(r) for r in rows], [3, 2])
        self.assertEqual(rows[0][1], (200, 10, 330, 200))
        self.assertEqual(rows[1][0], (30, 260, 250, 440))
        with self.assertRaises(ValueError):
            mv.find_panels(sheet, (3, 3))

    def test_clean_alpha_drops_specks_but_keeps_real_holes(self):
        import multiview as mv
        alpha = np.zeros((200, 200), np.uint8)
        alpha[20:180, 20:180] = 255
        alpha[60:120, 60:120] = 0     # vrai trou (espace entre sangle et dos)
        alpha[5:7, 5:7] = 255         # poussière
        alpha[30:32, 30:32] = 0       # minuscule trou parasite
        cleaned = mv._clean_alpha(alpha)
        self.assertFalse(cleaned[5, 5])
        self.assertTrue(cleaned[30, 30])
        self.assertFalse(cleaned[90, 90])

    def test_carve_recovers_the_shape_and_reprojects_consistently(self):
        import multiview as mv
        views = self.silhouettes()
        flips = mv.choose_orientations(views, self.DIMS)
        field, grid = mv.carve(views, self.DIMS, flips, 64)
        keep = field > 0.5
        self.assertGreater(keep.mean(), 0.78)   # vrai volume : 82 % de la boîte englobante (+ léger gonflement)
        self.assertLess(keep.mean(), 0.97)
        ious = mv.reprojection_iou(views, (keep, grid), self.DIMS, flips)
        self.assertGreater(min(ious.values()), 0.85)

    def test_orientation_search_finds_a_flipped_bottom_view(self):
        import multiview as mv
        views = self.silhouettes({"bottom": (False, True)})
        flips = mv.choose_orientations(views, self.DIMS)
        self.assertEqual(flips["bottom"], (False, True))
        self.assertEqual(flips["top"], (False, False))

    def test_layout_can_ignore_unreliable_views_but_not_front_or_left(self):
        import multiview as mv
        boxes = {n: [0, 0, 10, 10] for n in mv.HULL_VIEWS}
        with tempfile.TemporaryDirectory() as tmp:
            def write(data):
                path = os.path.join(tmp, "l.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                return path
            loaded = mv.load_layout(write({"boxes": boxes, "ignore": ["top"]}))
            self.assertNotIn("top", loaded)
            self.assertIn("bottom", loaded)
            with self.assertRaises(ValueError):
                mv.load_layout(write({"boxes": {k: v for k, v in boxes.items() if k != "bottom"}}))
            with self.assertRaises(ValueError):
                mv.load_layout(write({"boxes": boxes, "ignore": ["front"]}))

    def test_pipeline_works_without_the_top_view(self):
        import multiview as mv
        views = {k: v for k, v in self.silhouettes().items() if k != "top"}
        dims = mv.estimate_dims(views)
        self.assertAlmostEqual(dims[0], 1.0, delta=0.2)  # largeur déduite des vues de face et de dos
        flips = mv.choose_orientations(views, self.DIMS)
        self.assertNotIn("top", flips)
        field, _ = mv.carve(views, self.DIMS, flips, 48)
        self.assertGreater((field > 0.5).mean(), 0.5)

    def test_near_symmetric_objects_keep_the_orientation_convention(self):
        import multiview as mv
        from scipy import ndimage
        n = 60
        xs, ys, zs = ((np.arange(n) + 0.5) / n * s - o for s, o in ((0.56, 0.28), (1.0, 0), (0.4, 0.2)))
        x, y, z = np.meshgrid(xs, ys, zs, indexing="ij")
        box = np.ones(x.shape, bool)  # boîte pleine : toute orientation donne le même volume
        views = {}
        for name in mv.HULL_VIEWS:
            u, v = mv.view_uv(name, x[box], y[box], z[box], self.DIMS)
            mask = np.zeros((90, 90), bool)
            mask[np.clip((v * 89).round().astype(int), 0, 89), np.clip((u * 89).round().astype(int), 0, 89)] = True
            views[name] = {"mask": ndimage.binary_closing(mask, iterations=2)}
        flips = mv.choose_orientations(views, self.DIMS)
        self.assertTrue(all(flip == (False, False) for flip in flips.values()), flips)

    def test_single_panel_mode_crops_and_upscales(self):
        with tempfile.TemporaryDirectory() as tmp:
            sheet = os.path.join(tmp, "s.png")
            Image.fromarray(np.full((100, 200, 3), 255, np.uint8)).save(sheet)
            path = image_to_3d._crop_panel(sheet, {"panel": [20, 10, 60, 50], "upscale": 3}, tmp)
            with Image.open(path) as crop:
                self.assertEqual(crop.size, (120, 120))
            layout_path, layout = image_to_3d._load_sheet_layout(sheet, None)
            self.assertIsNone(layout_path)
            self.assertEqual(layout, {})

    def test_hull_mesh_is_watertight_and_smooth(self):
        import multiview as mv
        views = self.silhouettes()
        flips = mv.choose_orientations(views, self.DIMS)
        field, grid = mv.carve(views, self.DIMS, flips, 64)
        mesh = mv.hull_mesh(field, grid)
        self.assertTrue(mesh.is_watertight)
        self.assertGreater(mesh.volume, 0)
        self.assertAlmostEqual(mesh.bounds[1][1] - mesh.bounds[0][1], 1.0, delta=0.08)

    def test_background_keying_removes_the_gap_between_handles_only_on_light_backgrounds(self):
        import multiview as mv
        crop = np.full((100, 100, 3), 235, np.uint8)
        crop[20:90, 10:90] = 30       # sac noir
        alpha = np.zeros((100, 100), np.uint8)
        alpha[10:90, 10:90] = 255     # le détourage garde aussi l'espace clair entre les anses (lignes 10-19)
        keyed = mv._key_out_background(Image.fromarray(crop), alpha)
        self.assertEqual(keyed[15, 50], 0)
        self.assertEqual(keyed[50, 50], 255)
        white_bag = np.full((100, 100, 3), 240, np.uint8)   # produit blanc sur fond blanc : on ne touche à rien
        self.assertTrue((mv._key_out_background(Image.fromarray(white_bag), alpha) == alpha).all())
        dark_backdrop = np.full((100, 100, 3), 20, np.uint8)
        self.assertTrue((mv._key_out_background(Image.fromarray(dark_backdrop), alpha) == alpha).all())

    def test_bright_hardware_inside_the_object_is_not_punched_out_but_a_real_gap_is(self):
        import multiview as mv
        crop = np.full((120, 120, 3), 245, np.uint8)
        crop[10:110, 10:110] = 25                                 # sac noir
        crop[30:50, 30:50] = 245                                  # vraie ouverture, couleur unie du fond
        yy, xx = np.mgrid[:20, :20]
        crop[60:80, 60:80] = (150 + 4 * (xx + yy)).clip(0, 255)[..., None]   # reflet de ferrure : dégradé clair
        alpha = np.zeros((120, 120), np.uint8)
        alpha[10:110, 10:110] = 255
        keyed = mv._key_out_background(Image.fromarray(crop), alpha)
        self.assertEqual(keyed[40, 40], 0)
        self.assertGreater(keyed[70, 70], 127)

    def test_soft_field_is_continuous_and_bilinear_lookup_interpolates(self):
        import multiview as mv
        mask = np.zeros((600, 600), bool)   # taille d'une vue agrandie : le flou est une fraction de la taille
        mask[200:400, 200:400] = True
        field = mv._soft(mask)
        self.assertGreater(field[300, 300], 0.9)
        self.assertLess(field[2, 2], 0.05)
        self.assertGreater(len(np.unique(field.round(3))), 10)   # dégradé continu, pas un masque binaire
        ramp = np.tile(np.linspace(0, 1, 11, dtype=np.float32), (11, 1))
        self.assertAlmostEqual(float(mv._lookup_soft(ramp, np.array([0.25]), np.array([0.5]))[0]), 0.25, places=5)
        subpixel = mv._soft(mask, alpha=np.where(mask, 1.0, 0.0).astype(np.float32) * 0.5)
        self.assertLess(subpixel[300, 300], field[300, 300])     # l'alpha continu pilote le champ


class MaterialAndUpscale(unittest.TestCase):
    """Rendu : cartes PBR cuites depuis la texture et super-résolution des vues sources."""

    @staticmethod
    def texture(rgb, gold_patch=None):
        pixels = np.full((128, 128, 3), rgb, np.uint8)
        if gold_patch:
            pixels[gold_patch[0]:gold_patch[1], gold_patch[0]:gold_patch[1]] = (212, 175, 55)
        return Image.fromarray(pixels)

    def test_gold_hardware_becomes_metal_but_a_gold_bag_does_not(self):
        import finish_mesh
        _, mr = finish_mesh.material_maps(self.texture((25, 25, 25), gold_patch=(8, 24)))
        metal = np.asarray(mr)[..., 2]
        self.assertGreater(metal.max(), 200)      # ferrure dorée : métal
        self.assertLess(np.median(metal), 5)      # cuir noir : diélectrique
        _, mr_bag = finish_mesh.material_maps(self.texture((212, 175, 55)))
        self.assertEqual(int(np.asarray(mr_bag)[..., 2].max()), 0)   # sac entièrement doré : pas de métal

    def test_material_has_all_pbr_textures_in_compact_format(self):
        import finish_mesh
        material = finish_mesh.make_material(self.texture((90, 60, 40)))
        for texture in (material.baseColorTexture, material.normalTexture, material.metallicRoughnessTexture):
            self.assertEqual(texture.format, "JPEG")

    def test_upscale_skips_large_views_and_missing_weights(self):
        import upscale
        big = np.zeros((10, upscale.SKIP_ABOVE, 3), np.uint8)
        self.assertIs(upscale.upscale_rgb(big), big)
        small = np.zeros((20, 20, 3), np.uint8)
        with mock.patch.object(upscale, "WEIGHTS", os.path.join(tempfile.gettempdir(), "absent.pth")):
            self.assertIs(upscale.upscale_rgb(small), small)


if __name__ == "__main__":
    unittest.main()
