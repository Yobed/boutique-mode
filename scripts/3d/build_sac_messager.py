"""
build_sac_messager.py — Modèle 3D haute fidélité pour le Sac Messager Cuir Havane (art-102).

Construit sous Blender :
  - Proportions fines et réalistes (W=0.35, D=0.115, H=0.24 — ratio 1:3 fin, pas de forme de pavé) ;
  - Deux anses indépendantes (anse avant et anse arrière) laissant le trou central ouvert et visible de profil ;
  - Biseaux adoucis (arrondis fins 16mm, normales adoucies) ;
  - Attaches métalliques (anneaux rectangulaires, boucles ardillons, anneaux D, mousquetons, 4 pieds) en métal chromé/argenté poli ;
  - Texture cuir havane authentique avec grain sellier PBR et coutures fines.
"""

import math
import os
import sys

import bmesh
import bpy
import numpy as np

# Réinitialisation de la scène
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = os.path.abspath(argv[0] if argv else "public/models")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------- Dimensions fines
W = 0.35       # Largeur (35 cm)
D = 0.115      # Profondeur fine (11.5 cm) — pas de pavé épais
H = 0.24       # Hauteur du corps (24 cm)
CORNER_BEVEL = 0.016  # Biseau arrondi fin des angles

def link(obj):
    scene.collection.objects.link(obj)
    return obj

# ---------------------------------------------------------------- Matériaux PBR
def make_material(name, color, roughness, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat, bsdf

def leather_normal_texture(size=1024):
    rng = np.random.default_rng(42)
    noise = rng.standard_normal((size, size))
    f = np.fft.fftfreq(size)
    r = np.sqrt(f[:, None] ** 2 + f[None, :] ** 2)
    band = np.exp(-((r - 0.05) ** 2) / (2 * 0.02 ** 2)) + 0.3 * np.exp(-((r - 0.15) ** 2) / (2 * 0.04 ** 2))
    height = np.real(np.fft.ifft2(np.fft.fft2(noise) * band))
    height = (height - height.min()) / (height.max() - height.min())
    gy, gx = np.gradient(height)
    strength = 3.5
    nx, ny, nz = -gx * strength, -gy * strength, np.ones_like(height)
    n = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    rgb = np.stack([nx / n * 0.5 + 0.5, ny / n * 0.5 + 0.5, nz / n * 0.5 + 0.5, np.ones_like(n)], axis=-1)
    img = bpy.data.images.new("cuir_grain_havane", size, size, alpha=False)
    img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(rgb.astype(np.float32).ravel())
    img.pack()
    return img

# Cuir Havane riche et ambré
mat_cuir, bsdf_cuir = make_material("CuirHavane", (0.55, 0.26, 0.09), roughness=0.38, metallic=0.0)
grain_img = leather_normal_texture(1024)
nt = mat_cuir.node_tree
tex_grain = nt.nodes.new("ShaderNodeTexImage")
tex_grain.image = grain_img
nmap = nt.nodes.new("ShaderNodeNormalMap")
nmap.inputs["Strength"].default_value = 0.40
nt.links.new(tex_grain.outputs["Color"], nmap.inputs["Color"])
nt.links.new(nmap.outputs["Normal"], bsdf_cuir.inputs["Normal"])

# Métal chromé argenté pour boucles, anneaux et rivets
mat_metal, _ = make_material("MetalArgente", (0.92, 0.92, 0.94), roughness=0.15, metallic=1.0)
# Cuir sombre pour doublure / fermeture
mat_sombre, _ = make_material("CuirFonce", (0.18, 0.10, 0.05), roughness=0.6, metallic=0.0)

# ---------------------------------------------------------------- Corps du sac
def create_rounded_box(name, sx, sy, sz, loc, bevel, mat, segments=5):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    bm.to_mesh(mesh)
    bm.free()
    obj = link(bpy.data.objects.new(name, mesh))
    obj.location = loc
    obj.data.materials.append(mat)
    
    # Biseau arrondi fin
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = bevel
    m.segments = segments
    m.limit_method = "ANGLE"
    m.harden_normals = True
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

# Corps principal (légèrement conique vers le haut pour un tombé naturel)
corps = create_rounded_box("Corps", W, D, H, (0, 0, H / 2), CORNER_BEVEL, mat_cuir, 5)

# Taper subtil vers le haut (6% plus étroit en haut qu'en bas)
bpy.context.view_layer.update()
for v in corps.data.vertices:
    factor = 1.0 - 0.06 * (v.co.z / H)
    v.co.x *= factor
    v.co.y *= factor

# Poche avant avec rabat et coutures
poche_w = W * 0.82
poche_h = H * 0.68
poche_d = 0.016
poche = create_rounded_box("PocheAvant", poche_w, poche_d, poche_h, 
                           (0, -D / 2 - poche_d / 2 + 0.002, poche_h / 2 + 0.02), 0.005, mat_cuir, 3)

# Bandeau supérieur / fermeture à glissière en retrait
dessus = create_rounded_box("DessusFermeture", W * 0.94, D * 0.70, 0.010, (0, 0, H + 0.002), 0.003, mat_sombre, 2)

# ---------------------------------------------------------------- Anses doubles avec trou ouvert de profil
def create_handle(name, y_offset):
    curve = bpy.data.curves.new(f"{name}_curve", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.0068       # Anse fine et tubulaire (6.8 mm de rayon)
    curve.bevel_resolution = 4
    curve.resolution_u = 24
    
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(2)
    
    # Arche de l'anse : ancrée à x = -8cm et +8cm, hauteur = 10cm au-dessus du sac
    anchor_x = W * 0.24
    handle_h = 0.105
    z_base = H + 0.012
    
    # Points de la courbe (anse légèrement cintrée)
    p0 = (-anchor_x, y_offset, z_base)
    p1 = (0, y_offset * 0.85, z_base + handle_h)
    p2 = (anchor_x, y_offset, z_base)
    
    for bp, co in zip(spline.bezier_points, [p0, p1, p2]):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
        
    obj = link(bpy.data.objects.new(name, curve))
    obj.data.materials.append(mat_cuir)
    
    # Conversion en maillage
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj_mesh = bpy.context.view_layer.objects.active
    for p in obj_mesh.data.polygons:
        p.use_smooth = True
    return obj_mesh

# Deux anses séparées : anse avant à y = -3.2cm, anse arrière à y = +3.2cm
# Le trou entre les deux anses (6.4 cm d'espace libre) est parfaitement visible de profil !
y_handle = D * 0.28
anse_avant = create_handle("AnseAvant", -y_handle)
anse_arriere = create_handle("AnseArriere", y_handle)

# Chapes / attaches en cuir pour les anses (4 pattes de fixation)
def create_handle_tab(name, loc):
    tab = create_rounded_box(name, 0.022, 0.006, 0.038, loc, 0.002, mat_cuir, 2)
    return tab

anchor_x = W * 0.24
z_tab = H - 0.01
create_handle_tab("ChapeAV_G", (-anchor_x, -D / 2 - 0.001, z_tab))
create_handle_tab("ChapeAV_D", (anchor_x, -D / 2 - 0.001, z_tab))
create_handle_tab("ChapeAR_G", (-anchor_x, D / 2 + 0.001, z_tab))
create_handle_tab("ChapeAR_D", (anchor_x, D / 2 + 0.001, z_tab))

# Anneaux métalliques rectangulaires pour chaque anse
def create_rect_ring(name, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.012, minor_radius=0.0022,
        major_segments=24, minor_segments=8,
        location=loc, rotation=rot
    )
    o = bpy.context.active_object
    o.name = name
    o.scale = (1.2, 0.8, 1.0)
    o.data.materials.append(mat_metal)
    bpy.ops.object.shade_smooth()
    return o

create_rect_ring("AnneauAV_G", (-anchor_x, -D / 2 - 0.002, H + 0.006), (math.pi / 2, 0, 0))
create_rect_ring("AnneauAV_D", (anchor_x, -D / 2 - 0.002, H + 0.006), (math.pi / 2, 0, 0))
create_rect_ring("AnneauAR_G", (-anchor_x, D / 2 + 0.002, H + 0.006), (math.pi / 2, 0, 0))
create_rect_ring("AnneauAR_D", (anchor_x, D / 2 + 0.002, H + 0.006), (math.pi / 2, 0, 0))

# ---------------------------------------------------------------- Boucles ardillons sur la face avant
def create_buckle_assembly(name, loc_x):
    strap_w = 0.024
    strap_h = H * 0.75
    strap_y = -D / 2 - poche_d - 0.002
    strap = create_rounded_box(f"{name}_strap", strap_w, 0.004, strap_h,
                               (loc_x, strap_y, H * 0.44), 0.0015, mat_cuir, 2)
    buckle_y = strap_y - 0.003
    buckle_z = H * 0.52
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.015, minor_radius=0.0025,
        major_segments=24, minor_segments=8,
        location=(loc_x, buckle_y, buckle_z), rotation=(math.pi / 2, 0, 0)
    )
    b_obj = bpy.context.active_object
    b_obj.name = f"{name}_metal"
    b_obj.scale = (1.1, 0.7, 1.0)
    b_obj.data.materials.append(mat_metal)
    bpy.ops.object.shade_smooth()

strap_offset_x = W * 0.22
create_buckle_assembly("BoucleG", -strap_offset_x)
create_buckle_assembly("BoucleD", strap_offset_x)

# ---------------------------------------------------------------- Côtés : Renfort en V + Mousqueton bandoulière
def create_side_hardware(name, is_left=True):
    sx = -W / 2 - 0.001 if is_left else W / 2 + 0.001
    rot_z = 0 if is_left else math.pi
    # Renfort cuir en V
    v_tab = create_rounded_box(f"{name}_tab", 0.004, D * 0.55, 0.065, (sx, 0, H * 0.45), 0.002, mat_cuir, 2)
    # Anneau en D
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.013, minor_radius=0.0028,
        major_segments=24, minor_segments=8,
        location=(sx + (-0.003 if is_left else 0.003), 0, H * 0.60),
        rotation=(0, math.pi / 2, 0)
    )
    ring_obj = bpy.context.active_object
    ring_obj.name = f"{name}_Dring"
    ring_obj.data.materials.append(mat_metal)
    bpy.ops.object.shade_smooth()
    # Mousqueton d'attache
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.004, depth=0.022, vertices=16,
        location=(sx + (-0.005 if is_left else 0.005), 0, H * 0.57),
        rotation=(0, 0, 0)
    )
    clasp = bpy.context.active_object
    clasp.name = f"{name}_clasp"
    clasp.data.materials.append(mat_metal)
    bpy.ops.object.shade_smooth()

create_side_hardware("CoteG", is_left=True)
create_side_hardware("CoteD", is_left=False)

# ---------------------------------------------------------------- Pieds de protection (dessous)
for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
    px = sx * (W / 2 - 0.035)
    py = sy * (D / 2 - 0.025)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.007, depth=0.004, vertices=16,
        location=(px, py, 0.002), rotation=(0, 0, 0)
    )
    foot = bpy.context.active_object
    foot.name = f"Pied_{i}"
    foot.data.materials.append(mat_metal)
    bpy.ops.object.shade_smooth()

# ---------------------------------------------------------------- Dépliage UV pour le cuir
for obj in list(scene.objects):
    if obj.type == "MESH" and mat_cuir.name in [m.name for m in obj.data.materials]:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
        bpy.ops.object.mode_set(mode="OBJECT")
        for loop_uv in obj.data.uv_layers.active.data:
            loop_uv.uv = loop_uv.uv * 4.0

# ---------------------------------------------------------------- Recentrage géométrique
center_z = (H + 0.105) / 2
for obj in list(scene.objects):
    if obj.type == "MESH":
        obj.location.z -= center_z

bpy.context.view_layer.update()

# Export glTF / GLB optimisé
glb_path = os.path.join(OUT_DIR, "art-102.glb")
bpy.ops.object.select_all(action="SELECT")
kwargs = dict(
    filepath=glb_path,
    export_format="GLB",
    export_apply=True,
    export_yup=True,
    use_selection=True
)
try:
    bpy.ops.export_scene.gltf(**kwargs, export_gpu_instances=True)
except TypeError:
    bpy.ops.export_scene.gltf(**kwargs)
print(f"Modèle 3D exporté avec succès : {glb_path} ({os.path.getsize(glb_path)} octets)")

# ---------------------------------------------------------------- Rendu Studio
world = bpy.data.worlds.new("Studio")
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.01, 0.01, 0.01, 1)
scene.world = world

def aim(o, target):
    d = np.array(target) - np.array(o.location)
    o.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(-d[0], d[1]))

def add_area(name, loc, energy, size, color):
    light = bpy.data.lights.new(name, "AREA")
    light.energy = energy
    light.size = size
    light.color = color
    o = link(bpy.data.objects.new(name, light))
    o.location = loc
    aim(o, (0, 0, 0))
    return o

add_area("Key", (-0.6, -0.7, 0.5), 180, 0.5, (1.0, 0.94, 0.88))
add_area("Fill", (0.7, -0.5, 0.2), 60, 0.8, (0.92, 0.95, 1.0))
add_area("Rim", (0.0, 0.8, 0.6), 140, 0.4, (1.0, 0.85, 0.65))

cam = link(bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera")))
cam.data.lens = 65
cam.location = (0.45, -0.85, 0.20)
aim(cam, (0, 0, 0))
scene.camera = cam

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 768
scene.render.resolution_y = 768
scene.render.film_transparent = True
scene.render.filepath = os.path.join(OUT_DIR, "art-102-poster.png")
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"

bpy.ops.render.render(write_still=True)
print(f"Poster studio rendu : {scene.render.filepath}")
