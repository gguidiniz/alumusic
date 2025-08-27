from app.celery_app import celery_app
from app.services.classification_service import classify_comment
from app.repositories.comment_repository import comment_repository
from app.schemas import CommentSchema, ClassificationResultSchema
from app.core.extensions import db

@celery_app.task
def process_and_save_comment(comment_data_dict):
    comment_data = CommentSchema.model_validate(comment_data_dict)
    
    try:
        classification_output = classify_comment(comment_data.text)
        if not classification_output:
            print(f"Falha ao classificar comentário ID: {comment_data.id}. Pulando.")
            return

        tags_output = classification_output.get("tags_funcionalidades", {})
        result_obj = {
            "comment_id": comment_data.id,
            "category": classification_output.get("categoria", "CLASSIFICATION_ERROR"),
            "confidence": classification_output.get("confianca", 0.0),
            "tags": [{"tag": k, "explanation": v} for k, v in tags_output.items()]
        }
        validated_result = ClassificationResultSchema.model_validate(result_obj)
        
        comment_repository.save_comment_classification(comment_data, validated_result)
        db.session.commit()
        print(f"Comentário ID: {comment_data.id} processado e salvo com sucesso.")

    except Exception as e:
        print(f"ERRO ao processar comentário ID {comment_data.id}: {e}")
        db.session.rollback()
