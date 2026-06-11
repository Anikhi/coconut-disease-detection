"""
Model Training Script - Custom CNN Baseline
============================================
Simple CNN built from scratch - baseline for comparison

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
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score

plt.style.use('seaborn-v0_8-paper')
np.random.seed(42)
tf.random.set_seed(42)


class CustomCNNClassifier:
    """Custom CNN baseline - built from scratch"""
    
    def __init__(self, train_dir, val_dir, test_dir, num_classes=5, img_size=(224, 224), batch_size=32):
        self.train_dir = Path(train_dir)
        self.val_dir = Path(val_dir)
        self.test_dir = Path(test_dir)
        self.num_classes = num_classes
        self.img_size = img_size
        self.batch_size = batch_size
        
        self.model = None
        self.history = None
        self.class_names = None
        
        self.output_dir = Path('outputs')
        self.models_dir = Path('models/saved_models')
        self.results_dir = Path('results')
        
        for dir_path in [self.output_dir, self.models_dir, self.results_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        (self.results_dir / 'confusion_matrices').mkdir(exist_ok=True)
        (self.results_dir / 'metrics').mkdir(exist_ok=True)
        (self.output_dir / 'visualizations').mkdir(exist_ok=True)
    
    def create_data_generators(self):
        print("\n" + "="*60)
        print("CREATING DATA GENERATORS")
        print("="*60)
        
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2
        )
        
        val_test_datagen = ImageDataGenerator(rescale=1./255)
        
        self.train_generator = train_datagen.flow_from_directory(
            self.train_dir, target_size=self.img_size, batch_size=self.batch_size,
            class_mode='categorical', shuffle=True, seed=42
        )
        
        self.val_generator = val_test_datagen.flow_from_directory(
            self.val_dir, target_size=self.img_size, batch_size=self.batch_size,
            class_mode='categorical', shuffle=False
        )
        
        self.test_generator = val_test_datagen.flow_from_directory(
            self.test_dir, target_size=self.img_size, batch_size=self.batch_size,
            class_mode='categorical', shuffle=False
        )
        
        self.class_names = list(self.train_generator.class_indices.keys())
        
        print(f"\n✓ Data generators created")
        print(f"  Training: {self.train_generator.samples}")
        print(f"  Validation: {self.val_generator.samples}")
        print(f"  Test: {self.test_generator.samples}")
        print("="*60 + "\n")
    
    def build_model(self):
        print("\n" + "="*60)
        print("BUILDING MODEL: Custom CNN (Baseline)")
        print("="*60)
        
        model = keras.Sequential([
            # Block 1
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(*self.img_size, 3)),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Block 2
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Block 3
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Block 4
            layers.Conv2D(256, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Dense layers
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        self.model = model
        
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        print(f"\n✓ Custom CNN built from scratch")
        print(f"  Architecture: 4 Conv blocks + 2 Dense layers")
        print(f"  Total parameters: {self.model.count_params():,}")
        print("="*60 + "\n")
    
    def train_model(self, epochs=50):
        print("\n" + "="*60)
        print("TRAINING MODEL")
        print("="*60 + "\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        callbacks = [
            ModelCheckpoint(
                str(self.models_dir / f'custom_cnn_best_{timestamp}.h5'),
                monitor='val_accuracy', save_best_only=True, mode='max', verbose=1
            ),
            EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=1),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=7, min_lr=1e-7, verbose=1),
            CSVLogger(str(self.results_dir / 'metrics' / f'custom_cnn_log_{timestamp}.csv'))
        ]
        
        self.history = self.model.fit(
            self.train_generator,
            validation_data=self.val_generator,
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )
        
        print("\n" + "="*60)
        print("TRAINING COMPLETE")
        print("="*60 + "\n")
    
    def evaluate_model(self):
        print("\n" + "="*60)
        print("EVALUATING MODEL")
        print("="*60 + "\n")
        
        self.test_generator.reset()
        predictions = self.model.predict(self.test_generator, verbose=1)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = self.test_generator.classes
        
        accuracy = accuracy_score(true_classes, predicted_classes)
        precision = precision_score(true_classes, predicted_classes, average='weighted')
        recall = recall_score(true_classes, predicted_classes, average='weighted')
        f1 = f1_score(true_classes, predicted_classes, average='weighted')
        
        print(f"\n{'='*60}")
        print("TEST RESULTS - Custom CNN (Baseline)")
        print(f"{'='*60}")
        print(f"Accuracy:  {accuracy*100:.2f}%")
        print(f"Precision: {precision*100:.2f}%")
        print(f"Recall:    {recall*100:.2f}%")
        print(f"F1-Score:  {f1*100:.2f}%")
        print(f"{'='*60}\n")
        
        report = classification_report(true_classes, predicted_classes,
                                       target_names=self.class_names, output_dict=True)
        
        metrics = {
            'model': 'Custom CNN',
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'classification_report': report
        }
        
        with open(self.results_dir / 'metrics' / 'custom_cnn_test_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        self.plot_confusion_matrix(true_classes, predicted_classes)
        
        df = pd.DataFrame(report).transpose()
        df.to_csv(self.results_dir / 'metrics' / 'custom_cnn_classification_report.csv')
        
        return metrics
    
    def plot_confusion_matrix(self, true_classes, predicted_classes):
        cm = confusion_matrix(true_classes, predicted_classes)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.class_names, yticklabels=self.class_names)
        plt.title('Confusion Matrix - Custom CNN', fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('True Label', fontsize=12, fontweight='bold')
        plt.xlabel('Predicted Label', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        plt.savefig(self.results_dir / 'confusion_matrices' / 'confusion_matrix_custom_cnn.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_training_history(self):
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        axes[0, 0].plot(self.history.history['accuracy'], label='Train', linewidth=2)
        axes[0, 0].plot(self.history.history['val_accuracy'], label='Val', linewidth=2)
        axes[0, 0].set_title('Accuracy', fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(alpha=0.3)
        
        axes[0, 1].plot(self.history.history['loss'], label='Train', linewidth=2)
        axes[0, 1].plot(self.history.history['val_loss'], label='Val', linewidth=2)
        axes[0, 1].set_title('Loss', fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(alpha=0.3)
        
        axes[1, 0].plot(self.history.history['precision'], label='Train', linewidth=2)
        axes[1, 0].plot(self.history.history['val_precision'], label='Val', linewidth=2)
        axes[1, 0].set_title('Precision', fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(alpha=0.3)
        
        axes[1, 1].plot(self.history.history['recall'], label='Train', linewidth=2)
        axes[1, 1].plot(self.history.history['val_recall'], label='Val', linewidth=2)
        axes[1, 1].set_title('Recall', fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(alpha=0.3)
        
        plt.suptitle('Training History - Custom CNN', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'visualizations' / 'training_history_custom_cnn.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def run_full_pipeline(self, epochs=50):
        print("\n" + "="*80)
        print("COCONUT DISEASE CLASSIFICATION - Custom CNN (Baseline)")
        print("="*80)
        
        self.create_data_generators()
        self.build_model()
        self.train_model(epochs=epochs)
        self.plot_training_history()
        metrics = self.evaluate_model()
        
        print("\n" + "="*80)
        print("PIPELINE COMPLETE - Custom CNN")
        print("="*80 + "\n")
        
        return metrics


def main():
    classifier = CustomCNNClassifier(
        train_dir="data/processed/train",
        val_dir="data/processed/val",
        test_dir="data/processed/test"
    )
    
    metrics = classifier.run_full_pipeline(epochs=50)
    
    print(f"\nFINAL RESULTS - BASELINE:")
    print(f"Accuracy:  {metrics['accuracy']*100:.2f}%")
    print(f"Precision: {metrics['precision']*100:.2f}%")
    print(f"Recall:    {metrics['recall']*100:.2f}%")
    print(f"F1-Score:  {metrics['f1_score']*100:.2f}%\n")


if __name__ == "__main__":
    main()