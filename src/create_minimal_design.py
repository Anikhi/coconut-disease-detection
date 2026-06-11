"""
Beautiful Login/Registration Design
====================================
Modern split-screen design with illustration

Author: [Nikhitha A]
Date: February 2026
"""

from pathlib import Path

print("\nCreating beautiful login/registration pages...")

app_dir = Path("web_app_integrated")
templates_dir = app_dir / "templates"
templates_dir.mkdir(parents=True, exist_ok=True)

# Beautiful Login Page
login_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Login - Coconut Disease Detection</title>
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #a0827d 0%, #8b6f6a 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .main-container {
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            max-width: 1200px;
            width: 100%;
            background: white;
            border-radius: 30px;
            overflow: hidden;
            box-shadow: 0 30px 90px rgba(0,0,0,0.3);
            min-height: 600px;
        }
        
        .form-section {
            padding: 60px 50px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: #f5f5f5;
        }
        
        .logo-section {
            margin-bottom: 40px;
        }
        
        .logo-section h1 {
            font-size: 2.5em;
            color: #2c2c2c;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .logo-section p {
            color: #666;
            font-size: 1em;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group input {
            width: 100%;
            padding: 18px 20px;
            border: none;
            border-radius: 12px;
            font-size: 1em;
            background: white;
            color: #2c2c2c;
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .form-group input::placeholder {
            color: #aaa;
        }
        
        .form-group input:focus {
            outline: none;
            box-shadow: 0 4px 15px rgba(160, 130, 125, 0.2);
            transform: translateY(-2px);
        }
        
        .submit-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #a0827d 0%, #8b6f6a 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        
        .submit-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(160, 130, 125, 0.3);
        }
        
        .submit-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .link-text {
            text-align: center;
            margin-top: 25px;
            color: #666;
            font-size: 0.95em;
        }
        
        .link-text a {
            color: #a0827d;
            text-decoration: none;
            font-weight: 600;
        }
        
        .link-text a:hover {
            text-decoration: underline;
        }
        
        .divider {
            text-align: center;
            margin: 30px 0;
            color: #999;
            position: relative;
        }
        
        .divider::before,
        .divider::after {
            content: '';
            position: absolute;
            top: 50%;
            width: 40%;
            height: 1px;
            background: #ddd;
        }
        
        .divider::before { left: 0; }
        .divider::after { right: 0; }
        
        .social-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
        }
        
        .social-btn {
            width: 60px;
            height: 60px;
            border-radius: 15px;
            background: white;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        .social-btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        
        .social-btn img {
            width: 28px;
            height: 28px;
        }
        
        .illustration-section {
            background: linear-gradient(135deg, #7a5f8f 0%, #d4a574 50%, #e8c4a0 100%);
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .illustration {
            width: 100%;
            height: 100%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .coconut-tree {
            font-size: 15em;
            opacity: 0.9;
            text-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .landscape {
            position: absolute;
            bottom: 0;
            width: 100%;
            height: 40%;
            background: linear-gradient(to bottom, transparent 0%, rgba(123, 104, 135, 0.3) 100%);
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: none;
            animation: slideIn 0.3s;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .alert-error {
            background: #ffe6e6;
            color: #d32f2f;
            border-left: 4px solid #d32f2f;
        }
        
        .alert-success {
            background: #e8f5e9;
            color: #2e7d32;
            border-left: 4px solid #2e7d32;
        }
        
        @media (max-width: 968px) {
            .main-container {
                grid-template-columns: 1fr;
            }
            
            .illustration-section {
                display: none;
            }
            
            .form-section {
                padding: 40px 30px;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="form-section">
            <div class="logo-section">
                <h1>Welcome Back</h1>
                <p>Sign in to continue to Coconut Disease Detection</p>
            </div>
            
            <div id="alert" class="alert"></div>
            
            <form id="loginForm">
                <div class="form-group">
                    <input type="text" id="username" placeholder="Username" required>
                </div>
                
                <div class="form-group">
                    <input type="password" id="password" placeholder="Password" required>
                </div>
                
                <button type="submit" class="submit-btn" id="loginBtn">Sign In</button>
            </form>
            
            <div class="link-text">
                Don't have an account? <a href="/register">Create account</a>
            </div>
            
            <div class="divider">or</div>
            
            <div class="social-buttons">
                <button class="social-btn" title="Sign in with Google">
                    <svg width="28" height="28" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
                </button>
                <button class="social-btn" title="Sign in with Apple">
                    <svg width="28" height="28" viewBox="0 0 24 24"><path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" fill="#000"/></svg>
                </button>
                <button class="social-btn" title="Sign in with Facebook">
                    <svg width="28" height="28" viewBox="0 0 24 24"><path fill="#1877F2" d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                </button>
            </div>
        </div>
        
        <div class="illustration-section">
            <div class="illustration">
                <div class="coconut-tree">🌴</div>
                <div class="landscape"></div>
            </div>
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
            btn.textContent = 'Signing in...';
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert.className = 'alert alert-success';
                    alert.textContent = '✓ Login successful! Redirecting...';
                    alert.style.display = 'block';
                    setTimeout(() => window.location.href = '/dashboard', 1000);
                } else {
                    alert.className = 'alert alert-error';
                    alert.textContent = '✗ ' + data.message;
                    alert.style.display = 'block';
                    btn.disabled = false;
                    btn.textContent = 'Sign In';
                }
            } catch (error) {
                alert.className = 'alert alert-error';
                alert.textContent = '✗ Login failed. Please try again.';
                alert.style.display = 'block';
                btn.disabled = false;
                btn.textContent = 'Sign In';
            }
        });
    </script>
</body>
</html>
'''

with open(templates_dir / "login.html", "w", encoding='utf-8') as f:
    f.write(login_html)

print("✓ Created beautiful login.html")

# Beautiful Registration Page
register_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Register - Coconut Disease Detection</title>
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #a0827d 0%, #8b6f6a 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .main-container {
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            max-width: 1200px;
            width: 100%;
            background: white;
            border-radius: 30px;
            overflow: hidden;
            box-shadow: 0 30px 90px rgba(0,0,0,0.3);
            min-height: 650px;
        }
        
        .form-section {
            padding: 50px 50px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: #f5f5f5;
        }
        
        .logo-section {
            margin-bottom: 30px;
        }
        
        .logo-section h1 {
            font-size: 2.5em;
            color: #2c2c2c;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .logo-section p {
            color: #666;
            font-size: 0.95em;
        }
        
        .form-group {
            margin-bottom: 18px;
        }
        
        .form-group input {
            width: 100%;
            padding: 16px 20px;
            border: none;
            border-radius: 12px;
            font-size: 0.95em;
            background: white;
            color: #2c2c2c;
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .form-group input::placeholder {
            color: #aaa;
        }
        
        .form-group input:focus {
            outline: none;
            box-shadow: 0 4px 15px rgba(160, 130, 125, 0.2);
            transform: translateY(-2px);
        }
        
        .submit-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #a0827d 0%, #8b6f6a 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.05em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        
        .submit-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(160, 130, 125, 0.3);
        }
        
        .submit-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .link-text {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 0.9em;
        }
        
        .link-text a {
            color: #a0827d;
            text-decoration: none;
            font-weight: 600;
        }
        
        .link-text a:hover {
            text-decoration: underline;
        }
        
        .divider {
            text-align: center;
            margin: 25px 0;
            color: #999;
            position: relative;
            font-size: 0.9em;
        }
        
        .divider::before,
        .divider::after {
            content: '';
            position: absolute;
            top: 50%;
            width: 40%;
            height: 1px;
            background: #ddd;
        }
        
        .divider::before { left: 0; }
        .divider::after { right: 0; }
        
        .social-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
        }
        
        .social-btn {
            width: 60px;
            height: 60px;
            border-radius: 15px;
            background: white;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        .social-btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        
        .social-btn img {
            width: 28px;
            height: 28px;
        }
        
        .illustration-section {
            background: linear-gradient(135deg, #7a5f8f 0%, #d4a574 50%, #e8c4a0 100%);
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .illustration {
            width: 100%;
            height: 100%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .coconut-tree {
            font-size: 15em;
            opacity: 0.9;
            text-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .landscape {
            position: absolute;
            bottom: 0;
            width: 100%;
            height: 40%;
            background: linear-gradient(to bottom, transparent 0%, rgba(123, 104, 135, 0.3) 100%);
        }
        
        .alert {
            padding: 12px 18px;
            border-radius: 12px;
            margin-bottom: 18px;
            display: none;
            animation: slideIn 0.3s;
            font-size: 0.9em;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .alert-error {
            background: #ffe6e6;
            color: #d32f2f;
            border-left: 4px solid #d32f2f;
        }
        
        .alert-success {
            background: #e8f5e9;
            color: #2e7d32;
            border-left: 4px solid #2e7d32;
        }
        
        @media (max-width: 968px) {
            .main-container {
                grid-template-columns: 1fr;
            }
            
            .illustration-section {
                display: none;
            }
            
            .form-section {
                padding: 40px 30px;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="form-section">
            <div class="logo-section">
                <h1>Create account</h1>
                <p>Let's get started with your journey</p>
            </div>
            
            <div id="alert" class="alert"></div>
            
            <form id="registerForm">
                <div class="form-group">
                    <input type="text" id="name" placeholder="Full Name" required>
                </div>
                
                <div class="form-group">
                    <input type="tel" id="phone" placeholder="Phone Number (10 digits)" pattern="[0-9]{10}" required>
                </div>
                
                <div class="form-group">
                    <input type="text" id="username" placeholder="Username (min 4 characters)" minlength="4" required>
                </div>
                
                <div class="form-group">
                    <input type="password" id="password" placeholder="Password (min 6 characters)" minlength="6" required>
                </div>
                
                <button type="submit" class="submit-btn" id="registerBtn">Create account</button>
            </form>
            
            <div class="link-text">
                Already have an account? <a href="/login">Login</a>
            </div>
            
            <div class="divider">or</div>
            
            <div class="social-buttons">
                <button class="social-btn" title="Sign up with Google">
                    <svg width="28" height="28" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
                </button>
                <button class="social-btn" title="Sign up with Apple">
                    <svg width="28" height="28" viewBox="0 0 24 24"><path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" fill="#000"/></svg>
                </button>
                <button class="social-btn" title="Sign up with Facebook">
                    <svg width="28" height="28" viewBox="0 0 24 24"><path fill="#1877F2" d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                </button>
            </div>
        </div>
        
        <div class="illustration-section">
            <div class="illustration">
                <div class="coconut-tree">🌴</div>
                <div class="landscape"></div>
            </div>
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
            btn.textContent = 'Creating account...';
            
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, phone, username, password})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert.className = 'alert alert-success';
                    alert.textContent = '✓ Account created! Redirecting...';
                    alert.style.display = 'block';
                    setTimeout(() => window.location.href = '/dashboard', 1000);
                } else {
                    alert.className = 'alert alert-error';
                    alert.textContent = '✗ ' + data.message;
                    alert.style.display = 'block';
                    btn.disabled = false;
                    btn.textContent = 'Create account';
                }
            } catch (error) {
                alert.className = 'alert alert-error';
                alert.textContent = '✗ Registration failed. Please try again.';
                alert.style.display = 'block';
                btn.disabled = false;
                btn.textContent = 'Create account';
            }
        });
    </script>
</body>
</html>
'''

with open(templates_dir / "register.html", "w", encoding='utf-8') as f:
    f.write(register_html)

print("✓ Created beautiful register.html")

print("\n" + "="*60)
print("✅ BEAUTIFUL LOGIN/REGISTER PAGES CREATED!")
print("="*60)
print("\nFeatures:")
print("  ✓ Split-screen modern design")
print("  ✓ Warm color palette (browns, rose)")
print("  ✓ Smooth animations")
print("  ✓ Social login buttons (Google, Apple, Facebook)")
print("  ✓ Clean minimalist forms")
print("  ✓ Mobile responsive")
print("  ✓ Coconut tree illustration")
print("  ✓ Soft shadows and gradients")
print("\nFiles created:")
print("  ✓ web_app_integrated/templates/login.html")
print("  ✓ web_app_integrated/templates/register.html")
print("="*60)
