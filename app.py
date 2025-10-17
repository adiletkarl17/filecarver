from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
import subprocess
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
RECOVERED_FOLDER = 'recovered_files'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'img'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RECOVERED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part in request')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('⚠ No selected file')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(filepath)

        try:
            result = subprocess.run(
                ['python', 'main.py', '--image', filepath, '--out', RECOVERED_FOLDER],
                check=True, capture_output=True, text=True
            )
            print("Carver output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Carver error:", e.stderr)
            flash('Error during file recovery. Check server logs.')
            return redirect(url_for('index'))

        return redirect(url_for('results'))

    else:
        flash('Unsupported file format.')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    files = [f for f in os.listdir(RECOVERED_FOLDER) if not f.startswith('.')]
    return render_template('results.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(RECOVERED_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
