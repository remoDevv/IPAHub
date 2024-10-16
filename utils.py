import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, filename):
    # Ensure the upload folder exists
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Generate a unique filename to prevent overwriting
    unique_filename = f"{uuid.uuid4().hex}_{secure_filename(filename)}"
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    return file_path
