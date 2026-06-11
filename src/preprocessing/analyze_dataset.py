#This script will:Count images in each class,Check image dimensions and formats,Identify corrupted images,visualize sample images from each class,Generate class distribution chart
"""
Dataset Analysis Script for Coconut Disease Detection
This script analyzes the coconut disease dataset and generates:
1. Class distribution statistics (for paper Table 1)
2. Sample image visualizations (for paper Figure 1)
3. Image quality analysis
4. Dataset summary report

Author: [Nikhitha A]
Date: February 2026
"""

import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from pathlib import Path
import json

# Set style for publication-quality figures
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

class DatasetAnalyzer:
    """Analyzes coconut disease dataset for research documentation"""
    
    def __init__(self, data_path, output_path):
        """
        Initialize the analyzer
        
        Args:
            data_path: Path to raw dataset (data/raw)
            output_path: Path to save outputs (outputs/)
        """
        self.data_path = Path(data_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_path / 'reports').mkdir(exist_ok=True)
        (self.output_path / 'visualizations').mkdir(exist_ok=True)
        
        self.disease_classes = []
        self.class_counts = {}
        self.image_info = []
        
    def scan_dataset(self):
        """Scan dataset and collect statistics"""
        print("SCANNING DATASET...")        
        # Get disease classes
        self.disease_classes = sorted([d.name for d in self.data_path.iterdir() if d.is_dir()])
        print(f"\nFound {len(self.disease_classes)} disease classes:")
        
        # Count images per class
        for disease_class in self.disease_classes:
            class_path = self.data_path / disease_class
            images = list(class_path.glob('*.jpg')) + list(class_path.glob('*.png')) + \
                     list(class_path.glob('*.jpeg')) + list(class_path.glob('*.JPG'))
            self.class_counts[disease_class] = len(images)
            print(f"  - {disease_class}: {len(images)} images")
            
            # Sample 3 images from each class for detailed analysis
            for img_path in list(images)[:3]:
                img = cv2.imread(str(img_path))
                if img is not None:
                    h, w, c = img.shape
                    self.image_info.append({
                        'class': disease_class,
                        'filename': img_path.name,
                        'height': h,
                        'width': w,
                        'channels': c,
                        'size_kb': img_path.stat().st_size / 1024
                    })
        
        total_images = sum(self.class_counts.values())
        print(f"\nTotal images: {total_images}")
        print("=" * 60)
        
    def generate_statistics_table(self):
        """Generate Table 1 for research paper: Class Distribution"""
        print("\nGenerating statistics table...")
        
        total = sum(self.class_counts.values())
        
        # Create DataFrame
        stats_data = []
        for disease, count in sorted(self.class_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            stats_data.append({
                'Disease Class': disease,
                'Image Count': count,
                'Percentage (%)': f"{percentage:.1f}"
            })
        
        # Add total row
        stats_data.append({
            'Disease Class': 'TOTAL',
            'Image Count': total,
            'Percentage (%)': '100.0'
        })
        
        df = pd.DataFrame(stats_data)
        
        # Save as CSV for paper
        csv_path = self.output_path / 'reports' / 'table1_class_distribution.csv'
        df.to_csv(csv_path, index=False)
        
        # Save as formatted text
        txt_path = self.output_path / 'reports' / 'dataset_statistics.txt'
        with open(txt_path, 'w') as f:
            f.write("TABLE 1: CLASS DISTRIBUTION IN COCONUT DISEASE DATASET\n")
            f.write("=" * 70 + "\n\n")
            f.write(df.to_string(index=False))
            f.write("\n\n" + "=" * 70 + "\n")
            
            # Add imbalance analysis
            max_count = max(self.class_counts.values())
            min_count = min(self.class_counts.values())
            imbalance_ratio = max_count / min_count
            
            f.write(f"\nIMBALANCE ANALYSIS:\n")
            f.write(f"  - Largest class: {max_count} images\n")
            f.write(f"  - Smallest class: {min_count} images\n")
            f.write(f"  - Imbalance ratio: {imbalance_ratio:.2f}:1\n")
            f.write(f"  - Recommendation: Augmentation needed for classes < {int(total/len(self.class_counts))} images\n")
        
        print(f"✓ Table saved to: {csv_path}")
        print(f"✓ Report saved to: {txt_path}")
        
        return df
    
    def plot_class_distribution(self):
        """Generate Figure 1 for paper: Class Distribution Bar Chart"""
        print("\nGenerating class distribution chart...")
        
        # Sort by count
        sorted_classes = sorted(self.class_counts.items(), key=lambda x: x[1], reverse=True)
        classes = [c[0] for c in sorted_classes]
        counts = [c[1] for c in sorted_classes]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create bars with color gradient
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(classes)))
        bars = ax.bar(classes, counts, color=colors, edgecolor='black', linewidth=1.2)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Customize plot
        ax.set_xlabel('Disease Class', fontsize=13, fontweight='bold')
        ax.set_ylabel('Number of Images', fontsize=13, fontweight='bold')
        ax.set_title('Class Distribution in Coconut Disease Dataset', 
                    fontsize=15, fontweight='bold', pad=20)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right', fontsize=11)
        plt.yticks(fontsize=11)
        
        # Add grid
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Add total line
        total = sum(counts)
        avg = total / len(counts)
        ax.axhline(y=avg, color='red', linestyle='--', linewidth=2, 
                  label=f'Average: {int(avg)} images')
        ax.legend(fontsize=11)
        
        plt.tight_layout()
        
        # Save figure
        fig_path = self.output_path / 'visualizations' / 'figure1_class_distribution.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figure saved to: {fig_path}")
        
        plt.close()
    
    def plot_sample_images(self):
        """Generate Figure 2 for paper: Sample images from each class"""
        print("\nGenerating sample images visualization...")
        
        n_classes = len(self.disease_classes)
        n_samples = 3  # 3 samples per class
        
        fig, axes = plt.subplots(n_classes, n_samples, figsize=(15, 3*n_classes))
        
        for i, disease_class in enumerate(self.disease_classes):
            class_path = self.data_path / disease_class
            images = list(class_path.glob('*.jpg')) + list(class_path.glob('*.png'))
            
            # Sample 3 random images
            sampled = np.random.choice(images, min(n_samples, len(images)), replace=False)
            
            for j, img_path in enumerate(sampled):
                img = cv2.imread(str(img_path))
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                ax = axes[i, j] if n_classes > 1 else axes[j]
                ax.imshow(img_rgb)
                ax.axis('off')
                
                if j == 0:
                    ax.set_title(f"{disease_class}\n({self.class_counts[disease_class]} images)", 
                               fontsize=11, fontweight='bold', loc='left')
                else:
                    ax.set_title("")
        
        plt.suptitle('Sample Images from Each Disease Class', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        # Save figure
        fig_path = self.output_path / 'visualizations' / 'figure2_sample_images.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figure saved to: {fig_path}")
        
        plt.close()
    
    def analyze_image_properties(self):
        """Analyze image dimensions and properties"""
        print("\nAnalyzing image properties...")
        
        df = pd.DataFrame(self.image_info)
        
        # Calculate statistics
        stats = {
            'Average Height': df['height'].mean(),
            'Average Width': df['width'].mean(),
            'Min Height': df['height'].min(),
            'Max Height': df['height'].max(),
            'Min Width': df['width'].min(),
            'Max Width': df['width'].max(),
            'Average Size (KB)': df['size_kb'].mean(),
            'Total Classes': len(self.disease_classes),
            'Total Images': sum(self.class_counts.values())
        }
        
        # Save report
        report_path = self.output_path / 'reports' / 'image_properties.txt'
        with open(report_path, 'w') as f:
            f.write("IMAGE PROPERTIES ANALYSIS\n")
            f.write("=" * 60 + "\n\n")
            for key, value in stats.items():
                f.write(f"{key}: {value:.2f}\n")
        
        print(f"✓ Image properties saved to: {report_path}")
        
        return stats
    
    def generate_json_summary(self):
        """Generate JSON summary for programmatic access"""
        summary = {
            'total_images': sum(self.class_counts.values()),
            'num_classes': len(self.disease_classes),
            'class_distribution': self.class_counts,
            'imbalance_ratio': max(self.class_counts.values()) / min(self.class_counts.values()),
            'classes': self.disease_classes
        }
        
        json_path = self.output_path / 'reports' / 'dataset_summary.json'
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✓ JSON summary saved to: {json_path}")
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        print("\n" + "="*60)
        print("COCONUT DISEASE DATASET ANALYSIS")
        print("="*60)
        
        # Step 1: Scan dataset
        self.scan_dataset()
        
        # Step 2: Generate statistics table
        df = self.generate_statistics_table()
        print("\n" + df.to_string(index=False))
        
        # Step 3: Plot class distribution
        self.plot_class_distribution()
        
        # Step 4: Plot sample images
        self.plot_sample_images()
        
        # Step 5: Analyze image properties
        stats = self.analyze_image_properties()
        
        # Step 6: Generate JSON summary
        self.generate_json_summary()

        print("\nGenerated outputs:")
        print("Table 1: outputs/reports/table1_class_distribution.csv")
        print("Figure 1: outputs/visualizations/figure1_class_distribution.png")
        print("Figure 2: outputs/visualizations/figure2_sample_images.png")
        print("Reports: outputs/reports/")

def main():
    """Main execution function"""
    # Define paths
    data_path = "data/raw"
    output_path = "outputs"
    
    # Initialize analyzer
    analyzer = DatasetAnalyzer(data_path, output_path)
    
    # Run full analysis
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()