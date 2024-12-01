from datetime import datetime
import sqlite3
import bcrypt
from flask import Blueprint, jsonify, render_template, request, url_for, redirect, flash, session
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
    users_is_admin = request.json.get('is_admin')
    
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
        cursor.execute("INSERT INTO users (email, senha, nome, is_admin) VALUES (?, ?, ?, ?)", (users_email, hashed_senha, users_nome, users_is_admin))
        db.commit()
        
        return jsonify({"message": "Usuario adicionado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": "Erro ao adicionar usuario", "details": str(e)}), 500

def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Número de registros por página
    offset = (page - 1) * per_page
    try:
        db = get_db()
        cursor = db.cursor()

        # Contar o total de registros
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        total_records = cursor.fetchone()['total']
        # Buscar registros da página atual
        cursor.execute("SELECT * FROM users LIMIT ? OFFSET ?", (per_page, offset))
        users = cursor.fetchall()
        # Calcular o número total de páginas
        total_pages = (total_records + per_page - 1) // per_page
        # Passar os dados para o template
        return render_template(
            "users.html", 
            dados=users,  # Corrigido para "dados"
            page=page, 
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": "Erro ao buscar usuario", "details": str(e)}), 500
    finally:
        db.close()

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

#------------Administrador------------#

@users_bp.route('/users/<int:user_id>/admin', methods=['PATCH', 'DELETE'])
def toggle_admin(user_id):
    """
    Promove um usuário a administrador ou remove o status de administrador.
    PATCH: Torna o usuário um administrador.
    DELETE: Remove o status de administrador do usuário.
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        db = get_db()
        cursor = db.cursor()

        # Buscar o usuário pelo ID
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'ID do usuário não encontrado'}), 404

        # Verificar o método da requisição
        if request.method == 'PATCH':  # Promover a administrador
            if user['is_admin'] == 1:
                return jsonify({'error': f'O usuário {user["nome"]} já é administrador.'}), 400
            cursor.execute('UPDATE users SET is_admin = 1, modified = ? WHERE id = ?', (now, user_id))
            db.commit()
            return jsonify({'message': f'O usuário {user["nome"]} agora é administrador.'}), 200

        elif request.method == 'DELETE':  # Remover status de administrador
            if user['is_admin'] == 0:
                return jsonify({'error': f'O usuário {user["nome"]} já é um usuário padrão.'}), 400
            cursor.execute('UPDATE users SET is_admin = 0, modified = ? WHERE id = ?', (now, user_id))
            db.commit()
            return jsonify({'message': f'O status de administrador foi removido do usuário {user["nome"]}.'}), 200

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
            if user[4] == 0:  # status do usuário
                flash(f'Usuário bloqueado!', 'error')
                return redirect(url_for('login'))
            if bcrypt.checkpw(senha.encode('utf-8'), user[2]):  # senha correta
                flash(f'Usuário logado!', 'success')
                # Armazenando informações do usuário na sessão
                session['user'] = {
                    'id': user[0],  # ID do usuário
                    'email': user[1],  # Email do usuário
                    'is_admin': user[4],  # Verifica se é admin
                    'nome': user[5]  # Nome do usuário (ajuste conforme sua tabela)
                }
                return redirect(url_for('home'))
            else:
                flash(f'Senha incorreta!', 'error')
                return redirect(url_for('login'))
        else:
            flash(f'Usuário não encontrado!', 'error')
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
    is_admin = request.form.get('is_admin', '0')  # Valor padrão é '0' (não administrador)

    # Validações básicas
    if not email or not senha or not nome:
        flash(f'Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('register'))
    if not validar_email(email):
        flash(f'Email deve ser um e-mail válido!', 'error')
        return redirect(url_for('register'))
    if is_admin not in ['0', '1']:
        flash(f'Valor inválido para o campo de administrador!', 'error')
        return redirect(url_for('register'))

    try:
        db = get_db()
        cursor = db.cursor()

        # Verificar se o e-mail já existe
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user:
            flash(f'E-mail já cadastrado!', 'error')
            return redirect(url_for('register'))

        # Hash da senha e inserção do usuário
        hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            'INSERT INTO users (email, senha, nome, is_admin) VALUES (?, ?, ?, ?)',
            (email, hashed_senha, nome, int(is_admin))
        )
        db.commit()
        flash(f'Usuário {nome} cadastrado com sucesso!', 'success')
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