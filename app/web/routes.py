from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required
from app.services.report_service import report_service
from app.core.extensions import cache

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
    return"<h1>Bem-vindo ao Dashboard!<h1>"