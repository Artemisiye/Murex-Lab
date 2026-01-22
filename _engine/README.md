# 🏗️ Murex Engine Infrastructure

This folder contains the reusable core components for packaging web-based games into native executables.

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
    
    # Add project root to path so we can find _engine
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    
    from _engine.game_client import launch
    launch(app, title="My Awesome Game", width=1280, height=800)
```

## 🔨 How to Build an EXE

Run the builder script from the project root:

```powershell
# Syntax: python _engine/builder.py <folder> <main_script> <exe_name>

python _engine/builder.py apps/Idea-E app.py "CodexGame"
```

The resulting optimized `.exe` will be in the `dist/` folder.
