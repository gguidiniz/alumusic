from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.schemas import CommentSchema
from app.tasks import process_and_save_comment

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/comments', methods=['POST'])
@jwt_required()
def criar_comentario():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"erro": "Requisição sem corpo JSON"}), 400
    
    is_batch = isinstance(json_data, list)
    comments_to_process = json_data if is_batch else [json_data]

    try:
        validated_comments = [CommentSchema.model_validate(item) for item in comments_to_process]

        for comment in validated_comments:
            process_and_save_comment.delay(comment.model_dump())

        return jsonify({"msg": f"{len(validated_comments)} comentários recebidos e enfileirados para processamento."}), 202

    except ValidationError as e:
        return jsonify({"erro": "Dados inválidos", "detalhes": e.errors()}), 422
    except Exception as e:
        print(f"Erro inesperado ao enfileirar tarefas: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor ao enfileirar tarefas"}), 500