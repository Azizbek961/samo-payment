#!/usr/bin/env python
"""
Database initialization script for Samo Payment Application.

This script ensures the database is properly set up when running
in packaged (PyInstaller) mode.

Usage:
    python init_db.py
"""

import os
import sys
import logging
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


def init_database():
    """Initialize the database with migrations and create superuser if needed."""
    try:
        import django
        django.setup()
        logger.info("Django setup completed.")

        from django.core.management import call_command
        from django.contrib.auth import get_user_model
        from django.db import connection

        # Check if database tables exist
        tables = connection.introspection.table_names()
        
        if not tables:
            logger.info("Database is empty. Running migrations...")
            call_command('migrate', '--run-syncdb', verbosity=1)
            logger.info("Migrations completed.")
        else:
            logger.info(f"Database already has {len(tables)} tables.")
            # Run any pending migrations
            call_command('migrate', '--run-syncdb', verbosity=0)

        # Check if admin user exists
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            logger.info("Creating default admin user...")
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            logger.info("Default admin user created (username: admin, password: admin123)")
        else:
            logger.info("Admin user already exists.")

        logger.info("Database initialization completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("  Samo Payment Application - Database Initialization")
    logger.info("=" * 60)
    logger.info(f"  Base Directory: {BASE_DIR}")
    logger.info(f"  Frozen Mode: {is_frozen()}")
    logger.info("=" * 60)
    
    success = init_database()
    sys.exit(0 if success else 1)
