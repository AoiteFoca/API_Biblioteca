#Configuração do banco de dados sqlite3
import sqlite3
from flask import current_app, g

DATABASE = 'database.db'
 
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db
 
def init_db():
    with current_app.app_context():
        db = get_db()
        with current_app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()