# Coconut Disease Detection with Authentication

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
