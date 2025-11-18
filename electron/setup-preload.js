/**
 * Setup Wizard Preload Script
 */

const { contextBridge, ipcRenderer } = require('electron');

// Setup API 노출
contextBridge.exposeInMainWorld('setupAPI', {
    // Ollama 설치 확인
    checkOllama: () => ipcRenderer.invoke('setup:check-ollama'),

    // Ollama 설치
    installOllama: () => ipcRenderer.invoke('setup:install-ollama'),

    // 모델 다운로드
    downloadModel: () => ipcRenderer.invoke('setup:download-model'),

    // 모델 다운로드 진행률 수신
    onModelProgress: (callback) => {
        ipcRenderer.on('setup:model-progress', (event, progress) => {
            callback(progress);
        });
    },

    // 설정 완료
    finishSetup: () => ipcRenderer.send('setup:finish'),
});
