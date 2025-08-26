import click
from app.core.extensions import db
from app.models import User

def register_cli_commands(app):
    @app.cli.command('create-user')
    @click.argument('email')
    @click.argument('password')
    def create_user(email, password):
        if User.query.filter_by(email=email).first():
            click.echo(f"-> Usuário com email '{email}' já existe.")
            return
        
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        click.echo(f"-> Usuário '{email}' criado com sucesso.")