"""
materials.py — Bibliothèque Universelle & Luxe de Matériaux PBR pour Blender 5.x
Fournit des shaders Principled BSDF étalonnés selon la physique des matériaux.
Compatible mode, maroquinerie, horlogerie, design produit et architecture.
"""

import bpy

MATERIAL_PRESETS = {
    # 1. Laques et Céramiques
    "white_satin_lacquer": {
        "base_color": (0.918, 0.922, 0.926, 1.0),
        "roughness": 0.26,
        "metallic": 0.0,
        "specular_ior_level": 0.50,
        "coat_weight": 0.14,
        "coat_roughness": 0.16,
        "coat_ior": 1.50
    },
    "glazed_ceramic_white": {
        "base_color": (0.940, 0.945, 0.950, 1.0),
        "roughness": 0.10,
        "metallic": 0.0,
        "specular_ior_level": 0.55,
        "coat_weight": 0.40,
        "coat_roughness": 0.08,
        "coat_ior": 1.52
    },
    "glazed_ceramic_terracotta": {
        "base_color": (0.780, 0.420, 0.260, 1.0),
        "roughness": 0.14,
        "metallic": 0.0,
        "specular_ior_level": 0.52,
        "coat_weight": 0.35,
        "coat_roughness": 0.10,
        "coat_ior": 1.52
    },

    # 2. Métaux Industriels et Horlogers
    "polished_chrome": {
        "base_color": (0.970, 0.970, 0.970, 1.0),
        "roughness": 0.065,
        "metallic": 1.0,
        "specular_ior_level": 0.50,
        "coat_weight": 0.0
    },
    "brushed_stainless": {
        "base_color": (0.865, 0.875, 0.885, 1.0),
        "roughness": 0.23,
        "metallic": 0.99,
        "anisotropic": 0.75,
        "anisotropic_rotation": 0.0,
        "coat_weight": 0.0
    },
    "anodized_aluminum": {
        "base_color": (0.750, 0.760, 0.770, 1.0),
        "roughness": 0.30,
        "metallic": 0.95,
        "anisotropic": 0.30,
        "coat_weight": 0.0
    },

    # 3. Polymères et Caoutchoucs
    "dark_polymer": {
        "base_color": (0.065, 0.065, 0.065, 1.0),
        "roughness": 0.36,
        "metallic": 0.0,
        "specular_ior_level": 0.52,
        "coat_weight": 0.0
    },
    "light_gray_base": {
        "base_color": (0.750, 0.760, 0.770, 1.0),
        "roughness": 0.48,
        "metallic": 0.0,
        "specular_ior_level": 0.50,
        "coat_weight": 0.0
    },
    "matte_rubber": {
        "base_color": (0.025, 0.025, 0.025, 1.0),
        "roughness": 0.88,
        "metallic": 0.0,
        "specular_ior_level": 0.35,
        "coat_weight": 0.0
    },

    # 4. Matières Naturelles et Textiles
    "natural_wood": {
        "base_color": (0.720, 0.540, 0.380, 1.0),
        "roughness": 0.52,
        "metallic": 0.0,
        "specular_ior_level": 0.45,
        "coat_weight": 0.0
    },
    "dark_acoustic_fabric": {
        "base_color": (0.080, 0.080, 0.090, 1.0),
        "roughness": 0.92,
        "metallic": 0.0,
        "specular_ior_level": 0.30,
        "sheen_weight": 0.40,
        "sheen_roughness": 0.50,
        "coat_weight": 0.0
    },
    "satin_silk_fabric": {
        "base_color": (0.850, 0.830, 0.800, 1.0),
        "roughness": 0.30,
        "metallic": 0.0,
        "specular_ior_level": 0.45,
        "sheen_weight": 0.75,
        "sheen_roughness": 0.30
    },
    "suede_nubuck": {
        "base_color": (0.550, 0.450, 0.360, 1.0),
        "roughness": 0.85,
        "metallic": 0.0,
        "specular_ior_level": 0.25,
        "sheen_weight": 0.60
    },
    "contemporary_lounge_fabric": {
        "base_color": (0.650, 0.620, 0.580, 1.0),
        "roughness": 0.88,
        "metallic": 0.0,
        "specular_ior_level": 0.35,
        "sheen_weight": 0.50,
        "sheen_roughness": 0.60
    },

    # 5. Maroquinerie & Cuirs Luxe
    "luxury_leather_black": {
        "base_color": (0.040, 0.040, 0.045, 1.0),
        "roughness": 0.38,
        "metallic": 0.0,
        "specular_ior_level": 0.52,
        "coat_weight": 0.12,
        "coat_roughness": 0.25
    },
    "luxury_leather_cognac": {
        "base_color": (0.480, 0.220, 0.090, 1.0),
        "roughness": 0.42,
        "metallic": 0.0,
        "specular_ior_level": 0.50,
        "coat_weight": 0.10,
        "coat_roughness": 0.28
    },
    "luxury_leather_bordeaux": {
        "base_color": (0.320, 0.050, 0.080, 1.0),
        "roughness": 0.35,
        "metallic": 0.0,
        "specular_ior_level": 0.52,
        "coat_weight": 0.15,
        "coat_roughness": 0.20
    },

    # 6. Bijouterie & Bouclerie Luxe
    "brushed_brass_gold": {
        "base_color": (0.920, 0.780, 0.380, 1.0),
        "roughness": 0.24,
        "metallic": 0.98,
        "anisotropic": 0.65,
        "specular_ior_level": 0.60
    },
    "luxury_gold_polished": {
        "base_color": (1.000, 0.820, 0.350, 1.0),
        "roughness": 0.08,
        "metallic": 1.00,
        "specular_ior_level": 0.65
    },

    # 7. Éclairage & Éléments Techniques
    "emissive_led_ring": {
        "base_color": (1.0, 1.0, 1.0, 1.0),
        "emission_color": (0.35, 0.75, 1.0, 1.0),
        "emission_strength": 4.0,
        "roughness": 0.20,
        "metallic": 0.0
    },
    "dark_cavity": {
        "base_color": (0.015, 0.015, 0.015, 1.0),
        "roughness": 0.95,
        "metallic": 0.0,
        "specular_ior_level": 0.10,
        "coat_weight": 0.0
    },
    "clear_glass": {
        "base_color": (0.980, 0.980, 0.990, 1.0),
        "roughness": 0.02,
        "metallic": 0.0,
        "transmission_weight": 0.95,
        "ior": 1.52,
        "specular_ior_level": 0.55
    }
}


def get_or_create_material(name, preset_key=None, custom_params=None):
    """
    Récupère ou crée un matériau Principled BSDF à partir d'un preset ou de paramètres personnalisés.
    Garantit la compatibilité ascendante Blender 5.x.
    """
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf:
        bsdf = nodes.new(type='BSDF_PRINCIPLED')
        out_node = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if not out_node:
            out_node = nodes.new(type='OUTPUT_MATERIAL')
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    # Fusion des paramètres
    params = {}
    if preset_key and preset_key in MATERIAL_PRESETS:
        params.update(MATERIAL_PRESETS[preset_key])
    if custom_params:
        params.update(custom_params)

    # Application des paramètres sur le Principled BSDF
    if "base_color" in params:
        bsdf.inputs["Base Color"].default_value = params["base_color"]
    if "roughness" in params:
        bsdf.inputs["Roughness"].default_value = params["roughness"]
    if "metallic" in params:
        bsdf.inputs["Metallic"].default_value = params["metallic"]
    if "specular_ior_level" in params and "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = params["specular_ior_level"]
    if "anisotropic" in params and "Anisotropic" in bsdf.inputs:
        bsdf.inputs["Anisotropic"].default_value = params["anisotropic"]
    if "anisotropic_rotation" in params and "Anisotropic Rotation" in bsdf.inputs:
        bsdf.inputs["Anisotropic Rotation"].default_value = params["anisotropic_rotation"]
    if "coat_weight" in params and "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = params["coat_weight"]
    if "coat_roughness" in params and "Coat Roughness" in bsdf.inputs:
        bsdf.inputs["Coat Roughness"].default_value = params.get("coat_roughness", 0.15)
    if "coat_ior" in params and "Coat IOR" in bsdf.inputs:
        bsdf.inputs["Coat IOR"].default_value = params.get("coat_ior", 1.50)
    if "sheen_weight" in params and "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = params["sheen_weight"]
    if "sheen_roughness" in params and "Sheen Roughness" in bsdf.inputs:
        bsdf.inputs["Sheen Roughness"].default_value = params.get("sheen_roughness", 0.30)
    if "transmission_weight" in params and "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = params["transmission_weight"]
    if "ior" in params and "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = params["ior"]
    if "emission_color" in params and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = params["emission_color"]
    if "emission_strength" in params and "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = params["emission_strength"]

    return mat
