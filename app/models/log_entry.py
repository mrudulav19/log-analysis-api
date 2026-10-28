from datetime import datetime, timezone

from app.extensions import db


class LogEntry(db.Model):
    __tablename__ = "log_entries"

    id = db.Column(db.Integer, primary_key=True)

    file_id = db.Column(
        db.Integer,
        db.ForeignKey("log_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    timestamp = db.Column(db.DateTime(timezone=True), nullable=True)
    level = db.Column(db.String(20), nullable=False, index=True)
    source = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    raw_line = db.Column(db.Text, nullable=False)
    line_number = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    log_file = db.relationship(
        "LogFile",
        back_populates="entries"
    )