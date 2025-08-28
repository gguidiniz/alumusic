import pytest
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

def test_create_comment_api_success(test_client: FlaskClient, mocker):
    mock_task = mocker.patch('app.api.comment_routes.process_and_save_comment.delay')

    access_token = create_access_token(identity="test_user")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    test_payload = [{
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "text": "Este é um comentário de teste."
    }]

    response = test_client.post('/api/comments', json=test_payload, headers=headers)

    assert response.status_code == 202
    response_data = response.get_json()
    assert "comentários recebidos e enfileirados" in response_data["msg"]
    mock_task.assert_called_once()

@pytest.mark.parametrize(
    "payload, expected_error_part",
    [
        (
            {"id": "nao-e-um-uuid", "text": "texto válido"},
            "Input should be a valid UUID"
        ),
        (
            {"id": "123e4567-e89b-12d3-a456-426614174000", "text": ""},
            "String should have at least 1 character"
        ),
        (
            {"id": "123e4567-e89b-12d3-a456-426614174000"},
            "Field required"
        ),
    ]
)
def test_create_comment_via_api_validation_errors(test_client: FlaskClient, payload: dict, expected_error_part: str):
    access_token = create_access_token(identity="test_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = test_client.post('/api/comments', json=payload, headers=headers)

    assert response.status_code == 422
    response_data = response.get_json()
    assert "detalhes" in response_data
    assert expected_error_part in str(response_data["detalhes"])