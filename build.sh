#!/bin/bash
# Build script for Samo Payment Application
# This script builds the executable using PyInstaller

set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "  Samo Payment Application - Build Script"
echo "=============================================="
echo "  Working directory: $SCRIPT_DIR"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found in $SCRIPT_DIR"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist __pycache__ apps/__pycache__ apps/*/__pycache__ config/__pycache__

# Install/upgrade dependencies
echo ""
echo "Checking dependencies..."
pip install -r requirements.txt --quiet

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Build with PyInstaller
echo ""
echo "Building executable with PyInstaller..."
pyinstaller desktop_app.spec --clean

# Check if build was successful
if [ -f "dist/SamoPayment.exe" ] || [ -f "dist/SamoPayment" ]; then
    echo ""
    echo "=============================================="
    echo "  Build successful!"
    echo "=============================================="
    echo ""
    echo "Executable location:"
    if [ -f "dist/SamoPayment.exe" ]; then
        echo "  $(pwd)/dist/SamoPayment.exe"
    else
        echo "  $(pwd)/dist/SamoPayment"
    fi
    echo ""
    echo "To run the application:"
    echo "  ./dist/SamoPayment[.exe]"
    echo ""
else
    echo ""
    echo "=============================================="
    echo "  Build failed!"
    echo "=============================================="
    echo "Check the build log for errors."
    exit 1
fi
