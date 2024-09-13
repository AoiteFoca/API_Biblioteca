from flask import request
from flask import render_template
from flask import Flask, request, jsonify; # type: ignore
import sqlite3;

#Cria a instancia do Flask
app = Flask(__name__,template_folder='templates')
 
#Configuração do banco de dados sqlite3
DATABASE = 'database.db'
 
def get_db():
    db = sqlite3.connect(DATABASE) #Driver sqlite3 conecta no banco de dados
    db.row_factory = sqlite3.Row #As linhas que o sqlite encontrar, ele retorna
    return db #Retorna db
 
#Cria a tabela de dados caso ainda não exista
def init_db():
    with app.app_context(): #Pega o contexto da aplicação (flask)
        db = get_db() #Conecta no banco de dados
        with app.open_resource('schema.sql', mode='r') as f: #abro o schema em modo leitura como 'f'
            db.cursor().executescript(f.read()) #O executor do banco de dados executa o script do schema (f)
        db.commit() #Comita as alterações no db

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

#-------------------------Final--------------------------#

#Inicializar o app Flask
if __name__ == '__main__':
    app.run(debug=True) #Roda o app em modo debug