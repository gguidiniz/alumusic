from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.schemas.comment_schema import CommentSchema, ClassificationResultSchema
from app.services.classification_service import classify_comment
from app.repositories.comment_repository import comment_repository
from app.core.extensions import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/comments', methods=['POST'])
def criar_comentario():
    json_data = request.get_json()

    if not json_data:
        return jsonify({"erro": "Requisição sem corpo JSON"}), 400
    
    is_batch = isinstance(json_data, list)
    comments_to_process = json_data if is_batch else [json_data]

    try:
        validated_comments = [CommentSchema.model_validate(item) for item in comments_to_process]

        results = []
        for comment_data in validated_comments:
            classification_output = classify_comment(comment_data.text)

            if not classification_output:
                continue

            tags_output = classification_output.get("tags_funcionalidades", {})
            result_obj = {
                "comment_id": comment_data.id,
                "category": classification_output.get("categoria", "CLASSIFICATION_ERROR"),
                "confidence": classification_output.get("confianca", 0.0),
                "tags": [{"tag": k, "explanation": v} for k, v in tags_output.items()]
            }
            validated_result = ClassificationResultSchema.model_validate(result_obj)

            comment_repository.save_comment_classification(comment_data, validated_result)

            results.append(validated_result)

        db.session.commit()

        if is_batch:
            response_data = [res.model_dump(mode='json') for res in results]
        else:
            response_data = results[0].model_dump(mode='json') if results else {}

        return jsonify(response_data), 200
    
    except ValidationError as e:
        db.session.rollback()
        return jsonify({"erro": "Dados inválidos", "detalhes": e.errors()}), 422
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500