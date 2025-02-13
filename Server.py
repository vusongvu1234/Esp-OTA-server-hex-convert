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

        # Ghi mã Arduino vào file
        sketch_dir = "temp"
        if not os.path.exists(sketch_dir):
          os.makedirs(sketch_dir)

file_path = os.path.join(sketch_dir, "temp.ino")

# Ghi mã Arduino vào file trong thư mục
with open(file_path, "w") as f:
    f.write(code)

print(f"✅ Đã lưu file {file_path}")

# Gọi lệnh biên dịch
result = subprocess.run(
    ["/opt/render/project/src/bin/arduino-cli", "compile", 
     "--fqbn", "arduino:avr:uno", sketch_dir], 
    capture_output=True, text=True
)

print("Return code:", result.returncode)
print("Stdout:", result.stdout)
print("Stderr:", result.stderr)

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        return jsonify({"message": "✅ Biên dịch thành công!"})

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
