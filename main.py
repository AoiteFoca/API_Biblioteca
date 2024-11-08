from flask import render_template, Flask, request, redirect, url_for, session, flash
from routes.db import init_db, close_db, get_db
from routes.users import users_bp, update_user
import logging
import os
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from dotenv import load_dotenv
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import bcrypt

#-------------------------Inicio---------------------------#
load_dotenv()

# Cria a instância do Flask
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Obtém o valor das variáveis do arquivo .env
client_id_google = os.getenv("CLIENT_ID_GOOGLE")
client_secret_google = os.getenv("CLIENT_SECRET_GOOGLE")
client_id_github = os.getenv("CLIENT_ID_GITHUB")
client_secret_github = os.getenv("CLIENT_SECRET_GITHUB")

# Configurações de segurança
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = '1'

app.secret_key = os.getenv("APP_SECRET_KEY") 

# Configuração do servidor de e-mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv("APP_EMAIL")
app.config['MAIL_PASSWORD'] = os.getenv("APP_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
serial = URLSafeTimedSerializer(app.secret_key)

#----------------------Blueprints-----------------------#

google_blueprint = make_google_blueprint(
    client_id=client_id_google,
    client_secret=client_secret_google,
    reprompt_consent=True,
    scope=["profile", "email"]
)
app.register_blueprint(google_blueprint, url_prefix="/login")

github_blueprint = make_github_blueprint(
    client_id=client_id_github,
    client_secret=client_secret_github,
    scope="user"
)
app.register_blueprint(github_blueprint, url_prefix="/login")

app.register_blueprint(users_bp)

#-------------------------Banco-------------------------#

app.teardown_appcontext(close_db)

#-------------------------Home--------------------------#

@app.route('/')
def home(): 
    return render_template('home.html')

#-------------------------InitDB--------------------------#

@app.route('/initdb')
def initialize_db():
    init_db()
    return render_template('initdb.html')

#-------------------------Register--------------------------#

@app.route('/register')
def register(): 
    return render_template('register.html')

#-------------------------Login--------------------------#

@app.route('/login')
def login():
    provider = request.args.get('provider')
    if provider == 'google':
        return redirect(url_for('google.login'))
    elif provider == 'github':
        return redirect(url_for('github.login'))
    else:
        return render_template('login.html')

#-------------------------Admin--------------------------#

@app.route('/admin')
def admin():
    if not is_admin():
        return "Você não possui permissão de administrador. Feche a página agora mesmo ou sofra as consequencias...", 403
    return render_template('admin.html')

def is_admin():
    user = session.get('user')
    return user and user.get("is_admin", 0)

#-------------------------Perfil--------------------------#

@app.route('/perfil')
def perfil(): 
    google_data = None
    github_data = None
    user_info_endpoint = '/oauth2/v2/userinfo'

    if google.authorized:
        google_data = google.get(user_info_endpoint).json()
    if github.authorized:
        github_data = github.get("/user").json()
    return render_template('perfil.html', google_data=google_data, github_data=github_data, fetch_url=google.base_url + user_info_endpoint)

#-------------------------Recuperação de Senha--------------------------#

@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Verifica se o e-mail existe no banco de dados
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        
        if not user:
            flash('Falha: o e-mail não existe no sistema.', category='error')
            return redirect(url_for('login'))
        
        # Preparação e envio do e-mail de recuperação
        token = serial.dumps(email, salt='password_recovery')
        msg = Message('Recuperar senha', sender=os.getenv("APP_EMAIL"), recipients=[email])
        link = url_for('reset_password_token', token=token, _external=True)
        msg.body = f'Clique no link a seguir para redefinir sua senha: {link}'
        mail.send(msg)

        flash('Um link de recuperação de senha foi enviado para o seu e-mail.', category='success')
        return redirect(url_for('home'))
    
    return render_template('reset_password.html')

@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password_token(token):
    try:
        email = serial.loads(token, salt='password_recovery', max_age=3600)  # 1 hora de validade
    except SignatureExpired:
        flash('O link de recuperação de senha expirou.', category='error')
        return redirect(url_for('reset_password'))
    except BadSignature:
        flash('Link inválido.', category='error')
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        # Nova senha pode ser fornecida pelo usuário
        new_password = request.form.get('password', 'nova_senha_padrao')  # Opção de senha fornecida pelo usuário
        # Encripta a nova senha antes de atualizar no banco
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        # Atualiza a senha no banco utilizando o email
        db = get_db()
        try:
            db.execute("UPDATE users SET senha = ?, modified = DATETIME(CURRENT_TIMESTAMP, '-3 hours') WHERE email = ?", (hashed_password, email))
            db.commit()
            flash('Senha alterada com sucesso.', category='success')
            return redirect(url_for('home')) 
        except Exception as e:
            print(f'Erro ao alterar a senha: {e}')
            flash('Erro ao alterar a senha. Tente novamente.', category='error')
            return redirect(url_for('reset_password'))

    return render_template('reset.html', token=token)

#-------------------------Fim--------------------------#

# Inicializar o app Flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)
