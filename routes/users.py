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
        return jsonify({"error": "As informações necessárias não foram informadas"}), 400
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (email, senha, nomeCompleto) VALUES (?, ?, ?)", (users_email, users_senha, users_nome))
        db.commit()
        return jsonify({"message": "Usuário adicionado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": "Erro ao adicionar usuário", "details": str(e)}), 500

def get_users():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return render_template('users.html', dados=users)
    except Exception as e:
        return jsonify({"error": "Erro ao buscar usuário", "details": str(e)}), 500

# @app.route('/artistas/<int:id>', methods=['GET', 'PUT', 'DELETE'])
# def handle_artista(id):
#     if request.method == 'GET':
#         return get_artista(id)
#     elif request.method == 'PUT':
#         return update_artista(id)
#     elif request.method == 'DELETE':
#         return delete_artista(id)

# def get_artista(id):
#     try:
#         db = get_db()
#         cursor = db.cursor()
#         cursor.execute("SELECT * FROM artistas WHERE id = ?", (id,))
#         artista = cursor.fetchone()
#         if not artista:
#             return jsonify({"error": "Artista não encontrado: ID não encontrado"}), 404
#         return jsonify(dict(artista)), 200
#     except Exception as e:
#         return jsonify({"error": "Erro ao buscar artista", "details": str(e)}), 500

# def update_artista(id):
#     data = request.json
#     artista_nome = data.get('nome')
#     gravadoras_id = data.get('gravadoras_id')
#     if not artista_nome or not gravadoras_id:
#         return jsonify({"error": "Nome do artista ou id da gravadora não informados"}), 400
#     try:
#         db = get_db()
#         cursor = db.cursor()
#         cursor.execute("UPDATE artistas SET nome = ?, gravadoras_id = ? WHERE id = ?", (artista_nome, gravadoras_id, id))
#         db.commit()
#         return jsonify({"message": "Artista atualizado com sucesso"}), 200
#     except Exception as e:
#         return jsonify({"error": "Erro ao atualizar artista", "details": str(e)}), 500

# def delete_artista(id):
#     try:
#         db = get_db()
#         cursor = db.cursor()
#         cursor.execute("DELETE FROM artistas WHERE id = ?", (id,))
#         db.commit()
#         return jsonify({"message": "Artista deletado com sucesso"}), 200
#     except Exception as e:
#         return jsonify({"error": "Erro ao deletar artista", "details": str(e)}), 500
