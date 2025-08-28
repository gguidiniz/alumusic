import pytest
from app.tasks import process_and_save_comment, generate_weekly_summary
from app.core.extensions import db
from app.models import Comment, WeeklySummary
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
import uuid

def test_process_and_save_comment_database_error(mocker, app):
    mocker.patch('app.tasks.classify_comment', return_value={
        "categoria": "TESTE",
        "tags_funcionalidades": {},
        "confianca": 1.0
    })

    mock_rollback = mocker.patch('app.core.extensions.db.session.rollback')

    comment_data_dict = {
        "id": uuid.uuid4(),
        "text": "Teste de falha no banco"
    }

    process_and_save_comment(comment_data_dict)

    mock_rollback.assert_called_once()

@pytest.fixture(scope='module')
def test_generate_weekly_summary(test_client, app, mocker):
    with app.app_context():
        comment1 = Comment(
            external_id='summary-uuid-1', 
            text="A produção desta música é incrível.", 
            created_at=datetime.now(timezone.utc) - timedelta(days=2)
        )
        comment2 = Comment(
            external_id='summary-uuid-2', 
            text='Comentário antigo.', 
            created_at=datetime.now(timezone.utc) - timedelta(days=10)
        )
        db.session.add_all([comment1, comment2])
        db.session.commit()

        fake_summary = "Ocorreram elogios sobre a produção musical."
        mock_response = MagicMock()
        mock_response.text = fake_summary
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mocker.patch('google.generativeai.GenerativeModel', return_value=mock_model)

        result_message = generate_weekly_summary()

        assert "Resumo gerado com sucesso" in result_message
        
        summary = db.session.query(WeeklySummary).one_or_none()
        assert summary is not None
        assert summary.summary_text == fake_summary
        
        prompt_enviado = mock_model.generate_content.call_args[0][0]
        assert comment1.text in prompt_enviado
        assert "Comentário antigo" not in prompt_enviado