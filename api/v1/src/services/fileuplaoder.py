import os
import logging
from flask import request, jsonify
from flask_uploads import UploadSet, configure_uploads, IMAGES, ALL
from werkzeug.utils import secure_filename
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up file uploads
UPLOAD_FOLDER = "uploads"
upload_set = UploadSet("files", ALL)
configure_uploads(upload_set, UPLOAD_FOLDER)


class FileUploader:
    def __init__(self, app):
        self.app = app

    def upload_file(self, request):
        # Validate file type and content
        if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        files = request.files.getlist("file")
        saved_files = []

        for file in files:
            # Validate file type
            if file.mimetype not in ["image/jpeg", "image/png", "application/pdf"]:
                return jsonify({"error": "Invalid file type"}), 400

            # Validate file size
            if file.size > 10 * 1024 * 1024:
                return jsonify({"error": "File too large"}), 400

            # Save file to disk asynchronously
            filename = secure_filename(file.filename)
            save_path = Path(UPLOAD_FOLDER) / filename
            file.save(save_path)

            # Log file upload
            logging.info(f"File uploaded: {filename}")

            saved_files.append(filename)

        return (
            jsonify({"message": "Files uploaded successfully", "files": saved_files}),
            200,
        )
