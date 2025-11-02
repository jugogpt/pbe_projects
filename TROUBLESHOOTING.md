# Troubleshooting Guide - Voice Assistant

## ✅ Problem Solved: API Key Not Loading

### What Was the Issue?

The OpenAI API key was in the `.env` file but wasn't being loaded by the Python modules.

### The Fix

Added `python-dotenv` loading to all necessary files:

```python
from dotenv import load_dotenv
load_dotenv()
```

This was added to:
- ✅ `voice_assistant.py`
- ✅ `voice_assistant_widget.py`
- ✅ `gui.py`

### Verification

Run the test script to verify everything is working:

```bash
python test_api_key.py
```

You should see:
```
[SUCCESS] All tests passed! Voice assistant should work.
```

---

## Common Issues & Solutions

### 1. "OpenAI API key is required"

**Symptoms:**
- Error message when starting voice assistant
- Widget shows "API key not configured"

**Solution:**
```bash
# 1. Check .env file exists
dir .env

# 2. Verify API key is present
type .env

# 3. Make sure it starts with sk-proj- or sk-
# Your .env should look like:
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...

# 4. Run test
python test_api_key.py
```

### 2. "Module 'openai' not found"

**Symptoms:**
- ImportError when starting app
- "No module named 'openai'"

**Solution:**
```bash
pip install openai
# or
pip install -r requirements.txt
```

### 3. "Module 'pyaudio' not found"

**Symptoms:**
- Error when trying to record
- ImportError for pyaudio

**Solution (Windows):**
```bash
# Option A: Try pip first
pip install pyaudio

# Option B: If that fails, use pre-compiled wheel
# Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Then:
pip install PyAudio-0.2.11-cp311-cp311-win_amd64.whl
```

### 4. "Module 'dotenv' not found"

**Symptoms:**
- ImportError: No module named 'dotenv'

**Solution:**
```bash
pip install python-dotenv
```

### 5. API Key Works in Test but Not in App

**Symptoms:**
- `test_api_key.py` passes
- But app still shows API error

**Solution:**
```bash
# Restart the application completely
# Close all Python processes
# Re-run:
python main.py
```

### 6. "Invalid API Key" Error

**Symptoms:**
- API call fails with 401 error
- "Incorrect API key provided"

**Solution:**
1. Verify your API key at https://platform.openai.com/api-keys
2. Check if key has been revoked
3. Make sure there are no extra spaces in `.env`:
   ```env
   OPENAI_API_KEY=sk-proj-...
   # NOT: OPENAI_API_KEY= sk-proj-...
   # NOT: OPENAI_API_KEY="sk-proj-..."
   ```
4. Regenerate key if needed

### 7. "Insufficient Quota" Error

**Symptoms:**
- "You exceeded your current quota"
- API calls fail after a while

**Solution:**
1. Check usage: https://platform.openai.com/usage
2. Add billing info: https://platform.openai.com/account/billing
3. Set spending limits for safety
4. Check if you have any credits

### 8. Microphone Not Working

**Symptoms:**
- No audio recorded
- "Failed to start recording"

**Solution:**
```bash
# 1. Check Windows permissions
# Settings > Privacy > Microphone > Allow apps to access

# 2. Test microphone
# Use Windows Voice Recorder

# 3. List audio devices
python -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"
```

### 9. Slow or No Responses

**Symptoms:**
- Long wait times (>10 seconds)
- No response from AI

**Possible Causes:**
- Poor internet connection
- OpenAI API slowdown
- Rate limiting

**Solution:**
1. Check internet speed
2. Try text mode instead of voice
3. Wait a few minutes and try again
4. Check OpenAI status: https://status.openai.com/

### 10. Unicode/Encoding Errors

**Symptoms:**
- UnicodeEncodeError
- Characters not displaying correctly

**Solution:**
Already fixed in the code with:
```python
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
```

---

## Diagnostic Commands

### Check All Dependencies

```bash
# Check Python version (need 3.9+)
python --version

# Check all packages
pip list | findstr "openai pyaudio dotenv PyQt5"

# Should show:
# openai           1.x.x
# PyAudio          0.2.11
# python-dotenv    1.x.x
# PyQt5            5.x.x
```

### Test Each Component

```bash
# 1. Test API key loading
python test_api_key.py

# 2. Test import of voice assistant
python -c "from voice_assistant import VoiceAssistant; print('OK')"

# 3. Test import of widget
python -c "from voice_assistant_widget import VoiceAssistantWidget; print('OK')"

# 4. Test full GUI
python main.py
```

### Environment Variables

```bash
# Check if .env is in right location
cd C:\Users\hugo2\OneDrive\Desktop\pbeprototype
dir .env

# View contents (Windows)
type .env

# Should see:
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-proj-...
```

---

## Still Having Issues?

### Collect Debug Information

1. Run the test script:
   ```bash
   python test_api_key.py > debug_output.txt 2>&1
   ```

2. Try running the app and note the exact error:
   ```bash
   python main.py 2> error_log.txt
   ```

3. Check Python version:
   ```bash
   python --version
   ```

4. List installed packages:
   ```bash
   pip freeze > installed_packages.txt
   ```

### Clean Reinstall

If all else fails:

```bash
# 1. Uninstall all related packages
pip uninstall openai pyaudio python-dotenv -y

# 2. Clear pip cache
pip cache purge

# 3. Reinstall
pip install openai python-dotenv

# 4. Install PyAudio (see Solution #3 above)

# 5. Test again
python test_api_key.py
```

---

## Contact Information

If you've tried everything and still have issues, check:

1. **OpenAI Status**: https://status.openai.com/
2. **OpenAI API Docs**: https://platform.openai.com/docs
3. **Your API Usage**: https://platform.openai.com/usage
4. **Billing Settings**: https://platform.openai.com/account/billing

---

## Success Checklist

Before using the voice assistant, verify:

- [x] Python 3.9+ installed
- [x] All dependencies installed (`pip install -r requirements.txt`)
- [x] `.env` file exists with OPENAI_API_KEY
- [x] `test_api_key.py` passes successfully
- [x] Microphone is working and permitted
- [x] Internet connection is active
- [x] OpenAI account has credits

---

**Last Updated**: 2024
**Version**: 1.0.0

**Quick Test**: `python test_api_key.py`
