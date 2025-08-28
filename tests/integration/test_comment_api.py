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