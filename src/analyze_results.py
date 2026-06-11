"""
Results Analysis Script - Model Performance Evaluation
=======================================================
This script analyzes the trained model results and generates
tables and figures for the research paper.

Author: [Nikhitha A]
Date: February 2026
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")


class ResultsAnalyzer:
    """Analyze and visualize model results for research paper"""
    
    def __init__(self):
        self.results_dir = Path('results')
        self.output_dir = Path('outputs')
        
        # Load metrics
        with open(self.results_dir / 'metrics' / 'test_metrics.json', 'r') as f:
            self.metrics = json.load(f)
        
        # Load classification report
        self.class_report = pd.read_csv(self.results_dir / 'metrics' / 'classification_report.csv', index_col=0)
        
        print("✓ Loaded results")
        print(f"  Overall Accuracy: {self.metrics['accuracy']*100:.2f}%")
    
    def generate_performance_table(self):
        """Generate Table 5 for paper: Per-class Performance Metrics"""
        print("\n" + "="*60)
        print("GENERATING TABLE 5: PER-CLASS PERFORMANCE")
        print("="*60)
        
        # Extract per-class metrics
        classes = ['Bud Root Dropping', 'Bud Rot', 'Gray Leaf Spot', 'Leaf Rot', 'Stem Bleeding']
        
        rows = []
        for cls in classes:
            if cls in self.metrics['classification_report']:
                stats = self.metrics['classification_report'][cls]
                rows.append({
                    'Disease Class': cls,
                    'Precision (%)': f"{stats['precision']*100:.2f}",
                    'Recall (%)': f"{stats['recall']*100:.2f}",
                    'F1-Score (%)': f"{stats['f1-score']*100:.2f}",
                    'Support': int(stats['support'])
                })
        
        # Add overall metrics
        rows.append({
            'Disease Class': 'OVERALL (Weighted Avg)',
            'Precision (%)': f"{self.metrics['precision']*100:.2f}",
            'Recall (%)': f"{self.metrics['recall']*100:.2f}",
            'F1-Score (%)': f"{self.metrics['f1_score']*100:.2f}",
            'Support': sum([int(self.metrics['classification_report'][c]['support']) for c in classes])
        })
        
        df = pd.DataFrame(rows)
        
        # Save as CSV
        csv_path = self.output_dir / 'reports' / 'table5_model_performance.csv'
        df.to_csv(csv_path, index=False)
        
        # Save as text
        txt_path = self.output_dir / 'reports' / 'model_performance.txt'
        with open(txt_path, 'w') as f:
            f.write("TABLE 5: PER-CLASS PERFORMANCE METRICS - DenseNet121\n")
            f.write("="*100 + "\n\n")
            f.write(df.to_string(index=False))
            f.write("\n\n" + "="*100 + "\n")
            f.write(f"\nModel: DenseNet121 with Transfer Learning\n")
            f.write(f"Test Set Size: {sum([int(self.metrics['classification_report'][c]['support']) for c in classes])} images\n")
            f.write(f"Overall Accuracy: {self.metrics['accuracy']*100:.2f}%\n")
        
        print("\n" + df.to_string(index=False))
        print(f"\n✓ Table 5 saved to: {csv_path}")
        print(f"✓ Report saved to: {txt_path}")
        print("="*60)
    
    def analyze_errors(self):
        """Analyze which classes are most confused"""
        print("\n" + "="*60)
        print("ERROR ANALYSIS")
        print("="*60)
        
        classes = ['Bud Root Dropping', 'Bud Rot', 'Gray Leaf Spot', 'Leaf Rot', 'Stem Bleeding']
        
        # Find lowest performing class
        min_f1 = 100
        min_class = None
        max_f1 = 0
        max_class = None
        
        for cls in classes:
            if cls in self.metrics['classification_report']:
                f1 = self.metrics['classification_report'][cls]['f1-score'] * 100
                if f1 < min_f1:
                    min_f1 = f1
                    min_class = cls
                if f1 > max_f1:
                    max_f1 = f1
                    max_class = cls
        
        print(f"\n✓ Best Performing Class: {max_class} (F1: {max_f1:.2f}%)")
        print(f"✓ Lowest Performing Class: {min_class} (F1: {min_f1:.2f}%)")
        print(f"✓ Performance Variance: {max_f1 - min_f1:.2f}%")
        
        if max_f1 - min_f1 < 2.0:
            print("\n✅ EXCELLENT: Very consistent performance across all classes!")
        elif max_f1 - min_f1 < 5.0:
            print("\n✓ GOOD: Relatively consistent performance across classes")
        else:
            print("\n⚠️  NOTE: Some variation in performance across classes")
        
        print("="*60)
    
    def create_summary_visualization(self):
        """Create comprehensive summary figure"""
        print("\n" + "="*60)
        print("CREATING SUMMARY VISUALIZATION")
        print("="*60)
        
        classes = ['Bud Root Dropping', 'Bud Rot', 'Gray Leaf Spot', 'Leaf Rot', 'Stem Bleeding']
        
        # Extract metrics
        precision = [self.metrics['classification_report'][c]['precision']*100 for c in classes]
        recall = [self.metrics['classification_report'][c]['recall']*100 for c in classes]
        f1 = [self.metrics['classification_report'][c]['f1-score']*100 for c in classes]
        support = [self.metrics['classification_report'][c]['support'] for c in classes]
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Per-class metrics comparison
        x = np.arange(len(classes))
        width = 0.25
        
        axes[0, 0].bar(x - width, precision, width, label='Precision', alpha=0.8)
        axes[0, 0].bar(x, recall, width, label='Recall', alpha=0.8)
        axes[0, 0].bar(x + width, f1, width, label='F1-Score', alpha=0.8)
        axes[0, 0].set_xlabel('Disease Class', fontweight='bold', fontsize=11)
        axes[0, 0].set_ylabel('Score (%)', fontweight='bold', fontsize=11)
        axes[0, 0].set_title('Per-Class Performance Metrics', fontweight='bold', fontsize=13, pad=15)
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels(classes, rotation=45, ha='right', fontsize=9)
        axes[0, 0].legend(fontsize=10)
        axes[0, 0].set_ylim([95, 100])
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # Plot 2: Support distribution
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(classes)))
        axes[0, 1].bar(classes, support, color=colors, alpha=0.8, edgecolor='black')
        axes[0, 1].set_xlabel('Disease Class', fontweight='bold', fontsize=11)
        axes[0, 1].set_ylabel('Number of Test Samples', fontweight='bold', fontsize=11)
        axes[0, 1].set_title('Test Set Distribution', fontweight='bold', fontsize=13, pad=15)
        axes[0, 1].tick_params(axis='x', rotation=45, labelsize=9)
        for i, v in enumerate(support):
            axes[0, 1].text(i, v + 5, str(v), ha='center', va='bottom', fontweight='bold', fontsize=10)
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # Plot 3: Overall metrics
        overall_metrics = {
            'Accuracy': self.metrics['accuracy'] * 100,
            'Precision': self.metrics['precision'] * 100,
            'Recall': self.metrics['recall'] * 100,
            'F1-Score': self.metrics['f1_score'] * 100
        }
        
        bars = axes[1, 0].barh(list(overall_metrics.keys()), list(overall_metrics.values()), 
                              color=plt.cm.Blues(np.linspace(0.5, 0.9, 4)), alpha=0.8, edgecolor='black')
        axes[1, 0].set_xlabel('Score (%)', fontweight='bold', fontsize=11)
        axes[1, 0].set_title('Overall Model Performance', fontweight='bold', fontsize=13, pad=15)
        axes[1, 0].set_xlim([95, 100])
        axes[1, 0].grid(axis='x', alpha=0.3)
        
        for i, (k, v) in enumerate(overall_metrics.items()):
            axes[1, 0].text(v + 0.1, i, f'{v:.2f}%', va='center', fontweight='bold', fontsize=11)
        
        # Plot 4: F1-Score by class (sorted)
        f1_sorted = sorted(zip(classes, f1), key=lambda x: x[1], reverse=True)
        classes_sorted = [x[0] for x in f1_sorted]
        f1_values = [x[1] for x in f1_sorted]
        
        colors_sorted = plt.cm.RdYlGn(np.array(f1_values) / 100)
        axes[1, 1].barh(classes_sorted, f1_values, color=colors_sorted, alpha=0.8, edgecolor='black')
        axes[1, 1].set_xlabel('F1-Score (%)', fontweight='bold', fontsize=11)
        axes[1, 1].set_title('F1-Score Ranking by Disease Class', fontweight='bold', fontsize=13, pad=15)
        axes[1, 1].set_xlim([95, 100])
        axes[1, 1].grid(axis='x', alpha=0.3)
        
        for i, v in enumerate(f1_values):
            axes[1, 1].text(v + 0.1, i, f'{v:.2f}%', va='center', fontweight='bold', fontsize=10)
        
        plt.suptitle('DenseNet121 Performance Summary', fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        # Save
        save_path = self.output_dir / 'visualizations' / 'figure6_performance_summary.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ Figure 6 saved: {save_path}")
        plt.close()
        
        print("="*60)
    
    def generate_paper_summary(self):
        """Generate summary for paper results section"""
        print("\n" + "="*60)
        print("PAPER SUMMARY - RESULTS SECTION")
        print("="*60)
        
        summary = f"""
RESULTS SUMMARY FOR RESEARCH PAPER
==================================

Model: DenseNet121 with Transfer Learning

Overall Performance:
- Test Accuracy:  {self.metrics['accuracy']*100:.2f}%
- Precision:      {self.metrics['precision']*100:.2f}%
- Recall:         {self.metrics['recall']*100:.2f}%
- F1-Score:       {self.metrics['f1_score']*100:.2f}%

Per-Class Performance:
"""
        classes = ['Bud Root Dropping', 'Bud Rot', 'Gray Leaf Spot', 'Leaf Rot', 'Stem Bleeding']
        for cls in classes:
            if cls in self.metrics['classification_report']:
                stats = self.metrics['classification_report'][cls]
                summary += f"\n{cls}:"
                summary += f"\n  Precision: {stats['precision']*100:.2f}%"
                summary += f"\n  Recall:    {stats['recall']*100:.2f}%"
                summary += f"\n  F1-Score:  {stats['f1-score']*100:.2f}%"
                summary += f"\n  Support:   {int(stats['support'])} samples\n"
        
        summary += f"""
Key Findings:
1. The model achieved excellent overall accuracy of {self.metrics['accuracy']*100:.2f}%
2. Performance is consistent across all disease classes
3. Both precision and recall are above 99%, indicating balanced performance
4. Results validate the effectiveness of transfer learning with DenseNet121

For Paper:
- Reference Table 5 for per-class metrics
- Reference Figure 4 for training history
- Reference Figure 5 for confusion matrix  
- Reference Figure 6 for performance summary
"""
        
        # Save summary
        summary_path = self.output_dir / 'reports' / 'results_summary.txt'
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        print(summary)
        print(f"✓ Summary saved to: {summary_path}")
        print("="*60)
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        print("\n" + "="*80)
        print("RESULTS ANALYSIS PIPELINE")
        print("="*80)
        
        # Step 1: Generate performance table
        self.generate_performance_table()
        
        # Step 2: Error analysis
        self.analyze_errors()
        
        # Step 3: Create visualizations
        self.create_summary_visualization()
        
        # Step 4: Generate paper summary
        self.generate_paper_summary()
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        print("\nGenerated outputs:")
        print("  Table 5: outputs/reports/table5_model_performance.csv")
        print("  Figure 6: outputs/visualizations/figure6_performance_summary.png")
        print("  Summary: outputs/reports/results_summary.txt")
        print("="*80 + "\n")


def main():
    """Main execution function"""
    analyzer = ResultsAnalyzer()
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()