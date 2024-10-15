import os
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'ipa', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folders():
    upload_folder = os.path.join(os.getcwd(), 'uploads')
    icons_folder = os.path.join(upload_folder, 'icons')
    ipas_folder = os.path.join(upload_folder, 'ipas')
    
    os.makedirs(icons_folder, exist_ok=True)
    os.makedirs(ipas_folder, exist_ok=True)
