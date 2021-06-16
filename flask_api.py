import os
import requests
from flask import Flask, request, jsonify, session, g, redirect, url_for, \
     abort, render_template, flash, Response
from flask_restful import Resource, Api
from requests.sessions import Request, get_auth_from_url
from sqlalchemy import create_engine
from json import dumps, loads
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_cors import CORS
from datetime import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = 'devsinflaskpetshowapp'
app.config.from_object(__name__)
urlApi = "http://petshow-api.herokuapp.com"
#"http://petshow-api.herokuapp.com"
#urlApi = "http://localhost:5000"
#"http://localhost:8080"
Bootstrap(app)
CORS(app)


class LoginForm(FlaskForm):
    username = StringField('Login', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Senha', validators=[InputRequired(), Length(min=4, max=15)])
    remember = BooleanField('Me mantenha conectado')


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
                return redirect(url_for("lista_produto"))
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


@app.route('/produtos', methods=["GET", 'POST'])
@app.route('/produtos/edit/<id>', methods=["POST"])
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

            if 'sucesso' in mensagem:
                flash(mensagem['sucesso'])
                return redirect(url_for("lista_produto"))
            else:
                flash('Ocorreu um problema')
                return redirect(url_for("lista_produto"))
        elif(id != None and request.method == 'POST'):
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

            if 'sucesso' in mensagem:
                flash(mensagem['sucesso'])
                return redirect(url_for("lista_produto"))
            else:
                flash("Ocorreu um erro")
                return redirect(url_for("lista_produto"))
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
            
@app.route('/produtos/lista/')
def lista_produto(id=None):
            produtos = listar(urlApi + "/produtos/")

            produto = None
            if request.args.get("editar"):
                produto = [p for p in produtos if int(p["id"]) == int(request.args.get("editar"))][0]

            marcas = listar(urlApi + "/produtos/marcas/")
            tamanhos = listar(urlApi + "/produtos/tamanhos/")
            animais = listar(urlApi + "/produtos/animais/")
        

            return render_template('lista_produtos.html', produtos=produtos, tamanhos=tamanhos, marcas=marcas, animais=animais, produto=produto, user=session['login'])
    
@app.route('/produtos/buscar/<id>')
def buscar_produto(id):
    return redirect(url_for('produtos', editar=id))

@app.route('/pedidos/', methods=["GET", 'POST'])
@app.route('/pedidos/<id>', methods=['GET','POST'])
def pedidos(id = None):
    try:
        if(id == None and request.method == "POST"):
            itens_form = int(request.form['itens'])
            itens = []
            for i in range(itens_form):
                item = {
                    'produto_id': int(request.form['produto_id['+str(i)+']']),
                    'quantidade': int(request.form['quantidade['+str(i)+']'])
                }
                itens.append(item)
            body = {
                "cliente_id": int(request.form["cliente_id"]),
                "observacao": request.form["observacao"],
                "usuario_id": session['login']['id'],
                "itens": itens
                }
            mensagem = cadastrar(urlApi + "/pedidos/", body)
            return redirect(url_for("pedidos"))
        elif(id != None and request.method == "GET"):
            msg = "Visualizar Pedido"
            pedidos = listar(urlApi + "/pedidos/")["pedidos"]
            produtos = listar(urlApi + "/produtos/")
            pedido = None
            
            for x in pedidos:
                if int(id) == x['pedido']['id']:
                    pedido = x
                    
            x = pedido['pedido']['data']
            x = datetime.strptime(x, "%a, %d %b %Y %H:%M:%S %Z")
            data = f'{x.day}/{x.month}/{x.year}'
            return render_template('visualizacao_pedido.html', msg=msg, user=session['login'], pedido=pedido, produtos=produtos, data=data)
        elif(id != None and request.method == "POST"):
            msg = "Alterar Pedido"
            body = {'situacao_id': int(request.form['situacao_id']), 'observacao': request.form['observacao']}
            resposta = alterar_todo(urlApi + '/pedidos/' + id + '/situacao/', body)
            if 'sucesso' in resposta:
                flash(resposta['sucesso'])
                return redirect(url_for('pedidos'))
            else:
                flash('Ocorreu um erro')
                return redirect(url_for('pedidos'))
        else:
            # listagem
            msg = "Pedidos"
            pedidos = listar(urlApi + "/pedidos/")["pedidos"]
            return render_template('lista_pedidos.html', msg=msg, pedidos=pedidos, user=session['login'])    
    except Exception as e:
        flash('Não foi possível a conexão com o banco')
        return redirect(url_for("login"))

@app.route('/pedidos/new/')
def cadastrar_pedido():
    clientes = listar(urlApi + "/clientes/")
    produtos = listar(urlApi + "/produtos/")
    return render_template('cadastro_pedido.html', user=session['login'], pedido=[], clientes=clientes, produtos=produtos)


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
    return redirect(url_for("usuarios"))


@app.route('/clientes-pet/', methods=["GET", "POST"])
def clientes():
    try:
        if request.method == 'GET':
            listaClientes = listar(urlApi + '/clientes/')       
            search = ''
            return render_template('cliente_pet.html', search=search , Listaclientes=listaClientes, user=session['login'])
        elif request.method == 'POST':
            listaClientes = listar(urlApi + '/clientes/')
            search = request.form["search"]
            print("search="+search)
            return render_template('cliente_pet.html', search=search, Listaclientes=listaClientes, user=session['login'])
    except Exception:
        flash('Não foi possível a conexão com o banco')
        return redirect(url_for("login"))



@app.route('/cadastro-clientes-pet/', methods=["GET","POST"])
def alterarcliente(id = None):
    try:

            
        id=0
        URL = request.url
        x = URL.split("/")
        if(x[4]!= '' ):            
            id = int(x[4].replace("?id=",""))


        if request.method == "GET":
            
            listaClientes = listar(urlApi + '/clientes/')
            return render_template('cadastro_cliente_pet.html',msg="", id=id, Listaclientes=listaClientes, user=session['login'])
        elif(request.method == 'POST'): 

                print("idcliente=",request.form["idcliente"])
                idcliente=request.form["idcliente"]

                if idcliente == "0":
                    
                    print("idcliente=",request.form["idcliente"])  
                    print("raca="+request.form["raca"])  
                    print("porte="+request.form["porte"])  
                    print("genero="+request.form["genero"])  
                    print("especie="+request.form["especie"])                      
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
                        # "pets":{}
                        "pets": [{
                                "nome": request.form["nome_pet"],
                                "raca": request.form["raca"],
                                "porte": request.form["porte"],
                                "genero": request.form["genero"],
                                "animal_id":  request.form["especie"]
                            }] 
                        }
            
                    
                    notificacao = cadastrar(urlApi + "/clientes/", body)
                    if 'erro' not in notificacao:
                        msg = "Cliente cadastrado com sucesso"
                    else:
                        msg = "Não foi possível cadastrar o cliente"
                    
                    return render_template('cadastro_cliente_pet.html', id = 0, msg=msg, user=session['login'])

                elif(idcliente != "0"): 
                    print("ola")
                    print("nome_pet="+request.form["nome_pet"])  
                    print("raca="+request.form["raca"])  
                    print("porte="+request.form["porte"])  
                    print("genero="+request.form["genero"])  
                    print("especie="+request.form["especie"])                      
                    body = {
                        "id": "1",
                        "nome": request.form["nome"],
                        "email": request.form["email"],
                        "cpf": request.form["cpf"],
                        "endereco":{
                        "cep": request.form["cep"],
                        "rua": request.form["rua"],
                        "numero": request.form["numero"],
                        "bairro": request.form["bairro"],
                        "cidade": request.form["cidade"],
                        "uf": request.form["uf"]},
                        "telefones": {},  
                        # "pets":{}
                        "pets": [{
                                 "id":"1",
                                 "nome": request.form["nome_pet"],
                                 "raca": request.form["raca"],
                                 "porte": request.form["porte"],
                                 "genero": request.form["genero"],
                                 "animal_id": request.form["especie"]
                             }] 
                        }
                       

                    notificacao = alterar_todo(urlApi + "/clientes/" + idcliente + "/alterar/", body)

                    if 'erro' not in notificacao:
                        msg = "Cliente alterado com sucesso"
                    else:
                        msg = "Não foi possível alterar o cliente"
        
                    #return redirect(url_for("cadastroclientes"))
                    return render_template('cadastro_cliente_pet.html', id = 0, msg=msg, user=session['login'])
    except Exception as e:
        print(e)
        flash('Não foi possível a conexão com o banco')
        #return redirect(url_for("login"))

# @app.route('/cadastro-clientes-pet/', methods=["GET", "POST"])
# def cadastroclientes():
#     try:
#         if request.method == "POST":

#             pets = []       
#             for key in request.form: 
#                 dict = {}                
#                 if key.startswith('nome_pet'):           
#                     dict["nome"] = request.form[key]
#                 if key.startswith('raca'):           
#                      dict["raca"] = request.form[key]             
#                 if key.startswith('porte'):           
#                     dict["porte"]  = request.form[key]
#                 if key.startswith('genero'):           
#                      dict["genero"] = request.form[key]
#                 if key.startswith('animal_id'):           
#                      dict["animal_id"] = request.form[key]
                
#                 pets.append(dict)

#             print(pets)

#             # pets = []
#             # dictForm = request.form.to_dict(flat=False)
#             # # Iterate over all the items in dictionary and filter items which has even keys
#             # for (key, value) in dictForm.items():
#             #     dict = {}
#             #      # Check if key is even then add pair to new dictionary
#             #     if 'nome_pet' in key:
                   
#             #         for (key, value) in dictForm.items(): 
#             #             index = key.split('[')[-1].split(']')[0]
                        
#             #             dict["nome_pet"] = value[0]
#             #             dict["animal_id"] = int(dictForm.get('animal_id'+"["+index+"]")[0])
#             #             pets.append(dict)
                    
   


   
#             # print(request.form["especie"])
#             # print(request.form["porte"])
#             # print(request.form["genero"])
            
                      
#             body = {
#                 "nome": request.form["nome"],
#                 "email": request.form["email"],
#                 "cpf": request.form["cpf"],
#                 "telefones": [{"telefone": request.form["telefone"]}],
#                 "endereco":{
#                 "cep": request.form["cep"],
#                 "rua": request.form["rua"],
#                 "numero": request.form["numero"],
#                 "bairro": request.form["bairro"],
#                 "cidade": request.form["cidade"],
#                 "uf": request.form["uf"]},  
#                 "pets":pets        
#                 # "pets": [{
#                 #             "nome": request.form["nome_pet"],
#                 #             "raca": request.form["raca"],
#                 #             "porte": request.form["porte"],
#                 #             "genero": request.form["genero"],
#                 #             "animal_id":  request.form["especie"]
#                 #         }]     
#                 }

           
#             notificacao = cadastrar(urlApi + "/clientes/", body)
#             msg = "Cadastrado com sucesso"
#             #return redirect(url_for("cadastroclientes"))
#             return render_template('cadastro_cliente_pet.html',msg=notificacao, user=session['login'])
#         elif request.method == 'GET':
#             return render_template('cadastro_cliente_pet.html', user=session['login'])
#     except Exception as e:
#         #print(e)
#         flash('Não foi possível a conexão com o banco')
#         #return redirect(url_for("login"))

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
    #print adicionado com atualizações em clientes
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
