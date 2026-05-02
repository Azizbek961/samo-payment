# Samo Payment Application - How to Run

Complete guide to running the Samo Payment Application on Windows and Linux.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Running in Development Mode](#running-in-development-mode)
4. [Building the Executable](#building-the-executable)
5. [Running the Executable](#running-the-executable)
6. [First-Time Setup](#first-time-setup)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Windows

**Option A: Run Without Building (Development)**
```batch
python run_server.py
```

**Option B: Build and Run (Production)**
```batch
build.bat
dist\SamoPayment.exe
```

### Linux

**Option A: Run Without Building (Development)**
```bash
python3 run_server.py
```

**Option B: Build and Run (Production)**
```bash
chmod +x build.sh
./build.sh
./dist/SamoPayment
```

---

## Prerequisites

| Requirement | Version | How to Install |
|-------------|---------|----------------|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| pip | Latest | Included with Python 3.4+ |
| Internet | Required | For downloading dependencies |

### Verify Installation

**Windows:**
```batch
python --version
pip --version
```

**Linux:**
```bash
python3 --version
pip3 --version
```

### Linux-Specific Dependencies

On Fedora/RHEL:
```bash
sudo dnf install python3-pip python3-devel gtk3 webkit2gtk3
```

On Ubuntu/Debian:
```bash
sudo apt-get install python3-pip python3-dev libgtk-3-dev libwebkit2gtk-4.0-dev
```

---

## Running in Development Mode

### Step 1: Install Dependencies

**Windows:**
```batch
pip install -r requirements.txt
```

**Linux:**
```bash
pip3 install -r requirements.txt
```

### Step 2: Collect Static Files

**Windows:**
```batch
python manage.py collectstatic --noinput
```

**Linux:**
```bash
python3 manage.py collectstatic --noinput
```

### Step 3: Initialize Database (First Time Only)

**Windows:**
```batch
python init_db.py
```

**Linux:**
```bash
python3 init_db.py
```

### Step 4: Run the Server

**Windows:**
```batch
python run_server.py
```

**Linux:**
```bash
python3 run_server.py
```

**Available Options:**

| Option | Description | Example |
|--------|-------------|---------|
| `--no-browser` | Don't open browser | `python run_server.py --no-browser` |
| `--port PORT` | Custom port | `python run_server.py --port 8080` |
| `--host HOST` | Custom host | `python run_server.py --host 0.0.0.0` |

### Step 5: Access the Application

The application will automatically open in your browser at:
```
http://127.0.0.1:8000
```

If it doesn't open automatically, navigate to the URL manually.

---

## Building the Executable

### Method 1: Using Build Script (Recommended)

**Windows:**
```batch
build.bat
```

**Linux:**
```bash
chmod +x build.sh
./build.sh
```

This script will:
1. Clean previous builds
2. Install dependencies
3. Collect static files
4. Build the executable with PyInstaller

### Method 2: Manual Build

**Windows:**
```batch
REM 1. Clean previous builds
rmdir /s /q build dist
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

REM 2. Install dependencies
pip install -r requirements.txt

REM 3. Collect static files
python manage.py collectstatic --noinput --clear

REM 4. Build with PyInstaller
pyinstaller desktop_app.spec --clean
```

**Linux:**
```bash
# 1. Clean previous builds
rm -rf build dist
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Collect static files
python3 manage.py collectstatic --noinput --clear

# 4. Build with PyInstaller
pyinstaller desktop_app.spec --clean
```

### Build Output

After successful build:

**Windows:**
```
dist/
└── SamoPayment.exe    (~50-100 MB)
```

**Linux:**
```
dist/
└── SamoPayment        (~100-150 MB)
```

---

## Running the Executable

### Method 1: Double-Click

**Windows:** Simply double-click `dist\SamoPayment.exe`

**Linux:** Double-click `dist/SamoPayment` in your file manager

### Method 2: Command Line

**Windows:**
```batch
cd dist
SamoPayment.exe
```

**Linux:**
```bash
cd dist
./SamoPayment
```

### What Happens on Startup

1. ✅ Django server initializes
2. ✅ Database is checked/migrated
3. ✅ Server starts on `http://127.0.0.1:8000`
4. ✅ Browser window opens automatically
5. ✅ Application is ready to use

### Console Output

You'll see output like:
```
============================================================
  Samo Payment Application - Django Server Launcher
============================================================
  Base Directory: C:\path\to\dist
  Frozen Mode: True
  Host: 127.0.0.1
  Port: 8000
============================================================
Django setup completed successfully.
Database check completed.
Starting Django server on http://127.0.0.1:8000
Press Ctrl+C to stop the server.
```

---

## First-Time Setup

### Default Admin Account

On first run, a default admin user is created:

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `admin123` |
| **Email** | `admin@example.com` |

### ⚠️ Important Security Steps

1. **Change the default password immediately!**
2. Go to: `http://127.0.0.1:8000/admin/`
3. Click on your username → Change password

### Creating Additional Users

1. Login as admin
2. Go to `/admin/`
3. Click "Users" → "Add user"
4. Fill in details and set permissions

---

## Configuration

### Environment Variables (.env file)

Create a `.env` file in the project root:

```env
# Security
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database (optional - SQLite is default)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DESKTOP_SQLITE=1

# Server
ALLOWED_HOSTS=127.0.0.1,localhost
```

### Database Configuration

**SQLite (Default)**
- Database file: `db.sqlite3`
- Location: Same directory as executable
- No additional setup required

**PostgreSQL (Optional)**
1. Install PostgreSQL
2. Create database and user
3. Set `DATABASE_URL` in `.env`
4. Set `DESKTOP_SQLITE=0`

---

## Troubleshooting

### Build Issues

#### "Module not found"
```batch
pip install -r requirements.txt --upgrade
pip install --upgrade pyinstaller
```

#### "Build failed"
Check the build log for specific errors. Common issues:
- Missing dependencies
- Insufficient disk space (need ~500 MB)
- Antivirus blocking PyInstaller

### Runtime Issues

#### "Port 8000 already in use"
```batch
python run_server.py --port 8080
```

Or kill the process using port 8000:
```batch
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### "Database not found"
Run database initialization:
```batch
python init_db.py
```

Or copy `db.sqlite3` to the `dist/` folder.

#### "Static files not loading"
```batch
python manage.py collectstatic --noinput --clear
```

Then rebuild:
```batch
build.bat
```

#### "Permission denied"
Run as Administrator or check folder permissions.

#### Application crashes on startup
1. Check console output for error messages
2. Ensure all dependencies are installed
3. Try running with `--no-browser` flag
4. Check if port 8000 is available

### Printer Issues

#### "win32print not available"
- Printing is only supported on Windows
- Ensure `pywin32` is installed:
  ```batch
  pip install pywin32
  ```

#### Printer not responding
1. Check printer is connected and online
2. Verify printer name in Printer Configuration
3. Test with a simple print job first

---

## File Locations

### Development Mode
```
samo-payment-main/
├── db.sqlite3              # Database
├── staticfiles/            # Static assets
├── templates/              # HTML templates
└── media/                  # Uploaded files
```

### Executable Mode
```
dist/
├── SamoPayment.exe         # Main executable
├── db.sqlite3              # Database (if exists)
├── staticfiles/            # Static assets
└── templates/              # HTML templates
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Stop server (in console) |
| `F5` | Refresh browser |
| `Ctrl+Shift+R` | Hard refresh browser |

---

## Logs and Debugging

### Enable Debug Mode

In `.env` file:
```env
DEBUG=True
```

### View Logs

Logs are displayed in the console window. Key information:
- Server startup status
- Database migrations
- Request/response errors
- Printer status

### Log File (Advanced)

To save logs to a file, modify `run_server.py`:
```python
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## Support

### Common Error Messages

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `OperationalError` | Run `python init_db.py` |
| `PermissionError` | Run as Administrator |
| `ConnectionRefusedError` | Check if server is running |

### Getting Help

1. Check console output for error details
2. Review this documentation
3. Check Django logs in console
4. Verify all prerequisites are installed

---

## Quick Reference Card

**Windows:**
```
┌─────────────────────────────────────────────────────────────┐
│  SAMO PAYMENT - QUICK REFERENCE (Windows)                   │
├─────────────────────────────────────────────────────────────┤
│  Install:     pip install -r requirements.txt               │
│  Build:       build.bat                                     │
│  Run (dev):   python run_server.py                          │
│  Run (exe):   dist\SamoPayment.exe                          │
│  Init DB:     python init_db.py                             │
│  Collect:     python manage.py collectstatic --noinput      │
├─────────────────────────────────────────────────────────────┤
│  Default Login: admin / admin123                            │
│  URL:         http://127.0.0.1:8000                         │
│  Admin:       http://127.0.0.1:8000/admin/                  │
└─────────────────────────────────────────────────────────────┘
```

**Linux:**
```
┌─────────────────────────────────────────────────────────────┐
│  SAMO PAYMENT - QUICK REFERENCE (Linux)                     │
├─────────────────────────────────────────────────────────────┤
│  Install:     pip3 install -r requirements.txt              │
│  Build:       chmod +x build.sh && ./build.sh               │
│  Run (dev):   python3 run_server.py                         │
│  Run (exe):   ./dist/SamoPayment                            │
│  Init DB:     python3 init_db.py                            │
│  Collect:     python3 manage.py collectstatic --noinput     │
├─────────────────────────────────────────────────────────────┤
│  Default Login: admin / admin123                            │
│  URL:         http://127.0.0.1:8000                         │
│  Admin:       http://127.0.0.1:8000/admin/                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Version Information

| Component | Version |
|-----------|---------|
| Django | 5.2.11 |
| Python | 3.10+ |
| PyInstaller | 6.19.0 |
| Waitress | 3.0.2 |

---

**Last Updated:** March 2026  
**Document Version:** 1.0
