
import tensorflow as tf
from tensorflow import keras
import numpy as np
import cv2
import json
from pathlib import Path
from PIL import Image
import sqlite3
import hashlib
from datetime import datetime
import secrets

app = Flask(_name_)
app.secret_key = secrets.token_hex(32)

# Add parent directory to path
import sys
sys.path.append('..')

# Import treatment database
from coconut_treatment_recommendations import CoconutTreatmentDatabase

# Initialize treatment database
treatment_db = CoconutTreatmentDatabase()

# Database setup
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("✓ Database initialized")

# Initialize database on startup
init_db()

# Model information
MODEL_INFO = {
    'MobileNetV2': {
        'accuracy': '99.31%',
        'size': '2.26M parameters',
        'speed': 'Very Fast',
        'description': 'Lightweight model optimized for mobile devices'
    },
    'DenseNet121': {
        'accuracy': '99.20%',
        'size': '7.69M parameters',
        'speed': 'Medium',
        'description': 'Dense connections for better feature reuse'
    },
    'Custom CNN': {
        'accuracy': '99.31%',
        'size': '2.5M parameters',
        'speed': 'Fast',
        'description': 'Built from scratch for coconut diseases'
    }
}

class_names = ['Bud Root Dropping', 'Bud Rot', 'Gray Leaf Spot', 'Leaf Rot', 'Stem Bleeding']

# ★★★ CONFIDENCE THRESHOLD FOR HEALTHY DETECTION ★★★
CONFIDENCE_THRESHOLD = 80.0  # If confidence < 80%, classify as healthy

# Load all models
models = {}
model_patterns = {
    'MobileNetV2': 'mobilenet_best_*.h5',
    'DenseNet121': 'densenet121_best_*.h5',
    'Custom CNN': 'custom_cnn_best_*.h5'
}

print("\n" + "="*60)
print("LOADING MODELS")
print("="*60)

for model_name, pattern in model_patterns.items():
    model_files = list(Path("../models/saved_models").glob(pattern))
    if model_files:
        try:
            models[model_name] = keras.models.load_model(model_files[0])
            print(f"✓ {model_name}")
        except Exception as e:
            print(f"✗ {model_name}: {e}")

print(f"Total models: {len(models)}")
print(f"Healthy Detection Threshold: {CONFIDENCE_THRESHOLD}%")
print("="*60 + "\n")

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def filter_treatment_data(treatment):
    """Remove 'not applicable' and irrelevant fields from treatment"""
    cleaned = treatment.copy()
    
    # Remove not applicable fields
    fields_to_remove = ['dosage', 'frequency', 'timing', 'notes', 'cost_per_treatment', 'curative_use']
    
    for field in fields_to_remove:
        if field in cleaned:
            value = cleaned[field]
            if isinstance(value, str):
                if value.lower() in ['not applicable', 'na', 'n/a', '', 'not specified']:
                    cleaned.pop(field, None)
    
    return cleaned

def predict_with_model(model, image):
    """Get prediction from model"""
    try:
        img = cv2.resize(image, (224, 224)) / 255.0
        img = np.expand_dims(img, axis=0).astype(np.float32)
        
        pred = model.predict(img, verbose=0)
        pred_idx = np.argmax(pred[0])
        disease = class_names[pred_idx]
        confidence = float(pred[0][pred_idx] * 100)
        all_probs = {class_names[i]: float(pred[0][i] * 100) for i in range(len(class_names))}
        
        return {'disease': disease, 'confidence': confidence, 'all_probabilities': all_probs}
    except Exception as e:
        print(f"Error in predict_with_model: {e}")
        raise

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Landing page - redirects to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register')
def register():
    """Registration page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    """Handle registration"""
    data = request.json
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    # Validation
    if not all([name, phone, username, password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    if len(phone) != 10 or not phone.isdigit():
        return jsonify({'success': False, 'message': 'Phone number must be 10 digits'}), 400
    
    if len(username) < 4:
        return jsonify({'success': False, 'message': 'Username must be at least 4 characters'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    # Check if phone or username exists
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute('SELECT id FROM users WHERE phone = ?', (phone,))
    if c.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Phone number already registered'}), 400
    
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    if c.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Username already taken'}), 400
    
    # Insert user
    hashed_pw = hash_password(password)
    try:
        c.execute('INSERT INTO users (name, phone, username, password) VALUES (?, ?, ?, ?)',
                 (name, phone, username, hashed_pw))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        # Log user in
        session['user_id'] = user_id
        session['username'] = username
        session['name'] = name
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    hashed_pw = hash_password(password)
    c.execute('SELECT id, name, username FROM users WHERE username = ? AND password = ?',
             (username, hashed_pw))
    user = c.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        session['name'] = user[1]
        session['username'] = user[2]
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard - disease detection"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html',
                         username=session['name'],
                         model_count=len(models),
                         model_info=MODEL_INFO)

@app.route('/results')
def results_page():
    """Results page - shows disease detection results"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get results from session
    result = session.get('last_result', None)
    if not result:
        return redirect(url_for('dashboard'))
    
    return render_template('results.html',
                         username=session['name'],
                         result=result)

@app.route('/treatments')
def treatments():
    """Display all treatments for a disease"""
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if 'last_result' not in session:
            return redirect(url_for('dashboard'))
        
        result = session.get('last_result', {})
        disease = result.get('consensus', {}).get('majority_disease')
        is_healthy = result.get('consensus', {}).get('is_healthy', False)
        
        # Redirect if healthy plant
        if is_healthy:
            return redirect(url_for('results_page'))
        
        if not disease or disease == 'Healthy':
            return redirect(url_for('dashboard'))
        
        # Get all treatments
        all_treatments = treatment_db.get_disease_treatments(disease)
        
        print(f"\n{'='*60}")
        print(f"TREATMENTS PAGE: {disease}")
        print(f"Total treatments: {len(all_treatments)}")
        print(f"{'='*60}\n")
        
        return render_template(
            'treatments.html',
            disease=disease,
            treatments=all_treatments,
            user_name=session.get('name', 'User')
        )
    
    except Exception as e:
        print(f"❌ Error in /treatments route: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('dashboard'))


@app.route('/treatment-detail/<int:treatment_id>')
def treatment_detail(treatment_id):
    """Show detailed treatment information"""
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if 'last_result' not in session:
            return redirect(url_for('dashboard'))
        
        result = session.get('last_result', {})
        disease = result.get('consensus', {}).get('majority_disease')
        
        if not disease or disease == 'Healthy':
            return redirect(url_for('dashboard'))
        
        # Get all treatments and find the one with matching rank
        all_treatments = treatment_db.get_disease_treatments(disease)
        
        treatment = None
        for t in all_treatments:
            if t['rank'] == treatment_id:
                treatment = t
                break
        
        if not treatment:
            print(f"❌ Treatment with rank {treatment_id} not found")
            return redirect(url_for('treatments'))
        
        # Filter out "not applicable" fields
        treatment = filter_treatment_data(treatment)
        
        print(f"\n{'='*60}")
        print(f"TREATMENT DETAIL: {treatment['name']}")
        print(f"Rank: {treatment['rank']}")
        print(f"Disease: {disease}")
        print(f"{'='*60}\n")
        
        return render_template(
            'treatment-detail.html',
            disease=disease,
            treatment=treatment,
            user_name=session.get('name', 'User')
        )
    
    except Exception as e:
        print(f"❌ Error in /treatment-detail route: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('dashboard'))


@app.route('/predict', methods=['POST'])
def predict():
    """Make prediction with improved healthy plant detection"""
    try:
        print("\n" + "="*60)
        print("PREDICTION REQUEST RECEIVED")
        print("="*60)
        
        # Check authentication
        if 'user_id' not in session:
            print("❌ Not authenticated")
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        print(f"✓ User: {session.get('name')}")
        
        # Check models loaded
        if len(models) == 0:
            print("❌ No models loaded")
            return jsonify({'success': False, 'error': 'No models loaded'}), 500
        
        print(f"✓ Models loaded: {len(models)}")
        
        # Check file uploaded
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({'success': False, 'error': 'Empty filename'}), 400
        
        print(f"✓ File received: {file.filename}")
        
        # Read image with error handling
        try:
            image = Image.open(file.stream)
            image = np.array(image)
            print(f"✓ Image loaded: shape {image.shape}")
        except Exception as e:
            print(f"❌ Image loading error: {e}")
            return jsonify({'success': False, 'error': f'Invalid image file: {str(e)}'}), 400
        
        # Convert image format
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            print("✓ Converted grayscale to RGB")
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            print("✓ Converted RGBA to RGB")
        
        # Get predictions from all models
        predictions = {}
        all_probabilities = []
        print("\nRunning predictions...")
        
        for model_name, model in models.items():
            try:
                pred = predict_with_model(model, image)
                predictions[model_name] = pred
                all_probabilities.append(pred['all_probabilities'])
                print(f"✓ {model_name}: {pred['disease']} ({pred['confidence']:.2f}%)")
            except Exception as e:
                print(f"❌ {model_name} failed: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        if not predictions:
            print("❌ All models failed")
            return jsonify({'success': False, 'error': 'All models failed to predict'}), 500
        
        # Calculate consensus
        predicted_diseases = [p['disease'] for p in predictions.values()]
        confidences = [p['confidence'] for p in predictions.values()]
        
        all_agree = len(set(predicted_diseases)) == 1
        majority_disease = max(set(predicted_diseases), key=predicted_diseases.count)
        avg_confidence = sum(confidences) / len(confidences)
        
        # Calculate probability spread (difference between highest and second-highest)
        if all_probabilities:
            avg_probs = {}
            for disease in class_names:
                avg_probs[disease] = sum([p[disease] for p in all_probabilities]) / len(all_probabilities)
            
            sorted_probs = sorted(avg_probs.values(), reverse=True)
            prob_spread = sorted_probs[0] - sorted_probs[1] if len(sorted_probs) > 1 else sorted_probs[0]
        else:
            prob_spread = 100
        
        print(f"\n✓ Consensus: {majority_disease}")
        print(f"✓ Average Confidence: {avg_confidence:.2f}%")
        print(f"✓ Models Agree: {all_agree}")
        print(f"✓ Probability Spread: {prob_spread:.2f}%")
        
        # ★★★ IMPROVED HEALTHY DETECTION LOGIC ★★★
        is_healthy = False
        healthy_reasons = []
        
        # Criterion 1: Low confidence
        if avg_confidence < 70:
            healthy_reasons.append(f"Low confidence ({avg_confidence:.1f}%)")
        
        # Criterion 2: Models disagree
        if not all_agree:
            healthy_reasons.append("Models disagree on disease")
        
        # Criterion 3: Small probability spread (all probabilities similar)
        if prob_spread < 20:
            healthy_reasons.append(f"Unclear prediction (spread: {prob_spread:.1f}%)")
        
        # Criterion 4: Very low confidence (strong indicator)
        if avg_confidence < 60:
            healthy_reasons.append(f"Very low confidence ({avg_confidence:.1f}%)")
        
        # Decision: If 2 or more criteria met, classify as healthy
        if len(healthy_reasons) >= 2:
            is_healthy = True
            majority_disease = "Healthy"
            print(f"\n✓ Classification: HEALTHY")
            print(f"  Reasons: {', '.join(healthy_reasons)}")
        else:
            print(f"\n✓ Classification: DISEASED ({majority_disease})")
            if healthy_reasons:
                print(f"  Note: Some uncertainty - {', '.join(healthy_reasons)}")
        
        # Get treatment count only (not full details)
        treatment_count = 0
        
        if not is_healthy:
            print(f"\nFetching treatment count for: {majority_disease}")
            try:
                all_treatments = treatment_db.get_disease_treatments(majority_disease)
                treatment_count = len(all_treatments)
                print(f"✓ Found {treatment_count} treatments")
            except Exception as e:
                print(f"⚠️ Error getting treatment count: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n✓ No treatments needed (healthy plant)")
        
        result = {
            'predictions': predictions,
            'model_info': MODEL_INFO,
            'consensus': {
                'all_agree': all_agree,
                'majority_disease': majority_disease,
                'agreement_count': predicted_diseases.count(majority_disease),
                'avg_confidence': avg_confidence,
                'is_healthy': is_healthy,
                'healthy_reasons': healthy_reasons if is_healthy else []
            },
            'treatment_count': treatment_count
        }
        
        # Save result to session
        session['last_result'] = result
        
        print(f"✓ Result saved to session")
        print("="*60 + "\n")
        
        return jsonify({'success': True, 'result': result, 'redirect': '/results'})
    
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


# ============================================================================
# SERVER START
# ============================================================================

if _name_ == '_main_':
    print("="*60)
    print("COCONUT DISEASE DETECTION WITH AUTHENTICATION")
    print("="*60)
    print(f"Models: {len(models)}")
    print(f"Healthy Detection: Enabled (Threshold: {CONFIDENCE_THRESHOLD}%)")
    print(f"Treatment Database: {len(treatment_db.treatments)} diseases loaded")
    
    # Print treatment counts
    for disease in treatment_db.treatments.keys():
        count = len(treatment_db.get_disease_treatments(disease))
        print(f"  - {disease}: {count} treatments")
    
    print("\nServer: http://localhost:5000")
    print("Access: http://0.0.0.0:5000 (for mobile on same WiFi)")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)