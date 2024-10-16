import os
import zipfile

def create_project_zip(output_filename='project.zip'):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Exclude unnecessary directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.cache', '.local', '.pythonlibs', '.upm']]
            
            for file in files:
                if not file.endswith('.pyc') and file != output_filename:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, '.')
                    zipf.write(file_path, arcname)

    print(f"Project zip file '{output_filename}' created successfully.")

if __name__ == '__main__':
    create_project_zip()
