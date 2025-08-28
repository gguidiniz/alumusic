from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token


def test_weekly_report_page_loads_successfully(test_client: FlaskClient):
    response = test_client.get('/relatorio/semanal')
    assert response.status_code == 200
    assert "Relatório Semanal de Comentários".encode('utf-8') in response.data

def test_dashboard_page_unauthorized_access(test_client: FlaskClient):
    response = test_client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

def test_dashboard_page_authorized_access_empty_db(test_client: FlaskClient, app):
    with app.app_context():
        access_token = create_access_token(identity="test_user")

    headers = {'Authorization': f'Bearer {access_token}'}
    response = test_client.get('/dashboard', headers=headers)

    assert response.status_code == 200
    assert "Nenhum comentário encontrado" in response.data.decode('utf-8')