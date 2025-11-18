/**
 * PeroEngine Electron 빌드 스크립트
 *
 * 사용법:
 *   node build.js           # 현재 플랫폼용 빌드
 *   node build.js --win     # Windows 빌드
 *   node build.js --mac     # macOS 빌드
 *   node build.js --linux   # Linux 빌드
 */

const { build } = require('electron-builder');
const fs = require('fs');
const path = require('path');

// 빌드 설정
const config = {
    appId: 'com.peroengine.desktop',
    productName: 'PeroEngine',

    directories: {
        output: 'dist',
        buildResources: 'assets'
    },

    files: [
        'main.js',
        'preload.js',
        'assets/**/*',
        'package.json'
    ],

    extraResources: [
        {
            from: '../run_server.py',
            to: 'run_server.py'
        },
        {
            from: '../src',
            to: 'src'
        },
        {
            from: '../static',
            to: 'static'
        },
        {
            from: '../config.yaml',
            to: 'config.yaml'
        },
        {
            from: '../requirements.txt',
            to: 'requirements.txt'
        }
    ],

    // Windows 설정
    win: {
        target: ['nsis'],
        icon: 'assets/icon.png',
        artifactName: 'PeroEngine-Setup-${version}.${ext}'
    },

    nsis: {
        oneClick: false,
        allowToChangeInstallationDirectory: true,
        createDesktopShortcut: true,
        createStartMenuShortcut: true,
        shortcutName: 'PeroEngine'
    },

    // macOS 설정
    mac: {
        target: ['dmg'],
        icon: 'assets/icon.png',
        category: 'public.app-category.productivity',
        artifactName: 'PeroEngine-${version}.${ext}'
    },

    dmg: {
        title: 'PeroEngine ${version}',
        icon: 'assets/icon.png'
    },

    // Linux 설정
    linux: {
        target: ['AppImage', 'deb'],
        icon: 'assets/icon.png',
        category: 'Utility',
        artifactName: 'PeroEngine-${version}.${ext}'
    }
};

// 빌드 실행
async function runBuild() {
    console.log('=' .repeat(60));
    console.log('🏗️  PeroEngine Desktop 빌드 시작...');
    console.log('=' .repeat(60));

    // 명령줄 인자 파싱
    const args = process.argv.slice(2);
    let platform = process.platform;

    if (args.includes('--win') || args.includes('-w')) {
        platform = 'win32';
    } else if (args.includes('--mac') || args.includes('-m')) {
        platform = 'darwin';
    } else if (args.includes('--linux') || args.includes('-l')) {
        platform = 'linux';
    }

    console.log(`📦 플랫폼: ${platform}`);
    console.log();

    try {
        // 빌드 실행
        await build({
            targets: undefined,  // 자동 감지
            config: config,
            projectDir: __dirname
        });

        console.log();
        console.log('=' .repeat(60));
        console.log('✅ 빌드 완료!');
        console.log('=' .repeat(60));
        console.log();
        console.log('📁 출력 디렉토리: ./dist/');
        console.log();

        // 생성된 파일 목록
        const distPath = path.join(__dirname, 'dist');
        if (fs.existsSync(distPath)) {
            const files = fs.readdirSync(distPath);
            console.log('생성된 파일:');
            files.forEach(file => {
                const stats = fs.statSync(path.join(distPath, file));
                const size = (stats.size / 1024 / 1024).toFixed(2);
                console.log(`  - ${file} (${size} MB)`);
            });
        }

        console.log();
        console.log('💡 설치 파일을 배포하기 전에 반드시 테스트하세요!');

    } catch (error) {
        console.error('❌ 빌드 실패:', error);
        process.exit(1);
    }
}

// 실행
runBuild();
