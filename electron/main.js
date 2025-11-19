const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function startPythonServer() {
  const pythonScript = path.join(__dirname, '../python/server.py');
  // Assuming 'python' is in PATH. In production, this needs to be robust.
  pythonProcess = spawn('python', [pythonScript]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Python]: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Python Error]: ${data}`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 400, // Smaller initial size for the "portrait" feel
    height: 600,
    transparent: true, // Enable transparency
    frame: false,      // Remove system frame
    hasShadow: false,  // Remove system shadow for cleaner look
    alwaysOnTop: false, // Can be toggled later
    resizable: false,  // Fixed size for now
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    show: false,
  });

  // In dev, load Vite server. In prod, load index.html
  mainWindow.loadURL('http://localhost:5173');

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

// IPC Handlers for Custom Window Controls
ipcMain.on('minimize-window', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.on('close-window', () => {
  if (mainWindow) mainWindow.close();
});

app.on('ready', () => {
  startPythonServer();
  createWindow();
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    if (pythonProcess) pythonProcess.kill();
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('will-quit', () => {
  if (pythonProcess) pythonProcess.kill();
});
