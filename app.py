# app.py

import os
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    session, redirect, url_for
)
import logging

from callback_ldap_auth import authenticate_and_authorize
from callbacks_update import ssh_login, run_update

# ————————————— Carrega variáveis de ambiente —————————————
load_dotenv()  # lê o arquivo .env na raiz
secret = os.getenv("FLASK_SECRET")
if not secret:
    # fallback rápido em dev; em produção sempre defina FLASK_SECRET no .env
    secret = os.urandom(24).hex()

# ————————————— Setup do Flask —————————————
app = Flask(__name__)
app.secret_key = secret
logging.basicConfig(level=logging.INFO)

# ————————————— Rotas de Autenticação —————————————
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = request.form["username"]
        pwd  = request.form["password"]
        if authenticate_and_authorize(user, pwd):
            session["username"] = user
            return redirect(url_for("index"))
        else:
            error = "Acesso negado"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ————————————— Rota Principal —————————————
@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    output = None
    if request.method == "POST":
        # Delegação para callbacks_update.py
        ssh = ssh_login(app.logger)
        output = run_update(ssh, app.logger)

    return render_template("screen-update.html", output=output)

# ————————————— Execução —————————————
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)