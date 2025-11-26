#!/bin/bash
# PeroEngine Animation 엔진 설치 스크립트
# FasterLivePortrait + JoyVASA 설치

set -e

echo "=============================================="
echo "🎬 PeroEngine Animation 엔진 설치"
echo "=============================================="

# 설치 경로
INSTALL_DIR="${HOME}"
LIVEPORTRAIT_DIR="${INSTALL_DIR}/FasterLivePortrait"
JOYVASA_DIR="${INSTALL_DIR}/JoyVASA"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수: 에러 체크
check_error() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 오류 발생: $1${NC}"
        exit 1
    fi
}

# 함수: GPU 확인
check_gpu() {
    echo ""
    echo "🔍 GPU 확인 중..."

    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
        echo -e "${GREEN}✅ NVIDIA GPU 감지됨${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  NVIDIA GPU를 감지할 수 없습니다.${NC}"
        echo "   CPU 모드로 실행됩니다 (느림)."
        return 1
    fi
}

# 함수: FasterLivePortrait 설치
install_liveportrait() {
    echo ""
    echo "=============================================="
    echo "📦 FasterLivePortrait 설치"
    echo "=============================================="

    if [ -d "$LIVEPORTRAIT_DIR" ]; then
        echo -e "${YELLOW}⚠️  이미 설치됨: $LIVEPORTRAIT_DIR${NC}"
        read -p "다시 설치하시겠습니까? (y/N): " reinstall
        if [ "$reinstall" != "y" ] && [ "$reinstall" != "Y" ]; then
            echo "건너뜀."
            return 0
        fi
        rm -rf "$LIVEPORTRAIT_DIR"
    fi

    echo "📥 FasterLivePortrait 클론 중..."
    cd "$INSTALL_DIR"
    git clone https://github.com/warmshao/FasterLivePortrait.git
    check_error "FasterLivePortrait 클론 실패"

    echo "📦 의존성 설치 중..."
    cd "$LIVEPORTRAIT_DIR"
    pip install -r requirements.txt
    check_error "의존성 설치 실패"

    echo "📥 모델 다운로드 중..."
    # 모델 다운로드 (HuggingFace)
    if command -v huggingface-cli &> /dev/null; then
        huggingface-cli download warmshao/FasterLivePortrait --local-dir pretrained_weights
    else
        echo -e "${YELLOW}⚠️  huggingface-cli가 없습니다. 수동으로 모델을 다운로드해주세요.${NC}"
        echo "   pip install huggingface_hub"
        echo "   huggingface-cli download warmshao/FasterLivePortrait --local-dir pretrained_weights"
    fi

    echo -e "${GREEN}✅ FasterLivePortrait 설치 완료!${NC}"
}

# 함수: JoyVASA 설치
install_joyvasa() {
    echo ""
    echo "=============================================="
    echo "📦 JoyVASA 설치 (오디오 드리븐)"
    echo "=============================================="

    if [ -d "$JOYVASA_DIR" ]; then
        echo -e "${YELLOW}⚠️  이미 설치됨: $JOYVASA_DIR${NC}"
        read -p "다시 설치하시겠습니까? (y/N): " reinstall
        if [ "$reinstall" != "y" ] && [ "$reinstall" != "Y" ]; then
            echo "건너뜀."
            return 0
        fi
        rm -rf "$JOYVASA_DIR"
    fi

    echo "📥 JoyVASA 클론 중..."
    cd "$INSTALL_DIR"
    git clone https://github.com/jdh-algo/JoyVASA.git
    check_error "JoyVASA 클론 실패"

    echo "📦 의존성 설치 중..."
    cd "$JOYVASA_DIR"
    pip install -r requirements.txt
    check_error "의존성 설치 실패"

    echo "📥 모델 다운로드 중..."
    # 모델 다운로드
    if command -v huggingface-cli &> /dev/null; then
        huggingface-cli download jdh-algo/JoyVASA --local-dir pretrained_weights
    else
        echo -e "${YELLOW}⚠️  huggingface-cli가 없습니다. 수동으로 모델을 다운로드해주세요.${NC}"
    fi

    echo -e "${GREEN}✅ JoyVASA 설치 완료!${NC}"
}

# 함수: TensorRT 설치 (선택)
install_tensorrt() {
    echo ""
    echo "=============================================="
    echo "📦 TensorRT 설치 (선택사항 - 성능 최적화)"
    echo "=============================================="

    read -p "TensorRT를 설치하시겠습니까? RTX GPU 필요 (y/N): " install_trt
    if [ "$install_trt" != "y" ] && [ "$install_trt" != "Y" ]; then
        echo "건너뜀. ONNX 백엔드를 사용합니다."
        return 0
    fi

    echo "📦 TensorRT 설치 중..."
    pip install tensorrt
    check_error "TensorRT 설치 실패"

    echo -e "${GREEN}✅ TensorRT 설치 완료!${NC}"
}

# 함수: 테스트
run_test() {
    echo ""
    echo "=============================================="
    echo "🧪 설치 테스트"
    echo "=============================================="

    # Python 테스트
    python3 -c "
from pero_engine.animation import LivePortraitClient
import asyncio

async def test():
    client = LivePortraitClient()
    available = await client.is_available()
    print(f'LivePortrait 사용 가능: {available}')

asyncio.run(test())
"
    check_error "테스트 실패"

    echo -e "${GREEN}✅ 테스트 완료!${NC}"
}

# 메인 실행
main() {
    check_gpu

    echo ""
    echo "설치 옵션:"
    echo "1) 전체 설치 (FasterLivePortrait + JoyVASA)"
    echo "2) FasterLivePortrait만 설치"
    echo "3) JoyVASA만 설치"
    echo "4) 테스트만 실행"
    echo "5) 취소"
    echo ""
    read -p "선택 (1-5): " choice

    case $choice in
        1)
            install_liveportrait
            install_joyvasa
            install_tensorrt
            run_test
            ;;
        2)
            install_liveportrait
            install_tensorrt
            ;;
        3)
            install_joyvasa
            ;;
        4)
            run_test
            ;;
        5)
            echo "취소됨."
            exit 0
            ;;
        *)
            echo "잘못된 선택입니다."
            exit 1
            ;;
    esac

    echo ""
    echo "=============================================="
    echo -e "${GREEN}🎉 설치 완료!${NC}"
    echo "=============================================="
    echo ""
    echo "사용 방법:"
    echo "  1. config.yaml에서 animation.provider를 'liveportrait'로 설정"
    echo "  2. python run_server.py 실행"
    echo ""
    echo "경로:"
    echo "  FasterLivePortrait: $LIVEPORTRAIT_DIR"
    echo "  JoyVASA: $JOYVASA_DIR"
}

main
