@echo off
echo Starting Activity Tracker AI...

cd frontend
echo Installing dependencies if needed...
call npm install

echo Starting the application...
call npm run dev

pause
