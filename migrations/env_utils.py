# -*- coding: utf-8 -*-
import importlib
import os


def create_folder_if_not_exists(folder_path: str):
    """특정 폴더가 없으면 생성"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"폴더 생성됨: {folder_path}")
    else:
        print(f"폴더가 이미 존재합니다: {folder_path}")


def load_models():
    import pkgutil

    import src.core.infrastructure.database.models as models_module

    for _, module_name, _ in pkgutil.walk_packages(
        models_module.__path__, models_module.__name__ + "."
    ):
        importlib.import_module(module_name)
