
from sqlalchemy import text

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    result = db.session.execute(text("SELECT 1"))
    print("Database connection successful:", result.scalar_one())
