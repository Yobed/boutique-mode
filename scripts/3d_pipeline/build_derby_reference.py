"""Build a cognac cap-toe Derby pair from the ELSI reference board.

Run with Blender 5.2:
  blender --background --factory-startup --python build_derby_reference.py -- --root <project>

This is a product-specific procedural mesh. Its silhouette and visible construction
details follow the supplied board; dimensions remain illustrative as stated on it.
"""

import array
import math
import os
import random
import sys

import bpy
from mathutils import Euler, Matrix, Vector


def cli_root():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--root" in args:
        return os.path.abspath(args[args.index("--root") + 1])
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


ROOT = cli_root()
MODEL_DIR = os.path.join(ROOT, "public", "models")
GLB_PATH = os.path.join(MODEL_DIR, "chaussure-homme-cognac.glb")
POSTER_PATH = os.path.join(MODEL_DIR, "chaussure-homme-cognac-poster.png")
os.makedirs(MODEL_DIR, exist_ok=True)


def srgb_to_linear(v):
    v = v / 255.0
    return v / 12.92 if v < 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def color(hex_value, alpha=1.0):
    h = hex_value.lstrip("#")
    return tuple(srgb_to_linear(int(h[i:i + 2], 16)) for i in (0, 2, 4)) + (alpha,)


def material(name, hex_value, roughness, metallic=0.0, coat=0.0, specular=0.14):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color(hex_value)
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = color(hex_value)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if "Specular IOR Level" in shader.inputs:
        shader.inputs["Specular IOR Level"].default_value = specular
    if "Coat Weight" in shader.inputs:
        shader.inputs["Coat Weight"].default_value = coat
        shader.inputs["Coat Roughness"].default_value = 0.22
    return mat


def make_leather_image():
    size = 512
    rng = random.Random(305)
    texels = array.array("f")
    # Keep the packed texture nearly neutral so the GLB base-color factor can
    # recolor the whole leather surface without inheriting a brown tint.
    base = tuple(srgb_to_linear(c) for c in (215, 215, 215))
    coarse = [[rng.random() for _ in range(32)] for _ in range(32)]
    for y in range(size):
        v = y / size * 32
        gy = int(v) % 32
        fy = v - int(v)
        for x in range(size):
            u = x / size * 32
            gx = int(u) % 32
            fx = u - int(u)
            a = coarse[gy][gx]
            b = coarse[gy][(gx + 1) % 32]
            c = coarse[(gy + 1) % 32][gx]
            d = coarse[(gy + 1) % 32][(gx + 1) % 32]
            sx = fx * fx * (3 - 2 * fx)
            sy = fy * fy * (3 - 2 * fy)
            cloud = (a * (1 - sx) + b * sx) * (1 - sy) + (c * (1 - sx) + d * sx) * sy
            grain = (rng.random() - 0.5) * 0.006
            light = 0.97 + (cloud - 0.5) * 0.06 + grain
            texels.extend((base[0] * light, base[1] * light, base[2] * light, 1.0))
    image = bpy.data.images.new("Cognac leather | subtle full-grain", width=size, height=size, alpha=False)
    image.colorspace_settings.name = "sRGB"
    image.pixels.foreach_set(texels)
    image.pack()
    return image


def set_active(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def mesh_object(name, vertices, faces, mat, uvs=None, smooth=True):
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if uvs:
        uv_layer = mesh.uv_layers.new(name="UVMap")
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                uv_layer.data[loop_index].uv = uvs[vertex_index]
    if smooth:
        for face in mesh.polygons:
            face.use_smooth = True
    return obj


def curve_object(name, points, mat, radius=0.00055, resolution=3):
    curve = bpy.data.curves.new(name + " curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = radius
    curve.bevel_resolution = resolution
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coord in zip(spline.points, points):
        point.co = (coord[0], coord[1], coord[2], 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


PROFILE = [
    (-0.151, 0.027, 0.085),
    (-0.139, 0.035, 0.116),
    (-0.119, 0.040, 0.128),
    (-0.095, 0.043, 0.119),
    (-0.067, 0.047, 0.108),
    (-0.037, 0.051, 0.097),
    (-0.004, 0.053, 0.088),
    (0.031, 0.052, 0.080),
    (0.068, 0.047, 0.072),
    (0.103, 0.038, 0.064),
    (0.131, 0.026, 0.057),
    (0.151, 0.001, 0.052),
]
BASE_Z = 0.027


def profile_at(x):
    if x <= PROFILE[0][0]:
        return PROFILE[0][1], PROFILE[0][2]
    if x >= PROFILE[-1][0]:
        return PROFILE[-1][1], PROFILE[-1][2]
    for i, (a, b) in enumerate(zip(PROFILE, PROFILE[1:])):
        if a[0] <= x <= b[0]:
            t = (x - a[0]) / (b[0] - a[0])
            span = b[0] - a[0]
            previous = PROFILE[max(0, i - 1)]
            following = PROFILE[min(len(PROFILE) - 1, i + 2)]
            values = []
            for column in (1, 2):
                m0 = (b[column] - previous[column]) / (b[0] - previous[0])
                m1 = (following[column] - a[column]) / (following[0] - a[0])
                h00 = 2 * t**3 - 3 * t**2 + 1
                h10 = t**3 - 2 * t**2 + t
                h01 = -2 * t**3 + 3 * t**2
                h11 = t**3 - t**2
                values.append(h00 * a[column] + h10 * span * m0 + h01 * b[column] + h11 * span * m1)
            return values[0], values[1]
    return PROFILE[-1][1], PROFILE[-1][2]


def surface_z(x, y):
    half_width, crown = profile_at(x)
    ratio = min(0.999, abs(y) / max(half_width, 0.0001))
    return BASE_Z + (crown - BASE_Z) * math.sqrt(max(0.001, 1.0 - ratio * ratio))


def make_upper(name, leather):
    x_count, arc_count = 144, 48
    vertices, faces, uvs = [], [], []
    for i in range(x_count):
        x = PROFILE[0][0] + (PROFILE[-1][0] - PROFILE[0][0]) * i / (x_count - 1)
        half_width, crown = profile_at(x)
        for j in range(arc_count + 1):
            theta = math.pi * (j / arc_count - 0.5)
            y = half_width * math.sin(theta)
            z = BASE_Z + (crown - BASE_Z) * math.cos(theta)
            vertices.append((x, y, z))
            uvs.append((i / (x_count - 1), j / arc_count))
    for i in range(x_count - 1):
        for j in range(arc_count):
            a = i * (arc_count + 1) + j
            b = (i + 1) * (arc_count + 1) + j
            faces.append((a, b, b + 1, a + 1))
    return mesh_object(name + " · cuir pleine fleur", vertices, faces, leather, uvs)


def footprint(x, scale=1.0):
    half_width, _ = profile_at(x)
    return max(0.0006, half_width * scale)


def make_layered_sole(name, rubber, welt, thread):
    n = 160
    rings = [(0.003, 1.065), (0.008, 1.09), (0.013, 1.09), (0.017, 1.035)]
    vertices, faces = [], []
    for z, scale in rings:
        for i in range(n):
            angle = 2 * math.pi * i / n
            x = 0.151 * math.cos(angle)
            y = footprint(x, scale) * math.sin(angle)
            vertices.append((x, y, z))
    for r in range(len(rings) - 1):
        for i in range(n):
            a = r * n + i
            b = r * n + (i + 1) % n
            c = (r + 1) * n + (i + 1) % n
            d = (r + 1) * n + i
            faces.append((a, b, c, d))
    faces.append(tuple(range(n - 1, -1, -1)))
    faces.append(tuple((len(rings) - 1) * n + i for i in range(n)))
    mesh_object(name + " · semelle extérieure", vertices, faces, rubber)

    # Leather welt: narrow stepped edge and fine perimeter stitching.
    welt_vertices, welt_faces = [], []
    for z, scale in [(0.016, 1.09), (0.019, 1.105), (0.022, 1.085)]:
        for i in range(n):
            angle = 2 * math.pi * i / n
            x = 0.151 * math.cos(angle)
            y = footprint(x, scale) * math.sin(angle)
            welt_vertices.append((x, y, z))
    for r in range(2):
        for i in range(n):
            a = r * n + i
            b = r * n + (i + 1) % n
            c = (r + 1) * n + (i + 1) % n
            d = (r + 1) * n + i
            welt_faces.append((a, b, c, d))
    mesh_object(name + " · trépointe cuir", welt_vertices, welt_faces, welt)
    stitches = []
    for i in range(320):
        angle = 2 * math.pi * i / 320
        x = 0.151 * math.cos(angle)
        y = footprint(x, 1.077) * math.sin(angle)
        stitches.append((x, y, 0.0212))
    curve_object(name + " · piqûre de trépointe", stitches, thread, 0.00028, 2)

    # The low stacked heel and its two visible leather/rubber layers.
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.109, 0, 0.017))
    heel = bpy.context.object
    heel.name = name + " · talon empilé"
    heel.dimensions = (0.075, 0.071, 0.028)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    heel.data.materials.append(rubber)
    bevel = heel.modifiers.new("Arêtes adoucies", "BEVEL")
    bevel.width = 0.004
    bevel.segments = 3
    heel.modifiers.new("Normales de finition", "WEIGHTED_NORMAL")

    # Fine transverse outsole grooves remain readable from the underside.
    tread = material("Gomme · relief de semelle", "#25211f", 0.46)
    for x in [-0.025, 0.005, 0.035, 0.065, 0.092, 0.115]:
        half = footprint(x, 0.73)
        points = [(x - 0.003, -half, 0.0034), (x + 0.003, 0, 0.0034), (x - 0.003, half, 0.0034)]
        curve_object(name + " · rainure semelle", points, tread, 0.00075, 2)


def make_patch(name, x0, x1, width_factor, mat, lift=0.0010, rows=56, cols=18):
    vertices, faces = [], []
    for i in range(rows):
        x = x0 + (x1 - x0) * i / (rows - 1)
        half_width, _ = profile_at(x)
        width = half_width * width_factor
        for j in range(cols + 1):
            y = width * (2 * j / cols - 1)
            vertices.append((x, y, surface_z(x, y) + lift))
    for i in range(rows - 1):
        for j in range(cols):
            a = i * (cols + 1) + j
            b = a + cols + 1
            faces.append((a, b, b + 1, a + 1))
    return mesh_object(name, vertices, faces, mat)


def ellipse_surface(name, center_x, radius_x, radius_y, mat, lift):
    count = 64
    vertices = [(center_x, 0, surface_z(center_x, 0) + lift)]
    for i in range(count):
        angle = 2 * math.pi * i / count
        x = center_x + radius_x * math.cos(angle)
        y = radius_y * math.sin(angle)
        vertices.append((x, y, surface_z(x, y) + lift))
    faces = [(0, i + 1, (i + 1) % count + 1) for i in range(count)]
    return mesh_object(name, vertices, faces, mat, smooth=True)


def add_eyelet(name, x, y, metal):
    z = surface_z(x, y) + 0.002
    bpy.ops.mesh.primitive_torus_add(
        major_segments=18, minor_segments=8, major_radius=0.0032,
        minor_radius=0.0009, location=(x, y, z),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(metal)
    for poly in obj.data.polygons:
        poly.use_smooth = True


def make_shoe(prefix, mats):
    start = set(bpy.data.objects)
    leather, cap, lining, rubber, welt, stitch, metal, lace, tread = mats
    make_upper(prefix, leather)
    make_layered_sole(prefix, rubber, welt, stitch)

    # Contrasting cap-toe panel and the fine double row of its stitching.
    make_patch(prefix + " · bout rapporté", 0.075, 0.149, 0.93, cap, 0.0013, rows=56, cols=26)
    cap_line = []
    for i in range(81):
        y = -0.97 + 1.94 * i / 80
        x = 0.075 + 0.003 * (1 - y * y)
        half_width, _ = profile_at(x)
        y *= half_width
        cap_line.append((x, y, surface_z(x, y) + 0.002))
    curve_object(prefix + " · couture bout", cap_line, stitch, 0.00043, 3)

    # Heel collar with a visible dark leather lining and a padded rim.
    ellipse_surface(prefix + " · ouverture doublée", -0.112, 0.033, 0.0185, lining, 0.0014)
    collar = []
    for i in range(97):
        angle = 2 * math.pi * i / 96
        x = -0.112 + 0.034 * math.cos(angle)
        y = 0.0192 * math.sin(angle)
        collar.append((x, y, surface_z(x, y) + 0.0025))
    curve_object(prefix + " · bourrelet de col", collar, cap, 0.00135, 4)

    # Tongue, derby facings and the curved quarter/counter seams.
    make_patch(prefix + " · languette", -0.090, 0.017, 0.32, lining, 0.0032, rows=54, cols=16)
    for sign in (-1, 1):
        points = []
        for i in range(48):
            x = -0.126 + 0.103 * i / 47
            half_width, _ = profile_at(x)
            y = sign * half_width * 0.74
            points.append((x, y, surface_z(x, y) + 0.0014))
        curve_object(prefix + " · couture quartier", points, stitch, 0.00042, 3)

        facing = []
        for i in range(40):
            x = -0.092 + 0.099 * i / 39
            half_width, _ = profile_at(x)
            y = sign * min(half_width * 0.86, 0.023)
            facing.append((x, y, surface_z(x, y) + 0.0022))
        curve_object(prefix + " · bord de laçage", facing, cap, 0.0011, 3)

    heel_seam = []
    for i in range(65):
        y = -0.72 + 1.44 * i / 64
        y *= profile_at(-0.128)[0]
        heel_seam.append((-0.128, y, surface_z(-0.128, y) + 0.0012))
    curve_object(prefix + " · couture contrefort", heel_seam, stitch, 0.00040, 3)

    # Six discreet metal eyelets on each facing.
    lace_x = [-0.074, -0.059, -0.044, -0.029, -0.014, 0.001]
    for row, x in enumerate(lace_x, 1):
        for sign in (-1, 1):
            y = sign * 0.0164
            add_eyelet(prefix + " · œillet " + str(row), x, y, metal)

    # Waxed leather laces, crossed over the tongue.
    for i in range(len(lace_x) - 1):
        x0, x1 = lace_x[i], lace_x[i + 1]
        for sign in (-1, 1):
            points = []
            for step in range(17):
                t = step / 16
                x = x0 + (x1 - x0) * t
                y = sign * 0.0164 * (1 - t) + (-sign) * 0.0164 * t
                z = surface_z(x, y) + 0.0042 + 0.0018 * math.sin(math.pi * t)
                points.append((x, y, z))
            curve_object(prefix + " · lacet ciré", points, lace, 0.00185, 4)

    # Two small loops and a knot at the throat of the Derby.
    knot_x = 0.010
    knot_z = surface_z(knot_x, 0) + 0.007
    for sign in (-1, 1):
        loop = []
        for i in range(49):
            angle = 2 * math.pi * i / 48
            x = knot_x + 0.013 * math.cos(angle)
            y = sign * (0.009 + 0.006 * math.sin(angle))
            loop.append((x, y, surface_z(x, y) + 0.007))
        curve_object(prefix + " · boucle de lacet", loop, lace, 0.00175, 4)
    curve_object(prefix + " · nœud", [(knot_x - 0.004, 0, knot_z), (knot_x + 0.004, 0, knot_z + 0.001)], lace, 0.0022, 4)

    # Restrained perimeter welt accent, visible as a second fine line.
    outer = []
    for i in range(240):
        angle = 2 * math.pi * i / 240
        x = 0.151 * math.cos(angle)
        y = footprint(x, 1.075) * math.sin(angle)
        outer.append((x, y, 0.0195))
    curve_object(prefix + " · liseré de semelle", outer, cap, 0.00034, 2)

    return [obj for obj in bpy.data.objects if obj not in start]


def add_area(name, location, power, size, hex_color, target):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    data.color = tuple(int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


def make_poster(objects):
    world = bpy.data.worlds.new("Fond studio charbon")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = color("#ded8d0")
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.4
    bpy.context.scene.world = world

    floor_mat = material("Studio · pierre sable", "#a99e92", 0.72)
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0, 0, 0.001))
    floor = bpy.context.object
    floor.name = "Studio floor · render only"
    floor.data.materials.append(floor_mat)

    target = (0.0, 0.0, 0.061)
    add_area("Softbox principal", (0.22, -0.33, 0.55), 20, 0.44, "#fff4e9", target)
    add_area("Reflet cuir chaud", (-0.16, 0.22, 0.35), 12, 0.30, "#edbd92", target)
    add_area("Lumière contour", (0.20, 0.32, 0.26), 16, 0.24, "#fff0df", target)
    add_area("Remplissage doux", (-0.30, -0.15, 0.22), 7, 0.38, "#e2e6ec", target)

    camera_data = bpy.data.cameras.new("Caméra produit")
    camera = bpy.data.objects.new("Caméra produit", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (0.47, -0.58, 0.35)
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 0.49
    bpy.context.scene.camera = camera

    scene = bpy.context.scene
    render_engines = {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in render_engines else "CYCLES"
    if scene.render.engine == "BLENDER_EEVEE" and hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 64
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.8
    scene.render.filepath = POSTER_PATH
    scene.camera.data.lens = 56
    bpy.ops.render.render(write_still=True)


def export_glb(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = next(obj for obj in objects if obj.type == "MESH")
    bpy.ops.export_scene.gltf(
        filepath=GLB_PATH,
        export_format="GLB",
        use_selection=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    leather = material("Cuir cognac · pleine fleur", "#75401f", 0.45, coat=0.01, specular=0.12)
    leather_img = make_leather_image()
    shader = next(n for n in leather.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    texture = leather.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = leather_img
    texture.interpolation = "Linear"
    texture_mix = leather.node_tree.nodes.new("ShaderNodeMixRGB")
    texture_mix.blend_type = "MULTIPLY"
    texture_mix.inputs[0].default_value = 1.0
    texture_mix.inputs[2].default_value = color("#75401f")
    leather.node_tree.links.new(texture.outputs["Color"], texture_mix.inputs[1])
    leather.node_tree.links.new(texture_mix.outputs["Color"], shader.inputs["Base Color"])

    # Share one leather material so the live color selector recolors the upper
    # and the cap-toe consistently in the exported GLB.
    cap = leather
    lining = material("Doublure cuir brun foncé", "#21120e", 0.52, specular=0.06)
    rubber = material("Semelle gomme noire", "#12100e", 0.58, specular=0.06)
    welt = material("Trépointe cuir brun", "#3d2115", 0.38)
    stitch = material("Fil de couture tabac", "#97633d", 0.7)
    metal = material("Œillets laiton bruni", "#4f3322", 0.24, metallic=0.66)
    lace = material("Lacets cirés brun profond", "#2a160f", 0.76, specular=0.05)
    tread = material("Gomme · relief de semelle", "#25211f", 0.46)
    mats = (leather, cap, lining, rubber, welt, stitch, metal, lace, tread)

    pair = []
    left = make_shoe("Derby cognac · chaussure avant", mats)
    left_transform = Matrix.Translation(Vector((0.023, -0.032, 0.0))) @ Euler((0, 0, 0.035)).to_matrix().to_4x4()
    for obj in left:
        obj.matrix_world = left_transform @ obj.matrix_world
    pair.extend(left)

    right = make_shoe("Derby cognac · chaussure arrière", mats)
    right_transform = Matrix.Translation(Vector((-0.052, 0.047, 0.0))) @ Euler((0, 0, -0.08)).to_matrix().to_4x4()
    for obj in right:
        obj.matrix_world = right_transform @ obj.matrix_world
    pair.extend(right)

    make_poster(pair)
    export_glb(pair)
    print("GLB:", GLB_PATH, os.path.getsize(GLB_PATH))
    print("Poster:", POSTER_PATH, os.path.getsize(POSTER_PATH))
    print("Shoe meshes:", sum(obj.type == "MESH" for obj in pair), "objects:", len(pair))


if __name__ == "__main__":
    main()
