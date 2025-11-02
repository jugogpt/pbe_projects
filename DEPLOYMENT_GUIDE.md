# 🚀 Activity Tracker - Deployment Guide

This guide explains how to deploy the Activity Tracker app as a standalone Windows executable.

## 📁 Available Builds

You now have two deployment options:

### 1. **Single File Executable** (Recommended for distribution)
- **Location**: `dist/ActivityTracker.exe`
- **Size**: ~70MB
- **Benefits**:
  - Single file to distribute
  - No dependencies needed
  - Easy to share and run
- **Drawbacks**:
  - Slower startup (extracts files to temp)
  - Larger file size

### 2. **Folder Distribution** (Recommended for development)
- **Location**: `dist/ActivityTracker/` (folder with executable + dependencies)
- **Benefits**:
  - Faster startup
  - Easier to debug
- **Drawbacks**:
  - Multiple files to distribute
  - Larger folder size

## 🛠️ Building the Application

### Prerequisites
- Python 3.11+ installed
- All dependencies installed: `pip install -r requirements.txt`
- PyInstaller installed: `pip install pyinstaller`

### Build Options

#### Option 1: Quick Single-File Build
```bash
# Run the automated build script
build_onefile.bat
```

#### Option 2: Folder Build
```bash
# Run the folder build script
build.bat
```

#### Option 3: Manual Build
```bash
# Single file
pyinstaller --onefile --windowed --name="ActivityTracker" main.py

# Folder build
pyinstaller ActivityTracker.spec
```

## 📦 Distribution

### For End Users (Single File)
1. Copy `dist/ActivityTracker.exe` to desired location
2. Double-click to run
3. The app will automatically create:
   - `data/` folder for SQLite database
   - `data/recordings/` folder for screen recordings

### For Development/Testing (Folder)
1. Copy entire `dist/ActivityTracker/` folder
2. Run `ActivityTracker.exe` inside the folder
3. Data folders are created automatically

## 🖥️ System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB for app + space for recordings
- **Permissions**:
  - Read/write access for data storage
  - Screen capture permissions (may require admin on some systems)

## 🎯 Installation Instructions for End Users

### Simple Installation
1. Download `ActivityTracker.exe`
2. Create a folder like `C:\ActivityTracker\`
3. Move the executable to this folder
4. Create a desktop shortcut (optional)
5. Run the application

### Creating a Desktop Shortcut
1. Right-click on `ActivityTracker.exe`
2. Select "Create shortcut"
3. Move shortcut to Desktop
4. Rename to "Activity Tracker"

## 🔧 Troubleshooting

### Common Issues

#### App Won't Start
- **Cause**: Missing Visual C++ Redistributables
- **Solution**: Install [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

#### Screen Recording Permission Denied
- **Cause**: Windows security restrictions
- **Solution**: Run as administrator (right-click → "Run as administrator")

#### Database Errors
- **Cause**: No write permissions
- **Solution**: Ensure the app folder has write permissions

#### Charts Not Displaying
- **Cause**: Missing matplotlib backend
- **Solution**: Install Microsoft Visual C++ Redistributable

### Performance Optimization

#### For Single File Executable
- First run is slower (extracts to temp)
- Subsequent runs are faster
- Consider using folder distribution for frequent use

#### For Folder Distribution
- Keep all files together
- Don't delete any DLL files
- Faster startup than single file

## 📊 Features Available in Deployed Version

✅ **Fully Functional Features**:
- Real-time activity tracking
- SQLite database storage
- Screen recording (MP4 format)
- Usage charts with matplotlib
- File explorer integration

⚠️ **Limitations**:
- No auto-update mechanism
- Manual installation required
- Windows-only

## 🔄 Updates and Maintenance

### Updating the Application
1. Build new version using build scripts
2. Replace old executable with new one
3. Data is preserved (stored in separate `data/` folder)

### Backing Up Data
- Copy the entire `data/` folder
- Contains SQLite database and recordings
- Can be restored to new installation

## 🎁 Distribution Checklist

Before distributing to users:

- [ ] Test executable on clean Windows machine
- [ ] Verify all features work (tracking, recording, charts)
- [ ] Include this deployment guide
- [ ] Test on different Windows versions if possible
- [ ] Ensure antivirus doesn't flag the executable

## 📝 Notes for Developers

### Build Process Notes
- PyInstaller automatically handles most dependencies
- Some Qt libraries may show warnings but app still works
- Build uses TkAgg backend for matplotlib (most compatible)
- SQLite is statically linked (no external database needed)

### Customization Options
- Add custom icon by modifying the `.spec` file
- Exclude additional modules to reduce size
- Add splash screen for branding

### File Structure After Build
```
dist/
├── ActivityTracker.exe          # Main executable
└── data/                        # Created at runtime
    ├── usage.db                 # SQLite database
    └── recordings/              # MP4 recordings
        ├── recording_20231201_143022.mp4
        └── recording_20231201_150315.mp4
```