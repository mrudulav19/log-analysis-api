
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app(tmp_path):
    upload_folder = tmp_path / "uploads"
    upload_folder.mkdir()

    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        UPLOAD_FOLDER = str(upload_folder)
        MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    app = create_app({
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "UPLOAD_FOLDER": str(upload_folder),
    "MAX_CONTENT_LENGTH": 5 * 1024 * 1024,
})

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
