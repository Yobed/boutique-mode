import math
import os
from dataclasses import dataclass, field
from typing import List, Union

import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F
import trimesh
from einops import rearrange
from huggingface_hub import hf_hub_download
from omegaconf import OmegaConf
from PIL import Image

from .models.isosurface import MarchingCubeHelper
from .utils import (
    BaseModule,
    ImagePreprocessor,
    find_class,
    get_spherical_cameras,
    scale_tensor,
)


QUERY_CHUNK = 200_000  # points interrogés par appel, borne la mémoire pendant extract_mesh

# Noms des couches ViT : transformers 4.35 (checkpoint) -> transformers 5.x (modèle instancié)
_VIT_KEY_RULES = [
    (r"\.encoder\.layer\.(\d+)\.attention\.attention\.query\.", r".layers.\1.attention.q_proj."),
    (r"\.encoder\.layer\.(\d+)\.attention\.attention\.key\.", r".layers.\1.attention.k_proj."),
    (r"\.encoder\.layer\.(\d+)\.attention\.attention\.value\.", r".layers.\1.attention.v_proj."),
    (r"\.encoder\.layer\.(\d+)\.attention\.output\.dense\.", r".layers.\1.attention.o_proj."),
    (r"\.encoder\.layer\.(\d+)\.intermediate\.dense\.", r".layers.\1.mlp.fc1."),
    (r"\.encoder\.layer\.(\d+)\.output\.dense\.", r".layers.\1.mlp.fc2."),
    (r"\.encoder\.layer\.(\d+)\.", r".layers.\1."),
]


def _convert_vit_keys(state_dict):
    import re

    converted = {}
    for key, tensor in state_dict.items():
        for pattern, repl in _VIT_KEY_RULES:
            key = re.sub(pattern, repl, key)
        converted[key] = tensor
    return converted


class TSR(BaseModule):
    @dataclass
    class Config(BaseModule.Config):
        cond_image_size: int

        image_tokenizer_cls: str
        image_tokenizer: dict

        tokenizer_cls: str
        tokenizer: dict

        backbone_cls: str
        backbone: dict

        post_processor_cls: str
        post_processor: dict

        decoder_cls: str
        decoder: dict

        renderer_cls: str
        renderer: dict

    cfg: Config

    @classmethod
    def from_pretrained(
        cls, pretrained_model_name_or_path: str, config_name: str, weight_name: str
    ):
        if os.path.isdir(pretrained_model_name_or_path):
            config_path = os.path.join(pretrained_model_name_or_path, config_name)
            weight_path = os.path.join(pretrained_model_name_or_path, weight_name)
        else:
            config_path = hf_hub_download(
                repo_id=pretrained_model_name_or_path, filename=config_name
            )
            weight_path = hf_hub_download(
                repo_id=pretrained_model_name_or_path, filename=weight_name
            )

        cfg = OmegaConf.load(config_path)
        OmegaConf.resolve(cfg)
        # ponytail: device meta + mmap + assign : aucune copie des 1,7 Go de poids
        with torch.device("meta"):
            model = cls(cfg)
        ckpt = torch.load(weight_path, map_location="cpu", mmap=True, weights_only=True)
        # transformers >= 5 a renommé les couches ViT ; avec 4.x les noms du checkpoint conviennent déjà
        if not any(".encoder.layer." in key for key in model.state_dict()):
            ckpt = _convert_vit_keys(ckpt)
        model.load_state_dict(ckpt, assign=True)
        leftover = [n for n, t in [*model.named_parameters(), *model.named_buffers()] if t.device.type == "meta"]
        if leftover:
            raise RuntimeError(f"Tenseurs restés sur meta après chargement : {leftover[:5]}")
        return model

    def configure(self):
        self.image_tokenizer = find_class(self.cfg.image_tokenizer_cls)(
            self.cfg.image_tokenizer
        )
        self.tokenizer = find_class(self.cfg.tokenizer_cls)(self.cfg.tokenizer)
        self.backbone = find_class(self.cfg.backbone_cls)(self.cfg.backbone)
        self.post_processor = find_class(self.cfg.post_processor_cls)(
            self.cfg.post_processor
        )
        self.decoder = find_class(self.cfg.decoder_cls)(self.cfg.decoder)
        self.renderer = find_class(self.cfg.renderer_cls)(self.cfg.renderer)
        self.image_processor = ImagePreprocessor()
        self.isosurface_helper = None

    def forward(
        self,
        image: Union[
            PIL.Image.Image,
            np.ndarray,
            torch.FloatTensor,
            List[PIL.Image.Image],
            List[np.ndarray],
            List[torch.FloatTensor],
        ],
        device: str,
    ) -> torch.FloatTensor:
        rgb_cond = self.image_processor(image, self.cfg.cond_image_size)[:, None].to(
            device
        )
        batch_size = rgb_cond.shape[0]

        input_image_tokens: torch.Tensor = self.image_tokenizer(
            rearrange(rgb_cond, "B Nv H W C -> B Nv C H W", Nv=1),
        )

        input_image_tokens = rearrange(
            input_image_tokens, "B Nv C Nt -> B (Nv Nt) C", Nv=1
        )

        tokens: torch.Tensor = self.tokenizer(batch_size)

        tokens = self.backbone(
            tokens,
            encoder_hidden_states=input_image_tokens,
        )

        scene_codes = self.post_processor(self.tokenizer.detokenize(tokens))
        return scene_codes

    def render(
        self,
        scene_codes,
        n_views: int,
        elevation_deg: float = 0.0,
        camera_distance: float = 1.9,
        fovy_deg: float = 40.0,
        height: int = 256,
        width: int = 256,
        return_type: str = "pil",
    ):
        rays_o, rays_d = get_spherical_cameras(
            n_views, elevation_deg, camera_distance, fovy_deg, height, width
        )
        rays_o, rays_d = rays_o.to(scene_codes.device), rays_d.to(scene_codes.device)

        def process_output(image: torch.FloatTensor):
            if return_type == "pt":
                return image
            elif return_type == "np":
                return image.detach().cpu().numpy()
            elif return_type == "pil":
                return Image.fromarray(
                    (image.detach().cpu().numpy() * 255.0).astype(np.uint8)
                )
            else:
                raise NotImplementedError

        images = []
        for scene_code in scene_codes:
            images_ = []
            for i in range(n_views):
                with torch.no_grad():
                    image = self.renderer(
                        self.decoder, scene_code, rays_o[i], rays_d[i]
                    )
                images_.append(process_output(image))
            images.append(images_)

        return images

    def set_marching_cubes_resolution(self, resolution: int):
        if (
            self.isosurface_helper is not None
            and self.isosurface_helper.resolution == resolution
        ):
            return
        self.isosurface_helper = MarchingCubeHelper(resolution)

    def extract_mesh(self, scene_codes, has_vertex_color, resolution: int = 256, threshold: float = 25.0):
        self.set_marching_cubes_resolution(resolution)
        meshes = []
        for scene_code in scene_codes:
            with torch.no_grad():
                grid = scale_tensor(
                    self.isosurface_helper.grid_vertices.to(scene_codes.device),
                    self.isosurface_helper.points_range,
                    (-self.renderer.cfg.radius, self.renderer.cfg.radius),
                )
                density = torch.cat([
                    self.renderer.query_triplane(
                        self.decoder, grid[i:i + QUERY_CHUNK], scene_code
                    )["density_act"]
                    for i in range(0, grid.shape[0], QUERY_CHUNK)
                ])
            v_pos, t_pos_idx = self.isosurface_helper(-(density - threshold))
            v_pos = scale_tensor(
                v_pos,
                self.isosurface_helper.points_range,
                (-self.renderer.cfg.radius, self.renderer.cfg.radius),
            )
            color = None
            if has_vertex_color:
                with torch.no_grad():
                    color = torch.cat([
                        self.renderer.query_triplane(
                            self.decoder, v_pos[i:i + QUERY_CHUNK], scene_code
                        )["color"]
                        for i in range(0, v_pos.shape[0], QUERY_CHUNK)
                    ])
            mesh = trimesh.Trimesh(
                vertices=v_pos.cpu().numpy(),
                faces=t_pos_idx.cpu().numpy(),
                vertex_colors=color.cpu().numpy() if has_vertex_color else None,
            )
            meshes.append(mesh)
        return meshes
