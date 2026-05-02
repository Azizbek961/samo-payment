import os
import sys
import threading
import socket
import time
import webview
import logging
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PyInstaller frozen mode path fix
if getattr(sys, "frozen", False):
    sys.path.insert(0, sys._MEIPASS)
    sys.path.insert(0, os.path.dirname(sys.executable))
    os.environ['_MEIPASS'] = sys._MEIPASS
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_server():
    """Run Django server using Waitress WSGI server."""
    try:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

        import django
        django.setup()

        from django.core.wsgi import get_wsgi_application
        from waitress import serve

        app = get_wsgi_application()
        
        logger.info("Starting Django server on http://127.0.0.1:8000")
        serve(app, host="127.0.0.1", port=8000, threads=8)

    except Exception as e:
        logger.error(f"SERVER ERROR: {e}", exc_info=True)
        raise


def wait_for_server(host="127.0.0.1", port=8000, timeout=30):
    """Wait for server to be ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def open_browser():
    """Open browser after server is ready."""
    if wait_for_server():
        logger.info("Server is ready, opening browser...")
        webbrowser.open("http://127.0.0.1:8000")
    else:
        logger.error("Server failed to start within timeout period.")


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Samo Payment Application Starting...")
    logger.info("=" * 50)

    # Start Django server in a daemon thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server and open browser
    if wait_for_server():
        logger.info("Server started successfully!")
        
        # Create webview window (embedded browser)
        try:
            window = webview.create_window(
                "Samo Payment",
                "http://127.0.0.1:8000",
                width=1280,
                height=800,
                resizable=True,
                fullscreen=False,
                min_size=(800, 600)
            )
            webview.start()
        except Exception as e:
            logger.warning(f"Webview failed: {e}, opening in default browser instead")
            webbrowser.open("http://127.0.0.1:8000")
            # Keep the application running
            while True:
                time.sleep(1)
    else:
        logger.error("Server ishga tushmadi.")
        input("Press Enter to exit...")
