from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Arduino OTA Server Đang Chạy!"

@app.route('/compile', methods=['POST'])
def compile_arduino():
    try:
        code = request.form.get("code")
        if not code:
            return jsonify({"error": "Không có mã Arduino nào được gửi!"}), 400

        # Lưu code vào file
        with open("temp.ino", "w") as f:
            f.write(code)

        # Biên dịch code thành .hex
        result = subprocess.run(["arduino-cli", "compile", "--fqbn", "arduino:avr:uno", "temp.ino"], capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        return jsonify({"message": "✅ Biên dịch thành công!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
   port = int(os.environ.get("PORT", 5000))  # Lấy PORT từ biến môi trường, mặc định là 5000
   app.run(host='0.0.0.0', port=port)
