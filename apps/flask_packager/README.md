# 🏗️ Flask Packager

This folder contains the reusable core components for packaging Flask-based web games into native executables. It is not a gameplay engine — see `apps/retro-py/engine/` (pygame runtime) or `MurexLabDesign/Specs/ARCHITECTURE_SPECS.md` (planned `murex-engine` facade) for that.

## Structure
- **`game_client.py`**: The runtime wrapper. Imports your Flask app and displays it in a native window.
- **`builder.py`**: The compiler. automates PyInstaller configuration, ensuring `templates`, `static`, and `data` folders are correctly bundled inside the .exe.

## 🚀 How to Create a New App

1. Create a folder in `apps/` (e.g. `apps/MyGame`)
2. Write your standard Flask app (e.g. `app.py`)
3. **Important**: Change the bottom execution block in your `app.py`:

```python
# app.py

# ... your flask code ...

if __name__ == "__main__":
    # Instead of app.run(), use the engine launcher
    import sys
    import os
    
    # Add apps/ to path so we can find flask_packager
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
    
    from flask_packager.game_client import launch
    launch(app, title="My Awesome Game", width=1280, height=800)
```

## 🔨 How to Build an EXE

Run the builder script from the project root:

```powershell
# Syntax: python apps/flask_packager/builder.py <folder> <main_script> <exe_name>

python apps/flask_packager/builder.py apps/Idea-E app.py "CodexGame"
```

The resulting optimized `.exe` will be in the `dist/` folder.
