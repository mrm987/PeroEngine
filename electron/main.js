/**
 * PeroEngine Desktop - Main Process
 *
 * 참고 프로젝트:
 * - Open-LLM-VTuber: 감정 키워드 기반 표정 제어, 모듈식 설계
 * - LLM-Live2D-Desktop-Assistant: 화면 인식, 클립보드 연동
 * - AIRI: 웹 기술 활용
 */

const {
    app,
    BrowserWindow,
    Tray,
    Menu,
    globalShortcut,
    ipcMain,
    screen,
    desktopCapturer,
    clipboard,
    nativeImage,
} = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// 개발 모드 확인
const isDev = process.argv.includes('--dev');

// 전역 변수
let characterWindow = null;
let tray = null;
let pythonProcess = null;
let isRecording = false;

// 설정
const CONFIG = {
    PYTHON_PORT: 8000,
    CHARACTER_SIZE: { width: 350, height: 450 },
    CHARACTER_POSITION: 'bottom-right',
    CHARACTER_MARGIN: 20,
    // 감정 매핑 (Open-LLM-VTuber 스타일)
    EMOTION_MAP: {
        '[happy]': 'happy',
        '[sad]': 'sad',
        '[angry]': 'angry',
        '[surprised]': 'surprised',
        '[thinking]': 'thinking',
        '[neutral]': 'neutral',
    },
};

// ============================================================
// Python 백엔드 관리
// ============================================================

function startPythonServer() {
    console.log('🐍 Python 서버 시작 중...');

    const pythonPath = isDev ? 'python' : path.join(process.resourcesPath, 'python', 'python.exe');
    const serverScript = isDev
        ? path.join(__dirname, '..', 'run_server.py')
        : path.join(process.resourcesPath, 'run_server.py');

    pythonProcess = spawn(pythonPath, [serverScript], {
        cwd: isDev ? path.join(__dirname, '..') : process.resourcesPath,
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });

    pythonProcess.stdout.on('data', (data) => console.log(`[Python] ${data}`));
    pythonProcess.stderr.on('data', (data) => console.error(`[Python] ${data}`));
    pythonProcess.on('close', (code) => console.log(`Python 종료 (코드: ${code})`));

    console.log('✅ Python 서버 시작됨');
}

function stopPythonServer() {
    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
    }
}

// ============================================================
// 캐릭터 윈도우 관리
// ============================================================

function getCharacterPosition() {
    const { workAreaSize } = screen.getPrimaryDisplay();
    const { width: sw, height: sh } = workAreaSize;
    const { width: ww, height: wh } = CONFIG.CHARACTER_SIZE;
    const m = CONFIG.CHARACTER_MARGIN;

    const positions = {
        'bottom-right': { x: sw - ww - m, y: sh - wh - m },
        'bottom-left': { x: m, y: sh - wh - m },
        'top-right': { x: sw - ww - m, y: m },
        'top-left': { x: m, y: m },
    };

    return positions[CONFIG.CHARACTER_POSITION] || positions['bottom-right'];
}

function createCharacterWindow() {
    const pos = getCharacterPosition();

    characterWindow = new BrowserWindow({
        width: CONFIG.CHARACTER_SIZE.width,
        height: CONFIG.CHARACTER_SIZE.height,
        x: pos.x,
        y: pos.y,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        skipTaskbar: true,
        resizable: false,
        hasShadow: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'character-preload.js'),
        },
    });

    characterWindow.loadFile(path.join(__dirname, 'character.html'));

    if (isDev) {
        characterWindow.webContents.openDevTools({ mode: 'detach' });
    }

    characterWindow.on('closed', () => { characterWindow = null; });

    console.log('✅ 캐릭터 윈도우 생성');
}

function sendToCharacter(channel, ...args) {
    if (characterWindow && !characterWindow.isDestroyed()) {
        characterWindow.webContents.send(channel, ...args);
    }
}

function moveCharacter(position) {
    CONFIG.CHARACTER_POSITION = position;
    if (characterWindow) {
        const pos = getCharacterPosition();
        characterWindow.setPosition(pos.x, pos.y, true);
    }
}

function resizeCharacter(width, height) {
    CONFIG.CHARACTER_SIZE = { width, height };
    if (characterWindow) {
        characterWindow.setSize(width, height, true);
        const pos = getCharacterPosition();
        characterWindow.setPosition(pos.x, pos.y, true);
    }
}

// ============================================================
// 시스템 트레이
// ============================================================

function createTray() {
    const iconPath = path.join(__dirname, 'assets', 'tray-icon.png');
    const fallback = path.join(__dirname, 'assets', 'icon.png');

    tray = new Tray(fs.existsSync(iconPath) ? iconPath : fallback);

    const contextMenu = Menu.buildFromTemplate([
        { label: '👋 인사하기', click: () => sendToCharacter('ui:speech-bubble', '안녕하세요!', 3000) },
        { type: 'separator' },
        {
            label: '📍 위치',
            submenu: [
                { label: '오른쪽 아래', click: () => moveCharacter('bottom-right') },
                { label: '왼쪽 아래', click: () => moveCharacter('bottom-left') },
                { label: '오른쪽 위', click: () => moveCharacter('top-right') },
                { label: '왼쪽 위', click: () => moveCharacter('top-left') },
            ]
        },
        {
            label: '📏 크기',
            submenu: [
                { label: '작게 (250x320)', click: () => resizeCharacter(250, 320) },
                { label: '보통 (350x450)', click: () => resizeCharacter(350, 450) },
                { label: '크게 (450x580)', click: () => resizeCharacter(450, 580) },
            ]
        },
        { type: 'separator' },
        { label: '👁️ 화면 보기', click: () => captureAndAnalyzeScreen() },
        { label: '📋 클립보드 읽기', click: () => readClipboard() },
        { type: 'separator' },
        {
            label: '❌ 종료',
            click: () => { app.isQuitting = true; app.quit(); }
        }
    ]);

    tray.setToolTip('PeroEngine - AI 어시스턴트');
    tray.setContextMenu(contextMenu);
    tray.on('click', () => {
        if (characterWindow) {
            characterWindow.isVisible() ? characterWindow.hide() : characterWindow.show();
        }
    });

    console.log('✅ 시스템 트레이 생성');
}

// ============================================================
// 단축키
// ============================================================

function registerGlobalShortcuts() {
    // Ctrl+Shift+P: 표시/숨기기
    globalShortcut.register('CommandOrControl+Shift+P', () => {
        if (characterWindow) {
            characterWindow.isVisible() ? characterWindow.hide() : characterWindow.show();
        }
    });

    // Ctrl+Shift+C: 채팅 열기
    globalShortcut.register('CommandOrControl+Shift+C', () => {
        if (characterWindow) {
            characterWindow.show();
            characterWindow.focus();
            sendToCharacter('ui:toggle-input');
        }
    });

    // Ctrl+Shift+S: 화면 보기
    globalShortcut.register('CommandOrControl+Shift+S', () => {
        captureAndAnalyzeScreen();
    });

    console.log('✅ 단축키: Ctrl+Shift+P/C/S');
}

// ============================================================
// API 통신
// ============================================================

async function callAPI(endpoint, method = 'GET', body = null) {
    try {
        const fetch = (await import('node-fetch')).default;
        const url = `http://localhost:${CONFIG.PYTHON_PORT}${endpoint}`;

        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error(`API 오류 (${endpoint}):`, error.message);
        return { success: false, error: error.message };
    }
}

// ============================================================
// 감정 추출 (Open-LLM-VTuber 스타일)
// ============================================================

function extractEmotion(text) {
    for (const [keyword, emotion] of Object.entries(CONFIG.EMOTION_MAP)) {
        if (text.includes(keyword)) {
            return {
                emotion,
                cleanText: text.replace(keyword, '').trim()
            };
        }
    }
    return { emotion: 'neutral', cleanText: text };
}

// ============================================================
// 화면 인식 (LLM-Live2D-Desktop-Assistant 스타일)
// ============================================================

async function captureAndAnalyzeScreen() {
    try {
        sendToCharacter('ui:status', 'thinking');
        sendToCharacter('ui:speech-bubble', '화면을 보고 있어요...', 0);

        const sources = await desktopCapturer.getSources({
            types: ['screen'],
            thumbnailSize: { width: 1920, height: 1080 }
        });

        if (sources.length > 0) {
            const screenshot = sources[0].thumbnail.toDataURL();

            // TODO: Vision LLM 연동
            // const response = await callAPI('/vision', 'POST', { image: screenshot, prompt: '화면에 무엇이 보이나요?' });

            sendToCharacter('ui:status', '');
            sendToCharacter('ui:speech-bubble', '화면을 봤어요! (Vision LLM 연동 예정)', 5000);

            return { success: true, screenshot };
        }

        throw new Error('화면을 캡처할 수 없습니다.');
    } catch (error) {
        sendToCharacter('ui:status', 'error');
        sendToCharacter('ui:speech-bubble', '화면을 볼 수 없어요...', 3000);
        return { success: false, error: error.message };
    }
}

// ============================================================
// 클립보드 읽기 (LLM-Live2D-Desktop-Assistant 스타일)
// ============================================================

async function readClipboard() {
    try {
        const text = clipboard.readText();
        const image = clipboard.readImage();

        if (text) {
            sendToCharacter('ui:speech-bubble', `클립보드: "${text.substring(0, 50)}..."`, 5000);

            // 클립보드 내용으로 대화
            const response = await processChat(`이 내용에 대해 알려줘: ${text}`);
            return response;
        } else if (!image.isEmpty()) {
            sendToCharacter('ui:speech-bubble', '이미지가 클립보드에 있어요!', 3000);
            // TODO: 이미지 분석
        } else {
            sendToCharacter('ui:speech-bubble', '클립보드가 비어있어요.', 3000);
        }
    } catch (error) {
        console.error('클립보드 읽기 오류:', error);
    }
}

// ============================================================
// 채팅 처리
// ============================================================

async function processChat(message) {
    try {
        sendToCharacter('ui:status', 'thinking');

        // LLM 응답
        const chatResponse = await callAPI('/chat', 'POST', { message, character_id: 'default' });

        if (!chatResponse.success) {
            throw new Error(chatResponse.error || '응답 실패');
        }

        // 감정 추출
        const { emotion, cleanText } = extractEmotion(chatResponse.message);
        console.log(`감정: ${emotion}, 응답: ${cleanText}`);

        // TTS 생성
        sendToCharacter('ui:status', 'speaking');
        const ttsResponse = await callAPI('/tts', 'POST', { text: cleanText });

        // 애니메이션 생성 (TODO)
        // const animResponse = await callAPI('/animate', 'POST', { ... });

        return {
            success: true,
            message: cleanText,
            emotion,
            audioUrl: ttsResponse.success ? `http://localhost:${CONFIG.PYTHON_PORT}/temp/speech.mp3` : null,
            videoUrl: null, // TODO
        };

    } catch (error) {
        console.error('채팅 오류:', error);
        sendToCharacter('ui:status', 'error');
        return { success: false, message: '오류가 발생했어요...', error: error.message };
    }
}

// ============================================================
// IPC 핸들러
// ============================================================

ipcMain.handle('chat:send', async (event, message) => {
    const result = await processChat(message);
    sendToCharacter('ui:speech-bubble', result.message, 0);
    setTimeout(() => sendToCharacter('ui:status', ''), 3000);
    return result;
});

ipcMain.handle('screen:capture', async () => {
    return await captureAndAnalyzeScreen();
});

ipcMain.handle('clipboard:read', async () => {
    return await readClipboard();
});

ipcMain.handle('config:get', async () => {
    const staticPath = isDev ? path.join(__dirname, '..', 'static') : path.join(process.resourcesPath, 'static');

    // 캐릭터 이미지 찾기
    let characterImage = null;
    const possiblePaths = [
        path.join(staticPath, 'p51-Photoroom.png'),
        path.join(staticPath, 'pero_sample_img.png'),
        path.join(staticPath, 'character.png'),
    ];

    for (const p of possiblePaths) {
        if (fs.existsSync(p)) {
            characterImage = `file://${p}`;
            break;
        }
    }

    return { characterImage, ...CONFIG };
});

ipcMain.on('settings:open', () => console.log('TODO: 설정 창'));
ipcMain.on('window:minimize', () => characterWindow?.minimize());
ipcMain.on('window:close', () => characterWindow?.hide());

// ============================================================
// 앱 라이프사이클
// ============================================================

app.whenReady().then(async () => {
    console.log('='.repeat(60));
    console.log('🎭 PeroEngine Desktop');
    console.log('='.repeat(60));

    startPythonServer();
    await new Promise(r => setTimeout(r, 2000)); // 서버 대기

    createCharacterWindow();
    createTray();
    registerGlobalShortcuts();

    console.log('='.repeat(60));
    console.log('✅ 준비 완료!');
    console.log('   Ctrl+Shift+P: 표시/숨기기');
    console.log('   Ctrl+Shift+C: 채팅');
    console.log('   Ctrl+Shift+S: 화면 보기');
    console.log('='.repeat(60));
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => { app.isQuitting = true; });

app.on('quit', () => {
    globalShortcut.unregisterAll();
    stopPythonServer();
    console.log('👋 종료');
});

app.setLoginItemSettings({ openAtLogin: false, openAsHidden: true });
