from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import IntegrityError
from werkzeug.security import generate_password_hash
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = "troque-esta-chave-no-projeto"


def conectar():
    return mysql.connector.connect(**DB_CONFIG)


# Cada cadastro abaixo usa somente uma tabela sem chave estrangeira (FK).
CONFIGS = {
    "usuarios": {
        "titulo": "Usuários", "tabela": "usuarios", "chave": "id_usuario",
        "campos": [
            {"nome": "nome", "rotulo": "Nome", "tipo": "text", "obrigatorio": True},
            {"nome": "email", "rotulo": "E-mail", "tipo": "email", "obrigatorio": True},
            {"nome": "senha", "rotulo": "Senha", "tipo": "password", "obrigatorio": True},
            {"nome": "tipo_usuario", "rotulo": "Tipo de usuário", "tipo": "select", "opcoes": ["ALUNO", "PROFESSOR", "ADMIN"], "obrigatorio": True},
            {"nome": "ativo", "rotulo": "Ativo", "tipo": "select", "opcoes": ["1", "0"], "rotulos_opcoes": ["Sim", "Não"], "obrigatorio": True},
        ],
        "colunas": ["id_usuario", "nome", "email", "tipo_usuario", "ativo"],
    },
    "permissoes": {
        "titulo": "Permissões", "tabela": "permissoes", "chave": "id_permissao",
        "campos": [
            {"nome": "nome", "rotulo": "Nome", "tipo": "text", "obrigatorio": True},
            {"nome": "descricao", "rotulo": "Descrição", "tipo": "text", "obrigatorio": False},
        ],
        "colunas": ["id_permissao", "nome", "descricao"],
    },
    "disciplinas": {
        "titulo": "Disciplinas", "tabela": "disciplinas", "chave": "id_disciplina",
        "campos": [
            {"nome": "nome", "rotulo": "Nome", "tipo": "text", "obrigatorio": True},
            {"nome": "descricao", "rotulo": "Descrição", "tipo": "textarea", "obrigatorio": False},
        ],
        "colunas": ["id_disciplina", "nome", "descricao"],
    },
    "turmas": {
        "titulo": "Turmas", "tabela": "turmas", "chave": "id_turma",
        "campos": [
            {"nome": "nome", "rotulo": "Nome da turma", "tipo": "text", "obrigatorio": True},
            {"nome": "ano", "rotulo": "Ano letivo", "tipo": "number", "obrigatorio": True},
        ],
        "colunas": ["id_turma", "nome", "ano"],
    },
}


def obter_config(recurso):
    return CONFIGS.get(recurso)


@app.route("/")
def inicio():
    return render_template("index.html", configs=CONFIGS)


@app.route("/<recurso>")
def listar(recurso):
    config = obter_config(recurso)
    if not config:
        return "Cadastro não encontrado.", 404
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    colunas = ", ".join(f"`{coluna}`" for coluna in config["colunas"])
    cursor.execute(f"SELECT {colunas} FROM `{config['tabela']}` ORDER BY `{config['chave']}` DESC")
    registros = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template("lista.html", recurso=recurso, config=config, registros=registros)


@app.route("/<recurso>/novo")
def novo(recurso):
    config = obter_config(recurso)
    if not config:
        return "Cadastro não encontrado.", 404
    return render_template("formulario.html", recurso=recurso, config=config, registro=None)


@app.route("/<recurso>/salvar", methods=["POST"])
def salvar(recurso):
    config = obter_config(recurso)
    if not config:
        return "Cadastro não encontrado.", 404

    nomes = [campo["nome"] for campo in config["campos"]]
    valores = []
    for campo in config["campos"]:
        valor = request.form.get(campo["nome"], "").strip()
        if campo["nome"] == "senha" and valor:
            valor = generate_password_hash(valor)
        if campo["nome"] == "ativo":
            valor = int(valor or "1")
        valores.append(valor if valor != "" else None)

    colunas = ", ".join(f"`{nome}`" for nome in nomes)
    marcadores = ", ".join(["%s"] * len(nomes))
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute(f"INSERT INTO `{config['tabela']}` ({colunas}) VALUES ({marcadores})", tuple(valores))
        conexao.commit()
        flash(f"{config['titulo']} cadastrado com sucesso.", "sucesso")
    except IntegrityError:
        conexao.rollback()
        flash("Não foi possível salvar. Verifique se um campo único, como e-mail ou nome da permissão, já existe.", "erro")
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for("listar", recurso=recurso))


@app.route("/<recurso>/editar/<int:id_registro>")
def editar(recurso, id_registro):
    config = obter_config(recurso)
    if not config:
        return "Cadastro não encontrado.", 404
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM `{config['tabela']}` WHERE `{config['chave']}` = %s", (id_registro,))
    registro = cursor.fetchone()
    cursor.close()
    conexao.close()
    if not registro:
        return "Registro não encontrado.", 404
    return render_template("formulario.html", recurso=recurso, config=config, registro=registro)


@app.route("/<recurso>/atualizar/<int:id_registro>", methods=["POST"])
def atualizar(recurso, id_registro):
    config = obter_config(recurso)
    if not config:
        return "Cadastro não encontrado.", 404
    campos = [campo for campo in config["campos"] if campo["nome"] != "senha"]
    nomes = [campo["nome"] for campo in campos]
    valores = []
    for campo in campos:
        valor = request.form.get(campo["nome"], "").strip()
        if campo["nome"] == "ativo":
            valor = int(valor or "1")
        valores.append(valor if valor != "" else None)
    senha = request.form.get("senha", "").strip()
    if senha:
        nomes.append("senha")
        valores.append(generate_password_hash(senha))
    atribuicoes = ", ".join(f"`{nome}` = %s" for nome in nomes)
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute(f"UPDATE `{config['tabela']}` SET {atribuicoes} WHERE `{config['chave']}` = %s", tuple(valores + [id_registro]))
        conexao.commit()
        flash(f"{config['titulo']} atualizado com sucesso.", "sucesso")
    except IntegrityError:
        conexao.rollback()
        flash("Não foi possível atualizar. Verifique os campos únicos.", "erro")
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for("listar", recurso=recurso))


@app.route("/<recurso>/excluir/<int:id_registro>", methods=["POST"])
def excluir(recurso, id_registro):
    config = obter_config(recurso)
    if not config:
        return "Cadastro não encontrado.", 404
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(f"DELETE FROM `{config['tabela']}` WHERE `{config['chave']}` = %s", (id_registro,))
    conexao.commit()
    cursor.close()
    conexao.close()
    flash("Registro excluído.", "sucesso")
    return redirect(url_for("listar", recurso=recurso))


if __name__ == "__main__":
    app.run(debug=True)
