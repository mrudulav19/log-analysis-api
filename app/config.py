
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-only-change-this"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MiB
    UPLOAD_FOLDER = os.path.join(
        os.path.abspath("instance"),
        "uploads"
    )
    ALLOWED_EXTENSIONS = {"log", "txt"}
