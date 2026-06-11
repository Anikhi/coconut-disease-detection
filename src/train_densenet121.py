"""
Model Training Script - DenseNet121 for Coconut Disease Detection
==================================================================
This script trains a DenseNet121 model using transfer learning.

Based on Paper 5 which achieved 99% accuracy with DenseNet-121.

Author: [Nikhitha A]
Date: February 2026
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score

# Set style for plots
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)


class CoconutDiseaseClassifier:
    """Train and evaluate DenseNet121 for coconut disease classification"""
    
    def __init__(self, train_dir, val_dir, test_dir, num_classes=5, img_size=(224, 224), batch_size=32):
        """
        Initialize the classifier
        
        Args:
            train_dir: Path to training data
            val_dir: Path to validation data
            test_dir: Path to test data
            num_classes: Number of disease classes
            img_size: Input image size
            batch_size: Batch size for training
        """
        self.train_dir = Path(train_dir)
        self.val_dir = Path(val_dir)
        self.test_dir = Path(test_dir)
        self.num_classes = num_classes
        self.img_size = img_size
        self.batch_size = batch_size
        
        self.model = None
        self.history = None
        self.class_names = None
        
        # Create output directories
        self.output_dir = Path('outputs')
        self.models_dir = Path('models/saved_models')
        self.results_dir = Path('results')
        
        for dir_path in [self.output_dir, self.models_dir, self.results_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        (self.results_dir / 'confusion_matrices').mkdir(exist_ok=True)
        (self.results_dir / 'metrics').mkdir(exist_ok=True)
        (self.output_dir / 'visualizations').mkdir(exist_ok=True)
    
    def create_data_generators(self):
        """Create data generators for train/val/test"""
        print("\n" + "="*60)
        print("CREATING DATA GENERATORS")
        print("="*60)
        
        # Training data generator with augmentation
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            fill_mode='nearest'
        )
        
        # Validation and test data generators (only rescaling)
        val_test_datagen = ImageDataGenerator(rescale=1./255)
        
        # Create generators
        self.train_generator = train_datagen.flow_from_directory(
            self.train_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=True,
            seed=42
        )
        
        self.val_generator = val_test_datagen.flow_from_directory(
            self.val_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        self.test_generator = val_test_datagen.flow_from_directory(
            self.test_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        # Get class names
        self.class_names = list(self.train_generator.class_indices.keys())
        
        print(f"\n✓ Data generators created")
        print(f"Training samples: {self.train_generator.samples}")
        print(f"Validation samples: {self.val_generator.samples}")
        print(f"Test samples: {self.test_generator.samples}")
        print(f"Classes: {self.class_names}")
        print(f"Batch size: {self.batch_size}")
    
    def build_model(self):
        """Build DenseNet121 model with transfer learning"""
        print("\n" + "="*60)
        print("BUILDING MODEL: DenseNet121")
        print("="*60)
        
        # Load pre-trained DenseNet121 (without top layers)
        base_model = DenseNet121(
            include_top=False,
            weights='imagenet',
            input_shape=(*self.img_size, 3)
        )
        
        # Freeze base model layers initially
        base_model.trainable = False
        
        # Build custom top layers
        inputs = keras.Input(shape=(*self.img_size, 3))
        
        # Base model
        x = base_model(inputs, training=False)
        
        # Custom classification head
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(512, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(self.num_classes, activation='softmax')(x)
        
        # Create model
        self.model = keras.Model(inputs, outputs)
        
        # Compile model
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        print("\n✓ Model built successfully")
        print(f"Base Model: DenseNet121 (frozen)")
        print(f"Custom layers: GAP → Dense(512) → Dropout(0.5) → Dense(256) → Dropout(0.3) → Dense({self.num_classes})")
        print(f"Total parameters: {self.model.count_params():,}")
        print(f"Trainable parameters: {sum([tf.size(w).numpy() for w in self.model.trainable_weights]):,}")
    
    def train_model(self, epochs=50, patience=10):
        """Train the model"""
        print("TRAINING MODEL")
        print("="*60)
        print(f"Epochs: {epochs}")
        print(f"Early stopping patience: {patience}")
        
        # Callbacks
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        checkpoint = ModelCheckpoint(
            filepath=str(self.models_dir / f'densenet121_best_{timestamp}.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        )
        
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=patience,
            restore_best_weights=True,
            verbose=1
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
        
        csv_logger = CSVLogger(
            str(self.results_dir / 'metrics' / f'training_log_{timestamp}.csv')
        )
        
        # Train model
        self.history = self.model.fit(
            self.train_generator,
            validation_data=self.val_generator,
            epochs=epochs,
            callbacks=[checkpoint, early_stop, reduce_lr, csv_logger],
            verbose=1
        )        
        print("TRAINING COMPLETE")
    
    def evaluate_model(self):
        """Evaluate model on test set"""
        print("\n" + "="*60)
        print("EVALUATING MODEL ON TEST SET")
        print("="*60 + "\n")
        
        # Get predictions
        self.test_generator.reset()
        predictions = self.model.predict(self.test_generator, verbose=1)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = self.test_generator.classes
        
        # Calculate metrics
        accuracy = accuracy_score(true_classes, predicted_classes)
        precision = precision_score(true_classes, predicted_classes, average='weighted')
        recall = recall_score(true_classes, predicted_classes, average='weighted')
        f1 = f1_score(true_classes, predicted_classes, average='weighted')
        
        print("TEST SET RESULTS")
        print(f"Accuracy:  {accuracy*100:.2f}%")
        print(f"Precision: {precision*100:.2f}%")
        print(f"Recall:    {recall*100:.2f}%")
        print(f"F1-Score:  {f1*100:.2f}%")
        
        # Generate classification report
        report = classification_report(
            true_classes,
            predicted_classes,
            target_names=self.class_names,
            output_dict=True
        )
        
        # Save metrics
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'classification_report': report
        }
        
        with open(self.results_dir / 'metrics' / 'test_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Generate confusion matrix
        self.plot_confusion_matrix(true_classes, predicted_classes)
        
        # Generate classification report table
        self.save_classification_report(report)
        
        return metrics
    
    def plot_confusion_matrix(self, true_classes, predicted_classes):
        """Plot and save confusion matrix"""
        print("Generating confusion matrix...")
        
        cm = confusion_matrix(true_classes, predicted_classes)
        
        # Plot
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=self.class_names,
            yticklabels=self.class_names,
            cbar_kws={'label': 'Count'}
        )
        plt.title('Confusion Matrix - DenseNet121', fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('True Label', fontsize=12, fontweight='bold')
        plt.xlabel('Predicted Label', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        # Save
        save_path = self.results_dir / 'confusion_matrices' / 'confusion_matrix_densenet121.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Confusion matrix saved: {save_path}")
        plt.close()
    
    def save_classification_report(self, report):
        """Save classification report as CSV"""
        print("Generating classification report table...")
        
        # Convert to DataFrame
        df = pd.DataFrame(report).transpose()
        
        # Save
        save_path = self.results_dir / 'metrics' / 'classification_report.csv'
        df.to_csv(save_path)
        print(f"Classification report saved: {save_path}\n")
    
    def plot_training_history(self):
        """Plot training history"""
        print("Generating training history plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy
        axes[0, 0].plot(self.history.history['accuracy'], label='Train', linewidth=2)
        axes[0, 0].plot(self.history.history['val_accuracy'], label='Validation', linewidth=2)
        axes[0, 0].set_title('Model Accuracy', fontweight='bold', fontsize=12)
        axes[0, 0].set_ylabel('Accuracy', fontweight='bold')
        axes[0, 0].set_xlabel('Epoch', fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(alpha=0.3)
        
        # Loss
        axes[0, 1].plot(self.history.history['loss'], label='Train', linewidth=2)
        axes[0, 1].plot(self.history.history['val_loss'], label='Validation', linewidth=2)
        axes[0, 1].set_title('Model Loss', fontweight='bold', fontsize=12)
        axes[0, 1].set_ylabel('Loss', fontweight='bold')
        axes[0, 1].set_xlabel('Epoch', fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(alpha=0.3)
        
        # Precision
        axes[1, 0].plot(self.history.history['precision'], label='Train', linewidth=2)
        axes[1, 0].plot(self.history.history['val_precision'], label='Validation', linewidth=2)
        axes[1, 0].set_title('Model Precision', fontweight='bold', fontsize=12)
        axes[1, 0].set_ylabel('Precision', fontweight='bold')
        axes[1, 0].set_xlabel('Epoch', fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(alpha=0.3)
        
        # Recall
        axes[1, 1].plot(self.history.history['recall'], label='Train', linewidth=2)
        axes[1, 1].plot(self.history.history['val_recall'], label='Validation', linewidth=2)
        axes[1, 1].set_title('Model Recall', fontweight='bold', fontsize=12)
        axes[1, 1].set_ylabel('Recall', fontweight='bold')
        axes[1, 1].set_xlabel('Epoch', fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(alpha=0.3)
        
        plt.suptitle('Training History - DenseNet121', fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        # Save
        save_path = self.output_dir / 'visualizations' / 'training_history_densenet121.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Training history saved: {save_path}\n")
        plt.close()
    
    def run_full_pipeline(self, epochs=50):
        """Run complete training and evaluation pipeline"""
        print("COCONUT DISEASE CLASSIFICATION - DenseNet121")
        
        # Step 1: Create data generators
        self.create_data_generators()
        
        # Step 2: Build model
        self.build_model()
        
        # Step 3: Train model
        self.train_model(epochs=epochs)
        
        # Step 4: Plot training history
        self.plot_training_history()
        
        # Step 5: Evaluate on test set
        metrics = self.evaluate_model()
        
        print("PIPELINE COMPLETE!")
        print("\nGenerated outputs:")
        print(f"Model: models/saved_models/densenet121_best_*.h5")
        print(f"Training history: outputs/visualizations/training_history_densenet121.png")
        print(f"Confusion matrix: results/confusion_matrices/confusion_matrix_densenet121.png")
        print(f"Metrics: results/metrics/test_metrics.json")
        print(f"Classification report: results/metrics/classification_report.csv")
        
        return metrics


def main():
    """Main execution function"""
    # Paths
    train_dir = "data/processed/train"
    val_dir = "data/processed/val"
    test_dir = "data/processed/test"
    
    # Verify paths exist
    for path in [train_dir, val_dir, test_dir]:
        if not Path(path).exists():
            print(f"ERROR: {path} does not exist!")
            print("Please run preprocessing scripts first.")
            return
    
    # Initialize classifier
    classifier = CoconutDiseaseClassifier(
        train_dir=train_dir,
        val_dir=val_dir,
        test_dir=test_dir,
        num_classes=5,
        img_size=(224, 224),
        batch_size=32
    )
    
    # Run pipeline
    metrics = classifier.run_full_pipeline(epochs=50)
    
    # Print final summary
    print("FINAL RESULTS")
    print(f"Test Accuracy:  {metrics['accuracy']*100:.2f}%")
    print(f"Test Precision: {metrics['precision']*100:.2f}%")
    print(f"Test Recall:    {metrics['recall']*100:.2f}%")
    print(f"Test F1-Score:  {metrics['f1_score']*100:.2f}%")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

