import os
import requests
from flask import Flask, request, jsonify, session, g, redirect, url_for, \
     abort, render_template, flash
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length


'''
DATABASE = './tmp/flaskr.db'
DEBUG = False
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
'''


app = Flask(__name__)
app.config.from_object(__name__)
urlApi = "http://petshow-api.herokuapp.com"


#faltando teste e mensagens
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return '<h1>' + form.username.data + ' ' + form.password.data
    return render_template('produtos.html', form=form)

    if mensagem.erro:
            return render_template('login.html', mensagem=mensagem)
    elif mensagem.sucesso:
            return redirect(url_for("produtos"))
    return render_template('login.html')


#faltando mensagens
@app.route('/produtos', methods=["GET", 'POST'])
@app.route('/produtos/edit/<id>', methods=["POST"])
@app.route('/produtos/delete/<id>', methods=["GET"])
def produtos(id = None):
    if(id == None and request.method == "POST"):
        body = {
            "nome": request.form["nome"],
            "descricao": request.form["descricao"],
            "modelo": request.form["modelo"],
            "cod_barras": int(request.form["cod_barras"]),
            "porcentagem": float(request.form["porcentagem"]),
            "preco_custo": float(request.form["preco_custo"]),
            "preco_venda": float(request.form["preco_venda"]),
            "quantidade": int(request.form["quantidade"]),
            "foto": request.form["foto"],
            "marca_id": int(request.form["marca_id"]),
            "tamanho_id": int(request.form["tamanho_id"]),
            "animal_id": int(request.form["animal_id"] )
        }

        mensagem = cadastrar(urlApi + "/produtos/", body)

        return redirect(url_for("produtos"))
    elif(id != None and request.method == "GET"):
        mensagem = deletar(urlApi + "/produtos/" + id + "/remover/")

        return redirect(url_for("produtos"))
    elif(id != None):
        body = {
            "nome": request.form["nome"],
            "descricao": request.form["descricao"],
            "modelo": request.form["modelo"],
            "cod_barras": int(request.form["cod_barras"]),
            "porcentagem": float(request.form["porcentagem"]),
            "preco_custo": float(request.form["preco_custo"]),
            "preco_venda": float(request.form["preco_venda"]),
            "quantidade": int(request.form["quantidade"]),
            "foto": request.form["foto"],
            "marca_id": int(request.form["marca_id"]),
            "tamanho_id": int(request.form["tamanho_id"]),
            "animal_id": int(request.form["animal_id"] )
        }

        mensagem = editar(urlApi + "/produtos/" + id + "/alterar/", body)

        return redirect(url_for("produtos"))
    else:
        produtos = listar(urlApi + "/produtos/")

        produto = None
        if request.args.get("editar"):
            produto = [p for p in produtos if int(p["id"]) == int(request.args.get("editar"))][0]

        marcas = listar(urlApi + "/produtos/marcas/")
        tamanhos = listar(urlApi + "/produtos/tamanhos/")
        animais = listar(urlApi + "/produtos/animais/")

        return render_template('produtos.html', produtos=produtos, tamanhos=tamanhos, marcas=marcas, animais=animais, produto=produto)


@app.route('/produtos/buscar/<id>')
def buscar_produto(id):
    return redirect(url_for('produtos', editar=id))


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
        body = {
            "endereco": {
                "rua": request.form["rua"],
                "numero": request.form["numero"],
                "bairro": request.form["bairro"],
                "cep": request.form["cep"],
                "cidade": request.form["cidade"],
                "uf": request.form["uf"]
            },
            "nome": request.form["nome"],
            "email": request.form["email"],
            "cpf": request.form["cpf"],
            "telefones": {
                "telefone": request.form["telefone"]
            }
        }
        
        mensagem = cadastrar(urlApi + "/clientes", body)

        print(mensagem)
        print(body)

        return render_template('cadastro_cliente_pet.html')
    elif(id != None and request.method == "GET"):
        return render_template('cadastro_cliente_pet.html')
    elif(id != None):
        return render_template('cadastro_cliente_pet.html')
    else:
        return render_template('cadastro_cliente_pet.html')


def listar(url):
    return requests.get(url).json()

def deletar(url):
    return requests.delete(url).json()

def cadastrar(url, body):
    return requests.post(url, data = dumps(body), headers={'content-type': 'application/json'}).json()

def editar(url, body):
    return requests.put(url, data = dumps(body), headers={'content-type': 'application/json'}).json()


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=port, debug=True)
    app.run(host='localhost', port=5000, debug=True)
