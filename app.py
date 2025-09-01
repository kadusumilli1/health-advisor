import os
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

from utils.auth import create_user, validate_user_credentials, get_user_by_email, update_user_profile
from utils.file_manager import load_json_file, save_health_data, delete_health_data

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
os.makedirs('data', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

USERS_FILE = 'data/users.json'
HEALTH_DATA_FILE = 'data/health_data.json'

@app.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if not name or not email or not password:
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        if create_user(name, email, password, USERS_FILE):
            session['user_email'] = email
            session['user_name'] = name
            flash('Account created successfully! Welcome!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email already exists', 'error')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = validate_user_credentials(email, password, USERS_FILE)
        if user:
            session['user_email'] = email
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    email = session['user_email']
    health_data = load_json_file(HEALTH_DATA_FILE)
    user_files = health_data.get(email, [])
    
    # Check if user should see profile completion prompt
    # Only show if they have uploaded files but profile is incomplete
    show_profile_prompt = False
    if user_files:  # User has uploaded at least one file
        user = get_user_by_email(email, USERS_FILE)
        profile_complete = all([user.get('age'), user.get('sex'), user.get('race')])
        show_profile_prompt = not profile_complete
    
    return render_template('dashboard.html', 
                         user_name=session['user_name'], 
                         files=user_files,
                         show_profile_prompt=show_profile_prompt)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    email = session['user_email']
    
    if request.method == 'POST':
        age = request.form.get('age')
        sex = request.form.get('sex')
        race = request.form.get('race')
        
        # Convert age to int if provided
        if age:
            try:
                age = int(age)
                if age < 1 or age > 150:
                    flash('Please enter a valid age between 1 and 150', 'error')
                    return redirect(url_for('profile'))
            except ValueError:
                flash('Please enter a valid age', 'error')
                return redirect(url_for('profile'))
        else:
            age = None
            
        # Set empty strings to None
        sex = sex if sex else None
        race = race if race else None
        
        if update_user_profile(email, age, sex, race, USERS_FILE):
            flash('Profile updated successfully!', 'success')
        else:
            flash('Error updating profile', 'error')
        
        return redirect(url_for('profile'))
    
    user = get_user_by_email(email, USERS_FILE)
    return render_template('profile.html', user=user)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('dashboard'))
    
    if file:
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        save_health_data(session['user_email'], filename, file.filename, HEALTH_DATA_FILE)
        flash('File uploaded successfully!', 'success')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    email = session['user_email']
    
    if delete_health_data(email, filename, HEALTH_DATA_FILE, app.config['UPLOAD_FOLDER']):
        flash('File deleted successfully!', 'success')
    else:
        flash('Error deleting file. File may not exist.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)