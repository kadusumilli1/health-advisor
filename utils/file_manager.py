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