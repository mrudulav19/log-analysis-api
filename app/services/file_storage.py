
import os
from uuid import uuid4

from werkzeug.utils import secure_filename


def save_uploaded_file(file, upload_folder):
    """Save an uploaded file using a unique storage name."""

    original_name = secure_filename(file.filename or "")

    if not original_name:
        raise ValueError("Invalid filename.")

    extension = original_name.rsplit(".", 1)[-1].lower()

    if "." not in original_name or extension not in {"log", "txt"}:
        raise ValueError("Only .log and .txt files are allowed.")

    os.makedirs(upload_folder, exist_ok=True)

    stored_filename = f"{uuid4().hex}.{extension}"
    file_path = os.path.join(upload_folder, stored_filename)

    file.save(file_path)

    return original_name, stored_filename, file_path
