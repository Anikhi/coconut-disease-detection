#Standard preprocessing:Resize all images to 224×224 pixels (for transfer learning),Normalize pixel values to [0, 1] range,Convert to RGB format (if needed),Save processed images to data/processed/
"""
Image Preprocessing Script for Coconut Disease Detection
This script preprocesses all images for model training:
- Resize to 224x224 pixels
- Normalize pixel values to [0, 1]
- Convert to RGB format
- Save preprocessed images

Author: [Nikhitha A]
Date: February 2026
"""

import os
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
import pandas as pd


class ImagePreprocessor:
    """Preprocesses coconut disease images for deep learning"""
    
    def __init__(self, source_path, dest_path, target_size=(224, 224)):
        """
        Initialize the preprocessor
        
        Args:
            source_path: Path to augmented dataset
            dest_path: Path to save preprocessed images
            target_size: Target image size (default: 224x224 for transfer learning)
        """
        self.source_path = Path(source_path)
        self.dest_path = Path(dest_path)
        self.target_size = target_size
        self.preprocessing_stats = {}
        
    def create_directories(self, splits=['train', 'val', 'test']):
        """Create directory structure for preprocessed data"""
        print("Creating preprocessed directory structure...")
        
        for split in splits:
            split_source = Path('data') / split
            if not split_source.exists():
                continue
            
            disease_classes = [d.name for d in split_source.iterdir() if d.is_dir()]
            
            for disease_class in disease_classes:
                dest_dir = self.dest_path / split / disease_class
                dest_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Created preprocessed directory structure at: {self.dest_path}\n")
    
    def preprocess_image(self, image_path):
        """
        Preprocess a single image
        
        Steps:
        1. Read image
        2. Convert to RGB
        3. Resize to target size
        4. Normalize to [0, 1]
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image as numpy array
        """
        # Read image
        img = cv2.imread(str(image_path))
        
        if img is None:
            return None
        
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize to target size
        img_resized = cv2.resize(img_rgb, self.target_size, interpolation=cv2.INTER_LANCZOS4)
        
        # Normalize to [0, 1] - will be done during training, but save as uint8 to save space
        # img_normalized = img_resized.astype(np.float32) / 255.0
        
        return img_resized
    
    def process_split(self, split_name):
        """Process all images in a split (train/val/test)"""
        split_source = Path('data') / split_name
        
        if not split_source.exists():
            print(f"Split '{split_name}' not found, skipping...")
            return
        
        print(f"\n{'='*60}")
        print(f"Processing {split_name.upper()} split")
        print(f"{'='*60}")
        
        disease_classes = sorted([d.name for d in split_source.iterdir() if d.is_dir()])
        
        split_stats = {}
        total_processed = 0
        total_failed = 0
        
        for disease_class in disease_classes:
            class_source = split_source / disease_class
            class_dest = self.dest_path / split_name / disease_class
            
            # Get all images
            images = list(class_source.glob('*.jpg')) + \
                     list(class_source.glob('*.png')) + \
                     list(class_source.glob('*.jpeg'))
            
            processed = 0
            failed = 0
            
            print(f"\n{disease_class}: Processing {len(images)} images...")
            
            # Process with progress bar
            for img_path in tqdm(images, desc=f"  {disease_class}", leave=False):
                # Preprocess image
                preprocessed = self.preprocess_image(img_path)
                
                if preprocessed is None:
                    failed += 1
                    continue
                
                # Save preprocessed image
                save_path = class_dest / f"{img_path.stem}.jpg"
                
                # Convert back to BGR for saving with cv2
                img_bgr = cv2.cvtColor(preprocessed, cv2.COLOR_RGB2BGR)
                cv2.imwrite(str(save_path), img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                processed += 1
            
            split_stats[disease_class] = {
                'total': len(images),
                'processed': processed,
                'failed': failed
            }
            
            total_processed += processed
            total_failed += failed
            
            print(f"  Processed: {processed}/{len(images)} (Failed: {failed})")
        
        # Store split statistics
        self.preprocessing_stats[split_name] = {
            'classes': split_stats,
            'total_processed': total_processed,
            'total_failed': total_failed
        }
        
        print(f"\n{'='*60}")
        print(f"{split_name.upper()} split complete: {total_processed} images processed")
        print(f"{'='*60}")
    
    def process_all_splits(self):
        """Process train, validation, and test splits"""
        print("IMAGE PREPROCESSING PIPELINE")
        print(f"Target size: {self.target_size[0]}x{self.target_size[1]} pixels")
        print(f"Output format: JPEG (quality: 95)")
        print(f"Color space: RGB")
        
        # Process each split
        for split in ['train', 'val', 'test']:
            self.process_split(split)
        
        print("ALL PREPROCESSING COMPLETE!")    
    def generate_preprocessing_report(self):
        """Generate preprocessing report for paper"""
        print("Generating preprocessing report...")
        
        # Collect statistics
        rows = []
        for split_name, split_data in self.preprocessing_stats.items():
            for disease_class, stats in sorted(split_data['classes'].items()):
                rows.append({
                    'Split': split_name.capitalize(),
                    'Disease Class': disease_class,
                    'Total Images': stats['total'],
                    'Processed': stats['processed'],
                    'Failed': stats['failed'],
                    'Success Rate (%)': f"{(stats['processed']/stats['total']*100):.1f}"
                })
        
        df = pd.DataFrame(rows)
        
        # Save as CSV
        report_path = Path('outputs/reports')
        report_path.mkdir(parents=True, exist_ok=True)
        
        csv_path = report_path / 'table4_preprocessing_statistics.csv'
        df.to_csv(csv_path, index=False)
        
        # Save detailed text report
        txt_path = report_path / 'preprocessing_report.txt'
        with open(txt_path, 'w') as f:
            f.write("TABLE 4: IMAGE PREPROCESSING STATISTICS\n")
            f.write("="*100 + "\n\n")
            f.write(df.to_string(index=False))
            f.write("\n\n" + "="*100 + "\n")
            
            # Summary statistics
            f.write("\nPREPROCESSING SUMMARY:\n")
            total_processed = sum(split_data['total_processed'] 
                                for split_data in self.preprocessing_stats.values())
            total_failed = sum(split_data['total_failed'] 
                             for split_data in self.preprocessing_stats.values())
            
            f.write(f"  Total Images Processed: {total_processed}\n")
            f.write(f"  Total Failed: {total_failed}\n")
            f.write(f"  Success Rate: {(total_processed/(total_processed+total_failed)*100):.2f}%\n\n")
            
            # Preprocessing parameters
            f.write("PREPROCESSING PARAMETERS:\n")
            f.write(f"  - Target Size: {self.target_size[0]}×{self.target_size[1]} pixels\n")
            f.write(f"  - Color Space: RGB\n")
            f.write(f"  - Normalization: Pixel values in [0, 255] (uint8)\n")
            f.write(f"  - Interpolation: LANCZOS4 (high-quality resampling)\n")
            f.write(f"  - Output Format: JPEG (quality: 95%)\n")
            f.write(f"  - Purpose: Transfer learning compatibility (ImageNet pretrained models)\n")
        
        print(f"Preprocessing report saved to: {csv_path}")
        print(f"Text report saved to: {txt_path}")
        
        return df
    
    def save_preprocessing_metadata(self):
        """Save preprocessing metadata as JSON"""
        metadata = {
            'target_size': {
                'width': self.target_size[0],
                'height': self.target_size[1]
            },
            'preprocessing_steps': [
                'Read image using OpenCV',
                'Convert BGR to RGB color space',
                f'Resize to {self.target_size[0]}×{self.target_size[1]} using LANCZOS4 interpolation',
                'Save as JPEG with 95% quality'
            ],
            'statistics': self.preprocessing_stats,
            'total_images': sum(split_data['total_processed'] 
                              for split_data in self.preprocessing_stats.values()),
            'failed_images': sum(split_data['total_failed'] 
                               for split_data in self.preprocessing_stats.values())
        }
        
        json_path = Path('outputs/reports/preprocessing_metadata.json')
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Metadata saved to: {json_path}\n")
    
    def verify_preprocessing(self):
        """Verify preprocessing results"""
        print("Verifying preprocessing...")
        
        sample_checks = 0
        errors = []
        
        for split in ['train', 'val', 'test']:
            split_path = self.dest_path / split
            if not split_path.exists():
                continue
            
            for disease_class in split_path.iterdir():
                if not disease_class.is_dir():
                    continue
                
                # Check a few random images
                images = list(disease_class.glob('*.jpg'))[:5]
                
                for img_path in images:
                    img = cv2.imread(str(img_path))
                    if img is None:
                        errors.append(f"Failed to read: {img_path}")
                        continue
                    
                    h, w = img.shape[:2]
                    if (h, w) != self.target_size:
                        errors.append(f"Size mismatch in {img_path}: {w}×{h} vs {self.target_size}")
                    
                    sample_checks += 1
        
        if errors:
            print("Verification found issues:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"Verification successful! Checked {sample_checks} sample images\n")
    
    def run_full_pipeline(self):
        """Run complete preprocessing pipeline"""
        print("STARTING PREPROCESSING PIPELINE")
        # Step 1: Create directories
        self.create_directories()
        
        # Step 2: Process all splits
        self.process_all_splits()
        
        # Step 3: Verify
        self.verify_preprocessing()
        
        # Step 4: Generate report
        df = self.generate_preprocessing_report()
        
        # Step 5: Save metadata
        self.save_preprocessing_metadata()
        print("PREPROCESSING PIPELINE COMPLETE!")
        print("\nGenerated outputs:")
        print("Table 4: outputs/reports/table4_preprocessing_statistics.csv")
        print("Report: outputs/reports/preprocessing_report.txt")
        print("Metadata: outputs/reports/preprocessing_metadata.json")
        print(f"\nPreprocessed data: {self.dest_path}")


def main():
    """Main execution function"""
    # Define paths
    source_path = "data"  # Will look in data/train, data/val, data/test
    dest_path = "data/processed"
    
    # Initialize preprocessor
    # 224x224 is standard for transfer learning (ResNet, VGG, etc.)
    preprocessor = ImagePreprocessor(
        source_path=source_path,
        dest_path=dest_path,
        target_size=(224, 224)
    )
    
    # Run full pipeline
    preprocessor.run_full_pipeline()


if __name__ == "__main__":
    main()