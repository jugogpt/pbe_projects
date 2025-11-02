# How to Run - Activity Tracker AI

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Core Use Cases](#core-use-cases)
6. [Features Overview](#features-overview)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.9+** (download from [python.org](https://www.python.org/downloads/))
- **Node.js 18+** (download from [nodejs.org](https://nodejs.org/))
- **Git** (optional, for cloning the repository)

### API Keys Required
- **OpenAI API Key** - For voice transcription and workflow generation
- **Anthropic API Key** (optional) - For video analysis

---

## Installation

### Step 1: Backend Dependencies

Navigate to the backend directory and install Python packages:

```bash
cd backend
pip install -r requirements.txt
```

Or if you're in the root directory:

```bash
pip install -r backend/requirements.txt
```

### Step 2: Frontend Dependencies

Navigate to the frontend directory and install Node.js packages:

```bash
cd frontend
npm install
```

### Step 3: Verify Installation

Check that Python packages are installed:
```bash
python -c "import fastapi, uvicorn, openai; print('✓ Backend dependencies installed')"
```

Check that Node.js packages are installed:
```bash
cd frontend
npm list react react-dom
```

---

## Configuration

### Step 1: Create `.env` File

Create a `.env` file in the **root directory** with your API keys:

```env
# OpenAI API Key (Required for voice assistant and workflow generation)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic API Key (Required for video analysis)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### Step 2: Get API Keys

**OpenAI API Key**:
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new API key
5. Copy the key (starts with `sk-`)

**Anthropic API Key** (optional, for video analysis):
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new API key

### Step 3: Directory Structure

The app automatically creates these directories on first run:

```
pbeprototype/
├── backend/
│   ├── data/
│   │   ├── recordings/      # Screen recordings (MP4)
│   │   ├── screenshots/     # Screenshots (PNG)
│   │   ├── transcripts/     # Voice transcripts (TXT)
│   │   ├── workflows/       # Generated workflows (JSON)
│   │   └── analyses/        # Video analyses (MD)
│   └── usage.db             # Activity database
├── .env                     # API keys (create this)
└── frontend/
```

---

## Running the Application

### Method 1: Quick Start (Recommended)

Use the provided batch script to start both backend and frontend:

**Windows:**
```bash
.\start_app_full.bat
```

This script:
1. Starts the Python backend on port 5000
2. Starts the React frontend on port 3000
3. Opens the Electron app automatically

### Method 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

Wait until you see:
```
✅ Backend ready on http://127.0.0.1:5000
INFO:     Uvicorn running on http://127.0.0.1:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

The Electron app will launch automatically when both servers are ready.

### Method 3: Using PowerShell

```powershell
# Stop any existing Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\hugo2\OneDrive\Desktop\pbeprototype\backend; python main.py"

# Wait a few seconds
Start-Sleep -Seconds 3

# Start frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\hugo2\OneDrive\Desktop\pbeprototype\frontend; npm run dev"
```

---

## Core Use Cases

### 1. Voice Assistant & Workflow Generation

**Purpose:** Convert voice commands into executable workflow steps

**How to Use:**
1. Navigate to the **Voice Assistant** tab
2. Click **"Start Recording"**
3. Speak your workflow (e.g., "Open Chrome, navigate to Google, and send an email to example@mail.com")
4. View real-time transcription as you speak
5. Click **"Stop Recording"**
6. Wait for workflow generation (progress bar shows status)
7. View the generated workflow with step-by-step instructions

**Output:** Structured JSON workflow with:
- Title and description
- Numbered steps with actions
- Automation instructions
- Estimated completion time

**Files Created:**
- Transcripts saved to `backend/data/transcripts/`
- Workflows saved to `backend/data/workflows/`

---

### 2. Video Analysis & Workflow Extraction

**Purpose:** Analyze screen recordings to extract workflows

**How to Use:**
1. Record your screen using the **Recording** tab
2. Or upload an existing video using **Browse** in the Analysis panel
3. Navigate to the **Analysis** tab
4. Select a recording from the list
5. Click **"Quick Analysis"** for summary
6. Click **"Detailed Analysis"** for step-by-step workflow
7. View the generated workflow below the analysis

**Output:**
- Video analysis explaining what happened
- Structured workflow matching the recorded actions
- Organized steps ready for automation

**Files Created:**
- Analyses saved to `backend/data/analyses/`
- Each analysis includes the original video and markdown documentation

---

### 3. Screen Recording

**Purpose:** Capture screen activity for later analysis

**How to Use:**
1. Navigate to the **Recording** tab
2. Click **"Start Recording"**
3. Perform your tasks on the computer
4. Click **"Stop Recording"** when done
5. Recording automatically saved to `data/recordings/`

**Features:**
- Low FPS (3 fps) for small file sizes
- Persistent storage - videos saved permanently
- All recordings available for future analysis

---

### 4. Activity Tracking

**Purpose:** Monitor which applications you use and for how long

**How to Use:**
- Runs automatically in the background
- View usage data in the **Activity** tab
- See real-time charts of your app usage

**Features:**
- Tracks all application switches
- Charts daily/weekly usage
- Stored in SQLite database

---

## Features Overview

### 🎤 Voice Assistant
- Real-time speech-to-text transcription
- AI-powered workflow generation
- Animated audio visualization
- Dark mode interface
- Progress indicators for workflow generation

### 📹 Video Analysis
- Screen recording with MP4 output
- AI analysis using frame extraction
- Workflow extraction from recordings
- Video upload support
- Persistent storage of all recordings

### 📊 Activity Tracking
- Automatic app usage monitoring
- SQLite database storage
- Visual usage charts
- Daily/weekly statistics

### 🔄 Workflow Generation
- Converts transcripts and video analysis into structured workflows
- Step-by-step automation instructions
- JSON format for programmatic use
- Export to files for future reference

---

## Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

---

### Port Already in Use

**Error:** `Address already in use` or `ERRADDRINUSE`

**Solution (Windows PowerShell):**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with the process ID)
taskkill /PID <PID> /F
```

Or restart your computer.

---

### Frontend Shows "Network Error"

**Solution:**
1. Verify backend is running on port 5000
2. Check backend terminal for errors
3. Ensure no firewall is blocking connections
4. Try accessing http://localhost:5000 in a browser

---

### Voice Assistant Not Working

**Error:** "OpenAI API key is required"

**Solution:**
1. Create `.env` file in root directory
2. Add: `OPENAI_API_KEY=sk-your-key-here`
3. Restart the backend

**Error:** No audio detected

**Solution:**
1. Check microphone permissions in Windows Settings
2. Ensure microphone is not muted
3. Close other apps using microphone (Discord, Skype, etc.)

---

### Workflow Generation Fails

**Error:** "Model not found" or "API key invalid"

**Solution:**
1. Verify `OPENAI_API_KEY` is set in `.env`
2. Check OpenAI account has credits
3. Check OpenAI account status at [platform.openai.com](https://platform.openai.com)

---

### Videos Not Saving

**Issue:** Recordings disappear after restart

**Solution:**
- Videos are now saved with absolute paths and persist across restarts
- Check `data/recordings/` directory
- Ensure backend has write permissions to the directory

---

### API Costs

**Estimated Costs:**
- Whisper API: $0.006 per minute of audio
- GPT-4 API: ~$0.01-0.03 per 1K tokens
- Anthropic API: ~$0.015-0.075 per 1K tokens

**Tip:** Monitor usage at [OpenAI Usage Dashboard](https://platform.openai.com/usage)

---

## Project Structure

```
pbeprototype/
├── backend/
│   ├── main.py                    # FastAPI backend entry point
│   ├── core/
│   │   ├── recording_manager.py   # Screen recording management
│   │   ├── voice_assistant_manager.py  # Voice assistant logic
│   │   ├── analysis_manager.py    # Video analysis orchestration
│   │   ├── workflow_manager.py   # Workflow generation
│   │   ├── screenshot_manager.py # Screenshot capture
│   │   └── tracker_manager.py   # Activity tracking
│   ├── data/                      # All data persists here
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── VoiceAssistant.jsx
│   │   │   ├── AnalysisPanel.jsx
│   │   │   ├── RecordingPanel.jsx
│   │   │   └── ActivityChart.jsx
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   └── styles/
│   │       └── App.css           # Dark theme styles
│   └── package.json               # Node.js dependencies
├── voice_assistant.py            # Voice assistant core
├── claude_api.py                 # Video analysis API
├── .env                          # API keys (create this)
├── requirements.txt              # Root level Python dependencies
└── HOWTORUN.md                   # This file
```

---

## Next Steps

1. **Create API keys** and add them to `.env`
2. **Install dependencies** using the commands above
3. **Run the application** using `start_app_full.bat`
4. **Test voice assistant** by recording a simple workflow
5. **Record a screen session** and analyze it
6. **Explore generated workflows** in the `backend/data/workflows/` directory

---

## Support

If you encounter issues:
1. Check this guide first
2. Review backend terminal for error messages
3. Check `TROUBLESHOOTING.md` for specific issues
4. Verify API keys and credits
5. Ensure all dependencies are installed

---

**Last Updated:** 2024
**Version:** 2.0.0

