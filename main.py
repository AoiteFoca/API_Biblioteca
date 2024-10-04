from flask import render_template, Flask, request, redirect, url_for, session
from routes.db import init_db, close_db
from routes.users import users_bp
import logging
import os
from flask_dance.contrib.google import make_google_blueprint
from dotenv import load_dotenv


#-------------------------Inicio--------------------------#

#Cria a instancia do Flask
app = Flask(__name__,template_folder='templates')
app.config['SECRET_KEY'] = 'chavesecreta'
# Carrega as variáveis do arquivo .env
load_dotenv()
# Obtém o valor das variáveis do arquivo .env
client_id = os.getenv("ClientIdGoogle")
client_secret = os.getenv("ClientSecretGoogle")
app.secret_key = "Makolindo"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'
 
#----------------------Blueprints-----------------------#

app.register_blueprint(users_bp)

Blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    reprompt_consent=True,
    scope=["profile", "email"]
)

app.register_blueprint(Blueprint, url_prefix="/login")

#-------------------------Banco-------------------------#

app.teardown_appcontext(close_db)

#-------------------------Home--------------------------#

#Rota root
@app.route('/')
def home(): 
    return render_template('home.html')
 
 #-------------------------InitDB--------------------------#
 
#Rota que inicializa o banco de dados
@app.route('/initdb')
def initialize_db():
    init_db()
    return render_template('initdb.html')

#-------------------------Register--------------------------#

#Rota para acessar a página de cadastro
@app.route('/register')
def register(): 
    return render_template('register.html')

#-------------------------Login--------------------------#

#Rota para acessar a página de login
@app.route('/login')
def login(): 
    return render_template('login.html')

#-------------------------Perfil--------------------------#

#Rota para acessar a página do perfil do usuario
@app.route('/perfil')
def perfil(): 
    return render_template('perfil.html')

 #-------------------------Fim--------------------------#

#Inicializar o app Flask
if __name__ == '__main__':
    app.run(debug=True) #Roda o app em modo debug