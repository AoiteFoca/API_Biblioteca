from flask import render_template, Flask, request, redirect, url_for, session, flash
from routes.db import init_db, close_db
from routes.users import users_bp, get_user_by_email
import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash
from models import db, User

# Carregar variáveis de ambiente e configurar o app
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.getenv("APP_SECRET_KEY")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv("APP_EMAIL")
app.config['MAIL_PASSWORD'] = os.getenv("APP_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
serial = URLSafeTimedSerializer(app.config['SECRET_KEY'])

app.register_blueprint(users_bp)
app.teardown_appcontext(close_db)

# Função de recuperação de senha
@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']

        # Verifica se o e-mail existe no banco de dados
        user = get_user_by_email(email)
        if user is None:
            flash('E-mail não encontrado.', category='error')
            return redirect(url_for('reset_password'))

        # Preparação e envio do e-mail com link de recuperação
        token = serial.dumps(email, salt='password_recovery')
        msg = Message('Recuperação de senha', sender=os.getenv("APP_EMAIL"), recipients=[email])
        link = url_for('reset_password_token', token=token, _external=True)
        msg.body = f'Clique no link a seguir para redefinir sua senha: {link}'
        mail.send(msg)

        flash('Um link de recuperação de senha foi enviado para o seu e-mail.', category='success')
        return redirect(url_for('home'))

    return render_template('reset_password.html')

# Rota para redefinir a senha com token
@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password_token(token):
    try:
        email = serial.loads(token, salt='password_recovery', max_age=3600)
    except SignatureExpired:
        flash('O link de recuperação de senha expirou.', category='error')
        return redirect(url_for('reset_password'))
    except BadSignature:
        flash('Link inválido.', category='error')
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        new_password = request.form['senha']

        # Verifica se o e-mail existe no banco de dados
        user = get_user_by_email(email)
        if user is None:
            flash('As informações necessárias não foram encontradas.', category='error')
            return redirect(url_for('reset_password'))

        # Atualiza a senha no banco de dados
        user.senha = generate_password_hash(new_password)
        db.session.commit()

        flash('Senha alterada com sucesso.', category='success')
        return redirect(url_for('home'))
    
    return render_template('reset.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)