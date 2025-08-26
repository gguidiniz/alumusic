from flask.testing import FlaskClient
from app.core.extensions import db
from app.models.comment import Comment, Classification

def test_weekly_report_page(test_client: FlaskClient):
    comment1 = Comment(external_id='test-uuid-1', text='Comentário de teste 1')
    db.session.add(comment1)

    classification1 = Classification(category='ELOGIO', confidence=0.9, comment=comment1)
    classification2 = Classification(category='CRÍTICA', confidence=0.8, comment=comment1)
    db.session.add_all([classification1, classification2])

    db.session.commit()

    response = test_client.get('/relatorio/semanal')

    assert response.status_code == 200
    assert "Relatório Semanal de Comentários".encode('utf-8') in response.data
    assert b"ELOGIO" in response.data