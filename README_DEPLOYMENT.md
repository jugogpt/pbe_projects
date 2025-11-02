# 🖥️ Activity Tracker + Screen Recorder - Windows Desktop App

## 🎯 Quick Start (End Users)

### Download & Run
1. Download `ActivityTracker.exe`
2. Double-click to run
3. The app will create data folders automatically

**That's it!** No Python installation required.

---

## 🚀 What This App Does

- **Tracks** which applications you use and for how long
- **Records** your screen on demand (lightweight MP4 files)
- **Charts** your daily activity with visual graphs
- **Stores** everything in a local SQLite database

Perfect for productivity analysis, time tracking, and creating screen recordings for tutorials or documentation.

---

## 🎮 How to Use

### Main Window
- **Start Recording**: Begin screen capture
- **Stop Recording**: End and save recording
- **Open Recordings Folder**: View saved MP4 files
- **Show Today's Usage Chart**: See your app usage as a bar chart

### Automatic Features
- Activity tracking runs automatically in the background
- Database saves every application switch
- Charts update in real-time

---

## 📁 File Locations

The app creates these folders automatically:
```
📁 data/
├── 📄 usage.db              # Your activity database
└── 📁 recordings/
    ├── 🎬 recording_20231201_143022.mp4
    └── 🎬 recording_20231201_150315.mp4
```

---

## 🔧 System Requirements

- **Windows 10/11** (64-bit)
- **2GB RAM** minimum
- **Write permissions** in the app folder
- **Screen recording permissions** (may need admin for some systems)

---

## 🛠️ For Developers

### Building from Source
```bash
# Install dependencies
pip install -r requirements.txt

# Quick build (single file)
build_onefile.bat

# Development build (folder)
build.bat
```

### Project Structure
```
📁 pbeprototype/
├── 📄 main.py              # Entry point
├── 📄 gui.py               # PyQt5 interface
├── 📄 tracker.py           # Activity tracking
├── 📄 recorder.py          # Screen recording
├── 📄 utils.py             # Helper functions
├── 📄 requirements.txt     # Dependencies
├── 📄 ActivityTracker.spec # PyInstaller config
└── 📁 dist/               # Built executables
```

---

## ⚡ Performance

- **First run**: ~5-10 seconds (single file extraction)
- **Subsequent runs**: ~2-3 seconds
- **Recording**: Low CPU usage (3 FPS default)
- **Storage**: Small MP4 files (~1MB per minute)

---

## 🔒 Privacy & Security

- **100% Local**: No data sent to external servers
- **Offline**: Works completely offline
- **Your Data**: SQLite database stays on your machine
- **No Network**: App doesn't require internet connection

---

## 🆘 Support & Troubleshooting

### App Won't Start?
- Install [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
- Try running as administrator

### Recording Not Working?
- Grant screen recording permissions
- Run as administrator if needed

### Need Help?
- Check `DEPLOYMENT_GUIDE.md` for detailed instructions
- View source code in the project folder

---

## 🎨 Features

✅ **Real-time Activity Tracking**
✅ **On-demand Screen Recording**
✅ **Visual Usage Charts**
✅ **SQLite Database Storage**
✅ **Lightweight MP4 Recordings**
✅ **No Dependencies Required**
✅ **Completely Offline**
✅ **Open Source**

---

## 📈 Use Cases

- **Productivity Analysis**: See where your time goes
- **Time Tracking**: Monitor work patterns
- **Screen Recording**: Create tutorials or documentation
- **Workflow Analysis**: Understand your computer usage
- **Project Management**: Track time on different applications

---

**Built with Python • PyQt5 • SQLite • OpenCV • Matplotlib**