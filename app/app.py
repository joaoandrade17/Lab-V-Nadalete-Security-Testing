"""
Mural Seguro - aplicacao de exemplo para a apresentacao de Security Testing.

Esta e a versao VULNERAVEL. As duas vulnerabilidades demonstradas na
apresentacao (SQL Injection no login e Stored XSS no mural) estao
PRESENTES e exploraveis aqui. Compare com a branch `corrigido` usando:

    git diff vulneravel corrigido -- app/app.py app/templates/mural.html

Os pontos relevantes de seguranca estao marcados com o comentario
`# [VULNERAVEL]` para facilitar a leitura durante a demonstracao.
"""

import os
import sqlite3

from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mural.db")

app = Flask(__name__)
app.secret_key = "chave-de-demonstracao-nao-usar-em-producao"


# --------------------------------------------------------------------------
# Banco de dados (SQLite) - criado e populado automaticamente na primeira vez
# --------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Recria o banco com dados de exemplo toda vez que o app sobe."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE comments (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            author  TEXT NOT NULL,
            content TEXT NOT NULL
        );

        INSERT INTO users (username, password) VALUES
            ('admin', 'supersecreta123'),
            ('maria', 'maria2024');

        INSERT INTO comments (author, content) VALUES
            ('maria', 'Primeiro recado no mural! :)'),
            ('admin', 'Bem-vindos ao mural da turma.');
        """
    )
    db.commit()
    db.close()


# --------------------------------------------------------------------------
# Rotas
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return redirect(url_for("mural"))


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        db = get_db()

        # [VULNERAVEL] A entrada do usuario e concatenada direto na string SQL.
        # Com  username = admin' --  o restante da consulta (a checagem de senha)
        # vira comentario e o login acontece sem a senha correta.
        sql = (
            "SELECT * FROM users WHERE username = '%s' AND password = '%s'"
            % (username, password)
        )
        user = db.execute(sql).fetchone()

        if user:
            session["user"] = user["username"]
            return redirect(url_for("mural"))
        erro = "Usuario ou senha invalidos."
    return render_template("login.html", erro=erro)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("mural"))


@app.route("/mural", methods=["GET", "POST"])
def mural():
    db = get_db()
    if request.method == "POST":
        if "user" not in session:
            return redirect(url_for("login"))
        content = request.form.get("content", "").strip()
        if content:
            # [SEGURANCA] O conteudo e salvo como texto puro. A protecao
            # contra XSS acontece na renderizacao (ver mural.html): o Jinja2
            # faz escape automatico de < > & " etc.
            db.execute(
                "INSERT INTO comments (author, content) VALUES (?, ?)",
                (session["user"], content),
            )
            db.commit()
        return redirect(url_for("mural"))

    comments = db.execute(
        "SELECT * FROM comments ORDER BY id DESC"
    ).fetchall()
    return render_template(
        "mural.html", comments=comments, user=session.get("user")
    )


if __name__ == "__main__":
    init_db()
    # Porta 5080 para evitar conflito com o AirPlay do macOS (porta 5000).
    app.run(host="127.0.0.1", port=5080, debug=True)
