from datetime import datetime
import sqlite3
import bcrypt
from flask import Blueprint, jsonify, render_template, request, url_for, redirect, flash
import re
from routes.db import get_db

users_bp = Blueprint('users', __name__)

#--------------ValidarEmail--------------#

def validar_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

#-------------CRUD---Usuarios------------#

@users_bp.route('/users', methods=['POST', 'GET'])
def manage_users():
    if request.method == 'POST':
        return add_users()
    elif request.method == 'GET':
        return get_users()

def add_users():
    users_email = request.json.get('email')
    users_senha = request.json.get('senha')
    users_nome = request.json.get('nome')
    
    if not users_email or not users_senha or not users_nome:
        return jsonify({"error": "As informacoes necessarias nao foram informadas"}), 400
    if not validar_email(users_email):
        return jsonify({'error': 'email deve ser um e-mail valido'})
    
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (users_email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"error": "Email ja cadastrado"}), 409
        hashed_senha = bcrypt.hashpw(users_senha.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (email, senha, nome) VALUES (?, ?, ?)", (users_email, hashed_senha, users_nome))
        db.commit()
        
        return jsonify({"message": "Usuario adicionado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": "Erro ao adicionar usuario", "details": str(e)}), 500

def get_users():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return render_template('users.html', dados=users)
    except Exception as e:
        return jsonify({"error": "Erro ao buscar usuario", "details": str(e)}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])

def handle_usuario (user_id):
    if request.method == 'GET':
        return get_user(user_id)
    elif request.method == 'PUT':
        return update_user(user_id)
    elif request.method == 'PATCH':
        return activate_user(user_id)
    elif request.method == 'DELETE':
        return delete_user(user_id)

def get_user(user_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT *, CASE WHEN status = 1 THEN \'Ativo\' WHEN status = 0 THEN \'Bloqueado\' END AS status_label FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if user: 
            return render_template("users.html", id = user)
        else:
            return jsonify({'error': 'ID nao encontrado'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

def update_user(user_id):
    email = request.json.get('email')
    senha = request.json.get('senha')
    nome = request.json.get('nome')
    status = request.json.get('status')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not email:
        return jsonify({'error': 'email e obrigatorio'})
    if not senha:
        return jsonify({'error': 'senha e obrigatoria'})
    if not nome:
        return jsonify({'error': 'nome e obrigatorio'})
    if not validar_email(email):
        return jsonify({'error': 'email deve ser um e-mail valido'})
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        id = cursor.fetchone()
        if id:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            ver_email = cursor.fetchone()
            if ver_email: 
                return jsonify({'error': 'email ja existe'})
            else:
                hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
                cursor.execute('UPDATE users set email = ?, senha = ?, nome = ?, status = ?, modified = ? WHERE id = ?', (email, hashed_senha, nome, status, now, user_id,))
                db.commit()
                return jsonify({'message': 'Dados alterados com sucesso!'}), 200
        else:
            return jsonify({'error': 'ID nao encontrado'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

def activate_user(user_id):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if user: 
            cursor.execute('UPDATE users set status = 1, modified = ? WHERE id = ?', (now,user_id,))
            db.commit()
            return jsonify({'message': 'Usuario ativado!'})
        else:
            return jsonify({'error': 'ID nao encontrado'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

def delete_user(user_id):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if user: 
            cursor.execute('UPDATE users set status = 0, modified = ? WHERE id = ?', (now, user_id,))
            db.commit()
            return jsonify({'message': 'Usuario bloqueado!'})
        else:
            return jsonify({'error': 'ID nao encontrado'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

#--------------LogarUser--------------#

@users_bp.route('/logins', methods=['POST'])
def manage_login():
    if request.method == 'POST':
        return login()

def login():
    email = request.form['email']
    senha = request.form['senha']
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user is not None:
            if user[4] == 0:
                flash(f'Usuario bloqueado!', 'error')
                return redirect(url_for('login'))
            if bcrypt.checkpw(senha.encode('utf-8'), user[2]):
                flash(f'Usuario logado!', 'success')
                return redirect(url_for('home'))
            else:
                flash(f'Senha incorreta!', 'error')
                return redirect(url_for('login'))
        else:
            flash(f'Usuario nao encontrado!', 'error')
            return redirect(url_for('login'))
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

#--------------RegistrarUser--------------#

@users_bp.route('/registers', methods=['POST'])
def manage_register():
    if request.method == 'POST':
        return register()

def register():
    email = request.form['email']
    senha = request.form['senha']
    nome = request.form['nome']
    if not email or not senha or not nome:
        flash(f'Todos os campos sao obrigatorios!', 'error')
        return redirect(url_for('register'))
    if not validar_email(email):
        flash(f'Email deve ser um e-mail valido!', 'error')
        return redirect(url_for('register'))
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user:
            flash(f'Email ja cadastrado!', 'error')
            return redirect(url_for('register'))
        hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('INSERT INTO users (email, senha, nome) VALUES (?, ?, ?)', (email, hashed_senha, nome))
        db.commit()
        flash(f'Usuario {nome} cadastrado!', 'success')
        return redirect(url_for('home'))
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@users_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        if not nome or not senha:
            flash('Preencha todos os campos!', 'error')
            return redirect(url_for('users.edit_user', id=id))
        try:
            db = get_db()
            cursor = db.cursor()
            # Verifica se o usuário existe
            cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
            user = cursor.fetchone()
            if user is None:
                flash('Usuário não encontrado!', 'error')
                return redirect(url_for('users'))
            hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('UPDATE users SET nome = ?, senha = ?, modified = ? WHERE id = ?', (nome, hashed_senha, now, id))
            db.commit()
            flash('Usuário atualizado', 'success')
            return redirect(url_for('home'))
        except sqlite3.Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            db.close()
    else:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
        user = cursor.fetchone()
        if user is None:
            flash('Usuário não encontrado!', 'error')
            return redirect(url_for('users'))
        return render_template('edit.html', dados=user)