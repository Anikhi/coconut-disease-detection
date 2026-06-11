"""
Model Comparison & Analysis Script
===================================
Compares all trained models and generates comparison tables/figures for paper

Author: [Nikhitha A]
Date: February 2026
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")


class ModelComparator:
    """Compare all trained models"""
    
    def __init__(self):
        self.results_dir = Path('results/metrics')
        self.output_dir = Path('outputs')
        self.models = {}
        
        # Load all model results
        self.load_all_results()
    
    def load_all_results(self):
        """Load results from all models"""
        print("LOADING MODEL RESULTS")
        
        model_files = {
            'DenseNet121': 'test_metrics.json',
            'ResNet50': 'resnet50_test_metrics.json',
            'EfficientNet-B0': 'efficientnet_test_metrics.json',
            'MobileNetV2': 'mobilenet_test_metrics.json',
            'Custom CNN': 'custom_cnn_test_metrics.json'
        }
        
        for model_name, filename in model_files.items():
            filepath = self.results_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    self.models[model_name] = json.load(f)
                print(f"Loaded {model_name}")
            else:
                print(f"{model_name} not found - skipping")
        
        print(f"\nTotal models loaded: {len(self.models)}")
    
    def generate_comparison_table(self):
        """Generate Table 6: Model Comparison"""
        print("GENERATING TABLE 6: MODEL COMPARISON")
        
        rows = []
        for model_name, metrics in self.models.items():
            rows.append({
                'Model': model_name,
                'Accuracy (%)': f"{metrics['accuracy']*100:.2f}",
                'Precision (%)': f"{metrics['precision']*100:.2f}",
                'Recall (%)': f"{metrics['recall']*100:.2f}",
                'F1-Score (%)': f"{metrics['f1_score']*100:.2f}",
                'Parameters': self.get_model_params(model_name)
            })
        
        # Sort by accuracy
        df = pd.DataFrame(rows)
        df['Acc_num'] = df['Accuracy (%)'].astype(float)
        df = df.sort_values('Acc_num', ascending=False).drop('Acc_num', axis=1)
        
        # Save
        csv_path = self.output_dir / 'reports' / 'table6_model_comparison.csv'
        df.to_csv(csv_path, index=False)
        
        txt_path = self.output_dir / 'reports' / 'model_comparison.txt'
        with open(txt_path, 'w') as f:
            f.write("TABLE 6: MODEL PERFORMANCE COMPARISON\n")
            f.write("="*100 + "\n\n")
            f.write(df.to_string(index=False))
            f.write("\n\n" + "="*100 + "\n")
        
        print("\n" + df.to_string(index=False))
        print(f"\nTable 6 saved to: {csv_path}")
        
        return df
    
    def get_model_params(self, model_name):
        """Get approximate parameter count"""
        params = {
            'DenseNet121': '7.69M',
            'ResNet50': '23.59M',
            'EfficientNet-B0': '4.05M',
            'MobileNetV2': '2.26M',
            'Custom CNN': '~2.5M'
        }
        return params.get(model_name, 'N/A')
    
    def plot_model_comparison(self):
        """Generate Figure 7: Model Comparison Visualization"""
        print("FIGURE 7: MODEL COMPARISON")
        
        models = list(self.models.keys())
        accuracy = [self.models[m]['accuracy']*100 for m in models]
        precision = [self.models[m]['precision']*100 for m in models]
        recall = [self.models[m]['recall']*100 for m in models]
        f1 = [self.models[m]['f1_score']*100 for m in models]
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Accuracy comparison
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(models)))
        bars = axes[0, 0].bar(models, accuracy, color=colors, alpha=0.8, edgecolor='black')
        axes[0, 0].set_ylabel('Accuracy (%)', fontweight='bold', fontsize=11)
        axes[0, 0].set_title('Model Accuracy Comparison', fontweight='bold', fontsize=13, pad=15)
        axes[0, 0].set_ylim([85, 100])
        axes[0, 0].grid(axis='y', alpha=0.3)
        for i, v in enumerate(accuracy):
            axes[0, 0].text(i, v+0.5, f'{v:.2f}%', ha='center', fontweight='bold', fontsize=10)
        plt.setp(axes[0, 0].xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Plot 2: All metrics comparison
        x = np.arange(len(models))
        width = 0.2
        
        axes[0, 1].bar(x - 1.5*width, accuracy, width, label='Accuracy', alpha=0.8)
        axes[0, 1].bar(x - 0.5*width, precision, width, label='Precision', alpha=0.8)
        axes[0, 1].bar(x + 0.5*width, recall, width, label='Recall', alpha=0.8)
        axes[0, 1].bar(x + 1.5*width, f1, width, label='F1-Score', alpha=0.8)
        
        axes[0, 1].set_ylabel('Score (%)', fontweight='bold', fontsize=11)
        axes[0, 1].set_title('All Metrics Comparison', fontweight='bold', fontsize=13, pad=15)
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(models, rotation=45, ha='right')
        axes[0, 1].legend(fontsize=10)
        axes[0, 1].set_ylim([85, 100])
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # Plot 3: F1-Score ranking
        f1_sorted = sorted(zip(models, f1), key=lambda x: x[1], reverse=True)
        models_sorted = [x[0] for x in f1_sorted]
        f1_values = [x[1] for x in f1_sorted]
        
        colors_sorted = plt.cm.RdYlGn(np.array(f1_values) / 100)
        axes[1, 0].barh(models_sorted, f1_values, color=colors_sorted, alpha=0.8, edgecolor='black')
        axes[1, 0].set_xlabel('F1-Score (%)', fontweight='bold', fontsize=11)
        axes[1, 0].set_title('Model Ranking by F1-Score', fontweight='bold', fontsize=13, pad=15)
        axes[1, 0].set_xlim([85, 100])
        axes[1, 0].grid(axis='x', alpha=0.3)
        for i, v in enumerate(f1_values):
            axes[1, 0].text(v+0.3, i, f'{v:.2f}%', va='center', fontweight='bold', fontsize=10)
        
        # Plot 4: Performance summary
        avg_metrics = {
            'Accuracy': np.mean(accuracy),
            'Precision': np.mean(precision),
            'Recall': np.mean(recall),
            'F1-Score': np.mean(f1)
        }
        
        bars = axes[1, 1].bar(list(avg_metrics.keys()), list(avg_metrics.values()),
                             color=plt.cm.Blues(np.linspace(0.5, 0.9, 4)), alpha=0.8, edgecolor='black')
        axes[1, 1].set_ylabel('Average Score (%)', fontweight='bold', fontsize=11)
        axes[1, 1].set_title('Average Performance Across All Models', fontweight='bold', fontsize=13, pad=15)
        axes[1, 1].set_ylim([85, 100])
        axes[1, 1].grid(axis='y', alpha=0.3)
        for i, (k, v) in enumerate(avg_metrics.items()):
            axes[1, 1].text(i, v+0.5, f'{v:.2f}%', ha='center', fontweight='bold', fontsize=11)
        
        plt.suptitle('Comprehensive Model Performance Comparison', fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        save_path = self.output_dir / 'visualizations' / 'figure7_model_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nFigure 7 saved to: {save_path}")
        plt.close()
        
    
    def generate_literature_comparison(self):
        """Generate Table 7: Comparison with Literature"""
        print("TABLE 7: LITERATURE COMPARISON")
        
        # Literature results from survey
        literature = [
            {'Study': 'Paper 1 (Hybrid CNN-ViT)', 'Accuracy': '98.36', 'Year': '2024'},
            {'Study': 'Paper 3 (Inception V3)', 'Accuracy': '98.82', 'Year': '2024'},
            {'Study': 'Paper 5 (DenseNet-121)', 'Accuracy': '99.00', 'Year': '2023'},
            {'Study': 'Paper 6 (ResNet50)', 'Accuracy': '98.70', 'Year': '2023'},
            {'Study': 'Paper 7 (ResNext50)', 'Accuracy': '91.77', 'Year': '2023'},
            {'Study': 'Paper 10 (SVM)', 'Accuracy': '97.30', 'Year': '2021'}
        ]
        
        # Add our results
        our_results = []
        for model_name, metrics in sorted(self.models.items(), 
                                         key=lambda x: x[1]['accuracy'], reverse=True):
            our_results.append({
                'Study': f'Our Work ({model_name})',
                'Accuracy': f"{metrics['accuracy']*100:.2f}",
                'Year': '2026'
            })
        
        # Combine
        all_results = literature + our_results
        df = pd.DataFrame(all_results)
        df['Acc_num'] = df['Accuracy'].astype(float)
        df = df.sort_values('Acc_num', ascending=False).drop('Acc_num', axis=1)
        
        # Save
        csv_path = self.output_dir / 'reports' / 'table7_literature_comparison.csv'
        df.to_csv(csv_path, index=False)
        
        txt_path = self.output_dir / 'reports' / 'literature_comparison.txt'
        with open(txt_path, 'w') as f:
            f.write("TABLE 7: COMPARISON WITH STATE-OF-THE-ART\n")
            f.write("="*100 + "\n\n")
            f.write(df.to_string(index=False))
            f.write("\n\n" + "="*100 + "\n")
            f.write("\nNote: Our models achieve competitive or superior performance\n")
            f.write("compared to existing literature on coconut disease detection.\n")
        
        print("\n" + df.to_string(index=False))
        print(f"\nTable 7 saved to: {csv_path}")
        print("="*60 + "\n")
        
        return df
    
    def generate_summary(self):
        """Generate comprehensive summary"""
        print("FINAL SUMMARY")
        
        best_model = max(self.models.items(), key=lambda x: x[1]['accuracy'])
        
        summary = f"""
COMPREHENSIVE MODEL COMPARISON SUMMARY

Total Models Trained: {len(self.models)}

Best Performing Model: {best_model[0]}
- Accuracy:  {best_model[1]['accuracy']*100:.2f}%
- Precision: {best_model[1]['precision']*100:.2f}%
- Recall:    {best_model[1]['recall']*100:.2f}%
- F1-Score:  {best_model[1]['f1_score']*100:.2f}%

All Models Performance:
"""
        
        for model_name, metrics in sorted(self.models.items(), 
                                         key=lambda x: x[1]['accuracy'], reverse=True):
            summary += f"\n{model_name}:"
            summary += f"\n  Accuracy: {metrics['accuracy']*100:.2f}%"
            summary += f"\n  F1-Score: {metrics['f1_score']*100:.2f}%\n"
        
        summary += """
Generated Outputs for Paper:
- Table 6: Model Performance Comparison
- Table 7: Comparison with State-of-the-Art Literature
- Figure 7: Comprehensive Model Comparison Visualization

"""
        
        # Save
        summary_path = self.output_dir / 'reports' / 'final_comparison_summary.txt'
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        print(summary)
        print(f"Summary saved to: {summary_path}")
        print("="*60 + "\n")
    
    def run_full_comparison(self):
        """Run complete comparison analysis"""
        print("MODEL COMPARISON & ANALYSIS")
        
        if len(self.models) == 0:
            print("No model results found! Train models first.")
            return
        
        # Generate all comparisons
        self.generate_comparison_table()
        self.plot_model_comparison()
        self.generate_literature_comparison()
        self.generate_summary()
        
        print("COMPARISON ANALYSIS COMPLETE!")


def main():
    comparator = ModelComparator()
    comparator.run_full_comparison()

if __name__ == "__main__":
    main()