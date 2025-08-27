from flask import Blueprint, render_template, Response, request
from flask_jwt_extended import jwt_required
from app.services.report_service import report_service
from app.core.extensions import cache
from app.repositories.comment_repository import comment_repository
import io
import csv

main_bp = Blueprint('main', __name__)

@main_bp.route('/relatorio/semanal', methods=['GET'])
@cache.cached(timeout=30)
def weekly_report():
    report_data = report_service.get_weekly_summary_data()

    return render_template('relatorio.html', report_data=report_data)

@main_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@main_bp.route('/dashboard')
@jwt_required()
def dashboard_page():
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('q', None)

    if search_term:
        pagination = comment_repository.search_comments(search_term, page=page)
    else:
        pagination = comment_repository.get_latest_comments(page=page)

    return render_template(
        'dashboard.html',
        pagination=pagination,
        search_term=search_term
    )

@main_bp.route('/export/csv')
@jwt_required()
def export_csv():
    all_comments = comment_repository.get_all_comments_with_latest_classification()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['ID Externo', 'Data', 'Texto', 'Categoria', 'Confiança', 'Tags'])

    for comment in all_comments:
        if comment.classifications:
            latest_classification = comment.classifications[-1]
            tags = ", ".join([tag.name for tag in latest_classification.tags])
            writer.writerow([
                str(comment.external_id),
                comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                comment.text,
                latest_classification.category,
                latest_classification.confidence,
                tags
            ])

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=relatorio_comentarios.csv"}
    )