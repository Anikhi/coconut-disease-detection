"""
Grad-CAM for DenseNet121 - Direct Layer Access
===============================================
Works by rebuilding the model without nesting issues

Author: [Nikhitha A]
Date: February 2026
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Model
import cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pathlib import Path

class WorkingGradCAM:
    """Grad-CAM that works with DenseNet by rebuilding model structure"""
    
    def __init__(self, model_path, img_size=(224, 224)):
        self.original_model = keras.models.load_model(model_path)
        self.img_size = img_size
        self.class_names = ['Bud Root Dropping', 'Bud Rot', 'Gray Leaf Spot', 
                           'Leaf Rot', 'Stem Bleeding']
        
        # Get the densenet base
        self.densenet_layer = None
        for layer in self.original_model.layers:
            if 'densenet' in layer.name.lower():
                self.densenet_layer = layer
                break
        
        # Build new model that outputs both base and final predictions
        if self.densenet_layer is not None:
            # Get input
            model_input = self.original_model.input
            
            # Get DenseNet output
            densenet_output = self.densenet_layer(model_input)
            
            # Get final output by passing through remaining layers
            x = densenet_output
            for layer in self.original_model.layers:
                if layer.name != self.densenet_layer.name and layer.name != 'input_layer_1':
                    x = layer(x)
            
            # Create gradient model
            self.grad_model = Model(
                inputs=model_input,
                outputs=[densenet_output, x]
            )
            
            print(f"✓ Loaded model")
            print(f"✓ Successfully built Grad-CAM model")
        else:
            print("✓ Loaded model")
            print("⚠️  No DenseNet layer found")
            self.grad_model = None
    
    def load_image(self, img_path):
        """Load and preprocess image"""
        img = cv2.imread(str(img_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_original = img.copy()
        
        img_resized = cv2.resize(img, self.img_size)
        img_array = np.expand_dims(img_resized, axis=0).astype(np.float32) / 255.0
        
        return img_array, img_original
    
    def generate_gradcam(self, img_array):
        """Generate Grad-CAM heatmap"""
        
        if self.grad_model is None:
            return None, None, None
        
        # Use GradientTape to get gradients
        with tf.GradientTape() as tape:
            # Get both conv output and predictions
            conv_output, predictions = self.grad_model(img_array, training=False)
            
            # Get predicted class
            pred_index = tf.argmax(predictions[0])
            
            # Get the score for predicted class
            class_score = predictions[:, pred_index]
        
        # Get gradients of class score with respect to conv output
        grads = tape.gradient(class_score, conv_output)
        
        # Pool the gradients across the spatial dimensions
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Weight the conv output by the pooled gradients
        conv_output = conv_output[0].numpy()
        pooled_grads = pooled_grads.numpy()
        
        # Multiply each channel by its gradient weight
        for i in range(pooled_grads.shape[0]):
            conv_output[:, :, i] *= pooled_grads[i]
        
        # Average across all channels to get heatmap
        heatmap = np.mean(conv_output, axis=-1)
        
        # Normalize heatmap
        heatmap = np.maximum(heatmap, 0)
        if np.max(heatmap) != 0:
            heatmap = heatmap / np.max(heatmap)
        
        return heatmap, predictions.numpy()[0], int(pred_index)
    
    def create_superimposed_image(self, img_original, heatmap):
        """Create heatmap overlay on original image"""
        
        # Resize heatmap to match original image
        heatmap_resized = cv2.resize(heatmap, 
                                     (img_original.shape[1], img_original.shape[0]))
        
        # Convert to RGB
        heatmap_colored = cm.jet(heatmap_resized)[:, :, :3] * 255
        heatmap_colored = heatmap_colored.astype(np.uint8)
        
        # Superimpose
        superimposed = cv2.addWeighted(img_original, 0.6, heatmap_colored, 0.4, 0)
        
        return heatmap_colored, superimposed
    
    def create_visualization(self, img_original, heatmap, pred_class, confidence, all_probs):
        """Create comprehensive 4-panel visualization"""
        
        heatmap_colored, superimposed = self.create_superimposed_image(img_original, heatmap)
        
        # Create figure
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Panel 1: Original Image
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.imshow(img_original)
        ax1.set_title('Original Coconut Leaf Image', fontsize=14, fontweight='bold', pad=15)
        ax1.axis('off')
        
        # Panel 2: Heatmap
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.imshow(heatmap_colored)
        ax2.set_title('Grad-CAM Attention Heatmap\n🔴 Red = High Model Attention', 
                     fontsize=14, fontweight='bold', pad=15)
        ax2.axis('off')
        
        # Panel 3: Superimposed
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.imshow(superimposed)
        ax3.set_title(f'Disease Focus Regions\n\n🦠 Predicted: {pred_class}\n✅ Confidence: {confidence:.1f}%', 
                     fontsize=14, fontweight='bold', pad=15)
        ax3.axis('off')
        
        # Panel 4: Probability bars
        ax4 = fig.add_subplot(gs[1, 1])
        
        probs_pct = all_probs * 100
        colors = ['#e74c3c' if i == np.argmax(all_probs) else '#3498db' 
                 for i in range(len(self.class_names))]
        
        bars = ax4.barh(self.class_names, probs_pct, color=colors, 
                       edgecolor='black', linewidth=1.5)
        
        ax4.set_xlabel('Confidence (%)', fontsize=12, fontweight='bold')
        ax4.set_title('Class Probabilities', fontsize=14, fontweight='bold', pad=15)
        ax4.set_xlim([0, 100])
        ax4.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add percentage labels
        for i, (bar, prob) in enumerate(zip(bars, probs_pct)):
            width = bar.get_width()
            label_x_pos = width + 2
            ax4.text(label_x_pos, bar.get_y() + bar.get_height()/2, 
                    f'{prob:.1f}%', va='center', fontweight='bold', fontsize=11)
        
        # Overall title
        fig.suptitle('Explainable AI: Coconut Disease Detection with Grad-CAM', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        return fig
    
    def explain_prediction(self, img_path, save_path):
        """Generate complete explanation with visualization"""
        
        # Load image
        img_array, img_original = self.load_image(img_path)
        
        # Generate Grad-CAM
        heatmap, predictions, pred_index = self.generate_gradcam(img_array)
        
        if heatmap is None:
            # Fallback: just use model prediction
            predictions = self.original_model.predict(img_array, verbose=0)[0]
            pred_index = np.argmax(predictions)
            print("⚠️  Grad-CAM not available, using prediction only")
            return self.class_names[pred_index], predictions[pred_index] * 100
        
        pred_class = self.class_names[pred_index]
        confidence = predictions[pred_index] * 100
        
        # Create and save visualization
        fig = self.create_visualization(img_original, heatmap, pred_class, confidence, predictions)
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return pred_class, confidence


def generate_sample_explanations():
    """Generate Grad-CAM visualizations for sample images"""
    
    print("\n" + "="*80)
    print("GRAD-CAM EXPLAINABLE AI - WORKING VERSION")
    print("="*80 + "\n")
    
    # Find model
    model_files = list(Path("models/saved_models").glob("densenet121_best_*.h5"))
    if not model_files:
        model_files = list(Path("models/saved_models").glob("mobilenet_best_*.h5"))
    
    if not model_files:
        print("❌ No trained model found!")
        return
    
    print(f"Loading model: {model_files[0].name}\n")
    
    try:
        explainer = WorkingGradCAM(model_files[0])
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Find test images
    test_dir = Path("data/processed/test")
    if not test_dir.exists():
        test_dir = Path("data/test")
    
    if not test_dir.exists():
        print("❌ Test data not found!")
        return
    
    # Create output directory
    output_dir = Path("outputs/explainable_ai")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating Grad-CAM visualizations...\n")
    print("-" * 80)
    
    # Generate 2 samples per disease class
    total_count = 0
    success_count = 0
    
    for disease_class in explainer.class_names:
        class_dir = test_dir / disease_class
        if not class_dir.exists():
            print(f"⚠️  Skipping {disease_class} - directory not found")
            continue
        
        images = list(class_dir.glob('*.jpg'))[:2]
        
        for i, img_path in enumerate(images):
            total_count += 1
            save_path = output_dir / f'{disease_class.replace(" ", "_")}_{i+1}.png'
            
            try:
                pred, conf = explainer.explain_prediction(img_path, save_path)
                status = "✓" if pred == disease_class else "⚠"
                print(f"{status} {disease_class:20s} → {pred:20s} ({conf:5.1f}%) | Saved: {save_path.name}")
                success_count += 1
            except Exception as e:
                print(f"✗ {disease_class:20s} → Error: {str(e)[:50]}")
    
    print("-" * 80)
    print(f"\n{'='*80}")
    print("GRAD-CAM GENERATION COMPLETE!")
    print(f"{'='*80}")
    print(f"✓ Successfully generated: {success_count}/{total_count} visualizations")
    print(f"✓ Output directory: {output_dir.absolute()}")
    print(f"\nEach visualization contains:")
    print(f"  1. Original leaf image")
    print(f"  2. Grad-CAM heatmap (red = diseased regions)")
    print(f"  3. Overlay showing disease focus areas")
    print(f"  4. Confidence scores for all disease classes")
    print(f"{'='*80}\n")
    
    if success_count == 0:
        print("⚠️  No visualizations were generated successfully.")
        print("   Please check the error messages above.")
    elif success_count < total_count:
        print(f"⚠️  Some visualizations failed ({total_count - success_count} failures)")
    else:
        print("🎉 All visualizations generated successfully!")


if __name__ == "__main__":
    generate_sample_explanations()