import os
import requests
from flask import Flask, request, jsonify, session, g, redirect, url_for, \
     abort, render_template, flash, Response
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps, loads
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_cors import CORS



app = Flask(__name__)
app.config['SECRET_KEY'] = 'devsinflaskpetshowapp'
app.config.from_object(__name__)
urlApi = "http://petshow-api.herokuapp.com"
#urlApi = "http://localhost:5000"
Bootstrap(app)
CORS(app)


class LoginForm(FlaskForm):
    username = StringField('Login', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Senha', validators=[InputRequired(), Length(min=4, max=15)])
    #remember = BooleanField('Me mantenha conectado')


#faltando teste e mensagens
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = request.form["username"]
        senha = request.form["password"]
        data = {
            'login': login,
            'senha': senha
        }
        try:
            resposta = requests.post(urlApi + '/usuarios/autenticar', data=dumps(data), headers={'content-type': 'application/json'}).json()
            if 'sucesso' in resposta:
                access_token = resposta['access_token']
                session['access_token'] = access_token
                #session['login'] = login
                user = listar(urlApi + f'/usuarios/{login}')
                session['login'] = user
                return redirect(url_for("produtos"))
            else:
                flash(resposta['erro'])
                return redirect(url_for("login"))
        except Exception:
            flash('Não foi possível a conexão com o banco')
            return redirect(url_for("login"))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('login')
    session.pop('access_token')
    return redirect(url_for('login'))


#faltando mensagens
@app.route('/produtos', methods=["GET", 'POST'])
@app.route('/produtos/edit/<id>', methods=["POST"])
@app.route('/produtos/delete/<id>', methods=["GET"])
def produtos(id = None):
    try:
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
                "animal_id": int(request.form["animal_id"]),
                "usuario_id": session['login']['id']
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
                "animal_id": int(request.form["animal_id"]),
                "usuario_id": session['login']['id']
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

            return render_template('produtos.html', produtos=produtos, tamanhos=tamanhos, marcas=marcas, animais=animais, produto=produto, user=session['login'])
    except Exception:
            flash('Não foi possível a conexão com o banco')
            return redirect(url_for("login"))

@app.route('/produtos/buscar/<id>')
def buscar_produto(id):
    return redirect(url_for('produtos', editar=id))


@app.route('/pedidos/', methods=["GET", 'POST'])
@app.route('/pedidos/edit/<id>', methods=["POST"])
@app.route('/pedidos/delete/<id>', methods=["GET"])
def pedidos(id = None):
    if(id == None and request.method == "POST"):
        msg = "Cadastrar um pedido"
        return render_template('pedidos.html', msg=msg, user=session['login'])
    elif(id != None and request.method == "GET"):
        msg = "Deletar um pedido"
        # @redirect("/pedidos")
        return render_template('pedidos.html', msg=msg, user=session['login'])
    elif(id != None):
        msg = "Editar um pedido"
        # @redirect("/pedidos")
        return render_template('pedidos.html', msg=msg, user=session['login'])
    else:
        msg = "Pedidos"
        return render_template('pedido.html', msg=msg, user=session['login'])


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

@app.route('/usuarios/', methods=["GET", "POST"])
def usuarios():
    try:
        if request.method == "POST":
            body = {
                "nome": request.form["nome"],
                "login": request.form["login"],
                "senha": request.form["senha"],
                "tipo": request.form["tipo"]
            }

            notificacao = cadastrar(urlApi + "/usuarios/novo", body)
            print(notificacao)
            if 'erro' not in notificacao:
                msg = "Cadastrado com sucesso"
                flash(msg)
                return redirect(url_for("usuarios"))
            else:
                flash(notificacao['erro'])
                return redirect(url_for("usuarios"))

        elif request.method == 'GET':
            usuarios = listar(urlApi + '/usuarios/')
            if 'msg' in usuarios:
                flash('Tempo encerrado, faça login novamente')
                return redirect(url_for("login"))
            msg = "Usuarios"
            return render_template('lista_usuarios.html', msg=msg, usuarios=usuarios, user=session['login'])
    except Exception:
        flash('Não foi possível a conexão com o banco')
        return redirect(url_for("login"))

@app.route('/usuarios/new/', methods=["GET"])
def cadastrar_usuario():
    msg = "Cadastrar um usuario"
    return render_template('cadastro_usuario.html', msg=msg, user=session['login'])
'''
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
        return render_template('cadastro_usuario.html', msg=msg, usuario=usuario, user=session['login'])
'''
@app.route('/usuarios/senha/<login>', methods=["GET", "POST"])
def alterar_senha(login):
    try:
        if request.method == 'GET':
            msg = "Editar senha"
            usuarios = listar(urlApi + '/usuarios/')
            
            for x in usuarios:
                if x['login'] == login:
                    usuario = x
            return render_template('cadastro_usuario.html', msg=msg, usuario=usuario, tipo='senha', user=session['login'])
        elif request.method == 'POST':
            body = {
                "login": request.form["login"],
                "senha": request.form["senha"]
            }
            notificacao = alterar_parte(urlApi + "/usuarios/alterarsenha", body)
            msg = "Alterada com sucesso"
            flash(msg)
            return redirect(url_for("usuarios"))
    except Exception:
        flash('Não foi possível a conexão com o banco')
        return redirect(url_for("login"))

@app.route('/usuarios/tipo/<login>', methods=["GET", "POST"])
def alterar_tipo(login):
    try:
        if request.method == 'GET':
            msg = "Editar senha"
            usuarios = listar(urlApi + '/usuarios/')
            
            for x in usuarios:
                if x['login'] == login:
                    usuario = x
            return render_template('cadastro_usuario.html', msg=msg, usuario=usuario, tipo='tipo', user=session['login'])
        elif request.method == 'POST':
            body = {
                "login": request.form["login"],
                "tipo": request.form["tipo"]
            }
            notificacao = alterar_parte(urlApi + "/usuarios/alterartipo", body)
            print(notificacao)
            if 'erro' not in notificacao:
                msg = "Alterado com sucesso"
                flash(msg)
                return redirect(url_for("usuarios"))
            else:
                flash(notificacao['erro'])
                return redirect(url_for("usuarios"))
                
    except Exception:
        flash('Não foi possível a conexão com o banco')
        return redirect(url_for("login"))


@app.route('/usuarios/delete/<login>', methods=["POST"])
def remover_usuario(login):
    req = requests.delete(urlApi + '/usuarios/' + login + '/remover/')
    msg = req.json()
    print(msg)
    return redirect(url_for("usuarios"))


@app.route('/clientes-pet/', methods=["GET", "POST"])
def clientes():
    try:
        if request.method == 'GET':
            listaClientes = listar(urlApi + '/clientes/')
            print(listaClientes)
            search = ''
            return render_template('cliente_pet.html', search=search , Listaclientes=listaClientes, user=session['login'])
        elif request.method == 'POST':
            listaClientes = listar(urlApi + '/clientes/')
            print(listaClientes)
            # search = "teste"
            search = request.form["search"]
            print("search="+search)
            return render_template('cliente_pet.html', search=search, Listaclientes=listaClientes, user=session['login'])
    except Exception:
        flash('Não foi possível a conexão com o banco')
        return redirect(url_for("login"))

@app.route('/cadastro-clientes-pet/', methods=["GET", "POST"])
def cadastroclientes():
    try:
        if request.method == "POST":
            print("Teste="+request.form["nome"])
            print(request.form["nome_pet"])
            print(request.form["raca"])
            print(request.form["especie"])
            print(request.form["porte"])
            print(request.form["genero"])
            
                      
            body = {
                "nome": request.form["nome"],
                "email": request.form["email"],
                "cpf": request.form["cpf"],
                "telefones": [{"telefone": request.form["telefone"]}],
                "endereco":{
                "cep": request.form["cep"],
                "rua": request.form["rua"],
                "numero": request.form["numero"],
                "bairro": request.form["bairro"],
                "cidade": request.form["cidade"],
                "uf": request.form["uf"]},          
                "pets": [{
                            "nome": request.form["nome_pet"],
                            "raca": request.form["raca"],
                            "porte": request.form["porte"],
                            "genero": request.form["genero"],
                            "animal_id":  request.form["especie"]
                        }]     
                }

           
            notificacao = cadastrar(urlApi + "/clientes/", body)
            msg = "Cadastrado com sucesso"
            #return redirect(url_for("cadastroclientes"))
            return render_template('cadastro_cliente_pet.html',msg=notificacao, user=session['login'])
        elif request.method == 'GET':
            return render_template('cadastro_cliente_pet.html', user=session['login'])
    except Exception as e:
        #print(e)
        flash('Não foi possível a conexão com o banco')
        #return redirect(url_for("login"))

# relatório de vendas
@app.route('/relatorio/', methods=['GET', 'POST'])
def relatorio():
    try:
        if request.method == 'POST':
            periodo = request.form['periodo']
            pedidos = listar(urlApi + '/relatorios/?data=' + periodo)

            return render_template('relatorio.html', user=session['login'], data=pedidos)
        else:
            return render_template('relatorio.html', user=session['login'], data=None)
    except Exception:
        flash('Não foi possível a conexão com o banco')
        return redirect(url_for("login"))


def listar(url):
    print(session)
    return requests.get(url, headers={'authorization': f"Bearer {session['access_token']}"}).json()

def deletar(url):
    return requests.delete(url).json()

def cadastrar(url, body):
    return requests.post(url, data=dumps(body), headers={'content-type': 'application/json', 'authorization': f"Bearer {session['access_token']}"}).json()

def alterar_parte(url, body):
    return requests.patch(url, data=dumps(body), headers={'content-type': 'application/json', 'authorization': f"Bearer {session['access_token']}"}).json()

def alterar_todo(url, body):
    return requests.put(url, data=dumps(body), headers={'content-type': 'application/json', 'authorization': f"Bearer {session['access_token']}"}).json()

def editar(url, body):
    return requests.put(url, data=dumps(body), headers={'content-type': 'application/json', 'authorization': f"Bearer {session['access_token']}"}).json()


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
    #app.run(host='localhost', port=5000, debug=True)
