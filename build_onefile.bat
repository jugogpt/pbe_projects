@echo off
echo Building Activity Tracker Application (Single File)...
echo.

REM Clean previous builds
if exist "dist" (
    echo Cleaning previous build...
    rmdir /s /q "dist"
)

if exist "build" (
    rmdir /s /q "build"
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building single-file executable...
pyinstaller --onefile --windowed --name="ActivityTracker" ^
    --hidden-import=PyQt5.QtCore ^
    --hidden-import=PyQt5.QtGui ^
    --hidden-import=PyQt5.QtWidgets ^
    --hidden-import=matplotlib.backends.backend_qt5agg ^
    --hidden-import=psutil ^
    --hidden-import=win32gui ^
    --hidden-import=win32process ^
    --hidden-import=mss ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --exclude-module=tkinter ^
    --exclude-module=unittest ^
    main.py

if %ERRORLEVEL% == 0 (
    echo.
    echo Build successful!
    echo Single executable created: dist\ActivityTracker.exe
    echo.
    echo Note: The app will create 'data' folders automatically when first run.
    echo.
    echo Build complete! You can now distribute 'dist\ActivityTracker.exe'
    pause
) else (
    echo.
    echo Build failed! Check the error messages above.
    pause
)