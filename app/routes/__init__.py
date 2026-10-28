
from app.routes.health import health_bp
from app.routes.files import files_bp


def register_routes(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(files_bp)
