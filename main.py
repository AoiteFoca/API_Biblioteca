from flask import render_template, Flask, request, redirect, url_for, session, flash
from routes.db import init_db, close_db
from routes.users import users_bp
import logging
import os
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from dotenv import load_dotenv
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


#-------------------------Inicio---------------------------#
load_dotenv()

# Cria a instância do Flask
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'chavesecreta'

# Obtém o valor das variáveis do arquivo .env
client_id_google = os.getenv("CLIENT_ID_GOOGLE")
client_secret_google = os.getenv("CLIENT_SECRET_GOOGLE")
client_id_github = os.getenv("CLIENT_ID_GITHUB")
client_secret_github = os.getenv("CLIENT_SECRET_GITHUB")

# Configurações de segurança
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'  # Permite o uso de http
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = '1'   # Permite o uso de escopos diferentes

app.secret_key = os.getenv("APP_SECRET_KEY") #Senha para os cookies de sessão

#Configuração do servidor de e-mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv("APP_EMAIL")
app.config['MAIL_PASSWORD'] = os.getenv("APP_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

#Serializador para gerar os tokens seguros
serial = URLSafeTimedSerializer(app.secret_key)

#----------------------Blueprints-----------------------#

# Blueprint de login via Google
google_blueprint = make_google_blueprint(
    client_id=client_id_google,
    client_secret=client_secret_google,
    reprompt_consent=True,
    scope=["profile", "email"]
)
app.register_blueprint(google_blueprint, url_prefix="/login")

# Blueprint de login via GitHub
github_blueprint = make_github_blueprint(
    client_id=client_id_github,
    client_secret=client_secret_github,
    scope="user"
)
app.register_blueprint(github_blueprint, url_prefix="/login")

# Registrar o blueprint de usuários
app.register_blueprint(users_bp)

#-------------------------Banco-------------------------#

app.teardown_appcontext(close_db)

#-------------------------Home--------------------------#

# Rota root
@app.route('/')
def home(): 
    google_data = None
    github_data = None
    user_info_endpoint = '/oauth2/v2/userinfo'

    if google.authorized:
        google_data = google.get(user_info_endpoint).json()
    if github.authorized:
        github_data = github.get("/user").json()

    return render_template('home.html', google_data=google_data, github_data=github_data)

#-------------------------InitDB--------------------------#

# Rota que inicializa o banco de dados
@app.route('/initdb')
def initialize_db():
    init_db()
    return render_template('initdb.html')

#-------------------------Register--------------------------#

# Rota para acessar a página de cadastro
@app.route('/register')
def register(): 
    return render_template('register.html')

#-------------------------Login--------------------------#

# Rota para acessar a página de login
@app.route('/login')
def login():
    provider = request.args.get('provider')
    if provider == 'google':
        return redirect(url_for('google.login'))
    elif provider == 'github':
        return redirect(url_for('github.login'))
    else:
        return render_template('login.html')  # Renderiza a página com a mensagem de erro

#-------------------------Perfil--------------------------#

# Rota para acessar a página do perfil do usuário
@app.route('/perfil')
def perfil(): 
    user_data = session.get('user')
    return render_template('perfil.html', google_data=user_data)

#-------------------------Perfil--------------------------#

@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']

        #Preparação e envio do e-mail
        token = serial.dumps(email, salt='password_recovery')
        msg = Message('Recuperação de senha', sender=os.getenv("APP_EMAIL"), recipients=[email])
        link = url_for('reset_password', token=token, _external=True)
        msg.body = f'Clique no link a seguir para redefinir sua senha: {link}'
        mail.send(msg)

        flash('Um link de recuperação de senha foi enviado para o seu e-mail.', category='success')

        return redirect(url_for('home'))
    
    return render_template('reset_password.html')

#Rota para redefinir a senha
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
        new_password = request.form['password']
        flash('Senha alterada com sucesso.', category='success')
        return redirect(url_for('home'))
    return render_template('reset.html')

#-------------------------Fim--------------------------#

# Inicializar o app Flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)
