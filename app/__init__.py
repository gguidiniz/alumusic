from flask import Flask
from app.core.config import settings
from app.core.extensions import db, migrate, jwt
from app.web.routes import main_bp

from app.api.comment_routes import api_bp

def create_app():
    app = Flask(__name__, template_folder='web/templates')

    app.config.from_object(settings)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.models import comment

    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)

    @app.route("/healthcheck")
    def healthcheck():
        return {"status": "ok"}, 200
    
    return app