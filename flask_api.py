# pip freeze > requeriments.txt
import os
from flask import Flask, request, jsonify, session, g, redirect, url_for, \
     abort, render_template, flash
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import requests
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_cors import CORS

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
app.config['SECRET_KEY'] = 'default'
app.config.from_object(__name__)
urlApi = "http://petshow-api.herokuapp.com"
Bootstrap(app)
CORS(app)


class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Senha', validators=[InputRequired(), Length(min=4, max=15)])
    remember = BooleanField('Me mantenha conectado')


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return '<h1>' + form.username.data + ' ' + form.password.data
    return render_template('produtos.html', form=form)


# Se entrar nessa rota, sem ID, por formulário, ele irá cadastrar
@app.route('/produtos', methods=["GET", 'POST'])
# Ao enviar um ID, pelo formulário, existente, fazemos o editar. Buscamos e editamos.
@app.route('/produtos/edit/<id>', methods=["POST"])
@app.route('/produtos/delete/<id>', methods=["GET"])
def produtos(id = None):
    if(id == None and request.method == "POST"):
        body = {
            "nome": request.form["nome"],
            "descricao": request.form["descricao"],
            "foto": request.form["foto"],
            "preco_custo": float(request.form["preco_custo"]),
            "preco_venda": float(request.form["preco_venda"]),
            "modelo": request.form["modelo"],
            "cod_barras": int(request.form["cod_barras"]),
            "porcentagem": float(request.form["porcentagem"]),
            "quantidade": int(request.form["quantidade"]),
            "tamanho_id": int(request.form["tamanho_id"]),
            "marca_id": int(request.form["marca_id"]),
            "animal_id": int(request.form["animal_id"] )
        }

        notificacao = cadastrar(urlApi + "/produtos/", body)

        print(notificacao)

        return redirect(url_for("produtos"))
    elif(id != None and request.method == "GET"):
        notificacao = deletar(urlApi + "/produtos/" + id + "/remover/")
        return redirect(url_for("produtos"))
    elif(id != None):
        produtos = "Editar um produto"
        # @redirect("/produtos")
        return render_template('produtos.html', produtos=produtos)
    else:
        tamanhos = listar(urlApi + "/produtos/tamanhos/")
        marcas = listar(urlApi + "/produtos/marcas/")
        animais = listar(urlApi + "/produtos/animais/")
        return render_template('produtos.html', produtos=listar(urlApi + "/produtos/"), tamanhos=tamanhos, marcas=marcas, animais=animais)


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
        return render_template('pedido.html', msg=msg)


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


'''
otolifi - 07/04/2021
Falta colocar flash messages nos templates para receber as respostas de sucesso ou erro da API
Falta popup preventivo pra remoção de registro de usuário: "Você tem certeza que quer apagar os dados?"
Falta restringir o acesso dos usuários a alteração de senha e alteração de tipo de usuário. Ex:
    só gerentes podem alterar tipo de usuário
    só usuário logado só pode alterar a própria senha
'''

@app.route('/usuarios/', methods=["GET", "POST"])
def usuarios():
    if request.method == "POST":
        body = {
            "nome": request.form["nome"],
            "login": request.form["login"],
            "senha": request.form["senha"],
            "tipo": request.form["tipo"]
        }
        notificacao = cadastrar(urlApi + "/usuarios/novo", body)
        msg = "Cadastrado com sucesso"
        return redirect(url_for("usuarios"))
    else:
        usuarios = listar(urlApi + '/usuarios/')
        print(usuarios)
        msg = "Usuarios"
        return render_template('lista_usuarios.html', msg=msg, usuarios=usuarios)

@app.route('/usuarios/new/', methods=["GET"])
def cadastrar_usuario():
    msg = "Cadastrar um usuario"
    return render_template('cadastro_usuario.html', msg=msg)

@app.route('/usuarios/edit/<login>/', methods=["GET", "POST"])
def alterar_usuario(login):
    if request.method == "POST":
        msg = "Alterar um usuario"
        return redirect(url_for("usuarios"))
    else:
        msg = "Editar um usuario"
        usuarios = listar(urlApi + '/usuarios/')
        for x in usuarios:
            if x['login'] == login:
                usuario = x
        return render_template('cadastro_usuario.html', msg=msg, usuario=usuario)

@app.route('/usuarios/senha/<login>/', methods=["GET", "POST"])
def alterar_senha(login):
    if request.method == 'GET':
        msg = "Editar senha"
        usuarios = listar(urlApi + '/usuarios/')
        for x in usuarios:
            if x['login'] == login:
                usuario = x
        return render_template('cadastro_usuario.html', msg=msg, usuario=usuario, tipo='senha')
    elif request.method == 'POST':
        body = {
            "login": request.form["login"],
            "senha": request.form["senha"]
        }
        notificacao = alterar_parte(urlApi + "/usuarios/alterarsenha", body)
        msg = "Alterada com sucesso"
        return redirect(url_for("usuarios"))

@app.route('/usuarios/tipo/<login>/', methods=["GET", "POST"])
def alterar_tipo(login):
    if request.method == 'GET':
        msg = "Editar senha"
        usuarios = listar(urlApi + '/usuarios/')
        for x in usuarios:
            if x['login'] == login:
                usuario = x
        return render_template('cadastro_usuario.html', msg=msg, usuario=usuario, tipo='tipo')
    elif request.method == 'POST':
        body = {
            "login": request.form["login"],
            "tipo": request.form["tipo"]
        }
        notificacao = alterar_parte(urlApi + "/usuarios/alterartipo", body)
        msg = "Alterado com sucesso"
        return redirect(url_for("usuarios"))


@app.route('/usuarios/delete/<login>/', methods=["POST"])
def remover_usuario(login):
    req = requests.delete(urlApi + '/usuarios/' + login + '/remover')
    msg = req.json()
    print(msg)
    return redirect(url_for("usuarios"))




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

def listar(url):
    return requests.get(url).json()

def deletar(url):
    return requests.delete(url).json()

def cadastrar(url, body):
    return requests.post(url, data=dumps(body), headers={'content-type': 'application/json'})

def alterar_parte(url, body):
    return requests.patch(url, data=dumps(body), headers={'content-type': 'application/json'})

def alterar_todo(url, body):
    return requests.put(url, data=dumps(body), headers={'content-type': 'application/json'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=port, debug=True)
    app.run(host='localhost', port=5000, debug=True)
