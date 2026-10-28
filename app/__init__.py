
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from app.config import Config
from app.extensions import db, migrate
from app.routes import register_routes


def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)
    
    
    
    if test_config is not None:
        app.config.update(test_config)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:5173"]
            }
        },
    )

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so migrations can discover them.
    from app.models import LogFile, LogEntry

    register_routes(app)

    return app
