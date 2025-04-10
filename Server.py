from flask import Flask, request, jsonify
from flask import send_file
import subprocess
import os

app = Flask(__name__)
@app.route('/')
def home():
	return "Server đang chạy🎉🎊🥇💵💸🏆💰"
@app.route('/get_hex', methods=['GET'])
def get_hex():
    sketch_dir = "/opt/render/project/src/temp"
    build_dir = os.path.join(sketch_dir, "build")  # Thêm dòng này để chỉ định thư mục build
    hex_files = [f for f in os.listdir(build_dir) if f.endswith('.hex')]  # Dùng build_dir ở đây
    if not hex_files:
        return jsonify({"error": "Biên dịch thành công nhưng không tìm thấy file .hex"}), 500
    hex_file_path = os.path.join(build_dir, hex_files[0])  # Cập nhật đường dẫn
    return send_file(hex_file_path, as_attachment=True)

@app.route('/debug_avr')
def avr_check():
    check_core = subprocess.run(["/opt/render/project/src/bin/arduino-cli", "core", "list"], capture_output=True, text=True)

    if "arduino:avr" not in check_core.stdout:
        print("⚠️ Chưa có core arduino:avr. Đang cài đặt...")
        install_core = subprocess.run(["/opt/render/project/src/bin/arduino-cli", "core", "install", "arduino:avr"], capture_output=True, text=True)
        print("Core Install Output:", install_core.stdout)

@app.route('/files', methods=['GET'])
def list_files():
    try:
        hex_files = [f for f in os.listdir('.') if f.endswith('.hex')]
        return jsonify({"files": hex_files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/install_avr')
def install_avr():
    try:
        cmd_update = "/opt/render/project/src/bin/arduino-cli core update-index"
        cmd_install = "/opt/render/project/src/bin/arduino-cli core install arduino:avr"
        
        update_result = subprocess.run(cmd_update.split(), capture_output=True, text=True)
        install_result = subprocess.run(cmd_install.split(), capture_output=True, text=True)

        return jsonify({
            "update_stdout": update_result.stdout,
            "update_stderr": update_result.stderr,
            "install_stdout": install_result.stdout,
            "install_stderr": install_result.stderr
        })
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

        sketch_dir = "/opt/render/project/src/temp" 
        if not os.path.exists(sketch_dir):
            os.makedirs(sketch_dir)

        file_path = os.path.join(sketch_dir, "temp.ino")
        
        with open(file_path, "w") as f:
             f.write(code)


        print(f"✅ Đã lưu file {file_path}")

        # Biên dịch bằng arduino-cli
                # Biên dịch bằng arduino-cli
        build_dir = os.path.join(sketch_dir, "build")
        if not os.path.exists(build_dir):
             os.makedirs(build_dir)

        result = subprocess.run(
            ["/opt/render/project/src/bin/arduino-cli", "compile", "--fqbn", "arduino:avr:uno", "--output-dir", build_dir, sketch_dir],
            capture_output=True, text=True
        )

        print("Return code:", result.returncode)
        print("Stdout:", result.stdout)
        print("Stderr:", result.stderr)

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        # Tìm file .hex được tạo ra
        hex_files = [f for f in os.listdir(build_dir) if f.endswith('.hex')]
        if not hex_files:
            return jsonify({"error": "Biên dịch thành công nhưng không tìm thấy file .hex"}), 500

        hex_file_path = os.path.join(build_dir, hex_files[0])  # Đường dẫn đúng cho file .hex

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
