from flask import render_template
from flask import Flask
from routes.db import init_db, close_db
from routes.users import users_bp

#-------------------------Inicio--------------------------#

#Cria a instancia do Flask
app = Flask(__name__,template_folder='templates')
app.config['SECRET_KEY'] = 'chavesecreta'
 
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