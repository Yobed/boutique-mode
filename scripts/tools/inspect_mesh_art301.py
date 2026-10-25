import os
import trimesh
import numpy as np

glb_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\3d_neural\art-301\mesh.glb"
scene = trimesh.load(glb_p)
if isinstance(scene, trimesh.Scene):
    mesh = scene.dump(concatenate=True)
else:
    mesh = scene

print(f"Mesh vertices: {len(mesh.vertices)}, faces: {len(mesh.faces)}")
print(f"is_watertight: {mesh.is_watertight}")
print(f"Euler number: {mesh.euler_number}")
print(f"Bounds: min={mesh.bounds[0]}, max={mesh.bounds[1]}")
dims = mesh.bounds[1] - mesh.bounds[0]
print(f"Dimensions (dx, dy, dz): {dims}")

# Check components
components = mesh.split(only_watertight=False)
print(f"Number of connected components in 3D mesh: {len(components)}")
for i, c in enumerate(components[:5]):
    print(f"  Comp {i}: {len(c.vertices)} vertices, {len(c.faces)} faces, watertight={c.is_watertight}")

# Check thickness along Z
z_vals = mesh.vertices[:, 2]
print(f"Z span: {z_vals.min():.4f} to {z_vals.max():.4f}, thickness={z_vals.max() - z_vals.min():.4f}")
