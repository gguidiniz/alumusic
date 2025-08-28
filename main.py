from flask import Flask, jsonify, redirect, url_for, request
from app.core.config import settings as default_settings
from app.core.extensions import db, migrate, jwt, cache
from app.web.routes import main_bp
from app.api.comment_routes import api_bp
from app.api.auth_routes import auth_bp
from app.cli import register_cli_commands
from app.utils import format_datetime_local
from app.celery_app import init_celery

def create_app(settings_override=None):
    app = Flask(__name__, template_folder='app/web/templates')

    if settings_override:
        app.config.from_object(settings_override)
    else:
        app.config.from_object(default_settings)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    init_celery(app)

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        if request.blueprint == 'api':
            return jsonify(msg="Missing or invalid token"), 401
        return redirect(url_for('main.login_page'))

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

app = create_app()
celery = app.extensions["celery"]