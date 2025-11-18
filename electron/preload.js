/**
 * PeroEngine Electron Preload Script
 *
 * 보안을 위한 중간 계층
 * 렌더러 프로세스(웹)와 메인 프로세스 간 안전한 통신
 */

const { contextBridge, ipcRenderer } = require('electron');

// 웹 페이지에 안전하게 API 노출
contextBridge.exposeInMainWorld('electronAPI', {
    // 앱 정보
    getVersion: () => ipcRenderer.invoke('get-app-version'),

    // 창 제어
    minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
    maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
    closeWindow: () => ipcRenderer.invoke('close-window'),

    // 플랫폼 정보
    platform: process.platform,

    // 개발 모드 여부
    isDev: process.argv.includes('--dev'),
});

console.log('✅ Preload script loaded');
