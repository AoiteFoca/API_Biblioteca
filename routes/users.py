from flask import Blueprint, jsonify, render_template, request
import re
from db import get_db

users_bp = Blueprint('users', __name__)

#--------------ValidarEmail--------------#

def validar_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

#----------------Usuarios----------------#

@users_bp.route('/users', methods=['POST', 'GET'])
def manage_users():
    if request.method == 'POST':
        return add_users()
    elif request.method == 'GET':
        return get_users()

def add_users():
    users_email = request.json.get('email')
    users_senha = request.json.get('senha')
    users_nome = request.json.get('nomeCompleto')
    
    if not users_email or not users_senha or not users_nome:
        return jsonify({"error": "As informacoes necessarias nao foram informadas"}), 400
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (email, senha, nomeCompleto) VALUES (?, ?, ?)", (users_email, users_senha, users_nome))
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
    nomeCompleto = request.json.get("nome_completo")
    status = request.json.get("status")


    if not email:
        return jsonify({'error': 'email e obrigatorio'})
    if not senha:
        return jsonify({'error': 'senha e obrigatoria'})
    if not nomeCompleto:
        return jsonify({'error': 'nome_completo e obrigatorio'})
    if not validar_email(email):
        return jsonify({'error': 'email deve ser um e-mail valido'})

def activate_user(user_id):
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
                cursor.execute('UPDATE users set email = ?, senha = ?, nome_completo = ?, status = ?, modified = ? WHERE id = ?', (email, hashed_senha, nomeCompleto, status, now, user_id,))
                db.commit()
                return jsonify({'message': 'Dados alterados com sucesso!'}), 200
        else:
            return jsonify({'error': 'ID nao encontrado'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

def delete_user(user_id):
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