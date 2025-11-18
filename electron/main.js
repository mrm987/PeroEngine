/**
 * PeroEngine Electron 메인 프로세스
 */

const { app, BrowserWindow, Tray, Menu, globalShortcut, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const installer = require('./installer');

// 개발 모드 확인
const isDev = process.argv.includes('--dev');

// 전역 변수
let mainWindow = null;
let setupWindow = null;
let tray = null;
let pythonProcess = null;
const PYTHON_PORT = 8000;

/**
 * Python 백엔드 서버 시작
 */
function startPythonServer() {
    console.log('🐍 Python 서버 시작 중...');

    const pythonPath = isDev
        ? 'python'  // 개발 모드: 시스템 Python
        : path.join(process.resourcesPath, 'python', 'python.exe');  // 프로덕션: 내장 Python

    const serverScript = isDev
        ? path.join(__dirname, '..', 'run_server.py')
        : path.join(process.resourcesPath, 'run_server.py');

    // Python 서버 실행
    pythonProcess = spawn(pythonPath, [serverScript], {
        cwd: isDev ? path.join(__dirname, '..') : process.resourcesPath,
        env: {
            ...process.env,
            PYTHONUNBUFFERED: '1',  // 버퍼링 비활성화
        }
    });

    // 출력 로그
    pythonProcess.stdout.on('data', (data) => {
        console.log(`[Python] ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`[Python Error] ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python 프로세스 종료 (코드: ${code})`);
    });

    console.log('✅ Python 서버 시작됨');
}

/**
 * Python 서버 종료
 */
function stopPythonServer() {
    if (pythonProcess) {
        console.log('🛑 Python 서버 종료 중...');
        pythonProcess.kill();
        pythonProcess = null;
    }
}

/**
 * 메인 윈도우 생성
 */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        title: 'PeroEngine',
        icon: path.join(__dirname, 'assets', 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        autoHideMenuBar: true,  // 메뉴바 숨기기
    });

    // Python 서버가 준비될 때까지 대기
    setTimeout(() => {
        mainWindow.loadURL(`http://localhost:${PYTHON_PORT}/static/index.html`);
    }, 3000);  // 3초 대기

    // 개발자 도구 (개발 모드에서만)
    if (isDev) {
        mainWindow.webContents.openDevTools();
    }

    // 창 닫기 이벤트
    mainWindow.on('close', (event) => {
        if (!app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();  // 창만 숨김 (백그라운드 실행)
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    console.log('✅ 메인 윈도우 생성 완료');
}

/**
 * 시스템 트레이 생성
 */
function createTray() {
    const trayIconPath = path.join(__dirname, 'assets', 'tray-icon.png');

    // 아이콘이 없으면 기본 아이콘 사용
    const iconPath = fs.existsSync(trayIconPath)
        ? trayIconPath
        : path.join(__dirname, 'assets', 'icon.png');

    tray = new Tray(iconPath);

    const contextMenu = Menu.buildFromTemplate([
        {
            label: '열기',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                    mainWindow.focus();
                }
            }
        },
        {
            label: '설정',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                    mainWindow.focus();
                    // TODO: 설정 페이지로 이동
                }
            }
        },
        { type: 'separator' },
        {
            label: '종료',
            click: () => {
                app.isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setToolTip('PeroEngine - AI 어시스턴트');
    tray.setContextMenu(contextMenu);

    // 트레이 아이콘 더블클릭 시 창 표시
    tray.on('double-click', () => {
        if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
        }
    });

    console.log('✅ 시스템 트레이 생성 완료');
}

/**
 * 전역 단축키 등록
 */
function registerGlobalShortcuts() {
    // Ctrl+Shift+P: PeroEngine 열기
    const registered = globalShortcut.register('CommandOrControl+Shift+P', () => {
        if (mainWindow) {
            if (mainWindow.isVisible()) {
                mainWindow.hide();
            } else {
                mainWindow.show();
                mainWindow.focus();
            }
        }
    });

    if (registered) {
        console.log('✅ 전역 단축키 등록: Ctrl+Shift+P');
    } else {
        console.warn('⚠️  전역 단축키 등록 실패');
    }
}

/**
 * Setup Wizard 창 생성
 */
function createSetupWindow() {
    setupWindow = new BrowserWindow({
        width: 700,
        height: 600,
        resizable: false,
        title: 'PeroEngine 초기 설정',
        icon: path.join(__dirname, 'assets', 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'setup-preload.js')
        },
        autoHideMenuBar: true,
    });

    setupWindow.loadFile(path.join(__dirname, 'setup-wizard.html'));

    if (isDev) {
        setupWindow.webContents.openDevTools();
    }

    setupWindow.on('closed', () => {
        setupWindow = null;
    });

    console.log('✅ Setup Wizard 창 생성 완료');
}

/**
 * 앱 준비 완료
 */
app.whenReady().then(async () => {
    console.log('=' .repeat(60));
    console.log('🎭 PeroEngine Desktop 시작 중...');
    console.log('=' .repeat(60));

    // 첫 실행 확인 (개발 모드에서는 스킵)
    if (!isDev && installer.isFirstRun()) {
        console.log('🔧 첫 실행 감지 - Setup Wizard 시작');
        createSetupWindow();
        return;
    }

    // 정상 시작
    console.log('✅ 이미 설정 완료됨 - 정상 시작');

    // Python 서버 시작
    startPythonServer();

    // 윈도우 생성
    createWindow();

    // 시스템 트레이 생성
    createTray();

    // 전역 단축키 등록
    registerGlobalShortcuts();

    console.log('=' .repeat(60));
    console.log('✅ PeroEngine Desktop 준비 완료!');
    console.log('🌐 서버: http://localhost:' + PYTHON_PORT);
    console.log('⌨️  단축키: Ctrl+Shift+P (열기/숨기기)');
    console.log('=' .repeat(60));

    // macOS: 독에서 클릭 시 창 표시
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        } else if (mainWindow) {
            mainWindow.show();
        }
    });
});

/**
 * 모든 창이 닫힐 때
 */
app.on('window-all-closed', () => {
    // macOS가 아니면 앱 종료
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

/**
 * 앱 종료 전
 */
app.on('before-quit', () => {
    app.isQuitting = true;
});

/**
 * 앱 종료
 */
app.on('quit', () => {
    // 전역 단축키 해제
    globalShortcut.unregisterAll();

    // Python 서버 종료
    stopPythonServer();

    console.log('👋 PeroEngine 종료');
});

/**
 * IPC 통신 핸들러
 */
ipcMain.handle('get-app-version', () => {
    return app.getVersion();
});

ipcMain.handle('minimize-window', () => {
    if (mainWindow) {
        mainWindow.minimize();
    }
});

ipcMain.handle('maximize-window', () => {
    if (mainWindow) {
        if (mainWindow.isMaximized()) {
            mainWindow.unmaximize();
        } else {
            mainWindow.maximize();
        }
    }
});

ipcMain.handle('close-window', () => {
    if (mainWindow) {
        mainWindow.hide();
    }
});

/**
 * Setup Wizard IPC 핸들러
 */

// Ollama 설치 확인
ipcMain.handle('setup:check-ollama', async () => {
    try {
        const installed = await installer.checkOllamaInstalled();
        console.log(`Ollama 설치 여부: ${installed}`);
        return installed;
    } catch (error) {
        console.error('Ollama 확인 실패:', error);
        return false;
    }
});

// Ollama 설치
ipcMain.handle('setup:install-ollama', async () => {
    try {
        console.log('📥 Ollama 설치 시작...');

        const success = await installer.installOllama((progress) => {
            // 진행률 전송 (다운로드 단계)
            if (setupWindow) {
                setupWindow.webContents.send('setup:model-progress', progress * 0.5);
            }
        });

        if (success) {
            console.log('✅ Ollama 설치 완료');

            // 설치 완료 후 서비스 시작 대기
            await new Promise(resolve => setTimeout(resolve, 5000));
        }

        return success;
    } catch (error) {
        console.error('❌ Ollama 설치 실패:', error);
        return false;
    }
});

// 모델 다운로드
ipcMain.handle('setup:download-model', async () => {
    try {
        console.log('📥 모델 다운로드 시작...');

        // config.yaml에서 모델명 읽기
        const configPath = isDev
            ? path.join(__dirname, '..', 'config.yaml')
            : path.join(process.resourcesPath, 'config.yaml');

        let modelName = 'llama3.2:3b'; // 기본값

        if (fs.existsSync(configPath)) {
            const configContent = fs.readFileSync(configPath, 'utf8');
            const match = configContent.match(/model:\s*"(.+?)"/);
            if (match) {
                modelName = match[1];
            }
        }

        console.log(`대상 모델: ${modelName}`);

        const success = await installer.downloadOllamaModel(modelName, (progress) => {
            if (setupWindow) {
                setupWindow.webContents.send('setup:model-progress', progress);
            }
        });

        return success;
    } catch (error) {
        console.error('❌ 모델 다운로드 실패:', error);
        return false;
    }
});

// 설정 완료
ipcMain.on('setup:finish', () => {
    console.log('✅ Setup Wizard 완료');

    // 설정 완료 플래그 생성
    installer.markSetupComplete();

    // Setup 창 닫기
    if (setupWindow) {
        setupWindow.close();
        setupWindow = null;
    }

    // 메인 앱 시작
    console.log('🚀 메인 애플리케이션 시작...');

    // Python 서버 시작
    startPythonServer();

    // 윈도우 생성
    createWindow();

    // 시스템 트레이 생성
    createTray();

    // 전역 단축키 등록
    registerGlobalShortcuts();

    console.log('✅ PeroEngine 시작 완료!');
});

// 자동 시작 설정 (선택사항)
app.setLoginItemSettings({
    openAtLogin: false,  // 기본값: false (사용자가 설정에서 변경 가능)
    openAsHidden: true   // 시작 시 숨김
});
