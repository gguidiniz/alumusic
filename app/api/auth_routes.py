from flask import Blueprint, request, jsonify, redirect, url_for
from app.models import User
from flask_jwt_extended import create_access_token, set_access_cookies

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json.get('email', None)
        password = request.json.get('password', None)
    else:
        email = request.form.get('email', None)
        password = request.form.get('password', None)

    if not email or not password:
        return jsonify({"msg": "Email e senha são obrigatórios"}), 400
    
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))

        response = redirect(url_for('main.dashboard_page'))

        set_access_cookies(response, access_token)

        return response
    
    return redirect(url_for('main.login_page'))