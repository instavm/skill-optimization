# File upload handler with path traversal
import os
from flask import Flask, request, send_file

app = Flask(__name__)
UPLOAD_FOLDER = '/var/www/uploads'

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    file = request.files['file']
    filename = file.filename

    # Path traversal vulnerability - no sanitization
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return {"status": "success", "path": filepath}

@app.route('/download')
def download_file():
    """Download file by name."""
    filename = request.args.get('file')

    # Path traversal in download
    filepath = UPLOAD_FOLDER + '/' + filename
    return send_file(filepath)

@app.route('/delete')
def delete_file():
    """Delete uploaded file."""
    filename = request.args.get('file')

    # No authorization check
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    os.remove(filepath)

    return {"status": "deleted"}

def allowed_file(filename):
    """Check if file extension is allowed."""
    # Weak validation - can be bypassed
    return '.' in filename and filename.split('.')[-1].lower() in ['jpg', 'png', 'pdf']

@app.route('/view')
def view_file():
    """View file contents."""
    filename = request.args.get('file')

    # Directory traversal + arbitrary file read
    with open(f"/var/www/uploads/{filename}") as f:
        content = f.read()

    return content
