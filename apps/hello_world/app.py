from flask import Flask, render_template
import sys
import os

# Add project root to path so we can find _engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from _engine.game_client import launch

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/click')
def click():
    return "Clicked! Hello from Python Logic!"

if __name__ == "__main__":
    # Launch in native window using Murex Engine
    launch(app, title="Murex Hello World", width=800, height=600)
