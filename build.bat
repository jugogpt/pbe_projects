@echo off
echo Building Activity Tracker Application...
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
echo Building executable with PyInstaller...
pyinstaller ActivityTracker.spec

if %ERRORLEVEL% == 0 (
    echo.
    echo Build successful!
    echo Executable created in: dist\ActivityTracker\ActivityTracker.exe
    echo.
    echo Creating data directories in output folder...
    mkdir "dist\ActivityTracker\data\recordings" 2>nul

    echo.
    echo Build complete! You can now distribute the 'dist\ActivityTracker' folder.
    echo To run the app, navigate to 'dist\ActivityTracker' and run 'ActivityTracker.exe'
    pause
) else (
    echo.
    echo Build failed! Check the error messages above.
    pause
)