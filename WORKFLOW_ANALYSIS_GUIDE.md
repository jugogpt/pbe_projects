# 📋 Detailed Workflow Analysis Feature

## Overview
The **Detailed Workflow Analysis** feature uses AI to observe screen recordings and output hyperspecific, step-by-step breakdowns of user actions with exact app names, function names, and action names.

---

## How It Works

### 1. **Record Your Screen**
- Click **"START RECORDING"** button
- Perform your workflow (coding, browsing, editing, etc.)
- Click **"STOP RECORDING"** button when done
- Recording saved as MP4 in `data/recordings/`

### 2. **Analyze the Recording**
- Click **"DETAILED WORKFLOW ANALYSIS"** button
- The app will:
  1. Extract 5 frames from your latest recording at even intervals
  2. Send frames to Claude AI API
  3. AI analyzes each frame for specific actions
  4. Returns hyperspecific numbered list

### 3. **View Results**
- Analysis appears in the right panel
- Shows numbered steps with format:
  - `[App Name] - [Function/Feature] - [Specific Action]`

---

## Output Format

The AI provides a numbered list like:

```
1. Visual Studio Code - File Explorer Panel - Clicked "src" folder
2. Visual Studio Code - Editor Window - Opened "main.py" file
3. Visual Studio Code - Editor - Typed "import numpy as np" on line 5
4. Visual Studio Code - Top Menu - Clicked "File" → "Save"
5. Google Chrome - Address Bar - Typed "stackoverflow.com"
6. Google Chrome - Search Results - Clicked first result link
7. Google Chrome - Article Page - Scrolled down to code example
8. Google Chrome - Code Block - Selected code snippet
9. Visual Studio Code - Editor - Pressed Ctrl+V to paste code
10. Visual Studio Code - Terminal - Typed "python main.py"
```

---

## What Gets Captured

### Application Names
- Exact app names (e.g., "Visual Studio Code", "Google Chrome", "Microsoft Excel")
- System apps (e.g., "Windows Explorer", "Command Prompt")

### Functions/Features
- UI components (e.g., "File Explorer Panel", "Address Bar", "Terminal")
- Menu items (e.g., "Edit Menu", "Settings Dialog")
- Toolbars and panels

### Specific Actions
- Mouse clicks (e.g., "Clicked Save button")
- Keyboard input (e.g., "Typed 'Hello World'")
- Keyboard shortcuts (e.g., "Pressed Ctrl+S")
- Navigation (e.g., "Scrolled down", "Switched tabs")
- File operations (e.g., "Opened file.txt", "Saved document")

---

## Requirements

### Claude API Setup
1. Get API key from [Anthropic Console](https://console.anthropic.com/)
2. Create `.env` file in project root:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
3. API costs approximately $0.001-0.003 per analysis

### Screen Recording
- Record at least 10-15 seconds for meaningful analysis
- Low FPS (3fps) is sufficient for workflow capture
- Keep actions visible on screen

---

## Tips for Best Results

### Recording Tips
✅ **Do:**
- Perform clear, deliberate actions
- Keep UI elements visible
- Work at a steady pace
- Use full-screen or maximized windows

❌ **Avoid:**
- Very rapid switching between apps
- Minimized or hidden windows
- Very short recordings (<5 seconds)
- Too many overlapping windows

### Analysis Tips
- **Longer recordings** = more detailed breakdown
- **Clear workflows** = more accurate detection
- **Distinct apps** = easier identification
- **Visible text** = better action description

---

## Comparison: Regular vs Workflow Analysis

### Regular Analysis (ANALYZE LATEST VIDEO button)
- General overview of activity
- Productivity insights
- Application usage summary
- ~200 words, high-level

### Workflow Analysis (DETAILED WORKFLOW ANALYSIS button)
- Step-by-step numbered list
- Hyperspecific actions
- Exact app/function/action names
- Detailed workflow reconstruction

---

## Use Cases

### 1. **Training & Documentation**
- Record software tutorials
- Generate step-by-step guides
- Create process documentation

### 2. **Productivity Analysis**
- Understand your workflows
- Identify inefficiencies
- Optimize repetitive tasks

### 3. **Quality Assurance**
- Document testing procedures
- Create bug reproduction steps
- Verify workflow compliance

### 4. **Learning & Review**
- Review your coding sessions
- Analyze problem-solving approaches
- Study your own work patterns

---

## Technical Details

### Frame Extraction
- **Frames analyzed**: 5 frames per video
- **Distribution**: Evenly spaced throughout recording
- **Format**: JPEG, 70% quality, base64 encoded

### AI Model
- **Model**: Claude 3 Haiku
- **Max tokens**: 1500 (allows detailed output)
- **Timeout**: 45 seconds
- **Cost**: ~$0.001-0.003 per analysis

### Processing Time
- Typical: 15-30 seconds
- Depends on: video length, internet speed, API load

---

## Troubleshooting

### "No recordings found"
- Record a video first using START/STOP RECORDING
- Check `data/recordings/` folder exists

### "Claude API key not configured"
- Create `.env` file with `ANTHROPIC_API_KEY=your_key`
- Restart the application

### Analysis takes too long
- Normal: 15-45 seconds for detailed analysis
- Check internet connection
- Verify API key is valid

### Poor quality results
- Record longer videos (15+ seconds)
- Use clearer, slower actions
- Ensure apps are visible and not minimized

---

## Example Workflow

**Scenario**: User wants to document their Git workflow

1. **Start Recording** → Click START RECORDING
2. **Perform Actions**:
   - Open terminal
   - Type git commands
   - Switch to VS Code
   - Edit files
   - Commit changes
3. **Stop Recording** → Click STOP RECORDING
4. **Analyze** → Click DETAILED WORKFLOW ANALYSIS
5. **Wait** → 20-30 seconds
6. **Review** → Get numbered list like:
   ```
   1. Windows Terminal - Command Line - Typed "git status"
   2. Windows Terminal - Command Line - Pressed Enter
   3. Windows Terminal - Output - Viewed modified files list
   4. Visual Studio Code - File Tree - Clicked "index.html"
   5. Visual Studio Code - Editor - Modified line 42
   6. Visual Studio Code - Save - Pressed Ctrl+S
   7. Windows Terminal - Command Line - Typed "git add ."
   8. Windows Terminal - Command Line - Typed "git commit -m 'Update homepage'"
   ```

---

## Privacy & Security

- 🔒 All recordings stored locally (`data/recordings/`)
- 🌐 Only selected frames sent to Claude API
- 🗑️ Delete recordings manually anytime
- 🔐 API key stored in `.env` (add to `.gitignore`)

---

## Future Enhancements

Potential improvements:
- Real-time streaming analysis
- Custom prompt templates
- Export to Markdown/PDF
- Workflow comparison
- Action timestamps
- Multi-monitor support

---

## Support

For issues or questions:
1. Check logs in system log panel
2. Verify `.env` configuration
3. Test with demo analysis first
4. Check `data/recordings/` folder permissions

