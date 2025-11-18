/**
 * PeroEngine 초기 설정 위저드 클라이언트
 */

let currentStep = 'welcome';
let logsVisible = false;

/**
 * 단계 전환
 */
function showStep(stepName) {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById(`step-${stepName}`).classList.add('active');
    currentStep = stepName;
}

/**
 * 진행률 업데이트
 */
function updateProgress(percent) {
    document.getElementById('progress-fill').style.width = `${percent}%`;
}

/**
 * 작업 상태 업데이트
 */
function updateTask(taskId, status, message) {
    const task = document.getElementById(`task-${taskId}`);
    if (!task) return;

    const icon = task.querySelector('.task-icon');
    const statusText = document.getElementById(`status-${taskId}`);

    // 아이콘 업데이트
    icon.className = 'task-icon';

    switch (status) {
        case 'working':
            icon.classList.add('working');
            icon.textContent = '⏳';
            break;
        case 'done':
            icon.classList.add('done');
            icon.textContent = '✓';
            break;
        case 'error':
            icon.classList.add('error');
            icon.textContent = '✗';
            break;
        default:
            icon.classList.add('pending');
            icon.textContent = '⏳';
    }

    // 상태 텍스트 업데이트
    if (statusText && message) {
        statusText.textContent = message;
    }
}

/**
 * 로그 추가
 */
function addLog(message, type = 'info') {
    const logOutput = document.getElementById('log-output');
    const logLine = document.createElement('div');
    logLine.className = 'log-line';

    const timestamp = new Date().toLocaleTimeString('ko-KR');
    const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';

    logLine.textContent = `[${timestamp}] ${prefix} ${message}`;
    logOutput.appendChild(logLine);

    // 자동 스크롤
    logOutput.scrollTop = logOutput.scrollHeight;
}

/**
 * 에러 메시지 표시
 */
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
}

/**
 * 로그 토글
 */
function showLogs() {
    const logOutput = document.getElementById('log-output');
    logsVisible = !logsVisible;

    if (logsVisible) {
        logOutput.classList.add('show');
        document.getElementById('btn-show-logs').textContent = '로그 숨기기';
    } else {
        logOutput.classList.remove('show');
        document.getElementById('btn-show-logs').textContent = '로그 보기';
    }
}

/**
 * 설치 시작
 */
async function startSetup() {
    showStep('installing');
    addLog('설치 프로세스 시작');

    try {
        // 1. Ollama 확인
        updateTask('ollama', 'working', 'Ollama 확인 중...');
        addLog('Ollama 설치 여부 확인 중...');
        updateProgress(10);

        const ollamaInstalled = await window.setupAPI.checkOllama();

        if (!ollamaInstalled) {
            addLog('Ollama가 설치되어 있지 않습니다.', 'error');
            updateTask('ollama', 'working', 'Ollama 다운로드 중...');

            // Ollama 설치
            const installed = await window.setupAPI.installOllama();

            if (!installed) {
                throw new Error('Ollama 설치에 실패했습니다.');
            }

            addLog('Ollama 설치 완료', 'success');
        } else {
            addLog('Ollama가 이미 설치되어 있습니다.', 'success');
        }

        updateTask('ollama', 'done', '설치 완료');
        updateProgress(40);

        // 2. 모델 다운로드
        updateTask('model', 'working', '모델 다운로드 중...');
        addLog('AI 모델 다운로드 시작 (약 2GB)...');
        updateProgress(50);

        // 모델 다운로드 (진행률 수신)
        window.setupAPI.onModelProgress((progress) => {
            updateProgress(50 + (progress * 0.4)); // 50% ~ 90%
            updateTask('model', 'working', `다운로드 중... ${progress.toFixed(0)}%`);
            addLog(`모델 다운로드: ${progress.toFixed(1)}%`);
        });

        const modelDownloaded = await window.setupAPI.downloadModel();

        if (!modelDownloaded) {
            throw new Error('모델 다운로드에 실패했습니다.');
        }

        updateTask('model', 'done', '다운로드 완료');
        addLog('AI 모델 다운로드 완료', 'success');
        updateProgress(100);

        // 3. 완료
        addLog('모든 설정 완료!', 'success');
        setTimeout(() => {
            showStep('complete');
        }, 1000);

    } catch (error) {
        addLog(error.message, 'error');
        showError(`설치 중 오류 발생: ${error.message}`);

        // 재시도 버튼 표시
        const buttons = document.querySelector('#step-installing .buttons');
        buttons.innerHTML = `
            <button class="secondary" onclick="showLogs()">로그 보기</button>
            <button class="secondary" onclick="skipSetup()">건너뛰기</button>
            <button class="primary" onclick="startSetup()">다시 시도</button>
        `;
    }
}

/**
 * 설치 건너뛰기
 */
function skipSetup() {
    if (confirm('설치를 건너뛰면 일부 기능이 작동하지 않을 수 있습니다. 계속하시겠습니까?')) {
        addLog('설치를 건너뜀', 'info');
        finishSetup();
    }
}

/**
 * 설정 완료
 */
function finishSetup() {
    window.setupAPI.finishSetup();
}

// 페이지 로드 시
window.addEventListener('DOMContentLoaded', () => {
    addLog('PeroEngine 초기 설정 위저드 시작');
});
