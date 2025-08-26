from flask import Blueprint, render_template
from app.services.report_service import report_service
from app.core.extensions import cache

main_bp = Blueprint('main', __name__)

@main_bp.route('/relatorio/semanal', methods=['GET'])
@cache.cached(timeout=30)
def weekly_report():
    report_data = report_service.get_weekly_summary_data()

    return render_template('relatorio.html', report_data=report_data)