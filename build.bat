@echo off
REM Build script for Samo Payment Application (Windows)
REM This script builds the Windows executable using PyInstaller

echo ==============================================
echo   Samo Payment Application - Build Script
echo ==============================================

REM Check if we're in the right directory
if not exist "manage.py" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

REM Install/upgrade dependencies
echo.
echo Checking dependencies...
pip install -r requirements.txt --quiet

REM Collect static files
echo.
echo Collecting static files...
python manage.py collectstatic --noinput --clear

REM Build with PyInstaller
echo.
echo Building executable with PyInstaller...
pyinstaller desktop_app.spec --clean

REM Check if build was successful
if exist "dist\SamoPayment.exe" (
    echo.
    echo ==============================================
    echo   Build successful!
    echo ==============================================
    echo.
    echo Executable location:
    echo   %cd%\dist\SamoPayment.exe
    echo.
    echo To run the application:
    echo   dist\SamoPayment.exe
    echo.
) else (
    echo.
    echo ==============================================
    echo   Build failed!
    echo ==============================================
    echo Check the build log for errors.
    exit /b 1
)
