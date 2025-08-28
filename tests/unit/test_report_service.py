from app.services.report_service import report_service
from app.core.extensions import db
from app.models import Comment, Classification

def test_get_weekly_summary_data_returns_correct_structure(test_client, app):
    with app.app_context():
        comment = Comment(external_id='uuid-test-struct', text='Teste de estrutura')
        classification = Classification(category='ELOGIO', confidence=0.9, comment=comment)
        db.session.add_all([comment, classification])
        db.session.commit()

        report_data = report_service.get_weekly_summary_data()

    assert isinstance(report_data, dict)
    assert "categories_chart" in report_data
    assert "top_tags_chart" in report_data
    assert "over_time_chart" in report_data
    assert "avg_confidence_chart" in report_data
    assert "tags_by_category_chart" in report_data