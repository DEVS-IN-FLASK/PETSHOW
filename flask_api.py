# pip freeze > requeriments.txt
import os
from flask import Flask, request, jsonify, session, g, redirect, url_for, \
     abort, render_template, flash
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps


# configuração

'''
DATABASE = './tmp/flaskr.db'
DEBUG = False
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
'''

# criar nossa pequena aplicação :)
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['usuario'] != 'admin' or request.form['senha'] != 'admin':
            error = 'Credenciais inválidas. Por favor, digite novamente seu usuário e senha e tente mais uma vez.'
        else:
            return redirect(url_for('estoque'))
    msg1 = 'Bem vindo(a) ao PETSHOW!'
    msg2 = "Faça seu login aqui"
    return render_template('login.html', error=error, msg1=msg1, msg2=msg2)


@app.route('/estoque', methods=['GET'])
@app.route('/estoque/<nome>', methods=['GET'])
def estoque(nome = None):
    if(nome != None):
        msg = nome
        return render_template('estoque.html', msg=msg)
    msg = "Estoque"
    return render_template('estoque.html', msg=msg)


# Se entrar nessa rota, sem ID, por formulário, ele irá cadastrar
@app.route('/produtos', methods=["GET", 'POST'])
# Ao enviar um ID, pelo formulário, existente, fazemos o editar. Buscamos e editamos.
@app.route('/produtos/edit/<id>', methods=["POST"])
@app.route('/produtos/delete/<id>', methods=["GET"])
def produtos(id = None):
    if(id == None and request.method == "POST"):
        msg = "Cadastrar um produto"
        return render_template('produtos.html', msg=msg)
    elif(id != None and request.method == "GET"):
        msg = "Deletar um produto"
        # @redirect("/produtos")
        return render_template('produtos.html', msg=msg)
    elif(id != None):
        msg = "Editar um produto"
        # @redirect("/produtos")
        return render_template('produtos.html', msg=msg)
    else:
        msg = "Produtos"
        return render_template('produtos.html', msg=msg)


# Recebe o id, busca no banco, renderiza na página em questão. No HTML, fazemos a lógica para mostrar no formulário.
@app.route('/produtos/buscar/<id>')
def buscar_produto(id):
    msg = "Produto por id"
    return render_template('produtos.html', msg=msg)


@app.route('/pedidos', methods=["GET", 'POST'])
@app.route('/pedidos/edit/<id>', methods=["POST"])
@app.route('/pedidos/delete/<id>', methods=["GET"])
def pedidos(id = None):
    if(id == None and request.method == "POST"):
        msg = "Cadastrar um pedido"
        return render_template('pedidos.html', msg=msg)
    elif(id != None and request.method == "GET"):
        msg = "Deletar um pedido"
        # @redirect("/pedidos")
        return render_template('pedidos.html', msg=msg)
    elif(id != None):
        msg = "Editar um pedido"
        # @redirect("/pedidos")
        return render_template('pedidos.html', msg=msg)
    else:
        msg = "Pedidos"
        return render_template('pedidos.html', msg=msg)


@app.route('/vendas', methods=["GET", 'POST'])
@app.route('/vendas/edit/<id>', methods=["POST"])
@app.route('/vendas/delete/<id>', methods=["GET"])
def vendas(id = None):
    if(id == None and request.method == "POST"):
        msg = "Cadastrar uma venda"
        return render_template('vendas.html', msg=msg)
    elif(id != None and request.method == "GET"):
        msg = "Deletar uma venda"
        # @redirect("/vendas")
        return render_template('vendas.html', msg=msg)
    elif(id != None):
        msg = "Editar uma venda"
        # @redirect("/vendas")
        return render_template('vendas.html', msg=msg)
    else:
        msg = "Vendas"
        return render_template('vendas.html', msg=msg)


@app.route('/usuarios', methods=["GET", 'POST'])
@app.route('/usuarios/edit/<id>', methods=["POST"])
@app.route('/usuarios/delete/<id>', methods=["GET"])
def usuarios(id = None):
    if(id == None and request.method == "POST"):
        msg = "Cadastrar um usuario"
        return render_template('usuarios.html', msg=msg)
    elif(id != None and request.method == "GET"):
        msg = "Deletar um usuario"
        # @redirect("/usuarios")
        return render_template('usuarios.html', msg=msg)
    elif(id != None):
        msg = "Editar um usuario"
        # @redirect("/usuarios")
        return render_template('usuarios.html', msg=msg)
    else:
        msg = "Usuarios"
        return render_template('usuarios.html', msg=msg)


@app.route('/clientes-pet', methods=["GET", 'POST'])
@app.route('/clientes-pet/edit/<id>', methods=["POST"])
@app.route('/clientes-pet/delete/<id>', methods=["GET"])
def clientes(id = None):
    if(id == None and request.method == "POST"):
        msg = "Cadastrar um cliente"
        return render_template('cadastro_cliente_pet.html', msg=msg)
    elif(id != None and request.method == "GET"):
        msg = "Deletar um cliente"
        return render_template('cadastro_cliente_pet.html', msg=msg)
    elif(id != None):
        msg = "Editar um cliente"
        return render_template('cadastro_cliente_pet.html', msg=msg)
    else:
        msg = "Clientes"
        return render_template('cadastro_cliente_pet.html', msg=msg)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(host='localhost', port=5000, debug=True)
