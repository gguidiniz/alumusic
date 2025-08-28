import pytest
from main import create_app
from app.core.extensions import db

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    JWT_COOKIE_CSRF_PROTECT = False

@pytest.fixture(scope='function')
def app():
    app = create_app(settings_override=TestConfig)
    yield app

@pytest.fixture(scope='function')
def test_client(app):
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()