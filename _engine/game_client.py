import sys
import threading
import webview
import time
import socket
from screeninfo import get_monitors

class GameClient:
    def __init__(self, flask_app, title="Murex Game", width=1280, height=720, resizable=True, fullscreen=False):
        self.flask_app = flask_app
        self.title = title
        self.width = width
        self.height = height
        self.resizable = resizable
        self.fullscreen = fullscreen
        self.port = self._find_free_port()
        
    def _find_free_port(self):
        """Finds an available port to run the Flask server on."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    def _start_flask(self):
        """Runs the Flask server in a separate thread."""
        # Disable Flask logging to console to keep it clean
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        self.flask_app.run(port=self.port, use_reloader=False)

    def run(self):
        """Launches the native window wrapping the Flask app."""
        # 1. Start Flask in thread
        t = threading.Thread(target=self._start_flask, daemon=True)
        t.start()
        
        # Give Flask a moment to spin up
        time.sleep(0.5)
        
        # 2. Create Native Window
        # We point it to the localhost url of our flask app
        url = f"http://127.0.0.1:{self.port}"
        
        webview.create_window(
            self.title, 
            url,
            width=self.width, 
            height=self.height,
            resizable=self.resizable,
            fullscreen=self.fullscreen,
            background_color='#000000' # Prevent white flash on load
        )
        
        # 3. Start the GUI loop
        webview.start(debug=True) # Debug allows F12 dev tools, set False for release

def launch(app, **kwargs):
    """Helper entry point."""
    client = GameClient(app, **kwargs)
    client.run()
