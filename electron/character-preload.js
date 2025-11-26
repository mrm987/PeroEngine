/**
 * Character Window Preload Script
 * 렌더러 프로세스와 메인 프로세스 간의 안전한 통신
 */

const { contextBridge, ipcRenderer } = require('electron');

// API 노출
contextBridge.exposeInMainWorld('pero', {
    // 메시지 전송 (채팅)
    sendMessage: async (message) => {
        return await ipcRenderer.invoke('chat:send', message);
    },

    // 음성 녹음 시작
    startRecording: async () => {
        return await ipcRenderer.invoke('voice:start');
    },

    // 음성 녹음 중지
    stopRecording: async () => {
        return await ipcRenderer.invoke('voice:stop');
    },

    // 화면 캡처 및 인식
    captureScreen: async () => {
        return await ipcRenderer.invoke('screen:capture');
    },

    // 설정 열기
    openSettings: () => {
        ipcRenderer.send('settings:open');
    },

    // 설정 가져오기
    getConfig: async () => {
        return await ipcRenderer.invoke('config:get');
    },

    // 캐릭터 이미지 변경
    setCharacter: async (imagePath) => {
        return await ipcRenderer.invoke('character:set', imagePath);
    },

    // 윈도우 컨트롤
    minimizeWindow: () => {
        ipcRenderer.send('window:minimize');
    },

    closeWindow: () => {
        ipcRenderer.send('window:close');
    },

    // 이벤트 리스너
    onSpeechBubble: (callback) => {
        ipcRenderer.on('ui:speech-bubble', (event, text, duration) => {
            callback(text, duration);
        });
    },

    onStatusChange: (callback) => {
        ipcRenderer.on('ui:status', (event, status) => {
            callback(status);
        });
    },

    onPlayAnimation: (callback) => {
        ipcRenderer.on('ui:play-animation', (event, videoPath) => {
            callback(videoPath);
        });
    },

    onVoiceResult: (callback) => {
        ipcRenderer.on('voice:result', (event, text) => {
            callback(text);
        });
    },

    onToggleInput: (callback) => {
        ipcRenderer.on('ui:toggle-input', (event) => {
            callback();
        });
    },
});

console.log('✅ Character preload script loaded');
