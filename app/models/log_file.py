from datetime import datetime, timezone

from app.extensions import db


class LogFile(db.Model):
    __tablename__ = "log_files"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    uploaded_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    total_lines = db.Column(db.Integer, nullable=False, default=0)
    parsed_lines = db.Column(db.Integer, nullable=False, default=0)
    failed_lines = db.Column(db.Integer, nullable=False, default=0)

    entries = db.relationship(
        "LogEntry",
        back_populates="log_file",
        cascade="all, delete-orphan"
    )