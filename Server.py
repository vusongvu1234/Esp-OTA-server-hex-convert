from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Arduino OTA Server Đang Chạy!"

@app.route('/files', methods=['GET'])
def list_files():
    try:
        hex_files = [f for f in os.listdir('.') if f.endswith('.hex')]
        return jsonify({"files": hex_files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/compile', methods=['POST'])
def compile_arduino():
    try:
        # Kiểm tra dữ liệu gửi lên: JSON hoặc form-data
        code = None
        if request.is_json:
            code = request.json.get("code")
            print("Received JSON data:", request.json)
        else:
            code = request.form.get("code")
            print("Received form data:", request.form)

        if not code:
            return jsonify({"error": "Không có mã Arduino nào được gửi!"}), 400

        # Tạo thư mục temp nếu chưa có
        sketch_dir = "temp"
        if not os.path.exists(sketch_dir):
            os.makedirs(sketch_dir)

        # Đường dẫn đầy đủ đến file .ino
        file_path = os.path.join(sketch_dir, "src.ino")

        # Ghi mã Arduino vào file
        with open(file_path, "w") as f:
            f.write(code)

        print(f"✅ Đã lưu file {file_path}")

        # Biên dịch bằng arduino-cli
        result = subprocess.run(
            ["/opt/render/project/src/bin/arduino-cli", "compile", "--fqbn", "arduino:avr:uno", sketch_dir],
            capture_output=True, text=True
        )

        print("Return code:", result.returncode)
        print("Stdout:", result.stdout)
        print("Stderr:", result.stderr)

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        # Tìm file .hex được tạo ra
        hex_files = [f for f in os.listdir(sketch_dir) if f.endswith('.hex')]
        if not hex_files:
            return jsonify({"error": "Biên dịch thành công nhưng không tìm thấy file .hex"}), 500

        hex_file_path = os.path.join(sketch_dir, hex_files[0])

        return jsonify({"message": "✅ Biên dịch thành công!", "hex_file": hex_file_path})

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/debug', methods=['GET'])
def debug_info():
    return jsonify({
        "path": os.environ.get("PATH"),
        "arduino_cli_version": os.popen("/opt/render/project/src/bin/arduino-cli version").read(),
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
