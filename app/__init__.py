from flask import Flask
from app.core.config import settings as default_settings
from app.core.extensions import db, migrate, jwt, cache
from app.web.routes import main_bp
from app.cli import register_cli_commands
from app.api.auth_routes import auth_bp
from app.utils import format_datetime_local
from app.celery_app import init_celery

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
    init_celery(app)

    app.jinja_env.filters['localdatetime'] = format_datetime_local

    from app.models import User, Comment

    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    register_cli_commands(app)

    @app.route("/healthcheck")
    def healthcheck():
        return {"status": "ok"}, 200
    
    return app