import pytest
from flask.testing import FlaskClient
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

def test_create_comment_api_success(test_client: FlaskClient, mocker):
    mocker.patch(
        'app.api.comment_routes.classify_comment',
        return_value={
            "categoria": "ELOGIO",
            "tags_funcionalidades": {"teste_tag": "explicação da tag"},
            "confianca": 0.9
        }
    )

    mocker.patch('app.api.comment_routes.comment_repository.save_comment_classification')
    mocker.patch('app.api.comment_routes.db.session.commit')

    test_payload = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "text": "Este é um comentário de teste."
    }


    response = test_client.post('/api/comments', json=test_payload)

    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data["category"] == "ELOGIO"
    assert response_data["comment_id"] == "123e4567-e89b-12d3-a456-426614174000"