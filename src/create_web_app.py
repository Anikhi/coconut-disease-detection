"""
Multi-Model Comparison Web App
===============================
Compares predictions from all 3 models simultaneously

Author: [Nikhitha A]
Date: February 2026
"""

from pathlib import Path

print("\nCreating multi-model comparison web app...")

# Create directories
app_dir = Path("web_app_integrated")
app_dir.mkdir(exist_ok=True)
(app_dir / "templates").mkdir(exist_ok=True)

# Create multi-model app
app_code = '''from flask import Flask, render_template, request, jsonify
import tensorflow as tf
from tensorflow import keras
import numpy as np
import cv2
import json
from pathlib import Path
from PIL import Image

app = Flask(__name__)

# Model information
MODEL_INFO = {
    'MobileNetV2': {
        'accuracy': '99.31%',
        'size': '2.26M parameters',
        'speed': 'Very Fast',
        'color': '#4CAF50',
        'description': 'Lightweight model optimized for mobile devices'
    },
    'DenseNet121': {
        'accuracy': '99.20%',
        'size': '7.69M parameters',
        'speed': 'Medium',
        'color': '#2196F3',
        'description': 'Dense connections for better feature reuse'
    },
    'Custom CNN': {
        'accuracy': '99.31%',
        'size': '2.5M parameters',
        'speed': 'Fast',
        'color': '#FF9800',
        'description': 'Built from scratch for coconut diseases'
    }
}

class_names = ['Bud Root Dropping', 'Bud Rot', 'Gray Leaf Spot', 'Leaf Rot', 'Stem Bleeding']

# Load all available models
models = {}
model_patterns = {
    'MobileNetV2': 'mobilenet_best_*.h5',
    'DenseNet121': 'densenet121_best_*.h5',
    'Custom CNN': 'custom_cnn_best_*.h5'
}

print("\\n" + "="*60)
print("LOADING ALL MODELS")
print("="*60)

for model_name, pattern in model_patterns.items():
    model_files = list(Path("../models/saved_models").glob(pattern))
    if model_files:
        try:
            models[model_name] = keras.models.load_model(model_files[0])
            print(f" Loaded: {model_name} ({model_files[0].name})")
        except Exception as e:
            print(f" Failed to load {model_name}: {e}")
    else:
        print(f"⚠  {model_name} not found")

print(f"\\nTotal models loaded: {len(models)}")
print("="*60 + "\\n")

# Load treatments
treatments_path = Path("../outputs/reports/organic_treatments_database.json")
if treatments_path.exists():
    with open(treatments_path, encoding='utf-8') as f:
        treatments = json.load(f)
    print(" Loaded treatment database\\n")
else:
    treatments = {}
    print(" Treatment database not found\\n")

def predict_with_model(model, image):
    """Get prediction from a single model"""
    img = cv2.resize(image, (224, 224)) / 255.0
    img = np.expand_dims(img, axis=0)
    
    pred = model.predict(img, verbose=0)
    pred_idx = np.argmax(pred[0])
    disease = class_names[pred_idx]
    confidence = float(pred[0][pred_idx] * 100)
    
    all_probs = {class_names[i]: float(pred[0][i] * 100) for i in range(len(class_names))}
    
    return {
        'disease': disease,
        'confidence': confidence,
        'all_probabilities': all_probs
    }

@app.route('/')
def index():
    available_models = list(models.keys())
    return render_template('index.html', 
                         available_models=available_models,
                         model_count=len(available_models),
                         model_info=MODEL_INFO)

@app.route('/predict', methods=['POST'])
def predict():
    if len(models) == 0:
        return jsonify({'error': 'No models loaded'}), 500
    
    file = request.files['file']
    
    # Read image
    image = Image.open(file.stream)
    image = np.array(image)
    
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    
    # Get predictions from ALL models
    predictions = {}
    for model_name, model in models.items():
        predictions[model_name] = predict_with_model(model, image)
    
    # Calculate consensus
    predicted_diseases = [p['disease'] for p in predictions.values()]
    
    # Check if all agree
    all_agree = len(set(predicted_diseases)) == 1
    majority_disease = max(set(predicted_diseases), key=predicted_diseases.count)
    
    # Get treatment for majority disease
    treatment = treatments.get(majority_disease, None)
    
    result = {
        'predictions': predictions,
        'model_info': MODEL_INFO,
        'consensus': {
            'all_agree': all_agree,
            'majority_disease': majority_disease,
            'agreement_count': predicted_diseases.count(majority_disease)
        },
        'treatment': treatment
    }
    
    return jsonify({'success': True, 'result': result})

if __name__ == '__main__':
    print("="*60)
    print("MULTI-MODEL COMPARISON WEB APP")
    print("="*60)
    print(f"Loaded {len(models)} models for comparison")
    print("Starting server on http://localhost:5000")
    print("="*60 + "\\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

with open(app_dir / "app.py", "w", encoding='utf-8') as f:
    f.write(app_code)

# Create comparison HTML template
html_code = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Multi-Model Disease Detection</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container { 
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .header { 
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #2ecc71;
        }
        
        .header h1 { 
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle { 
            color: #7f8c8d;
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        
        .model-count {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            display: inline-block;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .upload-area { 
            border: 3px dashed #ddd;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            transition: all 0.3s;
        }
        
        .upload-area:hover {
            border-color: #2ecc71;
            background: #f0fff4;
        }
        
        .upload-btn { 
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 50px;
            font-size: 1.2em;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .upload-btn:hover { transform: scale(1.05); }
        
        .preview-section {
            text-align: center;
            margin: 30px 0;
        }
        
        .preview-section img {
            max-width: 500px;
            width: 100%;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .results { 
            margin-top: 30px;
        }
        
        .consensus-banner {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .consensus-banner.partial {
            background: linear-gradient(135deg, #FF9800, #F57C00);
        }
        
        .consensus-banner h2 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .consensus-banner p {
            font-size: 1.2em;
            opacity: 0.95;
        }
        
        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }
        
        .model-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-top: 5px solid;
            transition: transform 0.2s;
        }
        
        .model-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        .model-card.correct {
            border-top-color: #4CAF50;
            background: linear-gradient(to bottom, #f1f8f4 0%, white 100%);
        }
        
        .model-card.incorrect {
            border-top-color: #f44336;
            background: linear-gradient(to bottom, #fef1f1 0%, white 100%);
        }
        
        .model-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #ecf0f1;
        }
        
        .model-name {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .model-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .badge-correct {
            background: #4CAF50;
            color: white;
        }
        
        .badge-incorrect {
            background: #f44336;
            color: white;
        }
        
        .prediction {
            margin: 15px 0;
        }
        
        .prediction-disease {
            font-size: 1.8em;
            color: #e74c3c;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .prediction-confidence {
            font-size: 1.3em;
            color: #27ae60;
            font-weight: bold;
        }
        
        .model-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-label {
            font-size: 0.85em;
            color: #7f8c8d;
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-size: 1.1em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .treatment-section {
            background: #d4edda;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
            border-left: 5px solid #28a745;
        }
        
        .treatment-section h3 {
            color: #155724;
            margin-bottom: 20px;
        }
        
        .cost-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        
        .cost-box { 
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .cost-organic { 
            background: #d4edda;
            border: 3px solid #28a745;
        }
        
        .cost-chemical { 
            background: #f8d7da;
            border: 3px solid #dc3545;
        }
        
        .cost-box .price {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .savings {
            background: #28a745;
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.3em;
            font-weight: bold;
            margin-top: 20px;
        }
        
        .hidden { display: none; }
        
        @media (max-width: 768px) {
            .models-grid { grid-template-columns: 1fr; }
            .cost-comparison { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Multi-Model Disease Detection</h1>
            <p class="subtitle">Compare predictions from multiple AI models simultaneously</p>
        </div>
        
        <div class="upload-area">
            <h2>Upload Coconut Leaf Image</h2>
            <p style="margin: 15px 0; color: #666;">
                Upload once, get predictions from ALL models
            </p>
            <input type="file" id="fileInput" accept="image/*" style="display: none;">
            <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                 Choose Image
            </button>
        </div>
        
        <div id="preview" class="preview-section hidden">
            <img id="previewImg">
            <button class="upload-btn" onclick="analyzeImage()" style="margin-top: 20px;">
                 Compare All Models
            </button>
        </div>
        
        <div id="results" class="results hidden"></div>
    </div>
    
    <script>
        let selectedFile = null;
        
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                selectedFile = file;
                const reader = new FileReader();
                reader.onload = function(event) {
                    document.getElementById('previewImg').src = event.target.result;
                    document.getElementById('preview').classList.remove('hidden');
                    document.getElementById('results').classList.add('hidden');
                };
                reader.readAsDataURL(file);
            }
        });
        
        function analyzeImage() {
            const formData = new FormData();
            formData.append('file', selectedFile);
            
            document.getElementById('results').innerHTML = '<p style="text-align: center; padding: 40px;"> Analyzing with all models...</p>';
            document.getElementById('results').classList.remove('hidden');
            
            fetch('/predict', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayResults(data.result);
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('Error: ' + error.message);
            });
        }
        
        function displayResults(result) {
            const consensus = result.consensus;
            const predictions = result.predictions;
            const modelInfo = result.model_info;
            
            let html = '';
            
            // Consensus banner
            if (consensus.all_agree) {
                html += `
                    <div class="consensus-banner">
                        <h2> All Models Agree!</h2>
                        <p style="font-size: 2em; margin: 15px 0;"> ${consensus.majority_disease}</p>
                        <p>All ${consensus.agreement_count} models detected the same disease</p>
                    </div>
                `;
            } else {
                html += `
                    <div class="consensus-banner partial">
                        <h2> Models Partially Agree</h2>
                        <p style="font-size: 2em; margin: 15px 0;"> ${consensus.majority_disease}</p>
                        <p>${consensus.agreement_count} out of ${Object.keys(predictions).length} models agree</p>
                    </div>
                `;
            }
            
            // Model cards
            html += '<div class="models-grid">';
            
            for (const [modelName, pred] of Object.entries(predictions)) {
                const isCorrect = pred.disease === consensus.majority_disease;
                const info = modelInfo[modelName];
                
                html += `
                    <div class="model-card ${isCorrect ? 'correct' : 'incorrect'}">
                        <div class="model-header">
                            <div class="model-name">${modelName}</div>
                            <div class="model-badge ${isCorrect ? 'badge-correct' : 'badge-incorrect'}">
                                ${isCorrect ? '✓ Agrees' : '⚠ Differs'}
                            </div>
                        </div>
                        
                        <div class="prediction">
                            <div class="prediction-disease"> ${pred.disease}</div>
                            <div class="prediction-confidence">Confidence: ${pred.confidence.toFixed(1)}%</div>
                        </div>
                        
                        <div class="model-stats">
                            <div class="stat-item">
                                <div class="stat-label">Accuracy</div>
                                <div class="stat-value">${info.accuracy}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Speed</div>
                                <div class="stat-value">${info.speed}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Size</div>
                                <div class="stat-value">${info.size}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Type</div>
                                <div class="stat-value">${info.description.split(' ')[0]}</div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            
            // Treatment section
            if (result.treatment) {
                const treatment = result.treatment;
                const bestTreatment = treatment.organic_treatments[0];
                const chemical = treatment.chemical_alternative;
                
                html += `
                    <div class="treatment-section">
                        <h3> Recommended Treatment for ${consensus.majority_disease}</h3>
                        
                        <h4 style="color: #28a745; margin: 15px 0;">${bestTreatment.name}</h4>
                        <p><strong>Method:</strong> ${bestTreatment.method}</p>
                        <p><strong>Dosage:</strong> ${bestTreatment.dosage}</p>
                        <p><strong>Frequency:</strong> ${bestTreatment.frequency}</p>
                        <p><strong>Effectiveness:</strong> ${bestTreatment.effectiveness}</p>
                        
                        <h3 style="margin-top: 30px; text-align: center;"> Cost Comparison</h3>
                        <div class="cost-comparison">
                            <div class="cost-box cost-organic">
                                <h4> Organic</h4>
                                <div class="price">₹${bestTreatment.cost_per_tree.toFixed(2)}</div>
                                <p>per tree</p>
                            </div>
                            <div class="cost-box cost-chemical">
                                <h4> Chemical</h4>
                                <div class="price">₹${chemical.cost_per_tree.toFixed(2)}</div>
                                <p>per tree</p>
                            </div>
                        </div>
                        <div class="savings">
                             Save ₹${(chemical.cost_per_tree - bestTreatment.cost_per_tree).toFixed(2)} per tree!
                        </div>
                    </div>
                `;
            }
            
            document.getElementById('results').innerHTML = html;
        }
    </script>
</body>
</html>
'''

with open(app_dir / "templates" / "index.html", "w", encoding='utf-8') as f:
    f.write(html_code)

print(f" Created multi-model comparison app")
print(f" Compares ALL 3 models simultaneously")
print(f" Shows consensus and individual predictions")
print("\nTo run:")
print(f"  cd {app_dir}")
print("  python app.py")
print("  Open: http://localhost:5000")