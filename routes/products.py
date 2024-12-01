from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from routes.db import get_db
import sqlite3

products_bp = Blueprint('products', __name__, template_folder='templates')

@products_bp.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        return add_product()
    else:
        return get_products()

def add_product():
    nome = request.form['nome']
    descricao = request.form['descricao']
    preco = request.form['preco']
    quantidade = request.form['quantidade']

    # Validações básicas
    if not nome or not descricao or not preco or not quantidade:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('products.manage_products'))

    try:
        db = get_db()
        cursor = db.cursor()

        # Inserção do produto
        cursor.execute(
            'INSERT INTO products (nome, descricao, preco, quantidade) VALUES (?, ?, ?, ?)',
            (nome, descricao, float(preco), int(quantidade))
        )
        db.commit()
        flash(f'Produto "{nome}" cadastrado com sucesso!', 'success')
        return redirect(url_for('products.manage_products'))
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

def get_products():
    page = request.args.get('page', 1, type=int)  # Página atual, valor padrão 1
    per_page = 3  # Número de registros por página
    offset = (page - 1) * per_page  # Calculando o offset com base na página

    try:
        db = get_db()
        cursor = db.cursor()
        # Contar o total de registros (produtos)
        cursor.execute("SELECT COUNT(*) AS total FROM products")
        total_records = cursor.fetchone()['total']
        # Buscar registros da página atual
        cursor.execute("SELECT * FROM products LIMIT ? OFFSET ?", (per_page, offset))
        products = cursor.fetchall()
        # Calcular o número total de páginas
        total_pages = (total_records + per_page - 1) // per_page
        # Passar os dados para o template
        return render_template(
            "products.html", 
            products=products,
            page=page,  
            total_pages=total_pages  
        )
    except Exception as e:
        return jsonify({"error": "Erro ao buscar produtos", "details": str(e)}), 500
    finally:
        db.close()


@products_bp.route('/register_product', methods=['GET', 'POST'])
def register_product():
    if request.method == 'POST':
        # Obtendo dados do formulário
        product_name = request.form.get('product_name')
        product_price = request.form.get('product_price')

        if not product_name or not product_price:
            flash('Preencha todos os campos!', 'error')
            return redirect(url_for('products.register_product'))

        try:
            # Inserindo o produto no banco
            db = get_db()
            db.execute("INSERT INTO products (name, price) VALUES (?, ?)", (product_name, product_price))
            db.commit()
            flash('Produto cadastrado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao cadastrar o produto: {e}', 'error')

        return redirect(url_for('products.list_products'))

    return render_template('register_product.html')