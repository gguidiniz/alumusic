import json
from unittest.mock import MagicMock
from app.services.classification_service import classify_comment

def test_classify_comment_success(mocker):
    test_text = "Eu adorei a melodia dessa música."

    fake_llm_response_text = json.dumps({
        "categoria": "ELOGIO",
        "tags_funcionalidades": { "melodia_positiva": "Comentário elogia a melodia." },
        "confianca": 0.95
    })

    mock_response = MagicMock()
    mock_response.text = fake_llm_response_text

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    mocker.patch('google.generativeai.GenerativeModel', return_value=mock_model)

    result = classify_comment(test_text)

    assert result is not None
    assert isinstance(result, dict)

    assert result["categoria"] == "ELOGIO"
    assert result["confianca"] == 0.95
    assert "melodia_positiva" in result["tags_funcionalidades"]

    mock_model.generate_content.assert_called_once()