from datetime import datetime, timedelta, timezone
import google.generativeai as genai

from app.celery_app import celery_app
from app.services.classification_service import classify_comment
from app.repositories.comment_repository import comment_repository
from app.schemas import CommentSchema, ClassificationResultSchema
from app.core.extensions import db
from app.models import WeeklySummary
from main import create_app

@celery_app.task
def process_and_save_comment(comment_data_dict):
    comment_data = CommentSchema.model_validate(comment_data_dict)
    try:
        classification_output = classify_comment(comment_data.text)
        if not classification_output:
            print(f"-> Falha ao classificar comentário ID: {comment_data.id}. Pulando.")
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
        print(f"-> Comentário ID: {comment_data.id} salvo com sucesso.")

    except Exception as e:
        print(f"-> ERRO ao processar comentário ID {comment_data.id}: {e}")
        db.session.rollback()

@celery_app.task
def generate_weekly_summary():
    print ("--- Iniciando tarefa de resumo semanal ---")
    app = create_app()
    with app.app_context():
        comment_texts = comment_repository.get_comment_texts_from_last_week()

        if not comment_texts:
            print("-> Nenhum comentário na última semana. Resumo não gerado.")
            return "Nenhum comentário para resumir."
        
        full_text = "\n\n---\n\n".join(comment_texts)

        prompt = f"""
        Você é um analista de dados na empresa de música AluMusic.
        Sua tarefa é analisar a seguinte lista de comentários de usuários da última semana
        e escrever um resumo conciso (no máximo 150 palavras) em português.

        O resumo deve destacar:
        - Os principais pontos de elogio.
        - As principais críticas ou problemas mencionados.
        - Sugestões ou dúvidas recorrentes.
        - Qualquer tendência notável (ex: um aumento de comentários sobre um artista específico).

        Seja objetivo e foque nos insights mais importantes para a equipe de curadoria musical.

        COMENTÁRIOS PARA ANÁLISE:
        ---
        {full_text}
        ---

        RESUMO:
        """

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            summary_text = response.text.strip()

            today = datetime.now(timezone.utc).date()
            one_week_ago_date = today - timedelta(days=7)

            new_summary = WeeklySummary(
                start_date=one_week_ago_date,
                end_date=today,
                summary_text=summary_text
            )
            db.session.add(new_summary)
            db.session.commit()

            print(f"-> Resumo semanal gerado e salvo com sucesso! ID: {new_summary.id}")
            return f"Resumo gerado com sucesso para o período de {one_week_ago_date} a {today}."
        
        except Exception as e:
            print(f"-> ERRO ao gerar resumo semanal: {e}")
            db.session.rollback()
            return "Falha ao gerar resumo."