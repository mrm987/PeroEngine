# PeroEngine 아이콘 가이드

## 필요한 아이콘 파일

### 1. **icon.png** (필수)
- 크기: 512x512 픽셀
- 형식: PNG (투명 배경 권장)
- 용도: Linux, 개발 모드

### 2. **icon.ico** (Windows 빌드 시 필수)
- 크기: 256x256 픽셀
- 형식: ICO
- 용도: Windows 설치 파일

### 3. **icon.icns** (Mac 빌드 시 필수)
- 크기: 512x512 픽셀
- 형식: ICNS
- 용도: macOS 애플리케이션

### 4. **tray-icon.png** (선택사항)
- 크기: 16x16 또는 22x22 픽셀
- 형식: PNG (투명 배경)
- 용도: 시스템 트레이 아이콘

---

## 아이콘 준비 방법

### 옵션 1: 온라인 도구 사용

1. 512x512 PNG 아이콘 준비
2. 변환 사이트 이용:
   - https://icoconvert.com (PNG → ICO)
   - https://cloudconvert.com/png-to-icns (PNG → ICNS)

### 옵션 2: Electron Icon 빌더

```bash
npm install -g electron-icon-maker

# 512x512 PNG 아이콘에서 모든 형식 생성
electron-icon-maker --input=icon.png --output=./
```

---

## 임시 아이콘

현재는 아이콘이 없으므로 빌드 시 에러가 발생할 수 있습니다.

### 해결 방법:

1. **간단한 임시 아이콘 생성** (권장)
   - 온라인에서 무료 아이콘 다운로드
   - https://www.flaticon.com/
   - https://icons8.com/

2. **빌드 시 아이콘 무시**
   - package.json에서 icon 설정 제거

---

## 캐릭터 이미지를 아이콘으로 사용

PeroEngine의 특징인 "이미지 한 장" 컨셉을 살려,
사용자가 업로드한 캐릭터 이미지를 앱 아이콘으로도 사용할 수 있습니다.

### 구현 예정:
- 캐릭터 생성 시 자동으로 앱 아이콘 변경
- 시스템 트레이에 캐릭터 얼굴 표시
