from app.services.report_service import report_service
from app.core.extensions import db
from app.models import Comment, Classification, Tag
from datetime import datetime, timezone, timedelta

def test_get_weekly_summary_data(test_client, app):
    with app.app_context():
        # Cria dados de teste
        comment1 = Comment(external_id='uuid1', text='Elogio 1')
        comment2 = Comment(external_id='uuid2', text='Elogio 2')
        comment3 = Comment(external_id='uuid3', text='Critica 1')

        tag_rock = Tag(name='rock')
        tag_pop = Tag(name='pop')

        c1 = Classification(category='ELOGIO', confidence=0.9, comment=comment1, tags=[tag_rock, tag_pop], created_at=datetime.now(timezone.utc) - timedelta(days=1))
        c2 = Classification(category='ELOGIO', confidence=0.9, comment=comment2, tags=[tag_rock], created_at=datetime.now(timezone.utc) - timedelta(days=2))
        c3 = Classification(category='CRÍTICA', confidence=0.8, comment=comment3, tags=[tag_rock], created_at=datetime.now(timezone.utc) - timedelta(days=3))
        
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        report_data = report_service.get_weekly_summary_data()

    assert report_data is not None
    
    cat_chart = report_data['categories_chart']
    assert cat_chart['labels'] == ['ELOGIO', 'CRÍTICA']
    assert cat_chart['data'] == [2, 1]

    tags_chart = report_data['top_tags_chart']
    assert tags_chart['labels'] == ['rock', 'pop']
    assert tags_chart['data'] == [3, 1]