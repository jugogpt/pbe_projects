@echo off
echo ============================================
echo Activity Tracker AI - Voice Assistant Setup
echo ============================================
echo.

echo [1/3] Installing Python dependencies...
pip install openai python-dotenv
echo.

echo [2/3] Attempting to install PyAudio...
pip install pyaudio
if errorlevel 1 (
    echo.
    echo WARNING: PyAudio installation failed!
    echo.
    echo Please install PyAudio manually:
    echo 1. Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    echo 2. Download the .whl file for your Python version
    echo 3. Run: pip install PyAudio-X.X.X-cpXX-cpXX-win_amd64.whl
    echo.
    pause
)
echo.

echo [3/3] Checking configuration...
if not exist .env (
    echo Creating .env file...
    echo ANTHROPIC_API_KEY=your-anthropic-key-here > .env
    echo OPENAI_API_KEY=your-openai-api-key-here >> .env
    echo.
    echo IMPORTANT: Edit .env file and add your OpenAI API key!
) else (
    echo .env file already exists.
    echo Make sure OPENAI_API_KEY is configured in .env
)
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file and add your OpenAI API key
echo 2. Get API key from: https://platform.openai.com/api-keys
echo 3. Run the app: python main.py
echo 4. Click "Voice Assistant" tab
echo.
echo See VOICE_ASSISTANT_SETUP.md for full guide
echo.
pause
