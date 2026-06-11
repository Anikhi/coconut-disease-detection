"""
Web App with Authentication System
===================================
Login/Registration with SQLite database

Author: [Nikhitha A]
Date: February 2026
"""

from pathlib import Path

print("\nCreating web app with authentication system...")

app_dir = Path("web_app_integrated")
app_dir.mkdir(exist_ok=True)
(app_dir / "templates").mkdir(exist_ok=True)
(app_dir / "static").mkdir(exist_ok=True)

# Create main app with authentication
app_code = '''from flask import Flask, render_template, request, jsonify, session, redirect, url_for
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

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Secure secret key

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

# Load all models
models = {}
model_patterns = {
    'MobileNetV2': 'mobilenet_best_*.h5',
    'DenseNet121': 'densenet121_best_*.h5',
    'Custom CNN': 'custom_cnn_best_*.h5'
}

print("\\n" + "="*60)
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
print("="*60 + "\\n")

# Load treatments
treatments_path = Path("../outputs/reports/organic_treatments_database.json")
if treatments_path.exists():
    with open(treatments_path, encoding='utf-8') as f:
        treatments = json.load(f)
    print("✓ Treatment database loaded\\n")
else:
    treatments = {}

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def predict_with_model(model, image):
    """Get prediction from model"""
    img = cv2.resize(image, (224, 224)) / 255.0
    img = np.expand_dims(img, axis=0)
    
    pred = model.predict(img, verbose=0)
    pred_idx = np.argmax(pred[0])
    disease = class_names[pred_idx]
    confidence = float(pred[0][pred_idx] * 100)
    all_probs = {class_names[i]: float(pred[0][i] * 100) for i in range(len(class_names))}
    
    return {'disease': disease, 'confidence': confidence, 'all_probabilities': all_probs}

# Routes
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
    """Results page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get results from session
    result = session.get('last_result', None)
    if not result:
        return redirect(url_for('dashboard'))
    
    return render_template('results.html',
                         username=session['name'],
                         result=result)

@app.route('/predict', methods=['POST'])
def predict():
    """Make prediction"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
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
    
    # Get predictions from all models
    predictions = {}
    for model_name, model in models.items():
        predictions[model_name] = predict_with_model(model, image)
    
    # Calculate consensus
    predicted_diseases = [p['disease'] for p in predictions.values()]
    all_agree = len(set(predicted_diseases)) == 1
    majority_disease = max(set(predicted_diseases), key=predicted_diseases.count)
    
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
    
    # Save result to session
    session['last_result'] = result
    
    return jsonify({'success': True, 'result': result, 'redirect': '/results'})

if __name__ == '__main__':
    print("="*60)
    print("COCONUT DISEASE DETECTION WITH AUTHENTICATION")
    print("="*60)
    print(f"Models: {len(models)}")
    print("Server: http://localhost:5000")
    print("="*60 + "\\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

with open(app_dir / "app.py", "w", encoding='utf-8') as f:
    f.write(app_code)

print("✓ Created app.py with authentication")

# Create login page HTML
login_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Login - Coconut Disease Detection</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .login-container {
            background: white;
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 450px;
            width: 100%;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo h1 {
            color: #2c3e50;
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .logo p {
            color: #7f8c8d;
            font-size: 1em;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 600;
        }
        
        .form-group input {
            width: 100%;
            padding: 15px;
            border: 2px solid #ecf0f1;
            border-radius: 10px;
            font-size: 1em;
            transition: border 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #2ecc71;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            background: #95a5a6;
            cursor: not-allowed;
            transform: none;
        }
        
        .link-text {
            text-align: center;
            margin-top: 20px;
            color: #7f8c8d;
        }
        
        .link-text a {
            color: #2ecc71;
            text-decoration: none;
            font-weight: 600;
        }
        
        .link-text a:hover {
            text-decoration: underline;
        }
        
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🌴 Welcome Back</h1>
            <p>Coconut Disease Detection System</p>
        </div>
        
        <div id="alert" class="alert"></div>
        
        <form id="loginForm">
            <div class="form-group">
                <label>Username</label>
                <input type="text" id="username" required>
            </div>
            
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="password" required>
            </div>
            
            <button type="submit" class="btn" id="loginBtn">Login</button>
        </form>
        
        <div class="link-text">
            Don't have an account? <a href="/register">Register here</a>
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const btn = document.getElementById('loginBtn');
            const alert = document.getElementById('alert');
            
            btn.disabled = true;
            btn.textContent = 'Logging in...';
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert.className = 'alert alert-success';
                    alert.textContent = 'Login successful! Redirecting...';
                    alert.style.display = 'block';
                    setTimeout(() => window.location.href = '/dashboard', 1000);
                } else {
                    alert.className = 'alert alert-error';
                    alert.textContent = data.message;
                    alert.style.display = 'block';
                    btn.disabled = false;
                    btn.textContent = 'Login';
                }
            } catch (error) {
                alert.className = 'alert alert-error';
                alert.textContent = 'Login failed. Please try again.';
                alert.style.display = 'block';
                btn.disabled = false;
                btn.textContent = 'Login';
            }
        });
    </script>
</body>
</html>
'''

with open(app_dir / "templates" / "login.html", "w", encoding='utf-8') as f:
    f.write(login_html)

print("✓ Created login.html")

# Create registration page HTML
register_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Register - Coconut Disease Detection</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .register-container {
            background: white;
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo h1 {
            color: #2c3e50;
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .logo p {
            color: #7f8c8d;
            font-size: 1em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 600;
        }
        
        .form-group input {
            width: 100%;
            padding: 15px;
            border: 2px solid #ecf0f1;
            border-radius: 10px;
            font-size: 1em;
            transition: border 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #2ecc71;
        }
        
        .form-group small {
            display: block;
            margin-top: 5px;
            color: #7f8c8d;
            font-size: 0.85em;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            background: #95a5a6;
            cursor: not-allowed;
            transform: none;
        }
        
        .link-text {
            text-align: center;
            margin-top: 20px;
            color: #7f8c8d;
        }
        
        .link-text a {
            color: #2ecc71;
            text-decoration: none;
            font-weight: 600;
        }
        
        .link-text a:hover {
            text-decoration: underline;
        }
        
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
    </style>
</head>
<body>
    <div class="register-container">
        <div class="logo">
            <h1>🌴 Create Account</h1>
            <p>Join Coconut Disease Detection System</p>
        </div>
        
        <div id="alert" class="alert"></div>
        
        <form id="registerForm">
            <div class="form-group">
                <label>Full Name</label>
                <input type="text" id="name" required>
            </div>
            
            <div class="form-group">
                <label>Phone Number</label>
                <input type="tel" id="phone" pattern="[0-9]{10}" required>
                <small>Enter 10-digit phone number</small>
            </div>
            
            <div class="form-group">
                <label>Username</label>
                <input type="text" id="username" minlength="4" required>
                <small>At least 4 characters</small>
            </div>
            
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="password" minlength="6" required>
                <small>At least 6 characters</small>
            </div>
            
            <button type="submit" class="btn" id="registerBtn">Register</button>
        </form>
        
        <div class="link-text">
            Already have an account? <a href="/login">Login here</a>
        </div>
    </div>
    
    <script>
        document.getElementById('registerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('name').value;
            const phone = document.getElementById('phone').value;
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const btn = document.getElementById('registerBtn');
            const alert = document.getElementById('alert');
            
            btn.disabled = true;
            btn.textContent = 'Registering...';
            
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, phone, username, password})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert.className = 'alert alert-success';
                    alert.textContent = 'Registration successful! Redirecting...';
                    alert.style.display = 'block';
                    setTimeout(() => window.location.href = '/dashboard', 1000);
                } else {
                    alert.className = 'alert alert-error';
                    alert.textContent = data.message;
                    alert.style.display = 'block';
                    btn.disabled = false;
                    btn.textContent = 'Register';
                }
            } catch (error) {
                alert.className = 'alert alert-error';
                alert.textContent = 'Registration failed. Please try again.';
                alert.style.display = 'block';
                btn.disabled = false;
                btn.textContent = 'Register';
            }
        });
    </script>
</body>
</html>
'''

with open(app_dir / "templates" / "register.html", "w", encoding='utf-8') as f:
    f.write(register_html)

print("✓ Created register.html")

# Create dashboard (copy from previous multimodel but add logout)
dashboard_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dashboard - Disease Detection</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .navbar {
            background: white;
            padding: 15px 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .navbar-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .navbar-left h3 {
            color: #2c3e50;
        }
        
        .user-info {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .logout-btn {
            background: #e74c3c;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .logout-btn:hover {
            background: #c0392b;
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
        
        .header h1 { color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }
        .header .subtitle { color: #7f8c8d; font-size: 1.2em; margin-bottom: 10px; }
        
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
            background: #f8f9fa;
        }
        
        .upload-area h2 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .upload-options {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 30px;
            margin-top: 30px;
            align-items: center;
        }
        
        .option-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .option-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        
        .option-icon {
            font-size: 4em;
            margin-bottom: 15px;
        }
        
        .option-card h3 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.5em;
        }
        
        .option-card p {
            color: #7f8c8d;
            margin-bottom: 20px;
        }
        
        .option-divider {
            font-size: 1.5em;
            font-weight: bold;
            color: #95a5a6;
            padding: 20px;
            background: white;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        .camera-btn {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        }
        
        .camera-btn:hover {
            background: linear-gradient(135deg, #2980b9 0%, #21618c 100%);
        }
        
        .file-btn {
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        }
        
        .file-btn:hover {
            background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
        }
        
        @media (max-width: 768px) {
            .upload-options {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .option-divider {
                transform: rotate(90deg);
            }
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
        
        .preview-section { text-align: center; margin: 30px 0; }
        .preview-section img {
            max-width: 500px;
            width: 100%;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .hidden { display: none; }
        
        /* Consensus and model cards styles from previous version */
        .consensus-banner {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .consensus-banner h2 { font-size: 2em; margin-bottom: 10px; }
        .consensus-banner p { font-size: 1.2em; opacity: 0.95; }
        
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
            border-top: 5px solid #4CAF50;
        }
        
        .model-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #ecf0f1;
        }
        
        .model-name { font-size: 1.5em; font-weight: bold; color: #2c3e50; }
        
        .prediction-disease { font-size: 1.8em; color: #e74c3c; font-weight: bold; margin: 10px 0; }
        .prediction-confidence { font-size: 1.3em; color: #27ae60; font-weight: bold; }
        
        /* Treatment Sections */
        .treatment-section {
            background: linear-gradient(to bottom, #e8f5e9 0%, #f1f8e9 100%);
            padding: 40px;
            border-radius: 20px;
            margin: 30px 0;
            border: 3px solid #81c784;
        }
        
        .info-box {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            border-left: 5px solid #2196f3;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .info-box h3 {
            color: #1976d2;
            margin-bottom: 15px;
        }
        
        .info-box p {
            margin: 10px 0;
            line-height: 1.8;
            color: #424242;
        }
        
        .treatment-option {
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 15px;
            border-left: 5px solid #4caf50;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .treatment-option:hover {
            transform: translateX(10px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }
        
        .treatment-option h4 {
            color: #2e7d32;
            font-size: 1.3em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e8f5e9;
        }
        
        .treatment-details p {
            margin: 12px 0;
            line-height: 1.8;
            color: #424242;
        }
        
        .treatment-details strong {
            color: #1b5e20;
        }
        
        .preventive-box {
            background: #fff3e0;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #ff9800;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .preventive-box ul {
            margin-left: 20px;
        }
        
        .preventive-box li {
            margin: 15px 0;
            line-height: 1.8;
            color: #424242;
            font-size: 1.05em;
        }
        
        .cost-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin: 25px 0;
        }
        
        .cost-box {
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
            transition: transform 0.3s;
        }
        
        .cost-box:hover {
            transform: scale(1.05);
        }
        
        .cost-organic {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 4px solid #28a745;
        }
        
        .cost-chemical {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border: 4px solid #dc3545;
        }
        
        .cost-box h4 {
            font-size: 1.4em;
            margin-bottom: 15px;
        }
        
        .cost-box .price {
            font-size: 3em;
            font-weight: bold;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .savings {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 25px;
            box-shadow: 0 5px 20px rgba(40, 167, 69, 0.3);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        
        @media (max-width: 768px) {
            .cost-comparison { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-left">
            <h3>🌴 Coconut Disease Detection</h3>
            <div class="user-info">
                Welcome, <strong>{{ username }}</strong>
            </div>
        </div>
        <button class="logout-btn" onclick="window.location.href='/logout'">Logout</button>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>Multi-Model Disease Detection</h1>
            <p class="subtitle">Compare predictions from multiple AI models simultaneously</p>
            <div class="model-count">🤖 {{ model_count }} AI Models Active</div>
        </div>
        
        <div class="upload-area">
            <h2>Capture or Upload Coconut Leaf Image</h2>
            <p style="margin: 15px 0; color: #666;">Choose how you want to provide the image</p>
            
            <div class="upload-options">
                <div class="option-card">
                    <div class="option-icon">📷</div>
                    <h3>Take Photo</h3>
                    <p>Use your device camera</p>
                    <input type="file" id="cameraInput" accept="image/*" capture="environment" style="display: none;">
                    <button class="upload-btn camera-btn" onclick="document.getElementById('cameraInput').click()">
                        Open Camera
                    </button>
                </div>
                
                <div class="option-divider">OR</div>
                
                <div class="option-card">
                    <div class="option-icon">📁</div>
                    <h3>Upload Image</h3>
                    <p>Choose from device gallery</p>
                    <input type="file" id="fileInput" accept="image/*" style="display: none;">
                    <button class="upload-btn file-btn" onclick="document.getElementById('fileInput').click()">
                        Browse Files
                    </button>
                </div>
            </div>
        </div>
        
        <div id="preview" class="preview-section hidden">
            <p id="imageSource" style="color: #2c3e50; font-weight: bold; margin-bottom: 15px;"></p>
            <img id="previewImg">
            <button class="upload-btn" onclick="analyzeImage()" style="margin-top: 20px;">
                🔍 Compare All Models
            </button>
            <button class="upload-btn" onclick="resetUpload()" style="margin-top: 10px; background: #95a5a6;">
                🔄 Choose Different Image
            </button>
        </div>
        
        <div id="results" class="hidden"></div>
    </div>
    
    <script>
        let selectedFile = null;
        
        // Handle camera input
        document.getElementById('cameraInput').addEventListener('change', function(e) {
            handleImageSelection(e.target.files[0], 'Camera');
        });
        
        // Handle file input
        document.getElementById('fileInput').addEventListener('change', function(e) {
            handleImageSelection(e.target.files[0], 'Gallery');
        });
        
        function handleImageSelection(file, source) {
            if (file) {
                selectedFile = file;
                const reader = new FileReader();
                reader.onload = function(event) {
                    document.getElementById('previewImg').src = event.target.result;
                    document.getElementById('preview').classList.remove('hidden');
                    document.getElementById('results').classList.add('hidden');
                    
                    // Show source info
                    const sourceInfo = document.getElementById('imageSource');
                    if (sourceInfo) {
                        sourceInfo.textContent = `Image from: ${source}`;
                    }
                };
                reader.readAsDataURL(file);
            }
        }
        
        function resetUpload() {
            selectedFile = null;
            document.getElementById('preview').classList.add('hidden');
            document.getElementById('results').classList.add('hidden');
            document.getElementById('cameraInput').value = '';
            document.getElementById('fileInput').value = '';
        }
        
        function analyzeImage() {
            const formData = new FormData();
            formData.append('file', selectedFile);
            
            // Show loading
            document.getElementById('results').innerHTML = '<p style="text-align: center; padding: 40px;">⏳ Analyzing with all models...</p>';
            document.getElementById('results').classList.remove('hidden');
            
            fetch('/predict', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to results page
                    window.location.href = '/results';
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('Error: ' + error.message);
            });
        }
    </script>
</body>
</html>
'''

with open(app_dir / "templates" / "dashboard.html", "w", encoding='utf-8') as f:
    f.write(dashboard_html)

print("✓ Created dashboard.html")

# Create results page HTML
results_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Results - Disease Detection</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .navbar {
            background: white;
            padding: 15px 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .navbar-left { display: flex; align-items: center; gap: 15px; }
        .navbar-left h3 { color: #2c3e50; }
        
        .btn-group {
            display: flex;
            gap: 10px;
        }
        
        .nav-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .back-btn {
            background: #3498db;
            color: white;
        }
        
        .back-btn:hover {
            background: #2980b9;
        }
        
        .logout-btn {
            background: #e74c3c;
            color: white;
        }
        
        .logout-btn:hover {
            background: #c0392b;
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
        
        .header h1 { color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }
        
        .consensus-banner {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
        }
        
        .consensus-banner h2 { font-size: 2.5em; margin-bottom: 15px; }
        .consensus-banner .disease { font-size: 3em; margin: 20px 0; font-weight: bold; }
        .consensus-banner p { font-size: 1.3em; opacity: 0.95; }
        
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
            border-top: 5px solid #4CAF50;
            transition: transform 0.2s;
        }
        
        .model-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        .model-name { font-size: 1.5em; font-weight: bold; color: #2c3e50; margin-bottom: 15px; }
        .prediction-disease { font-size: 1.8em; color: #e74c3c; font-weight: bold; margin: 10px 0; }
        .prediction-confidence { font-size: 1.3em; color: #27ae60; font-weight: bold; }
        
        .treatment-section {
            background: linear-gradient(to bottom, #e8f5e9 0%, #f1f8e9 100%);
            padding: 40px;
            border-radius: 20px;
            margin: 30px 0;
            border: 3px solid #81c784;
        }
        
        .info-box {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            border-left: 5px solid #2196f3;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .info-box h3 { color: #1976d2; margin-bottom: 15px; font-size: 1.5em; }
        .info-box p { margin: 10px 0; line-height: 1.8; color: #424242; }
        
        .treatment-option {
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 15px;
            border-left: 5px solid #4caf50;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        }
        
        .treatment-option h4 {
            color: #2e7d32;
            font-size: 1.3em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e8f5e9;
        }
        
        .treatment-details p {
            margin: 12px 0;
            line-height: 1.8;
            color: #424242;
            font-size: 1.05em;
        }
        
        .treatment-details strong { color: #1b5e20; }
        
        .preventive-box {
            background: #fff3e0;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #ff9800;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .preventive-box ul { margin-left: 20px; }
        .preventive-box li {
            margin: 15px 0;
            line-height: 1.8;
            color: #424242;
            font-size: 1.05em;
        }
        
        .cost-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin: 25px 0;
        }
        
        .cost-box {
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }
        
        .cost-organic {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 4px solid #28a745;
        }
        
        .cost-chemical {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border: 4px solid #dc3545;
        }
        
        .cost-box h4 { font-size: 1.4em; margin-bottom: 15px; }
        .cost-box .price {
            font-size: 3em;
            font-weight: bold;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .savings {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 25px;
            box-shadow: 0 5px 20px rgba(40, 167, 69, 0.3);
        }
        
        @media (max-width: 768px) {
            .models-grid { grid-template-columns: 1fr; }
            .cost-comparison { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-left">
            <h3>🌴 Analysis Results</h3>
        </div>
        <div class="btn-group">
            <button class="nav-btn back-btn" onclick="window.location.href='/dashboard'">
                ← Back to Dashboard
            </button>
            <button class="nav-btn logout-btn" onclick="window.location.href='/logout'">
                Logout
            </button>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🔬 Disease Detection Results</h1>
        </div>
        
        <!-- Consensus Banner -->
        {% if result.consensus.all_agree %}
        <div class="consensus-banner">
            <h2>✅ All Models Agree!</h2>
            <div class="disease">🦠 {{ result.consensus.majority_disease }}</div>
            <p>All {{ result.consensus.agreement_count }} AI models detected the same disease with high confidence</p>
        </div>
        {% else %}
        <div class="consensus-banner" style="background: linear-gradient(135deg, #FF9800, #F57C00);">
            <h2>⚠️ Partial Agreement</h2>
            <div class="disease">🦠 {{ result.consensus.majority_disease }}</div>
            <p>{{ result.consensus.agreement_count }} out of {{ result.predictions|length }} models agree</p>
        </div>
        {% endif %}
        
        <!-- Model Predictions -->
        <h2 style="margin: 30px 0 20px 0; color: #2c3e50;">🤖 Model Predictions</h2>
        <div class="models-grid">
            {% for model_name, pred in result.predictions.items() %}
            <div class="model-card">
                <div class="model-name">{{ model_name }}</div>
                <div class="prediction-disease">🦠 {{ pred.disease }}</div>
                <div class="prediction-confidence">Confidence: {{ "%.1f"|format(pred.confidence) }}%</div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Treatment Guide -->
        {% if result.treatment %}
        <div class="treatment-section">
            <h2 style="color: #155724; margin-bottom: 20px;">🌱 Treatment & Prevention Guide</h2>
            
            <!-- Disease Information -->
            <div class="info-box">
                <h3>📋 Disease Information</h3>
                <p><strong>Pathogen:</strong> {{ result.treatment.disease_info.pathogen }}</p>
                <p><strong>Symptoms:</strong> {{ result.treatment.disease_info.symptoms }}</p>
                <p><strong>Severity:</strong> {{ result.treatment.disease_info.severity }}</p>
            </div>
            
            <!-- Organic Treatments -->
            <h3 style="color: #28a745; margin: 30px 0 15px 0;">🌿 Recommended Organic Treatments</h3>
            <p style="color: #155724; margin-bottom: 20px;">Choose any one of the following effective organic treatments:</p>
            
            {% for treatment in result.treatment.organic_treatments %}
            <div class="treatment-option">
                <h4>Option {{ loop.index }}: {{ treatment.name }}</h4>
                <div class="treatment-details">
                    <p><strong>📝 Method:</strong> {{ treatment.method }}</p>
                    <p><strong>💊 Dosage:</strong> {{ treatment.dosage }}</p>
                    <p><strong>📅 Frequency:</strong> {{ treatment.frequency }}</p>
                    <p><strong>⏰ Application Time:</strong> {{ treatment.application_time }}</p>
                    <p><strong>✅ Effectiveness:</strong> {{ treatment.effectiveness }}</p>
                    <p><strong>💰 Cost:</strong> ₹{{ "%.2f"|format(treatment.cost_per_tree) }} per tree</p>
                </div>
            </div>
            {% endfor %}
            
            <!-- Preventive Measures -->
            <h3 style="color: #e67e22; margin: 30px 0 15px 0;">⚠️ Preventive Measures (IMPORTANT)</h3>
            <div class="preventive-box">
                <ul>
                    {% for measure in result.treatment.preventive_measures %}
                    <li>{{ measure }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <!-- Cost Comparison -->
            <h3 style="text-align: center; margin: 30px 0 20px 0; color: #2c3e50;">💰 Cost Comparison</h3>
            <div class="cost-comparison">
                <div class="cost-box cost-organic">
                    <h4>🌱 Organic Treatment</h4>
                    <div class="price">₹{{ "%.2f"|format(result.treatment.organic_treatments[0].cost_per_tree) }}</div>
                    <p>per tree</p>
                    <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.3); border-radius: 8px;">
                        <strong style="color: #155724;">Benefits:</strong><br>
                        ✓ Eco-friendly<br>
                        ✓ No soil contamination<br>
                        ✓ Safe for beneficial insects<br>
                        ✓ Sustainable long-term
                    </div>
                </div>
                <div class="cost-box cost-chemical">
                    <h4>⚠️ Chemical Treatment</h4>
                    <div class="price">₹{{ "%.2f"|format(result.treatment.chemical_alternative.cost_per_tree) }}</div>
                    <p>per tree</p>
                    <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.3); border-radius: 8px;">
                        <strong style="color: #721c24;">Drawbacks:</strong><br>
                        {{ result.treatment.chemical_alternative.side_effects }}<br>
                        ✗ Not recommended
                    </div>
                </div>
            </div>
            <div class="savings">
                💰 Save ₹{{ "%.2f"|format(result.treatment.chemical_alternative.cost_per_tree - result.treatment.organic_treatments[0].cost_per_tree) }} per tree with organic treatment!
            </div>
        </div>
        {% endif %}
        
        <!-- Action Buttons -->
        <div style="text-align: center; margin-top: 40px;">
            <button class="nav-btn back-btn" onclick="window.location.href='/dashboard'" style="font-size: 1.2em; padding: 15px 40px;">
                ← Analyze Another Image
            </button>
        </div>
    </div>
</body>
</html>
'''

with open(app_dir / "templates" / "results.html", "w", encoding='utf-8') as f:
    f.write(results_html)

print("✓ Created results.html")

# Create README
readme = '''# Coconut Disease Detection with Authentication

## Features
- User registration and login
- SQLite database for user management
- Multi-model disease detection
- Organic treatment recommendations

## Setup

1. Install Flask (if not installed):
   ```
   pip install flask
   ```

2. Run the app:
   ```
   cd web_app_integrated
   python app.py
   ```

3. Open browser: http://localhost:5000

4. First time users: Click "Register here" to create an account
   - Enter name, phone number (10 digits)
   - Choose unique username (min 4 characters)
   - Set password (min 6 characters)

5. Existing users: Login with username and password

## Database
- Uses SQLite (users.db)
- Stores: name, phone, username, hashed password
- Phone numbers and usernames must be unique

## Security
- Passwords are hashed using SHA256
- Session-based authentication
- Protected routes (must login to access dashboard)
'''

with open(app_dir / "README.md", "w", encoding='utf-8') as f:
    f.write(readme)

print("✓ Created README.md")

print("\n" + "="*60)
print("✅ AUTHENTICATION SYSTEM COMPLETE!")
print("="*60)
print("\nCreated files:")
print("  ✓ app.py (with login/register/database)")
print("  ✓ templates/login.html")
print("  ✓ templates/register.html")
print("  ✓ templates/dashboard.html")
print("  ✓ README.md")
print("\nFeatures:")
print("  ✓ User registration with validation")
print("  ✓ Login system")
print("  ✓ SQLite database (users.db)")
print("  ✓ Password hashing")
print("  ✓ Unique phone & username check")
print("  ✓ Session management")
print("  ✓ Protected dashboard")
print("\nTo run:")
print("  cd web_app_integrated")
print("  python app.py")
print("="*60)