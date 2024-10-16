import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, filename):
    if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
        os.makedirs(current_app.config['UPLOAD_FOLDER'])
    
    # Generate a unique filename to prevent overwriting
    unique_filename = f"{uuid.uuid4().hex}_{secure_filename(filename)}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    return file_path
