import sys
import os
from flask import Flask, render_template, send_from_directory
from jinja2 import FileSystemLoader, ChoiceLoader

# Ensure we can find the project root and the main app modules
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
app_dir = os.path.abspath(os.path.join(current_dir, '../murex_lab'))

if project_root not in sys.path: sys.path.append(project_root)
if app_dir not in sys.path: sys.path.append(app_dir)

from _engine.game_client import launch
from apps.murex_lab.app import app  # Import the main flask app

# --- RETRO ASSET MANAGEMENT ---
# Inject retro templates into the app's loader
retro_templates_path = os.path.join(current_dir, 'templates')
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(retro_templates_path),
    app.jinja_loader
])

# Route to serve retro-specific static files (fonts, retro_core.js)
@app.route('/static/retro/<path:filename>')
def serve_retro_static(filename):
    return send_from_directory(os.path.join(current_dir, 'static', 'retro'), filename)

@app.route('/static/fonts/<path:filename>')
def serve_retro_fonts(filename):
    return send_from_directory(os.path.join(current_dir, 'static', 'fonts'), filename)

# Overwrite the home endpoint to launch into Retro mode
def retro_entry_point():
    """Main game entry point for the Retro App."""
    return render_template('retro/index.html')

app.view_functions['home'] = retro_entry_point

if __name__ == "__main__":
    # Launch via Capsule Engine with specific Retro settings
    launch(
        app, 
        title="Murex Lab [Retro Console]", 
        width=1920, 
        height=1080, 
        resizable=False,
        fullscreen=False
    )
