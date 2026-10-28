
import os

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import select
from werkzeug.exceptions import RequestEntityTooLarge

from app.extensions import db
from app.models import LogFile, LogEntry
from app.services.file_storage import save_uploaded_file
from app.services.log_parser import parse_lines


files_bp = Blueprint("files", __name__)


@files_bp.route("/api/v1/files", methods=["POST"])
def upload_file():
    uploaded = request.files.get("file")

    if uploaded is None or not uploaded.filename:
        return jsonify({
            "error": "A file is required in the 'file' field."
        }), 400

    file_path = None

    try:
        original_name, stored_name, file_path = save_uploaded_file(
            uploaded,
            current_app.config["UPLOAD_FOLDER"]
        )

        # Read as UTF-8, allowing a UTF-8 BOM.
        with open(file_path, "r", encoding="utf-8-sig") as log_file:
            lines = log_file.readlines()

        # Avoid accepting binary or invalid UTF-8 content.
        result = parse_lines(lines)

        log_file_record = LogFile(
            filename=original_name,
            stored_filename=stored_name,
            total_lines=result["total_lines"],
            parsed_lines=result["parsed_lines"],
            failed_lines=result["failed_lines"],
        )

        for entry in result["entries"]:
            log_file_record.entries.append(
                LogEntry(
                    timestamp=entry["timestamp"],
                    level=entry["level"],
                    source=entry["source"],
                    message=entry["message"],
                    raw_line=entry["raw_line"],
                    line_number=entry["line_number"],
                )
            )

        db.session.add(log_file_record)
        db.session.commit()

        return jsonify({
            "message": "File uploaded and processed successfully.",
            "file": {
                "id": log_file_record.id,
                "filename": log_file_record.filename,
                "total_lines": log_file_record.total_lines,
                "parsed_lines": log_file_record.parsed_lines,
                "failed_lines": log_file_record.failed_lines,
            }
        }), 201

    except ValueError as error:
        db.session.rollback()

        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({"error": str(error)}), 415

    except UnicodeDecodeError:
        db.session.rollback()

        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            "error": "File must contain valid UTF-8 text."
        }), 400

    except OSError:
        db.session.rollback()

        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        current_app.logger.exception("File storage or reading failed.")

        return jsonify({
            "error": "Unable to read or store the uploaded file."
        }), 500

    except Exception:
        db.session.rollback()

        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                current_app.logger.exception(
                    "Could not clean up uploaded file."
                )

        current_app.logger.exception("File upload failed.")

        return jsonify({
            "error": "An unexpected error occurred while processing the file."
        }), 500


@files_bp.route("/api/v1/files", methods=["GET"])
def list_files():
    records = db.session.scalars(
        select(LogFile).order_by(LogFile.uploaded_at.desc())
    ).all()

    return jsonify({
        "files": [
            {
                "id": record.id,
                "filename": record.filename,
                "uploaded_at": record.uploaded_at.isoformat(),
                "total_lines": record.total_lines,
                "parsed_lines": record.parsed_lines,
                "failed_lines": record.failed_lines,
            }
            for record in records
        ]
    }), 200


@files_bp.route("/api/v1/files/<int:file_id>", methods=["GET"])
def get_file(file_id):
    record = db.session.get(LogFile, file_id)

    if record is None:
        return jsonify({"error": "File not found."}), 404

    return jsonify({
        "id": record.id,
        "filename": record.filename,
        "uploaded_at": record.uploaded_at.isoformat(),
        "total_lines": record.total_lines,
        "parsed_lines": record.parsed_lines,
        "failed_lines": record.failed_lines,
    }), 200


@files_bp.route("/api/v1/files/<int:file_id>/entries", methods=["GET"])
def get_file_entries(file_id):
    # Confirm that the uploaded file exists.
    record = db.session.get(LogFile, file_id)

    if record is None:
        return jsonify({"error": "File not found."}), 404

    # Retrieve parsed entries in their original line order.
    entries = db.session.scalars(
        select(LogEntry)
        .where(LogEntry.file_id == file_id)
        .order_by(LogEntry.line_number.asc())
    ).all()

    return jsonify({
        "file_id": record.id,
        "filename": record.filename,
        "total_entries": len(entries),
        "entries": [
            {
                "id": entry.id,
                "timestamp": (
                    entry.timestamp.isoformat()
                    if entry.timestamp
                    else None
                ),
                "level": entry.level,
                "source": entry.source,
                "message": entry.message,
                "line_number": entry.line_number,
            }
            for entry in entries
        ],
    }), 200


@files_bp.route("/api/v1/files/<int:file_id>", methods=["DELETE"])
def delete_file(file_id):
    record = db.session.get(LogFile, file_id)

    if record is None:
        return jsonify({"error": "File not found."}), 404

    file_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        record.stored_filename
    )

    try:
        # Delete database records first. The relationship cascades
        # deletion to associated LogEntry records.
        db.session.delete(record)
        db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Database deletion failed.")

        return jsonify({
            "error": "Unable to delete file records."
        }), 500

    # Remove the physical file after the database commit.
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        current_app.logger.exception(
            "Database records deleted, but stored file cleanup failed."
        )

        return jsonify({
            "message": "Database records deleted, but stored file cleanup failed."
        }), 500

    return jsonify({
        "message": "File and associated log entries deleted successfully."
    }), 200


@files_bp.app_errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    return jsonify({
        "error": "File is too large. Maximum upload size is 5 MiB."
    }), 413
