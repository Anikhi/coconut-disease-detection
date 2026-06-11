#To handle class imbalance, we'll augment smaller classes: Bud Rot (470 → ~1,500 images) - need 1,030 augmented,Bud Root Dropping (514 → ~1,500 images) - need 986 augmented
#Augmentation techniques:Rotation: ±25 degreesHorizontal flip,Vertical flip,Zoom: 0.8-1.2x,Brightness adjustment: ±20%,Small translation/shifting
"""
Data Augmentation Script for Coconut Disease Detection
This script applies augmentation to balance class distribution and
increase training data diversity.

Target: Augment smaller classes to ~1500 images each

Author: [Nikhitha A]
Date: February 2026
"""

import os
import cv2
import numpy as np
from pathlib import Path
import random
from collections import Counter
import json
import pandas as pd
from tqdm import tqdm
import albumentations as A

random.seed(42)
np.random.seed(42)


class DataAugmenter:
    """Augments coconut disease dataset to balance classes"""
    
    def __init__(self, train_path, target_count=1500):
        """
        Initialize the augmenter
        
        Args:
            train_path: Path to training data
            target_count: Target number of images per class after augmentation
        """
        self.train_path = Path(train_path)
        self.target_count = target_count
        self.augmentation_stats = {}
        
        # Define augmentation pipeline using Albumentations
        self.transform = A.Compose([
            A.OneOf([
                A.HorizontalFlip(p=1.0),
                A.VerticalFlip(p=1.0),
                A.Rotate(limit=25, p=1.0),
            ], p=0.5),
            A.OneOf([
                A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=1.0),
                A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=20, p=1.0),
            ], p=0.3),
            A.OneOf([
                A.GaussianBlur(blur_limit=(3, 5), p=1.0),
                A.GaussNoise(var_limit=(10.0, 50.0), p=1.0),
            ], p=0.2),
            A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.2, rotate_limit=15, p=0.3),
        ])
    
    def count_images_per_class(self):
        """Count images in each disease class"""
        class_counts = {}
        disease_classes = sorted([d.name for d in self.train_path.iterdir() if d.is_dir()])
        
        for disease_class in disease_classes:
            class_path = self.train_path / disease_class
            images = list(class_path.glob('*.jpg')) + list(class_path.glob('*.png')) + \
                     list(class_path.glob('*.jpeg'))
            class_counts[disease_class] = len(images)
        
        return class_counts
    
    def augment_image(self, image):
        """Apply augmentation to a single image"""
        augmented = self.transform(image=image)
        return augmented['image']
    
    def augment_class(self, disease_class, current_count):
        """Augment images for a single disease class"""
        if current_count >= self.target_count:
            print(f"  ✓ {disease_class}: {current_count} images (no augmentation needed)")
            self.augmentation_stats[disease_class] = {
                'original': current_count,
                'augmented': 0,
                'final': current_count
            }
            return
        
        needed = self.target_count - current_count
        class_path = self.train_path / disease_class
        
        # Get existing images
        images = list(class_path.glob('*.jpg')) + list(class_path.glob('*.png')) + \
                 list(class_path.glob('*.jpeg'))
        
        print(f" {disease_class}: {current_count} → {self.target_count} (need {needed} more)")
        
        augmented_count = 0
        iterations = 0
        max_iterations_per_image = (needed // current_count) + 2
        
        # Progress bar
        pbar = tqdm(total=needed, desc=f"    Augmenting", leave=False)
        
        while augmented_count < needed and iterations < max_iterations_per_image:
            for img_path in images:
                if augmented_count >= needed:
                    break
                
                # Read image
                img = cv2.imread(str(img_path))
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Apply augmentation
                aug_img = self.augment_image(img_rgb)
                aug_img_bgr = cv2.cvtColor(aug_img, cv2.COLOR_RGB2BGR)
                
                # Save augmented image
                base_name = img_path.stem
                aug_name = f"{base_name}_aug_{augmented_count}.jpg"
                aug_path = class_path / aug_name
                
                cv2.imwrite(str(aug_path), aug_img_bgr)
                augmented_count += 1
                pbar.update(1)
            
            iterations += 1
        
        pbar.close()
        
        # Store statistics
        self.augmentation_stats[disease_class] = {
            'original': current_count,
            'augmented': augmented_count,
            'final': current_count + augmented_count
        }
        
        print(f"Added {augmented_count} augmented images")
    
    def run_augmentation(self):
        """Run augmentation pipeline"""
        print("DATA AUGMENTATION PIPELINE")
        print(f"Target count per class: {self.target_count} images\n")
        
        # Count current images
        class_counts = self.count_images_per_class()
        
        print("Current class distribution:")
        for disease, count in sorted(class_counts.items(), key=lambda x: x[1]):
            print(f"  {disease}: {count}")
        print()
        
        # Augment each class
        for disease_class, count in sorted(class_counts.items()):
            self.augment_class(disease_class, count)
        print("AUGMENTATION COMPLETE!")
    
    def generate_augmentation_report(self):
        """Generate Table 3 for paper: Before/After Augmentation"""
        print("Generating augmentation report...")
        
        # Create DataFrame
        rows = []
        for disease_class, stats in sorted(self.augmentation_stats.items()):
            rows.append({
                'Disease Class': disease_class,
                'Original Count': stats['original'],
                'Augmented Added': stats['augmented'],
                'Final Count': stats['final'],
                'Increase (%)': f"{((stats['final']/stats['original'] - 1)*100):.1f}" if stats['augmented'] > 0 else "0.0"
            })
        
        # Add totals
        total_original = sum(s['original'] for s in self.augmentation_stats.values())
        total_augmented = sum(s['augmented'] for s in self.augmentation_stats.values())
        total_final = sum(s['final'] for s in self.augmentation_stats.values())
        
        rows.append({
            'Disease Class': 'TOTAL',
            'Original Count': total_original,
            'Augmented Added': total_augmented,
            'Final Count': total_final,
            'Increase (%)': f"{((total_final/total_original - 1)*100):.1f}"
        })
        
        df = pd.DataFrame(rows)
        
        # Save as CSV
        report_path = Path('outputs/reports')
        report_path.mkdir(parents=True, exist_ok=True)
        
        csv_path = report_path / 'table3_augmentation_statistics.csv'
        df.to_csv(csv_path, index=False)
        
        # Save as text
        txt_path = report_path / 'augmentation_report.txt'
        with open(txt_path, 'w') as f:
            f.write("TABLE 3: DATA AUGMENTATION STATISTICS\n")
            f.write("="*100 + "\n\n")
            f.write(df.to_string(index=False))
            f.write("\n\n" + "="*100 + "\n")
            f.write("\nAugmentation Techniques Applied:\n")
            f.write("  - Rotation: ±25 degrees\n")
            f.write("  - Horizontal/Vertical Flipping\n")
            f.write("  - Brightness/Contrast Adjustment: ±20%\n")
            f.write("  - Zoom/Scale: 0.8-1.2×\n")
            f.write("  - Gaussian Blur and Noise\n")
            f.write("  - Small Translation/Shifting: ±10%\n")
            f.write(f"\nTarget Count: {self.target_count} images per class\n")
            f.write("Library: Albumentations (v1.3+)\n")
        
        print(f"Augmentation report saved to: {csv_path}")
        print(f"Text report saved to: {txt_path}")
        
        return df
    
    def save_augmentation_metadata(self):
        """Save augmentation metadata as JSON"""
        metadata = {
            'target_count_per_class': self.target_count,
            'augmentation_techniques': [
                'Rotation (±25°)',
                'Horizontal Flip',
                'Vertical Flip',
                'Brightness/Contrast (±20%)',
                'Zoom/Scale (0.8-1.2×)',
                'Gaussian Blur',
                'Gaussian Noise',
                'Translation/Shift (±10%)'
            ],
            'class_statistics': self.augmentation_stats,
            'total_original': sum(s['original'] for s in self.augmentation_stats.values()),
            'total_augmented': sum(s['augmented'] for s in self.augmentation_stats.values()),
            'total_final': sum(s['final'] for s in self.augmentation_stats.values())
        }
        
        json_path = Path('outputs/reports/augmentation_metadata.json')
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Metadata saved to: {json_path}\n")
    
    def verify_augmentation(self):
        """Verify augmentation results"""
        print("Verifying augmentation...")
        
        class_counts = self.count_images_per_class()
        
        for disease_class, count in class_counts.items():
            expected = self.augmentation_stats[disease_class]['final']
            assert count == expected, f"Count mismatch for {disease_class}: {count} vs {expected}"
        
        print("✓ Augmentation verification successful!\n")
    
    def run_full_pipeline(self):
        """Run complete augmentation pipeline"""
        print("STARTING AUGMENTATION PIPELINE")        
        # Step 1: Run augmentation
        self.run_augmentation()
        
        # Step 2: Verify
        self.verify_augmentation()
        
        # Step 3: Generate report
        df = self.generate_augmentation_report()
        print("\n" + df.to_string(index=False) + "\n")
        
        # Step 4: Save metadata
        self.save_augmentation_metadata()
        
        print("Table 3: outputs/reports/table3_augmentation_statistics.csv")
        print("Report: outputs/reports/augmentation_report.txt")
        print("Metadata: outputs/reports/augmentation_metadata.json")

def main():
    """Main execution function"""
    # Define path
    train_path = "data/train"
    
    # Initialize augmenter
    # Target: 1500 images per class (can be adjusted)
    augmenter = DataAugmenter(train_path=train_path, target_count=1500)
    
    # Run full pipeline
    augmenter.run_full_pipeline()


if __name__ == "__main__":
    main()