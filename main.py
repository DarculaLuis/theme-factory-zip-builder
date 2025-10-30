from flask import Flask, request, jsonify, send_file
import os, io, zipfile

app = Flask(__name__)

@app.route('/api/build-zip', methods=['POST'])
def build_zip():
    try:
        data = request.get_json()
        theme_name = data.get("theme_name", "wordpress-theme")
        files = data.get("files", {})

        # Crea cartella temporanea
        base_dir = f"/tmp/{theme_name}"
        os.makedirs(base_dir, exist_ok=True)

        # Scrivi file
        for path, content in files.items():
            full_path = os.path.join(base_dir, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        # Crea ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, file_names in os.walk(base_dir):
                for filename in file_names:
                    file_path = os.path.join(root, filename)
                    arcname = os.path.relpath(file_path, base_dir)
                    zipf.write(file_path, arcname)
        zip_buffer.seek(0)

        zip_filename = f"{theme_name}.zip"
        zip_path = f"/tmp/{zip_filename}"

        with open(zip_path, "wb") as f:
            f.write(zip_buffer.read())

        download_url = f"{request.url_root}download/{zip_filename}"
        return jsonify({"download_url": download_url})

    except Exception as e:
        print("Errore build-zip:", e)
        return jsonify({"error": "Errore interno"}), 500


@app.route('/download/<filename>')
def download(filename):
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File non trovato"}), 404


@app.route('/')
def index():
    return "✅ WordPress Theme Factory Zip Builder attivo!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
