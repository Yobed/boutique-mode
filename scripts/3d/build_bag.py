"""
ELSI — structured top-handle bag, built procedurally for the web viewer.

Run headless (Blender 4.2+ / 5.x):
  blender -b --factory-startup --python scripts/3d/build_bag.py -- <out_dir>

Outputs in <out_dir>:
  sac-elsi-raw.glb       high detail (compressed later by gltf-transform)
  sac-elsi-low-raw.glb   simplified mesh + 512px texture (mobile / distance)
  sac-elsi-poster.png    studio render used as poster and 2D fallback

Materials keep stable names the web viewer relies on:
  "Cuir"   leather (colour swapped at runtime: Noir / Bordeaux / Cognac)
  "Laiton" brushed brass hardware
  "Fil"    saddle-stitch thread
Repeated parts (4 feet, ~68 stitches) are linked duplicates, exported as GPU instances.
"""

import math
import os
import sys

import bmesh
import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0] if argv else "public/3d/raw")
os.makedirs(OUT, exist_ok=True)

W, D, H = 0.28, 0.11, 0.20          # bag body, metres
TAPER = 0.08                         # top is 8% narrower than the base
FLAP_H = 0.12


def taper(z):
    return 1.0 - TAPER * max(0.0, min(z, H)) / H


# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def link(obj):
    scene.collection.objects.link(obj)
    return obj


def box(name, sx, sy, sz, loc, mat):
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
    return obj


def apply_taper(obj):
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    inv = mw.inverted()
    for v in obj.data.vertices:
        w = mw @ v.co
        w.x *= taper(w.z)
        v.co = inv @ w


def finish(obj, bevel, segments=4):
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = bevel
    m.segments = segments
    m.limit_method = "ANGLE"
    m.harden_normals = True
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


# ---------------------------------------------------------------- materials
def principled(name, color, rough, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat, bsdf


def leather_grain(size):
    """Pebble grain normal map: band-passed noise -> height -> tangent-space normals."""
    rng = np.random.default_rng(7)
    noise = rng.standard_normal((size, size))
    f = np.fft.fftfreq(size)
    r = np.sqrt(f[:, None] ** 2 + f[None, :] ** 2)
    band = np.exp(-((r - 0.045) ** 2) / (2 * 0.018 ** 2)) + 0.25 * np.exp(-((r - 0.16) ** 2) / (2 * 0.05 ** 2))
    height = np.real(np.fft.ifft2(np.fft.fft2(noise) * band))
    height = (height - height.min()) / (height.max() - height.min())
    height = np.power(height, 0.8)  # rounder pebbles
    gy, gx = np.gradient(height)
    strength = 6.0
    nx, ny, nz = -gx * strength, -gy * strength, np.ones_like(height)
    n = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    rgb = np.stack([nx / n * 0.5 + 0.5, ny / n * 0.5 + 0.5, nz / n * 0.5 + 0.5, np.ones_like(n)], axis=-1)
    img = bpy.data.images.new("cuir_grain", size, size, alpha=False)
    img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(rgb.astype(np.float32).ravel())
    img.file_format = "PNG"
    img.pack()
    return img


cuir, cuir_bsdf = principled("Cuir", (0.018, 0.016, 0.015), 0.52)
grain = leather_grain(1024)
nt = cuir.node_tree
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = grain
nmap = nt.nodes.new("ShaderNodeNormalMap")
nmap.inputs["Strength"].default_value = 0.6
nt.links.new(tex.outputs["Color"], nmap.inputs["Color"])
nt.links.new(nmap.outputs["Normal"], cuir_bsdf.inputs["Normal"])

laiton, _ = principled("Laiton", (0.80, 0.62, 0.34), 0.28, 1.0)
fil, _ = principled("Fil", (0.62, 0.55, 0.45), 0.8)

# ---------------------------------------------------------------- body + flap
body = box("Corps", W, D, H, (0, 0, H / 2), cuir)
top = box("Dessus", W * 0.985, D * 0.9, 0.006, (0, 0, H + 0.003), cuir)
flap = box("Rabat", W * 1.012, 0.006, FLAP_H, (0, -D / 2 - 0.003, H - FLAP_H / 2 + 0.003), cuir)
for o in (body, top, flap):
    apply_taper(o)
finish(body, 0.016, 5)
finish(top, 0.0025, 2)
finish(flap, 0.0025, 3)

# ---------------------------------------------------------------- handle
curve = bpy.data.curves.new("PoigneeCourbe", "CURVE")
curve.dimensions = "3D"
curve.bevel_depth = 0.0075
curve.bevel_resolution = 4
curve.resolution_u = 24
spline = curve.splines.new("BEZIER")
spline.bezier_points.add(2)
pts = [(-0.075, 0, H + 0.012), (0, 0, H + 0.115), (0.075, 0, H + 0.012)]
for bp, co in zip(spline.bezier_points, pts):
    bp.co = co
    bp.handle_left_type = bp.handle_right_type = "AUTO"
handle_curve = link(bpy.data.objects.new("Poignee", curve))
handle_curve.data.materials.append(cuir)
bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = handle_curve
handle_curve.select_set(True)
bpy.ops.object.convert(target="MESH")
handle = bpy.context.view_layer.objects.active
for p in handle.data.polygons:
    p.use_smooth = True


# ---------------------------------------------------------------- brass hardware
def ring(name, loc):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.0095, minor_radius=0.0026, major_segments=32, minor_segments=12, location=loc, rotation=(math.pi / 2, 0, 0))
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(laiton)
    bpy.ops.object.shade_smooth()
    return o


ring("AnneauG", (-0.075, 0, H + 0.012))
ring("AnneauD", (0.075, 0, H + 0.012))

plate = box("Fermoir", 0.054, 0.006, 0.024, (0, -D / 2 - 0.0085, H - FLAP_H + 0.016), laiton)
finish(plate, 0.002, 3)
bpy.ops.mesh.primitive_cylinder_add(radius=0.0085, depth=0.007, vertices=40, location=(0, -D / 2 - 0.0125, H - FLAP_H + 0.016), rotation=(math.pi / 2, 0, 0))
lock = bpy.context.active_object
lock.name = "Tourniquet"
lock.data.materials.append(laiton)
finish(lock, 0.0012, 2)

# Feet: one mesh, four linked duplicates -> GPU instances
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.008, segments=24, ring_count=12, location=(0, 0, 0))
foot = bpy.context.active_object
foot.name = "Pied"
foot.data.materials.append(laiton)
bpy.ops.object.shade_smooth()
fx, fy = W / 2 - 0.028, D / 2 - 0.022
for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
    o = foot if i == 0 else link(bpy.data.objects.new(f"Pied.{i}", foot.data))
    o.location = (sx * fx * taper(0), sy * fy, 0.001)
    o.scale = (1, 1, 0.55)

# Saddle stitches around the flap: one mesh, many linked duplicates
bpy.ops.mesh.primitive_cylinder_add(radius=0.0009, depth=0.0042, vertices=8, location=(0, 0, 0))
stitch = bpy.context.active_object
stitch.name = "Point"
stitch.data.materials.append(fil)
inset, step = 0.007, 0.0072
y_front = -D / 2 - 0.0062
z_top, z_bot = H - 0.004, H - FLAP_H + inset + 0.003


def half(z):
    return (W * 1.012 / 2) * taper(z) - inset


path = [
    ((-half(z_top), z_top), (-half(z_bot), z_bot)),
    ((-half(z_bot), z_bot), (half(z_bot), z_bot)),
    ((half(z_bot), z_bot), (half(z_top), z_top)),
]
count = 0
for (x0, z0), (x1, z1) in path:
    length = math.hypot(x1 - x0, z1 - z0)
    n = int(length / step)
    ang = math.atan2(z1 - z0, x1 - x0)
    for k in range(n):
        t = (k + 0.5) / n
        o = stitch if count == 0 else link(bpy.data.objects.new(f"Point.{count}", stitch.data))
        o.location = (x0 + (x1 - x0) * t, y_front, z0 + (z1 - z0) * t)
        o.rotation_euler = (0, -ang + math.pi / 2, 0)
        count += 1
print(f"stitches: {count}")

# ---------------------------------------------------------------- UVs for leather parts
for o in (body, top, flap, handle):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    for loop_uv in o.data.uv_layers.active.data:  # tile the grain 3x
        loop_uv.uv = loop_uv.uv * 3.0

# One root node so the web viewer rotates a single transform
root = link(bpy.data.objects.new("SacELSI", None))
for o in list(scene.objects):
    if o is not root and o.parent is None:
        o.parent = root
bpy.context.view_layer.update()


def export(path):
    bpy.ops.object.select_all(action="SELECT")
    kwargs = dict(filepath=path, export_format="GLB", export_apply=True, export_yup=True, use_selection=True)
    try:
        bpy.ops.export_scene.gltf(**kwargs, export_gpu_instances=True)
    except TypeError:
        bpy.ops.export_scene.gltf(**kwargs)
    print("exported", path, os.path.getsize(path))


export(os.path.join(OUT, "sac-elsi-raw.glb"))

# ---------------------------------------------------------------- poster render
world = bpy.data.worlds.new("Studio")
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.0105, 0.0085, 0.0075, 1)
scene.world = world


def aim(o, target):
    """Point an object's local -Z (cameras, lights) at target: pitch about X, then yaw about Z."""
    d = np.array(target) - np.array(o.location)
    o.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(-d[0], d[1]))


def area(name, loc, energy, size, color):
    light = bpy.data.lights.new(name, "AREA")
    light.energy = energy
    light.size = size
    light.color = color
    o = link(bpy.data.objects.new(name, light))
    o.location = loc
    aim(o, (0, 0, H * 0.55))
    return o


area("Key", (-0.55, -0.6, 0.65), 55, 0.6, (1.0, 0.93, 0.84))
area("Fill", (0.7, -0.45, 0.25), 12, 0.9, (0.92, 0.94, 1.0))
area("Rim", (0.25, 0.75, 0.55), 70, 0.35, (1.0, 0.82, 0.55))
box("Sol", 4, 4, 0.002, (0, 0, -0.001), principled("Sol", (0.011, 0.009, 0.008), 0.9)[0])

cam = link(bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera")))
cam.data.lens = 70
cam.location = (0.62, -0.78, 0.36)
aim(cam, (0, 0, H * 0.52))
scene.camera = cam

scene.render.engine = "CYCLES"
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 960, 1200
scene.render.image_settings.file_format = "PNG"
try:
    scene.view_settings.view_transform = "AgX"
except TypeError:
    pass
scene.render.filepath = os.path.join(OUT, "sac-elsi-poster.png")
bpy.ops.render.render(write_still=True)
print("poster", scene.render.filepath)

for name in ("Sol", "Key", "Fill", "Rim", "Camera"):
    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

# ---------------------------------------------------------------- low LOD
for o in (body, top, flap):
    for m in o.modifiers:
        if m.type == "BEVEL":
            m.segments = 1
dec = handle.modifiers.new("Decimate", "DECIMATE")
dec.ratio = 0.35
grain.scale(512, 512)
grain.pack()
export(os.path.join(OUT, "sac-elsi-low-raw.glb"))
print("done")
