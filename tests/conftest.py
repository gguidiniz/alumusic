import pytest
from app import create_app
from app.core.extensions import db

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(settings_override=TestConfig)

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()