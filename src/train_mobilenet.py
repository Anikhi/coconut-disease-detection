"""
Model Training Script - MobileNetV2 for Coconut Disease Detection
==================================================================
MobileNetV2: Lightweight model for mobile deployment

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
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score

plt.style.use('seaborn-v0_8-paper')
np.random.seed(42)
tf.random.set_seed(42)


class MobileNetClassifier:
    """MobileNetV2 classifier - optimized for mobile deployment"""
    
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
            rotation_range=15,
            width_shift_range=0.15,
            height_shift_range=0.15,
            horizontal_flip=True,
            zoom_range=0.15
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
        print("BUILDING MODEL: MobileNetV2")
        print("="*60)
        
        base_model = MobileNetV2(
            include_top=False,
            weights='imagenet',
            input_shape=(*self.img_size, 3)
        )
        
        base_model.trainable = False
        
        inputs = keras.Input(shape=(*self.img_size, 3))
        x = base_model(inputs, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(self.num_classes, activation='softmax')(x)
        
        self.model = keras.Model(inputs, outputs)
        
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        print(f"\n✓ Model built - Lightweight for mobile")
        print(f"  Total parameters: {self.model.count_params():,}")
        print(f"  Trainable parameters: {sum([tf.size(w).numpy() for w in self.model.trainable_weights]):,}")
        print("="*60 + "\n")
    
    def train_model(self, epochs=50):
        print("\n" + "="*60)
        print("TRAINING MODEL")
        print("="*60 + "\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        callbacks = [
            ModelCheckpoint(
                str(self.models_dir / f'mobilenet_best_{timestamp}.h5'),
                monitor='val_accuracy', save_best_only=True, mode='max', verbose=1
            ),
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7, verbose=1),
            CSVLogger(str(self.results_dir / 'metrics' / f'mobilenet_log_{timestamp}.csv'))
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
        print("TEST RESULTS - MobileNetV2")
        print(f"{'='*60}")
        print(f"Accuracy:  {accuracy*100:.2f}%")
        print(f"Precision: {precision*100:.2f}%")
        print(f"Recall:    {recall*100:.2f}%")
        print(f"F1-Score:  {f1*100:.2f}%")
        print(f"{'='*60}\n")
        
        report = classification_report(true_classes, predicted_classes,
                                       target_names=self.class_names, output_dict=True)
        
        metrics = {
            'model': 'MobileNetV2',
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'classification_report': report,
            'model_size_mb': os.path.getsize(list(self.models_dir.glob('mobilenet_best_*.h5'))[0]) / (1024*1024)
        }
        
        with open(self.results_dir / 'metrics' / 'mobilenet_test_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        self.plot_confusion_matrix(true_classes, predicted_classes)
        
        df = pd.DataFrame(report).transpose()
        df.to_csv(self.results_dir / 'metrics' / 'mobilenet_classification_report.csv')
        
        print(f"Model size: {metrics['model_size_mb']:.2f} MB (suitable for mobile)\n")
        
        return metrics
    
    def plot_confusion_matrix(self, true_classes, predicted_classes):
        cm = confusion_matrix(true_classes, predicted_classes)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.class_names, yticklabels=self.class_names)
        plt.title('Confusion Matrix - MobileNetV2', fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('True Label', fontsize=12, fontweight='bold')
        plt.xlabel('Predicted Label', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        plt.savefig(self.results_dir / 'confusion_matrices' / 'confusion_matrix_mobilenet.png',
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
        
        plt.suptitle('Training History - MobileNetV2', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'visualizations' / 'training_history_mobilenet.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def run_full_pipeline(self, epochs=50):
        print("\n" + "="*80)
        print("COCONUT DISEASE CLASSIFICATION - MobileNetV2")
        print("="*80)
        
        self.create_data_generators()
        self.build_model()
        self.train_model(epochs=epochs)
        self.plot_training_history()
        metrics = self.evaluate_model()
        
        print("\n" + "="*80)
        print("PIPELINE COMPLETE - MobileNetV2")
        print("="*80 + "\n")
        
        return metrics


def main():
    classifier = MobileNetClassifier(
        train_dir="data/processed/train",
        val_dir="data/processed/val",
        test_dir="data/processed/test"
    )
    
    metrics = classifier.run_full_pipeline(epochs=50)
    
    print(f"\nFINAL RESULTS:")
    print(f"Accuracy:  {metrics['accuracy']*100:.2f}%")
    print(f"Model Size: {metrics['model_size_mb']:.2f} MB\n")


if __name__ == "__main__":
    main()