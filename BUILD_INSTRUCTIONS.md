# Samo Payment Application - Windows Executable Build Guide

This guide explains how to build and run the Samo Payment Application as a standalone Windows executable.

## 📋 Prerequisites

- **Python 3.10+** installed on Windows
- **pip** package manager
- **Internet connection** (for downloading dependencies)

## 🏗️ Building the Executable

### Option 1: Using Build Script (Recommended)

1. **Open Command Prompt** in the project directory
2. **Run the build script**:
   ```batch
   build.bat
   ```

### Option 2: Manual Build

1. **Install dependencies**:
   ```batch
   pip install -r requirements.txt
   ```

2. **Collect static files**:
   ```batch
   python manage.py collectstatic --noinput
   ```

3. **Build with PyInstaller**:
   ```batch
   pyinstaller desktop_app.spec --clean
   ```

## 📁 Output

After successful build, you'll find:
- **Executable**: `dist/SamoPayment.exe`
- **Database**: `dist/db.sqlite3` (if exists)
- **Static files**: `dist/staticfiles/`
- **Templates**: `dist/templates/`

## 🚀 Running the Application

### Method 1: Using the Executable

Simply double-click `dist/SamoPayment.exe` or run:
```batch
dist\SamoPayment.exe
```

The application will:
1. Start the Django backend server automatically
2. Initialize the database if needed
3. Open a webview window with the application
4. Listen on `http://127.0.0.1:8000`

### Method 2: Using run_server.py

```batch
python run_server.py
```

**Options**:
- `--no-browser` - Don't open browser automatically
- `--port 8080` - Use a different port
- `--host 0.0.0.0` - Listen on all interfaces

## 🔐 Default Credentials

After first run, a default admin user is created:
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ Change these credentials immediately after first login!**

## 📂 Project Structure

```
samo-payment-main/
├── config/                 # Django settings and configuration
│   ├── settings.py         # Main settings file
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI application
├── apps/                   # Django applications
│   ├── accounts/           # User accounts
│   ├── dashboard/          # Dashboard views
│   ├── students/           # Student management
│   ├── payments/           # Payment processing
│   ├── reports/            # Reports and exports
│   └── printers/           # Printer integration
├── templates/              # HTML templates
├── staticfiles/            # Static assets (CSS, JS, images)
├── run_server.py           # Server launcher script
├── init_db.py              # Database initialization script
├── desktop_app.py          # Desktop application with webview
├── desktop_app.spec        # PyInstaller specification
├── build.bat               # Windows build script
├── build.sh                # Linux/Mac build script
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DESKTOP_SQLITE=1
```

### Database Configuration

By default, the application uses SQLite (`db.sqlite3`). To use PostgreSQL:

1. Set `DATABASE_URL` environment variable
2. Set `DESKTOP_SQLITE=0`

## 🐛 Troubleshooting

### Build Errors

**"Module not found"**:
```batch
pip install -r requirements.txt --upgrade
```

**"PyInstaller failed"**:
```batch
pip install --upgrade pyinstaller
pyinstaller --version
```

### Runtime Errors

**"Database not found"**:
- Ensure `db.sqlite3` is in the same directory as the executable
- Or run `python init_db.py` to create a new database

**"Port already in use"**:
```batch
python run_server.py --port 8080
```

**"Static files not loading"**:
```batch
python manage.py collectstatic --noinput --clear
```

## 📝 Build Configuration (desktop_app.spec)

Key options in the spec file:

| Option | Description |
|--------|-------------|
| `--onefile` | Single executable (default) |
| `--add-data` | Include templates, static files |
| `--hidden-import` | Include Django modules |
| `--console` | Show console for debugging |

## 🔒 Security Notes

1. **Change default admin password** immediately
2. **Set `DEBUG=False`** in production
3. **Generate a new `SECRET_KEY`** for production
4. **Use HTTPS** in production environments

## 📞 Support

For issues or questions:
1. Check the console output for error messages
2. Review Django logs in the console
3. Ensure all dependencies are installed

## 📄 License

This project is proprietary software. All rights reserved.
