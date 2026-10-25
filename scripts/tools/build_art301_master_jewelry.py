"""
build_art301_master_jewelry.py — Script Maître d'Excellence Joaillère pour art-301
Projet : boutique-mode

Exécute la reconstruction intégrale du Collier Multirangs Perles de Corail (art-301)
avec le nouveau moteur paramétrique jewelry_engine.py :
- 5 rangs anatomiques concentriques (435 perles avec micro-variations physiques)
- Fermoir mousqueton réaliste en or 18k (lobster clasp, anneau de jonction, calottes)
- Shaders PBR avancés (diffusion sous-surfacique, lustre nacré, or poli anisotrope)
- Export GLB WebGL manifold et rendu du poster HD
"""

import os
import sys
import math
import bpy

# Add 3d_pipeline to path
curr_dir = os.path.dirname(os.path.abspath(__file__))
pipeline_dir = os.path.abspath(os.path.join(curr_dir, "..", "3d_pipeline"))
if pipeline_dir not in sys.path:
    sys.path.append(pipeline_dir)

import jewelry_engine

def build_master_necklace():
    # 1. Reset factory scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # 2. Setup materials
    mats = jewelry_engine.create_luxury_jewelry_materials()
    
    # 3. Paramètres des 5 rangs concentriques
    # Motifs :
    # Rang 1 (intérieur ras-du-cou) : perles bordeaux d'accent + or
    # Rang 2 & 3 : alternance corail & intercalaires or
    # Rang 4 : perles blanches nacrées & corail
    # Rang 5 (extérieur large) : perles de corail rouge et perles d'or
    tier_configs = [
        {
            "tier": 1,
            "num_beads": 68,
            "a_radius": 0.082,
            "b_radius": 0.078,
            "z_drop": 0.016,
            "y_chest_curve": 0.012,
            "pattern": ["burgundy", "gold", "coral", "gold", "pearl", "gold"]
        },
        {
            "tier": 2,
            "num_beads": 78,
            "a_radius": 0.092,
            "b_radius": 0.088,
            "z_drop": 0.026,
            "y_chest_curve": 0.018,
            "pattern": ["coral", "coral", "gold", "coral", "pearl", "gold"]
        },
        {
            "tier": 3,
            "num_beads": 88,
            "a_radius": 0.103,
            "b_radius": 0.098,
            "z_drop": 0.038,
            "y_chest_curve": 0.024,
            "pattern": ["coral", "gold", "coral", "coral", "gold"]
        },
        {
            "tier": 4,
            "num_beads": 96,
            "a_radius": 0.114,
            "b_radius": 0.108,
            "z_drop": 0.052,
            "y_chest_curve": 0.030,
            "pattern": ["pearl", "coral", "gold", "coral", "pearl", "gold"]
        },
        {
            "tier": 5,
            "num_beads": 105,
            "a_radius": 0.125,
            "b_radius": 0.118,
            "z_drop": 0.068,
            "y_chest_curve": 0.036,
            "pattern": ["coral", "coral", "coral", "gold", "coral", "gold"]
        }
    ]
    
    print("Génération des 5 rangs de perles...")
    bead_groups = jewelry_engine.generate_necklace_beads(tier_configs, seed=108)
    
    # Fusionner chaque groupe de matériau en un seul Mesh unifié pour minimiser les draw calls WebGL
    final_objects = []
    
    for mat_key, objs in bead_groups.items():
        if not objs:
            continue
        print(f"Fusion de {len(objs)} perles pour {mat_key}...")
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.join()
        
        joined = bpy.context.active_object
        joined.name = f"Collier_Perles_{mat_key.capitalize()}"
        
        # Assigner matériau PBR
        mat_target = mats[mat_key]
        if joined.data.materials:
            joined.data.materials[0] = mat_target
        else:
            joined.data.materials.append(mat_target)
            
        # Smooth shading
        bpy.ops.object.shade_smooth()
        final_objects.append(joined)
        bpy.ops.object.select_all(action='DESELECT')
        
    # 4. Ajouter le vrai fermoir joaillerie à l'arrière du cou (y > 0)
    # L'arrière du rang 1 se trouve à y = +b_radius = +0.078
    clasp_loc = (0.0, 0.078, 0.002)
    clasp = jewelry_engine.build_luxury_lobster_clasp(clasp_loc, scale=0.009)
    if clasp.data.materials:
        clasp.data.materials[0] = mats["gold"]
    else:
        clasp.data.materials.append(mats["gold"])
    bpy.ops.object.shade_smooth()
    final_objects.append(clasp)
    
    # 5. Centrage global et ajustement d'envergure
    # Calcul de la boîte englobante
    min_x = min_y = min_z = 1e9
    max_x = max_y = max_z = -1e9
    for obj in final_objects:
        for v in obj.data.vertices:
            wpos = obj.matrix_world @ v.co
            min_x = min(min_x, wpos.x)
            max_x = max(max_x, wpos.x)
            min_y = min(min_y, wpos.y)
            max_y = max(max_y, wpos.y)
            min_z = min(min_z, wpos.z)
            max_z = max(max_z, wpos.z)
            
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    cz = (min_z + max_z) / 2.0
    
    for obj in final_objects:
        obj.location.x -= cx
        obj.location.y -= cy
        obj.location.z -= cz
        
    print(f"Modèle assemblé avec succès : {len(final_objects)} objets unifiés.")
    return final_objects


def render_showcase(output_glb, output_poster, multi_angle_dir=None):
    os.makedirs(os.path.dirname(output_glb), exist_ok=True)
    os.makedirs(os.path.dirname(output_poster), exist_ok=True)
    
    # Export GLB
    bpy.ops.export_scene.gltf(
        filepath=output_glb,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT'
    )
    print(f"GLB exporté : {output_glb} ({os.path.getsize(output_glb)} octets)")
    
    # Setup Studio Lighting for Poster & Multi-angle views
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    scene.render.film_transparent = True
    
    # Camera
    cam_data = bpy.data.cameras.new("Studio_Cam")
    cam_data.lens = 75
    cam_obj = bpy.data.objects.new("Studio_Cam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # 3-Point Luxury Studio Lights
    # Key light (chaude)
    key_l = bpy.data.lights.new("Key_Gold", type='AREA')
    key_l.energy = 80.0
    key_l.size = 0.5
    key_l.color = (1.0, 0.95, 0.88)
    key_obj = bpy.data.objects.new("Key_Gold", key_l)
    key_obj.location = (0.35, -0.40, 0.35)
    bpy.context.collection.objects.link(key_obj)
    
    # Fill light (douce)
    fill_l = bpy.data.lights.new("Fill_Soft", type='AREA')
    fill_l.energy = 35.0
    fill_l.size = 0.8
    fill_l.color = (0.90, 0.94, 1.0)
    fill_obj = bpy.data.objects.new("Fill_Soft", fill_l)
    fill_obj.location = (-0.40, -0.30, 0.20)
    bpy.context.collection.objects.link(fill_obj)
    
    # Rim light (pour faire scintiller les perles et l'or)
    rim_l = bpy.data.lights.new("Rim_Sparkle", type='POINT')
    rim_l.energy = 50.0
    rim_l.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("Rim_Sparkle", rim_l)
    rim_obj.location = (0.0, 0.40, 0.30)
    bpy.context.collection.objects.link(rim_obj)
    
    # Setup camera track constraint
    empty = bpy.data.objects.new("LookTarget", None)
    bpy.context.collection.objects.link(empty)
    empty.location = (0, 0, 0)
    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    
    # Poster Render (Vue de face légèrement plongeante à 15°)
    dist = 0.46
    cam_obj.location = (0.0, -dist * math.cos(math.radians(15)), dist * math.sin(math.radians(15)))
    scene.render.filepath = output_poster
    bpy.ops.render.render(write_still=True)
    print(f"Poster rendu : {output_poster}")
    
    # Multi-angle renders if requested
    if multi_angle_dir:
        os.makedirs(multi_angle_dir, exist_ok=True)
        angles = [
            ("front_0", 0, 15),
            ("angle_35", 35, 20),
            ("side_90", 90, 10),
            ("back_180", 180, 20)
        ]
        for name, yaw, pitch in angles:
            ry = -dist * math.cos(math.radians(pitch)) * math.cos(math.radians(yaw))
            rx = dist * math.cos(math.radians(pitch)) * math.sin(math.radians(yaw))
            rz = dist * math.sin(math.radians(pitch))
            cam_obj.location = (rx, ry, rz)
            p = os.path.join(multi_angle_dir, f"art301_{name}.png")
            scene.render.filepath = p
            bpy.ops.render.render(write_still=True)
            print(f"Rendu {name} sauvegardé : {p}")


if __name__ == "__main__":
    out_glb = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\public\models\art-301.glb"
    out_poster = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\public\models\art-301-poster.png"
    multi_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic\masterpiece_views"
    
    build_master_necklace()
    render_showcase(out_glb, out_poster, multi_dir)
    print("RECONSTRUCTION JOAILLIÈRE TERMINÉE AVEC SUCCÈS !")
