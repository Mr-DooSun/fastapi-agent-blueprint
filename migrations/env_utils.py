# -*- coding: utf-8 -*-
import importlib
import os
import pkgutil
from pathlib import Path


def create_folder_if_not_exists(folder_path: str):
    """특정 폴더가 없으면 생성"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"폴더 생성됨: {folder_path}")
    else:
        print(f"폴더가 이미 존재합니다: {folder_path}")


def load_models():
    """프로젝트 전체에서 Base를 상속받은 모든 모델을 자동으로 import합니다."""
    # 프로젝트 루트의 src 디렉토리 경로
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    
    if not src_path.exists():
        print(f"경고: src 디렉토리를 찾을 수 없습니다: {src_path}")
        return
    
    # src 디렉토리 내의 모든 모듈을 탐색
    for module_dir in src_path.iterdir():
        # 숨김 파일이나 __pycache__ 등은 제외
        if module_dir.name.startswith("_") or module_dir.name.startswith("."):
            continue
            
        if not module_dir.is_dir():
            continue
        
        # infrastructure/database/models 경로 확인
        models_path = module_dir / "infrastructure" / "database" / "models"
        
        if not models_path.exists() or not models_path.is_dir():
            continue
        
        # __init__.py 파일이 있는지 확인하여 유효한 패키지인지 검증
        init_file = models_path / "__init__.py"
        if not init_file.exists():
            continue
        
        # 모듈 경로를 Python import 경로로 변환
        module_name = f"src.{module_dir.name}.infrastructure.database.models"
        
        try:
            # 모듈을 import
            models_module = importlib.import_module(module_name)
            
            # 해당 모듈 내의 모든 하위 모듈을 재귀적으로 import
            for _, submodule_name, _ in pkgutil.walk_packages(
                models_module.__path__, models_module.__name__ + "."
            ):
                try:
                    importlib.import_module(submodule_name)
                    print(f"모델 모듈 로드됨: {submodule_name}")
                except Exception as e:
                    print(f"경고: {submodule_name} 로드 실패 - {e}")
        except Exception as e:
            print(f"경고: {module_name} 로드 실패 - {e}")
    
    print("=" * 100)
    print("모든 모델 로드 완료")
    print("=" * 100)
