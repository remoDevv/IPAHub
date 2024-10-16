import os
import zipfile
import time
from datetime import datetime

def create_project_zip():
    project_root = os.path.dirname(os.path.abspath(__file__))
    zip_filename = 'ipa_library_project.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if file != zip_filename and not file.startswith('.') and not root.startswith(('__pycache__', '.git', '.local', '.pythonlibs', '.replit', '.upm')):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_root)
                    
                    # Get file stats
                    stats = os.stat(file_path)
                    
                    # Create a ZipInfo object
                    zinfo = zipfile.ZipInfo(arcname, time.localtime(stats.st_mtime)[:6])
                    
                    # Set file permissions
                    zinfo.external_attr = (stats.st_mode & 0xFFFF) << 16
                    
                    # Read the file content
                    with open(file_path, 'rb') as f:
                        zipf.writestr(zinfo, f.read())
    
    print(f"Project zip file '{zip_filename}' created successfully.")

if __name__ == '__main__':
    create_project_zip()
