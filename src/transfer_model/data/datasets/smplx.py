import os
import argparse

import pickle
import ruamel.yaml as ryaml

import torch
import numpy as np
from smplx import SMPLX

from torch.utils.data import Dataset
from pathlib import Path
import trimesh

from IPython import embed

class SMPLXDataset(Dataset):
    def __init__(self, cfg):
        self.cfg = cfg
        self.smplx_folder = cfg.datasets.mesh_folder.data_folder
        self.cfg_path = os.path.join(str(Path(self.smplx_folder).parent), "smplx_conf.yaml")
        self.base_models_path = os.path.join(cfg.body_model.folder, 'smplx')
        self.kid_template_path = os.path.join(self.base_models_path, "SMPLX_KID_TEMPLATE.npy")
        self.smplx_config = self.read_config()

        self.models_filename = sorted(os.listdir(self.smplx_folder))
        self.num_items = len(self.models_filename)
        self.num_betas = self.get_num_betas()

    def get_num_betas(self):
        model_path = os.path.join(self.smplx_folder, self.models_filename[0])
        fitted_model_params = pickle.load(open(model_path, 'rb'))
        return fitted_model_params['betas'].shape[-1]

    def read_config(self):
        config = ryaml.YAML(typ='rt')
        return config.load(open(self.cfg_path))
        
    def read_smplx_model(self):
        # read the SMPLX base template (the original models provided by the authors)
        base_model = SMPLX(model_path=self.base_models_path, 
                        model_type='smplx', 
                        num_betas=self.num_betas,
                        gender=self.smplx_config["gender"],
                        num_pca_comps=self.smplx_config["num_pca_comps"],
                        age=self.smplx_config["age"],
                        kid_template_path=self.kid_template_path,
                        )

        return base_model   

    def load_smplx(self, model_path: str):
        assert self.smplx_config is not None, "SMPLX config not loaded"
        base_model = self.read_smplx_model()   

        fitted_model_params = pickle.load(open(model_path, 'rb'))
        fitted_model_params = {k: torch.from_numpy(v) for k, v in fitted_model_params.items()}
        
        body_pose = fitted_model_params['body_pose'][..., 3:]
        smplx_model = base_model(
            betas=fitted_model_params['betas'],
            global_orient=fitted_model_params['global_orient'],
            transl=fitted_model_params['transl'],
            left_hand_pose=fitted_model_params['left_hand_pose'],
            right_hand_pose=fitted_model_params['right_hand_pose'],
            jaw_pose=fitted_model_params['jaw_pose'],
            leye_pose=fitted_model_params['leye_pose'],
            reye_pose=fitted_model_params['reye_pose'],
            expression=fitted_model_params['expression'],
            body_pose=body_pose,
            return_verts=True
        )
        
        return smplx_model, base_model

    def __len__(self) -> int:
        return self.num_items

    def __getitem__(self, index):
        model_filename = self.models_filename[index]
        model_path = os.path.join(self.smplx_folder, model_filename)

        # Load the model
        smplx_model, base_model = self.load_smplx(model_path)
        vertices = smplx_model.vertices.detach().cpu().numpy().astype(np.float32)
        faces = base_model.faces_tensor.detach().cpu().numpy().astype(np.int32)

        return {
            'vertices': vertices.squeeze(0),
            'faces': faces,
            'indices': index,
            'paths': model_path,
        }
