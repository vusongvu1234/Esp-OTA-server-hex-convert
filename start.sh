#!/bin/bash
# Cài đặt arduino-cli nếu chưa có
if ! command -v arduino-cli &> /dev/null
then
    echo "Installing arduino-cli..."
    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
fi

# Chạy server với gunicorn, lấy PORT từ biến môi trường
gunicorn -b 0.0.0.0:$PORT Server:app

