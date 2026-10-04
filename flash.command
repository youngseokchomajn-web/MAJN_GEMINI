#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "========================================================="
echo "  [MAJN] ESP32-WROOM-32UE BLE 펌웨어 자동 업로드 도구"
echo "========================================================="
echo ""

# 1. PlatformIO 탐색 (PATH, VS Code 기본 경로, Homebrew)
PIO_CMD=""
if command -v pio >/dev/null 2>&1; then
    PIO_CMD="pio"
elif [ -f "$HOME/.platformio/penv/bin/pio" ]; then
    PIO_CMD="$HOME/.platformio/penv/bin/pio"
elif [ -f "/opt/homebrew/bin/pio" ]; then
    PIO_CMD="/opt/homebrew/bin/pio"
elif [ -f "/usr/local/bin/pio" ]; then
    PIO_CMD="/usr/local/bin/pio"
elif [ -f "$HOME/.local/bin/pio" ]; then
    PIO_CMD="$HOME/.local/bin/pio"
fi

if [ -z "$PIO_CMD" ]; then
    echo "❌ PlatformIO(pio) 실행 파일을 찾을 수 없습니다."
    echo "기본 경로들을 확인했습니다:"
    echo " - $HOME/.platformio/penv/bin/pio"
    echo " - /opt/homebrew/bin/pio"
    echo " - /usr/local/bin/pio"
    echo ""
    echo "VS Code의 PlatformIO 확장을 열거나 터미널에서 pio 설치를 확인해주세요."
    echo ""
    read -p "엔터 키를 누르면 창이 닫힙니다..."
    exit 1
fi

echo "✅ PlatformIO 감지됨: $PIO_CMD"
echo "🔌 포트 확인: /dev/cu.usbserial-0001"
echo ""
echo "💡 [중요 안내] ESP32 다운로드 모드 진입 방법:"
echo "   보드의 UART_HDR 3번 핀(ESP_IO0)을 GND(6번 핀)에 연결(점퍼선)해 두거나,"
echo "   'Connecting........' 문구가 뜰 때 BOOT 버튼을 꾹 누르고 계시면 즉시 플래싱됩니다."
echo ""
echo "🚀 펌웨어 빌드 및 ESP32 업로드를 시작합니다..."
echo "---------------------------------------------------------"

cd "$DIR/인증준비/firmware"
"$PIO_CMD" run -e esp32_ble_test -t upload

UPLOAD_EXIT_CODE=$?

if [ $UPLOAD_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ 펌웨어 업로드 중 오류가 발생했습니다 (코드: $UPLOAD_EXIT_CODE)."
    echo "ESP32 보드의 USB 케이블 연결과 UART 스위치를 확인해주세요."
    echo ""
    read -p "엔터 키를 누르면 창이 닫힙니다..."
    exit $UPLOAD_EXIT_CODE
fi

echo ""
echo "========================================================="
echo "🎉 펌웨어 업로드 완료!"
echo "========================================================="
echo ""
echo "🌐 Chrome 브라우저에서 관제 대시보드를 엽니다..."
open "$DIR/bassinet_simulator/index.html"

echo ""
echo "👉 다음 단계:"
echo "1. 열린 Chrome 브라우저 상단 우측의 [ESP32 BLE 연결] 버튼을 누르세요."
echo "2. 검색된 'MAJN-Bassinet'을 선택하고 페어링을 완료하세요."
echo ""
read -p "모든 과정이 완료되었습니다. 엔터 키를 누르면 창을 닫습니다..."
