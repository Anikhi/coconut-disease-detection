"""
Dataset Splitting Script for Coconut Disease Detection
This script splits the dataset into train/validation/test sets using
stratified sampling to maintain class distribution.

Split ratio: 70% train / 15% validation / 15% test

Author: [Nikhitha A]
Date: February 2026
"""

import os
import shutil
import random
from pathlib import Path
from collections import defaultdict
import json
import pandas as pd

random.seed(42)  # For reproducibility

class DatasetSplitter:
    """Splits dataset into train/val/test with stratified sampling"""
    
    def __init__(self, source_path, dest_path, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15):
        """
        Initialize the splitter
        
        Args:
            source_path: Path to raw dataset
            dest_path: Path to save split data
            train_ratio: Proportion for training (default: 0.70)
            val_ratio: Proportion for validation (default: 0.15)
            test_ratio: Proportion for testing (default: 0.15)
        """
        self.source_path = Path(source_path)
        self.dest_path = Path(dest_path)
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        
        # Validate ratios
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, \
            "Ratios must sum to 1.0"
        
        # Create directories
        self.train_path = self.dest_path / 'train'
        self.val_path = self.dest_path / 'val'
        self.test_path = self.dest_path / 'test'
        
        self.split_stats = defaultdict(dict)
        
    def create_directories(self):
        """Create directory structure for train/val/test"""
        print("Creating directory structure...")
        
        # Get disease classes ONLY from source (raw) folder
        disease_classes = [d.name for d in self.source_path.iterdir() if d.is_dir()]
        
        for split_path in [self.train_path, self.val_path, self.test_path]:
            split_path.mkdir(parents=True, exist_ok=True)
            for disease_class in disease_classes:
                (split_path / disease_class).mkdir(exist_ok=True)
        
        print(f"✓ Created directories for {len(disease_classes)} disease classes")
        print(f"  - Train: {self.train_path}")
        print(f"  - Validation: {self.val_path}")
        print(f"  - Test: {self.test_path}\n")
    
    def split_class_data(self, disease_class):
        """Split images of a single disease class"""
        # EXPLICITLY use source_path (data/raw) - this is the fix!
        class_path = self.source_path / disease_class
        
        # Verify we're reading from the right place
        if not class_path.exists():
            raise FileNotFoundError(f"Class path does not exist: {class_path}")
        
        # Get all images ONLY from source folder
        images = []
        for ext in ['*.jpg', '*.png', '*.jpeg', '*.JPG', '*.PNG', '*.JPEG']:
            images.extend(list(class_path.glob(ext)))
        
        # Remove any duplicates (shouldn't happen but just in case)
        images = list(set(images))
        
        # Shuffle images
        random.shuffle(images)
        
        total = len(images)
        
        # Debug print
        print(f"  Reading from: {class_path}")
        print(f"  Found {total} images")
        
        train_count = int(total * self.train_ratio)
        val_count = int(total * self.val_ratio)
        
        # Split indices
        train_images = images[:train_count]
        val_images = images[train_count:train_count + val_count]
        test_images = images[train_count + val_count:]
        
        # Copy files to destination
        for img in train_images:
            dest = self.train_path / disease_class / img.name
            if not dest.exists():  # Don't copy if already exists
                shutil.copy2(img, dest)
        
        for img in val_images:
            dest = self.val_path / disease_class / img.name
            if not dest.exists():
                shutil.copy2(img, dest)
        
        for img in test_images:
            dest = self.test_path / disease_class / img.name
            if not dest.exists():
                shutil.copy2(img, dest)
        
        # Store statistics
        self.split_stats[disease_class] = {
            'total': total,
            'train': len(train_images),
            'val': len(val_images),
            'test': len(test_images)
        }
        
        return len(train_images), len(val_images), len(test_images)
    
    def split_dataset(self):
        """Split entire dataset"""
        print("="*60)
        print("SPLITTING DATASET")
        print("="*60)
        print(f"Split ratio: {self.train_ratio:.0%} / {self.val_ratio:.0%} / {self.test_ratio:.0%}\n")
        
        # Get disease classes ONLY from source (raw) folder
        disease_classes = sorted([d.name for d in self.source_path.iterdir() if d.is_dir()])
        
        total_train = 0
        total_val = 0
        total_test = 0
        
        for disease_class in disease_classes:
            train, val, test = self.split_class_data(disease_class)
            total_train += train
            total_val += val
            total_test += test
            
            print(f"{disease_class:25s} → Train: {train:4d} | Val: {val:4d} | Test: {test:4d} | Total: {train+val+test:4d}")
        
        print("-"*60)
        print(f"{'TOTAL':25s} → Train: {total_train:4d} | Val: {total_val:4d} | Test: {total_test:4d} | Total: {total_train+total_val+total_test:4d}")
        print("="*60 + "\n")
        
        return total_train, total_val, total_test
    
    def generate_split_report(self):
        """Generate detailed split report for paper"""
        print("Generating split report...")
        
        # Create DataFrame
        rows = []
        for disease_class, stats in sorted(self.split_stats.items()):
            rows.append({
                'Disease Class': disease_class,
                'Total': stats['total'],
                'Train': stats['train'],
                'Train %': f"{(stats['train']/stats['total']*100):.1f}",
                'Validation': stats['val'],
                'Val %': f"{(stats['val']/stats['total']*100):.1f}",
                'Test': stats['test'],
                'Test %': f"{(stats['test']/stats['total']*100):.1f}"
            })
        
        # Add totals
        total_row = {
            'Disease Class': 'TOTAL',
            'Total': sum(s['total'] for s in self.split_stats.values()),
            'Train': sum(s['train'] for s in self.split_stats.values()),
            'Train %': f"{self.train_ratio*100:.1f}",
            'Validation': sum(s['val'] for s in self.split_stats.values()),
            'Val %': f"{self.val_ratio*100:.1f}",
            'Test': sum(s['test'] for s in self.split_stats.values()),
            'Test %': f"{self.test_ratio*100:.1f}"
        }
        rows.append(total_row)
        
        df = pd.DataFrame(rows)
        
        # Save as CSV
        report_path = Path('outputs/reports')
        report_path.mkdir(parents=True, exist_ok=True)
        
        csv_path = report_path / 'table2_dataset_split.csv'
        df.to_csv(csv_path, index=False)
        
        # Save as text
        txt_path = report_path / 'split_report.txt'
        with open(txt_path, 'w') as f:
            f.write("TABLE 2: DATASET SPLIT STATISTICS\n")
            f.write("="*100 + "\n\n")
            f.write(df.to_string(index=False))
            f.write("\n\n" + "="*100 + "\n")
            f.write(f"\nSplit Strategy: Stratified Random Sampling\n")
            f.write(f"Random Seed: 42 (for reproducibility)\n")
            f.write(f"Split Ratio: {self.train_ratio:.0%} / {self.val_ratio:.0%} / {self.test_ratio:.0%}\n")
        
        print(f"✓ Split report saved to: {csv_path}")
        print(f"✓ Text report saved to: {txt_path}")
        
        return df
    
    def save_split_metadata(self):
        """Save split metadata as JSON"""
        metadata = {
            'split_ratio': {
                'train': self.train_ratio,
                'validation': self.val_ratio,
                'test': self.test_ratio
            },
            'split_statistics': self.split_stats,
            'random_seed': 42,
            'total_counts': {
                'train': sum(s['train'] for s in self.split_stats.values()),
                'val': sum(s['val'] for s in self.split_stats.values()),
                'test': sum(s['test'] for s in self.split_stats.values())
            }
        }
        
        json_path = Path('outputs/reports/split_metadata.json')
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Metadata saved to: {json_path}\n")
    
    def verify_split(self):
        """Verify split was successful"""
        print("Verifying split...")
        
        # Get classes from SOURCE folder only
        disease_classes = sorted([d.name for d in self.source_path.iterdir() if d.is_dir()])
        
        all_good = True
        for disease_class in disease_classes:
            train_count = len(list((self.train_path / disease_class).glob('*')))
            val_count = len(list((self.val_path / disease_class).glob('*')))
            test_count = len(list((self.test_path / disease_class).glob('*')))
            
            expected = self.split_stats[disease_class]
            
            if train_count != expected['train']:
                print(f"  ❌ {disease_class}: Train count mismatch ({train_count} vs {expected['train']})")
                all_good = False
            if val_count != expected['val']:
                print(f"  ❌ {disease_class}: Val count mismatch ({val_count} vs {expected['val']})")
                all_good = False
            if test_count != expected['test']:
                print(f"  ❌ {disease_class}: Test count mismatch ({test_count} vs {expected['test']})")
                all_good = False
        
        if all_good:
            print("✓ Split verification successful!\n")
        else:
            print("\n⚠️  Verification found issues (see above)\n")
    
    def run_split_pipeline(self):
        """Run complete split pipeline"""
        print("\n" + "="*60)
        print("DATASET SPLITTING PIPELINE")
        print("="*60 + "\n")
        
        # Step 1: Create directories
        self.create_directories()
        
        # Step 2: Split dataset
        self.split_dataset()
        
        # Step 3: Verify split
        self.verify_split()
        
        # Step 4: Generate report
        df = self.generate_split_report()
        print("\n" + df.to_string(index=False) + "\n")
        
        # Step 5: Save metadata
        self.save_split_metadata()

        print("="*60)
        print("SPLIT COMPLETE!")
        print("="*60)
        print("\nGenerated outputs:")
        print("  📊 Table 2: outputs/reports/table2_dataset_split.csv")
        print("  📄 Split Report: outputs/reports/split_report.txt")
        print("  📋 Metadata: outputs/reports/split_metadata.json")
        print("="*60 + "\n")


def main():
    """Main execution function"""
    # Define paths
    source_path = "data/raw"
    dest_path = "data"
    
    # Verify source path exists
    if not Path(source_path).exists():
        print(f"❌ ERROR: Source path '{source_path}' does not exist!")
        print("   Please make sure your dataset is in the 'data/raw/' folder")
        return
    
    # Initialize splitter
    splitter = DatasetSplitter(
        source_path=source_path,
        dest_path=dest_path,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15
    )
    
    # Run split pipeline
    splitter.run_split_pipeline()


if __name__ == "__main__":
    main()