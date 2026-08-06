import PyInstaller.__main__
import os
import shutil
import sys
from pathlib import Path

def build_exe(app_dir, entry_point_name, app_name, icon_path=None):
    """
    Generic builder that freezes a Flask+Pywebview app into a single EXE.
    
    Args:
        app_dir (str): Relative path to the app folder (e.g. "apps/Idea-E")
        entry_point (str): Name of the main python file (e.g. "main.py")
        app_name (str): Name of the resulting .exe
    """
    
    base_path = Path(os.getcwd())
    app_path = base_path / app_dir
    entry_point = app_path / entry_point_name
    
    if not entry_point.exists():
        print(f"Error: Could not find entry point: {entry_point}")
        return

    print(f"Building {app_name} from {entry_point}...")

    # 1. Detect Flask folders (templates/static) to include
    add_data_args = []
    
    templates_path = app_path / 'templates'
    static_path = app_path / 'static'
    data_path = app_path / 'data'
    
    # Format: "source_path;dest_folder" (Windows uses ;)
    if templates_path.exists():
        add_data_args.append(f'--add-data={templates_path};templates')
        print("   Found templates folder")
        
    if static_path.exists():
        add_data_args.append(f'--add-data={static_path};static')
        print("   Found static folder")
        
    if data_path.exists():
        add_data_args.append(f'--add-data={data_path};data')
        print("   Found data folder")

    # 2. Build PyInstaller Command
    args = [
        str(entry_point),
        f'--name={app_name}',
        '--noconfirm',
        '--clean',
        '--onefile',             # Single .exe file
        '--windowed',            # No console window
        '--contents-directory=.', # Keep contents in root of temp dir
        f'--paths={base_path}',   # Add project root to path so flask_packager imports work
    ]
    
    # Add data arguments
    args.extend(add_data_args)
    
    if icon_path and os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')

    # 3. Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print(f"\nBuild Complete! Check the 'dist' folder for {app_name}.exe")
    except Exception as e:
        print(f"\nBuild Failed: {e}")

if __name__ == "__main__":
    # Example usage CLI
    # python apps/flask_packager/builder.py apps/Idea-E app.py "ArtificerCodex"
    if len(sys.argv) < 4:
        print("Usage: python builder.py <app_dir> <entry_point> <exe_name>")
    else:
        build_exe(sys.argv[1], sys.argv[2], sys.argv[3])
