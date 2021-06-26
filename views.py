from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
from flask_mysqldb import MySQL
from models import Jogo, Usuario
from dao import JogoDao, UsuarioDao
import os
import time
from jogoteca import db, app
from helpers import recupera_imagem, deleta_arquivo

#criar um objeto
jogo_dao = JogoDao(db)
usuario_dao = UsuarioDao(db)

@app.route('/')
def index():
    lista = jogo_dao.listar()
    qtd_reg = len(lista)
    print("qtd de registros: " + str(qtd_reg))
    return render_template('lista.html', titulo='Jogos', jogos=lista, qtd=qtd_reg)

@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('novo.html', titulo='Novo Jogo')

@app.route('/criar', methods=['POST',])
def criar():
    nome = request. form['nome']
    categoria = request. form['categoria']
    console = request. form['console']
    jogo = Jogo(nome, categoria, console)
    jogo = jogo_dao.salvar(jogo)
    timestamp = time.time()

#salvar o arquivo
    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']
    arquivo.save(f'{upload_path}/capa{jogo.id}-{timestamp}.jpg')
    flash(nome + ' jogo salvo com sucesso!')
    return redirect(url_for('index'))

#Editar
@app.route('/editar/<int:id>') #passando como parametro o id
def editar(id): #recupero do banco este id
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('editar')))
    jogo = jogo_dao.busca_por_id(id)
    nome_imagem = recupera_imagem(id)

    nomejogo = jogo_dao.busca_por_id(id)
    capa_jogo_prt = f'capa{id}.jpg'

    return render_template('editar.html', titulo='Editando '+jogo.nome, jogo=jogo, capa_jogo = nome_imagem)

#recebendo do form
@app.route('/atualizar', methods=['POST',])
def atualizar():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    jogo = Jogo(nome, categoria, console, id=request.form['id'])
    jogo_dao.salvar(jogo)

    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']
    timestamp = time.time()
    deleta_arquivo(jogo.id) #deleta as imagens que ja existem
    arquivo.save(f'{upload_path}/capa{jogo.id}-{timestamp}.jpg')
    return redirect(url_for('index'))

#deletar
@app.route('/deletar/<int:id>') #passando como parametro o id
def deletar(id): #recupero do banco este id
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('index')))

    jogo_dao.deletar(id)
    flash("O jogo foi removido!")
    return redirect(url_for('index'))


@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)


@app.route('/autenticar', methods=['POST', ])
def autenticar():
    usuario = usuario_dao.buscar_por_id(request.form['usuario'])
    if usuario: #verifico se existe
        if usuario.senha == request.form['senha']:
            session['usuario_logado'] = usuario.id
            flash(usuario.nome + ' logou com sucesso!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)
    else:
        flash('Não logado, tente novamente!')
        return render_template('login.html')


@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('index'))

#rota especifica para imagens
@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)