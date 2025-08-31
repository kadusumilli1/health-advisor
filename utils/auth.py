from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .file_manager import load_json_file, save_json_file

def get_user_by_email(email, users_file_path):
    """Get user data by email."""
    users = load_json_file(users_file_path)
    return users.get(email)

def create_user(name, email, password, age, sex, race, users_file_path):
    """Create a new user account."""
    users = load_json_file(users_file_path)
    if email in users:
        return False
    
    users[email] = {
        'name': name,
        'email': email,
        'password': generate_password_hash(password),
        'age': age,
        'sex': sex,
        'race': race,
        'created_at': datetime.now().isoformat()
    }
    save_json_file(users_file_path, users)
    return True

def update_user_profile(email, age, sex, race, users_file_path):
    """Update user profile information."""
    users = load_json_file(users_file_path)
    if email not in users:
        return False
    
    users[email].update({
        'age': age,
        'sex': sex,
        'race': race,
        'updated_at': datetime.now().isoformat()
    })
    save_json_file(users_file_path, users)
    return True

def validate_user_credentials(email, password, users_file_path):
    """Validate user login credentials."""
    user = get_user_by_email(email, users_file_path)
    if user and check_password_hash(user['password'], password):
        return user
    return None