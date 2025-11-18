/**
 * PeroEngine Electron 개발 모드 실행 스크립트
 *
 * Python 서버와 Electron을 동시에 실행합니다.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let pythonProcess = null;
let electronProcess = null;

// 색상 코드
const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

function log(color, prefix, message) {
    console.log(`${color}[${prefix}]${colors.reset} ${message}`);
}

/**
 * Python 서버 시작
 */
function startPythonServer() {
    return new Promise((resolve, reject) => {
        log(colors.blue, 'Python', '서버 시작 중...');

        const projectRoot = path.join(__dirname, '..');

        pythonProcess = spawn('python', ['run_server.py'], {
            cwd: projectRoot,
            env: {
                ...process.env,
                PYTHONUNBUFFERED: '1'
            }
        });

        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString().trim();
            if (output) {
                log(colors.cyan, 'Python', output);

                // 서버 시작 감지
                if (output.includes('Uvicorn running') || output.includes('Application startup complete')) {
                    log(colors.green, 'Python', '✅ 서버 준비 완료!');
                    resolve();
                }
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            const output = data.toString().trim();
            if (output && !output.includes('WARNING')) {  // WARNING은 무시
                log(colors.yellow, 'Python', output);
            }
        });

        pythonProcess.on('error', (error) => {
            log(colors.red, 'Python', `❌ 에러: ${error.message}`);
            reject(error);
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                log(colors.red, 'Python', `프로세스 종료 (코드: ${code})`);
            }
        });

        // 타임아웃 (30초)
        setTimeout(() => {
            if (pythonProcess) {
                log(colors.green, 'Python', '서버 시작 완료로 간주 (타임아웃)');
                resolve();
            }
        }, 30000);
    });
}

/**
 * Electron 앱 시작
 */
function startElectron() {
    log(colors.magenta, 'Electron', '앱 시작 중...');

    electronProcess = spawn('electron', ['.', '--dev'], {
        cwd: __dirname,
        stdio: 'inherit'
    });

    electronProcess.on('close', (code) => {
        log(colors.magenta, 'Electron', `앱 종료 (코드: ${code})`);
        cleanup();
    });
}

/**
 * 정리 작업
 */
function cleanup() {
    log(colors.yellow, 'System', '종료 중...');

    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
    }

    if (electronProcess) {
        electronProcess.kill();
        electronProcess = null;
    }

    setTimeout(() => {
        process.exit(0);
    }, 1000);
}

/**
 * 메인 실행
 */
async function main() {
    console.log('='.repeat(60));
    console.log('🚀 PeroEngine 개발 모드');
    console.log('='.repeat(60));
    console.log();

    // 종료 시그널 처리
    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);

    try {
        // 1. Python 서버 시작
        await startPythonServer();

        // 2. 잠시 대기
        log(colors.yellow, 'System', '2초 후 Electron 시작...');
        await new Promise(resolve => setTimeout(resolve, 2000));

        // 3. Electron 시작
        startElectron();

    } catch (error) {
        log(colors.red, 'System', `❌ 시작 실패: ${error.message}`);
        cleanup();
    }
}

// 실행
main();
