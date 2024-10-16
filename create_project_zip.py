import os
import zipfile

def create_project_zip():
    project_root = os.getcwd()
    zip_filename = 'ipa_library_project.zip'
    
    excluded_dirs = {'__pycache__', '.git', '.local', '.pythonlibs', '.replit', '.upm'}
    excluded_files = {'.gitignore', 'ipa_library_project.zip'}
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for file in files:
                if file not in excluded_files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_root)
                    zipf.write(file_path, arcname)
    
    zip_size = os.path.getsize(zip_filename)
    print(f"Project zip file '{zip_filename}' created successfully.")
    print(f"Location: {os.path.abspath(zip_filename)}")
    print(f"Size: {zip_size / (1024 * 1024):.2f} MB")

if __name__ == "__main__":
    create_project_zip()
