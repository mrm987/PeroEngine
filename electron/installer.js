/**
 * PeroEngine 자동 설치 헬퍼
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('https');
const { app } = require('electron');

/**
 * Ollama 설치 확인
 */
async function checkOllamaInstalled() {
    return new Promise((resolve) => {
        const command = process.platform === 'win32' ? 'ollama.exe' : 'ollama';

        const check = spawn(command, ['--version'], {
            stdio: 'pipe'
        });

        check.on('error', () => {
            resolve(false);
        });

        check.on('close', (code) => {
            resolve(code === 0);
        });

        // 타임아웃 (5초)
        setTimeout(() => {
            check.kill();
            resolve(false);
        }, 5000);
    });
}

/**
 * Ollama 다운로드 URL
 */
function getOllamaDownloadUrl() {
    const platform = process.platform;

    if (platform === 'win32') {
        return 'https://ollama.com/download/OllamaSetup.exe';
    } else if (platform === 'darwin') {
        return 'https://ollama.com/download/Ollama-darwin.zip';
    } else {
        return 'https://ollama.com/download/ollama-linux-amd64';
    }
}

/**
 * 파일 다운로드
 */
async function downloadFile(url, destPath, onProgress) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(destPath);
        let receivedBytes = 0;

        https.get(url, (response) => {
            // 리다이렉트 처리
            if (response.statusCode === 302 || response.statusCode === 301) {
                file.close();
                fs.unlinkSync(destPath);
                return downloadFile(response.headers.location, destPath, onProgress)
                    .then(resolve)
                    .catch(reject);
            }

            const totalBytes = parseInt(response.headers['content-length'], 10);

            response.on('data', (chunk) => {
                receivedBytes += chunk.length;
                if (onProgress && totalBytes) {
                    const progress = (receivedBytes / totalBytes) * 100;
                    onProgress(progress);
                }
            });

            response.pipe(file);

            file.on('finish', () => {
                file.close();
                resolve(destPath);
            });

        }).on('error', (err) => {
            fs.unlinkSync(destPath);
            reject(err);
        });
    });
}

/**
 * Ollama 설치
 */
async function installOllama(onProgress) {
    const platform = process.platform;
    const downloadUrl = getOllamaDownloadUrl();
    const tempDir = app.getPath('temp');
    const installerName = platform === 'win32' ? 'OllamaSetup.exe' : 'ollama-installer';
    const installerPath = path.join(tempDir, installerName);

    try {
        console.log('📥 Ollama 다운로드 중...');
        console.log('   URL:', downloadUrl);
        console.log('   저장:', installerPath);

        // 다운로드
        await downloadFile(downloadUrl, installerPath, (progress) => {
            if (onProgress) onProgress(progress);
        });

        console.log('✅ Ollama 다운로드 완료');

        // Windows: 자동 설치 실행
        if (platform === 'win32') {
            console.log('🔧 Ollama 설치 중...');

            return new Promise((resolve, reject) => {
                // 자동 설치 (/S = silent mode)
                const installer = spawn(installerPath, ['/S'], {
                    detached: true,
                    stdio: 'ignore'
                });

                installer.on('error', reject);
                installer.on('close', (code) => {
                    // 설치 파일 정리
                    try {
                        fs.unlinkSync(installerPath);
                    } catch (e) {
                        // 무시
                    }

                    if (code === 0) {
                        console.log('✅ Ollama 설치 완료');
                        resolve(true);
                    } else {
                        reject(new Error(`설치 실패 (코드: ${code})`));
                    }
                });

                // 타임아웃 (3분)
                setTimeout(() => {
                    console.log('⚠️  Ollama 설치 타임아웃 (백그라운드 설치 진행 중일 수 있음)');
                    resolve(true);
                }, 180000);
            });
        } else {
            // macOS/Linux: 수동 설치 필요
            console.log('⚠️  macOS/Linux는 수동 설치가 필요합니다.');
            console.log('   설치 파일:', installerPath);
            return false;
        }

    } catch (error) {
        console.error('❌ Ollama 설치 실패:', error);
        throw error;
    }
}

/**
 * Ollama 모델 다운로드
 */
async function downloadOllamaModel(modelName, onProgress) {
    return new Promise((resolve, reject) => {
        console.log(`📥 모델 다운로드 시작: ${modelName}`);

        const pullProcess = spawn('ollama', ['pull', modelName], {
            stdio: 'pipe'
        });

        let lastProgress = 0;

        pullProcess.stdout.on('data', (data) => {
            const output = data.toString();
            console.log(`[Ollama Pull] ${output.trim()}`);

            // 진행률 파싱 (예: "pulling... 45%")
            const match = output.match(/(\d+)%/);
            if (match && onProgress) {
                const progress = parseInt(match[1], 10);
                if (progress > lastProgress) {
                    lastProgress = progress;
                    onProgress(progress);
                }
            }
        });

        pullProcess.stderr.on('data', (data) => {
            console.error(`[Ollama Error] ${data}`);
        });

        pullProcess.on('error', (error) => {
            reject(new Error(`모델 다운로드 실패: ${error.message}`));
        });

        pullProcess.on('close', (code) => {
            if (code === 0) {
                console.log(`✅ 모델 다운로드 완료: ${modelName}`);
                resolve(true);
            } else {
                reject(new Error(`모델 다운로드 실패 (코드: ${code})`));
            }
        });

        // 타임아웃 (30분 - 대용량 모델 고려)
        setTimeout(() => {
            pullProcess.kill();
            reject(new Error('모델 다운로드 타임아웃 (30분 초과)'));
        }, 1800000);
    });
}

/**
 * 첫 실행 여부 확인
 */
function isFirstRun() {
    const userDataPath = app.getPath('userData');
    const flagFile = path.join(userDataPath, '.setup-complete');
    return !fs.existsSync(flagFile);
}

/**
 * 설정 완료 플래그 생성
 */
function markSetupComplete() {
    const userDataPath = app.getPath('userData');
    const flagFile = path.join(userDataPath, '.setup-complete');

    try {
        fs.writeFileSync(flagFile, new Date().toISOString());
        console.log('✅ 설정 완료 플래그 생성');
        return true;
    } catch (error) {
        console.error('❌ 플래그 생성 실패:', error);
        return false;
    }
}

module.exports = {
    checkOllamaInstalled,
    installOllama,
    downloadOllamaModel,
    isFirstRun,
    markSetupComplete,
};
