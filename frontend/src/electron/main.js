const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess;

// Start Python backend
function startBackend() {
    const pythonPath = process.env.PYTHON_PATH || 'python';
    const backendScript = path.join(__dirname, '../../backend/main.py');

    backendProcess = spawn(pythonPath, [backendScript]);

    backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`Backend Error: ${data}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        backgroundColor: '#0a0e1a',
        titleBarStyle: 'hidden',
        frame: false
    });

    // Load React app
    const startURL = process.env.ELECTRON_START_URL || `file://${path.join(__dirname, '../build/index.html')}`;
    mainWindow.loadURL(startURL);

    // Open DevTools in development
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }
}

app.whenReady().then(() => {
    // Start backend first
    startBackend();

    // Wait a bit for backend to start, then create window
    setTimeout(createWindow, 2000);
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        // Kill backend process
        if (backendProcess) {
            backendProcess.kill();
        }
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Handle window controls
ipcMain.on('window-minimize', () => {
    mainWindow.minimize();
});

ipcMain.on('window-maximize', () => {
    if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
    } else {
        mainWindow.maximize();
    }
});

ipcMain.on('window-close', () => {
    mainWindow.close();
});
