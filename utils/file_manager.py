import os
import json
from datetime import datetime

def load_json_file(filename):
    """Load data from a JSON file."""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_json_file(filename, data):
    """Save data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def save_health_data(email, filename, original_filename, data_file_path):
    """Save health data information for a user."""
    health_data = load_json_file(data_file_path)
    if email not in health_data:
        health_data[email] = []
    
    health_data[email].append({
        'filename': filename,
        'original_filename': original_filename,
        'uploaded_at': datetime.now().isoformat()
    })
    save_json_file(data_file_path, health_data)

def delete_health_data(email, filename, data_file_path, upload_folder):
    """Delete a health data file and its metadata for a user."""
    health_data = load_json_file(data_file_path)
    
    if email not in health_data:
        return False
    
    # Find and remove the file from metadata
    user_files = health_data[email]
    file_found = False
    
    for i, file_info in enumerate(user_files):
        if file_info['filename'] == filename:
            user_files.pop(i)
            file_found = True
            break
    
    if not file_found:
        return False
    
    # Delete the actual file from uploads folder
    file_path = os.path.join(upload_folder, filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        return False
    
    # Save updated metadata
    save_json_file(data_file_path, health_data)
    return True