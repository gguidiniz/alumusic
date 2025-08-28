from app.tasks import process_and_save_comment
from app.core.extensions import db
from app.models import Comment
import uuid

def test_process_and_save_comment_database_error(mocker, app):
    mocker.patch('app.tasks.classify_comment', return_value={
        "categoria": "TESTE",
        "tags_funcionalidades": {},
        "confianca": 1.0
    })

    mock_commit = mocker.patch('app.core.extensions.db.session.commit', side_effect=Exception("Erro simulado no DB"))
    mock_rollback = mocker.patch('app.core.extensions.db.session.rollback')

    comment_data_dict = {
        "id": uuid.uuid4(),
        "text": "Teste de falha no banco"
    }

    process_and_save_comment(comment_data_dict)

    mock_rollback.assert_called_once()
