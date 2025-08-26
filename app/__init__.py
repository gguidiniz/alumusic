from flask import Flask
from app.core.config import settings as default_settings
from app.core.extensions import db, migrate, jwt, cache
from app.web.routes import main_bp

from app.api.comment_routes import api_bp

def create_app(settings_override=None):
    app = Flask(__name__, template_folder='web/templates')

    if settings_override:
        app.config.from_object(settings_override)
    else:
        app.config.from_object(default_settings)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)

    from app.models import comment

    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)

    @app.route("/healthcheck")
    def healthcheck():
        return {"status": "ok"}, 200
    
    return app