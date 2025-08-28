from flask.testing import FlaskClient
from app.core.extensions import db
from app.models import Comment, Classification
from datetime import datetime, timezone

def test_weekly_report_page(test_client: FlaskClient):
    comment1 = Comment(external_id='test-uuid-report', text='Teste para relatório')
    
    classification1 = Classification(
        category='SUGESTÃO',
        confidence=0.99,
        comment=comment1,
        created_at=datetime.now(timezone.utc)
    )
    db.session.add_all([comment1, classification1])
    db.session.commit()

    count = db.session.query(Classification).count()
    print(f"\n[DEBUG NO TESTE] Classificações no DB ANTES do request: {count}")

    response = test_client.get('/relatorio/semanal')

    assert response.status_code == 200
    assert "Relatório Semanal de Comentários".encode('utf-8') in response.data
    assert "SUGEST" in response.data.decode('utf-8').upper()