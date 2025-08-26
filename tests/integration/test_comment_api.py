from flask.testing import FlaskClient

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