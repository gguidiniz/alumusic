from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.models import User
from app.schemas import AuthLoginSchema, TokenSchema
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    json_data = request.get_json()
    if not json_data:
        return jsonify({ "msg": "Corpo da requisição JSON ausente"}), 400
    
    try:
        login_data = AuthLoginSchema.model_validate(json_data)

        user = User.query.filter_by(email=login_data.email).first()

        if user and user.check_password(login_data.password):
            access_token = create_access_token(identity=str(user.id))

            token_response = TokenSchema(access_token=access_token)
            return token_response.model_dump(), 200
        
        return jsonify({"msg": "Credenciais inválidas"}), 401
    
    except ValidationError as e:
        return jsonify({"erro": "Dados de entrada inválidos", "detalhes": e.errors()}), 422