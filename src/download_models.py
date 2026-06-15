"""
Download trained models from Google Drive on Render startup
"""

import os
import gdown
from pathlib import Path

# Google Drive folder ID (contains all .h5 files)
GOOGLE_DRIVE_FOLDER_ID = "19rtTUFf8BmbKyqaKxtr8QsvnYbhHIZ1D"  # Replace with your folder ID

def download_models_from_drive():
    """Download models from Google Drive"""
    models_dir = Path('models/saved_models')
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("DOWNLOADING MODELS FROM GOOGLE DRIVE")
    print("="*60 + "\n")
    
    # Download each model
    models_to_download = [
        ('mobilenet_best_20260217_125026.h5', 'mobilenet'),
        ('densenet121_best_20260214_202955.h5', 'densenet'),
        ('custom_cnn_best_20260217_141126.h5', 'custom_cnn')
    ]
    
    for filename, model_name in models_to_download:
        file_path = models_dir / filename
        
        # Skip if already exists
        if file_path.exists():
            print(f"✓ {model_name}: Already exists ({file_path.stat().st_size / (1024*1024):.2f} MB)")
            continue
        
        try:
            print(f"⏳ Downloading {model_name}...")
            # Download from Google Drive
            url = f'https://drive.google.com/uc?id=19rtTUFf8BmbKyqaKxtr8QsvnYbhHIZ1D&export=download'
            gdown.download(url, str(file_path), quiet=False)
            print(f"✓ {model_name}: Downloaded successfully\n")
        except Exception as e:
            print(f"❌ {model_name}: Download failed - {e}\n")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    download_models_from_drive()