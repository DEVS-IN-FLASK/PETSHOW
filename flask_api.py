# pip freeze > requeriments.txt
import os
from flask import Flask


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


@app.route('/')
def index():
    msg = 'Tela principal'
    return render_template('index.html', msg=msg)

@app.route('/login')
def login():
    msg = "Faça seu login aqui"
    return render_template('login.html', msg=msg)

@app.route('/clientes')
def cliente():
    msg = "Tela dos dados Cliente"
    return render_template('clientes.html', msg=msg)

@app.route('/pets')
def pet():
    msg = "Tela dos dados pets"
    return render_template('clientes.html', msg=msg)

@app.route('/produtos')
def produtos():
    msg = "Cadastre seus produtos"
    return render_template('clientes.html', msg=msg)

@app.route('/usuarios')
def usuários():
    msg = "Tela de Usuário"
    return render_template('clientes.html', msg=msg)

if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run(host='localhost', port=5000)
