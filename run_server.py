#!/usr/bin/env python
"""
Django Server Launcher for Samo Payment Application

This script automatically configures the Django environment and starts
the backend server. It works both in development and packaged (PyInstaller) mode.

Usage:
    python run_server.py [--no-browser] [--port 8000]
    
Options:
    --no-browser    Do not open browser automatically
    --port PORT     Specify port number (default: 8000)
"""

import os
import sys
import socket
import time
import logging
import argparse
import threading
import webbrowser
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def is_frozen():
    """Check if running as a PyInstaller frozen executable."""
    return getattr(sys, "frozen", False)


def get_base_dir():
    """Get the base directory depending on execution mode."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    else:
        return Path(__file__).resolve().parent


# Set up paths
BASE_DIR = get_base_dir()
if is_frozen():
    sys.path.insert(0, str(BASE_DIR))
    os.environ['_MEIPASS'] = getattr(sys, '_MEIPASS', str(BASE_DIR))
else:
    sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


def wait_for_server(host: str, port: int, timeout: int = 30) -> bool:
    """Wait for the server to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (OSError, socket.error):
            time.sleep(0.3)
    return False


def init_database():
    """Initialize database if needed."""
    try:
        import django
        django.setup()

        from django.core.management import call_command
        from django.contrib.auth import get_user_model
        from django.db import connection

        tables = connection.introspection.table_names()
        
        if not tables:
            logger.info("Database is empty. Running migrations...")
            call_command('migrate', '--run-syncdb', verbosity=0)
            
            # Create default admin user
            User = get_user_model()
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123',
                    first_name='Admin',
                    last_name='User'
                )
                logger.info("Default admin user created (admin/admin123)")
        else:
            # Run any pending migrations
            call_command('migrate', '--run-syncdb', verbosity=0)
            
        logger.info("Database check completed.")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def run_django_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the Django server using Waitress."""
    try:
        import django
        django.setup()
        logger.info("Django setup completed successfully.")

        # Initialize database
        init_database()

        from django.core.wsgi import get_wsgi_application
        from waitress import serve

        application = get_wsgi_application()
        
        logger.info(f"Starting Django server on http://{host}:{port}")
        logger.info("Press Ctrl+C to stop the server.")
        
        serve(application, host=host, port=port, threads=8)

    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure Django and Waitress are installed.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


def open_browser(host: str, port: int, delay: float = 2.0):
    """Open the default browser after a short delay."""
    time.sleep(delay)
    if wait_for_server(host, port, timeout=5):
        url = f"http://{host}:{port}"
        logger.info(f"Opening browser at {url}")
        webbrowser.open(url)
    else:
        logger.warning("Server not ready, browser not opened.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Samo Payment Django Server Launcher"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open browser automatically"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address (default: 127.0.0.1)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("  Samo Payment Application - Django Server Launcher")
    logger.info("=" * 60)
    logger.info(f"  Base Directory: {BASE_DIR}")
    logger.info(f"  Frozen Mode: {is_frozen()}")
    logger.info(f"  Host: {args.host}")
    logger.info(f"  Port: {args.port}")
    logger.info("=" * 60)

    # Start server in a separate thread
    server_thread = threading.Thread(
        target=run_django_server,
        kwargs={"host": args.host, "port": args.port},
        daemon=True
    )
    server_thread.start()

    # Optionally open browser
    if not args.no_browser:
        browser_thread = threading.Thread(
            target=open_browser,
            kwargs={"host": args.host, "port": args.port},
            daemon=True
        )
        browser_thread.start()

    # Keep main thread alive
    try:
        while server_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
        sys.exit(0)


if __name__ == '__main__':
    main()
