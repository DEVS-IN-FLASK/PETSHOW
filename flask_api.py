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
from flask_cors import CORS


'''
DATABASE = './tmp/flaskr.db'
DEBUG = False
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
'''


app = Flask(__name__)
app.config['SECRET_KEY'] = 'default'
app.config.from_object(__name__)
urlApi = "http://petshow-api.herokuapp.com"
Bootstrap(app)
CORS(app)


class LoginForm(Form):
    username = StringField('Usuário', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Senha', validators=[InputRequired(), Length(min=4, max=15)])
    remember = BooleanField('Me mantenha conectado')


#faltando teste e mensagens
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for("produtos"))
    return render_template('login.html', form=form)
    '''
    if mensagem.erro:
        return render_template('login.html', mensagem=mensagem)
    elif mensagem.sucesso:
        return redirect(url_for("produtos"))
    return render_template('login.html')
    '''


#faltando mensagens
@app.route('/produtos/', methods=["GET", 'POST'])
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
            "animal_id": int(request.form["animal_id"] ),
            "usuario_id": 3 #colocar id usuario logado
        }

        mensagem = cadastrar(urlApi + "/produtos/", body)
        print(body)
        print(mensagem)

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
            "animal_id": int(request.form["animal_id"] ),
            "usuario_id": 3 #colocar id usuario logado
        }

        mensagem = editar(urlApi + "/produtos/" + id + "/alterar/", body)

        print(mensagem)

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


@app.route('/pedidos/', methods=["GET", 'POST'])
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
    elif request.method == 'GET':
        usuarios = listar(urlApi + '/usuarios/')
        print(usuarios)
        msg = "Usuarios"
        return render_template('lista_usuarios.html', msg=msg, usuarios=usuarios)


@app.route('/usuarios/new', methods=["GET"])
def cadastrar_usuario():
    msg = "Cadastrar um usuario"
    return render_template('cadastro_usuario.html', msg=msg)

@app.route('/usuarios/edit/<login>', methods=["GET", "POST"])
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

@app.route('/usuarios/senha/<login>', methods=["GET", "POST"])
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

@app.route('/usuarios/tipo/<login>', methods=["GET", "POST"])
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


@app.route('/usuarios/delete/<login>', methods=["POST"])
def remover_usuario(login):
    req = requests.delete(urlApi + '/usuarios/' + login + '/remover')
    msg = req.json()
    print(msg)
    return redirect(url_for("usuarios"))

@app.route('/clientes-pet/', methods=["GET"])
def clientes():
    return render_template('cadastro_cliente_pet.html')




def listar(url):
    return requests.get(url).json()

def deletar(url):
    return requests.delete(url).json()

def cadastrar(url, body):
    return requests.post(url, data=dumps(body), headers={'content-type': 'application/json'}).json()

def alterar_parte(url, body):
    return requests.patch(url, data=dumps(body), headers={'content-type': 'application/json'})

def alterar_todo(url, body):
    return requests.put(url, data=dumps(body), headers={'content-type': 'application/json'})

def editar(url, body):
    return requests.put(url, data = dumps(body), headers={'content-type': 'application/json'}).json()


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    # app.run(host='localhost', port=5000, debug=True)