# PeroEngine Animation 엔진 설치 스크립트 (Windows)
# FasterLivePortrait + JoyVASA 설치

$ErrorActionPreference = "Stop"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  PeroEngine Animation 엔진 설치 (Windows)" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# 설치 경로
$INSTALL_DIR = $env:USERPROFILE
$LIVEPORTRAIT_DIR = "$INSTALL_DIR\FasterLivePortrait"
$JOYVASA_DIR = "$INSTALL_DIR\JoyVASA"

# GPU 확인
function Check-GPU {
    Write-Host "`nGPU 확인 중..." -ForegroundColor Yellow
    try {
        $gpu = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>$null
        if ($gpu) {
            Write-Host $gpu -ForegroundColor Green
            Write-Host "NVIDIA GPU 감지됨" -ForegroundColor Green
            return $true
        }
    } catch {}

    Write-Host "NVIDIA GPU를 감지할 수 없습니다. CPU 모드로 실행됩니다." -ForegroundColor Yellow
    return $false
}

# FasterLivePortrait 설치
function Install-LivePortrait {
    Write-Host "`n==============================================" -ForegroundColor Cyan
    Write-Host "  FasterLivePortrait 설치" -ForegroundColor Cyan
    Write-Host "==============================================" -ForegroundColor Cyan

    if (Test-Path $LIVEPORTRAIT_DIR) {
        Write-Host "이미 설치됨: $LIVEPORTRAIT_DIR" -ForegroundColor Yellow
        $reinstall = Read-Host "다시 설치하시겠습니까? (y/N)"
        if ($reinstall -ne "y" -and $reinstall -ne "Y") {
            Write-Host "건너뜀." -ForegroundColor Yellow
            return
        }
        Remove-Item -Recurse -Force $LIVEPORTRAIT_DIR
    }

    Write-Host "FasterLivePortrait 클론 중..." -ForegroundColor Yellow
    Set-Location $INSTALL_DIR
    git clone https://github.com/warmshao/FasterLivePortrait.git

    Write-Host "의존성 설치 중..." -ForegroundColor Yellow
    Set-Location $LIVEPORTRAIT_DIR
    pip install -r requirements.txt

    Write-Host "모델 다운로드 중..." -ForegroundColor Yellow
    try {
        huggingface-cli download warmshao/FasterLivePortrait --local-dir pretrained_weights
    } catch {
        Write-Host "huggingface-cli가 없습니다. 수동으로 모델을 다운로드해주세요." -ForegroundColor Yellow
        Write-Host "  pip install huggingface_hub" -ForegroundColor White
        Write-Host "  huggingface-cli download warmshao/FasterLivePortrait --local-dir pretrained_weights" -ForegroundColor White
    }

    Write-Host "FasterLivePortrait 설치 완료!" -ForegroundColor Green
}

# JoyVASA 설치
function Install-JoyVASA {
    Write-Host "`n==============================================" -ForegroundColor Cyan
    Write-Host "  JoyVASA 설치 (오디오 드리븐)" -ForegroundColor Cyan
    Write-Host "==============================================" -ForegroundColor Cyan

    if (Test-Path $JOYVASA_DIR) {
        Write-Host "이미 설치됨: $JOYVASA_DIR" -ForegroundColor Yellow
        $reinstall = Read-Host "다시 설치하시겠습니까? (y/N)"
        if ($reinstall -ne "y" -and $reinstall -ne "Y") {
            Write-Host "건너뜀." -ForegroundColor Yellow
            return
        }
        Remove-Item -Recurse -Force $JOYVASA_DIR
    }

    Write-Host "JoyVASA 클론 중..." -ForegroundColor Yellow
    Set-Location $INSTALL_DIR
    git clone https://github.com/jdh-algo/JoyVASA.git

    Write-Host "의존성 설치 중..." -ForegroundColor Yellow
    Set-Location $JOYVASA_DIR
    pip install -r requirements.txt

    Write-Host "모델 다운로드 중..." -ForegroundColor Yellow
    try {
        huggingface-cli download jdh-algo/JoyVASA --local-dir pretrained_weights
    } catch {
        Write-Host "huggingface-cli가 없습니다. 수동으로 모델을 다운로드해주세요." -ForegroundColor Yellow
    }

    Write-Host "JoyVASA 설치 완료!" -ForegroundColor Green
}

# TensorRT 설치
function Install-TensorRT {
    Write-Host "`n==============================================" -ForegroundColor Cyan
    Write-Host "  TensorRT 설치 (선택사항 - RTX GPU 필요)" -ForegroundColor Cyan
    Write-Host "==============================================" -ForegroundColor Cyan

    $install = Read-Host "TensorRT를 설치하시겠습니까? (y/N)"
    if ($install -ne "y" -and $install -ne "Y") {
        Write-Host "건너뜀. ONNX 백엔드를 사용합니다." -ForegroundColor Yellow
        return
    }

    pip install tensorrt
    Write-Host "TensorRT 설치 완료!" -ForegroundColor Green
}

# 메인 메뉴
function Main {
    Check-GPU

    Write-Host "`n설치 옵션:" -ForegroundColor White
    Write-Host "1) 전체 설치 (FasterLivePortrait + JoyVASA)"
    Write-Host "2) FasterLivePortrait만 설치"
    Write-Host "3) JoyVASA만 설치"
    Write-Host "4) 취소"
    Write-Host ""

    $choice = Read-Host "선택 (1-4)"

    switch ($choice) {
        "1" {
            Install-LivePortrait
            Install-JoyVASA
            Install-TensorRT
        }
        "2" {
            Install-LivePortrait
            Install-TensorRT
        }
        "3" {
            Install-JoyVASA
        }
        "4" {
            Write-Host "취소됨." -ForegroundColor Yellow
            exit
        }
        default {
            Write-Host "잘못된 선택입니다." -ForegroundColor Red
            exit 1
        }
    }

    Write-Host "`n==============================================" -ForegroundColor Green
    Write-Host "  설치 완료!" -ForegroundColor Green
    Write-Host "==============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "사용 방법:"
    Write-Host "  1. config.yaml에서 animation.provider를 'liveportrait'로 설정"
    Write-Host "  2. python run_server.py 실행"
    Write-Host ""
    Write-Host "경로:"
    Write-Host "  FasterLivePortrait: $LIVEPORTRAIT_DIR"
    Write-Host "  JoyVASA: $JOYVASA_DIR"
}

# 원래 디렉토리 저장
$OriginalLocation = Get-Location

try {
    Main
} finally {
    # 원래 디렉토리로 복귀
    Set-Location $OriginalLocation
}
