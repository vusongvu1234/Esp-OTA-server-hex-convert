#!/bin/bash
set -e  # Dừng script nếu có lỗi

echo "Current PATH: $PATH"

# Kiểm tra và cài đặt arduino-cli nếu chưa có
export PATH="/opt/render/project/src/bin:$PATH"
if ! command -v arduino-cli &>/dev/null; then
    echo "Installing arduino-cli..."
    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
fi

# Kiểm tra lại xem arduino-cli đã được cài đặt chưa
if ! command -v arduino-cli &>/dev/null; then
    echo "Error: arduino-cli installation failed!"
    exit 1
fi

# Cập nhật danh sách core và cài đặt core arduino:avr
echo "Updating Arduino CLI index..."
arduino-cli core update-index

echo "Installing Arduino AVR core..."
arduino-cli core install arduino:avr
arduino-cli lib install LiquidCrystal

# Chạy server với gunicorn
gunicorn -b 0.0.0.0:$PORT Server:app
