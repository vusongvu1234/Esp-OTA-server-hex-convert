from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)
@app.route('/', methods=['GET'])
def debug_status():
    return jsonify({
        "log":"server is live✔️"
    })
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
        with open("temp.ino", "w") as f:
            f.write(code)
        print("Đã lưu file temp.ino")

        # Gọi lệnh biên dịch
        result = subprocess.run(
            ["arduino-cli", "compile", "--fqbn", "arduino:avr:uno", "temp.ino"],
            capture_output=True, text=True
        )

        # In ra log lệnh biên dịch
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
