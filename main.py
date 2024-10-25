from flask import render_template, Flask, request, redirect, url_for, session
from routes.db import init_db, close_db
from routes.users import users_bp
import logging
import os
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from dotenv import load_dotenv


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

#-------------------------Fim--------------------------#

# Inicializar o app Flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)
