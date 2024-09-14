from flask import render_template
from flask import Flask, request, jsonify
from db import init_db, close_db
from routes.users import users_bp

#-------------------------Inicio--------------------------#

#Cria a instancia do Flask
app = Flask(__name__,template_folder='templates')
 
#----------------------Blueprints-----------------------#

app.register_blueprint(users_bp)

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
    return "<marquee><h1 style=\"background-image: linear-gradient(to left, violet, indigo, blue, green, yellow, orange, red)\">Banco de dados inicializado com sucesso!</h1></marquee>"

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