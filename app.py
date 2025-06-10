import os
import csv
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    session, redirect, url_for
)
import logging
from functools import wraps

from callback_ldap_auth import authenticate_and_authorize
from callbacks_update import ssh_login, run_update
from config import HISTORY_FILE

# carrega as variáveis de .env
load_dotenv()
secret = os.getenv("FLASK_SECRET", os.urandom(24).hex())

app = Flask(__name__)
app.secret_key = secret
logging.basicConfig(level=logging.INFO)

# —————— Carrega histórico do CSV ——————
executed_versions = []
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # lemos na ordem cronológica (antigo → novo) e depois invert
        rows = list(reader)
        for row in reversed(rows):
            executed_versions.append({
                'version': row['version'],
                'log': row['log']
            })

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

@app.before_request
def require_login():
    public = ("login", "static", "logout")
    if request.endpoint not in public and "username" not in session:
        return redirect(url_for("login"))

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

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    output = None

    if request.method == "POST":
        # pega a versão do formulário
        version = request.form.get("version", "").strip()
        if version:
            version_label = f"Git v{version}"
            # executa o update via SSH
            ssh = ssh_login(app.logger)
            output = run_update(ssh, app.logger)

            # adiciona ao histórico em memória
            executed_versions.insert(0, {
                'version': version_label,
                'log': output
            })

            # salva no CSV (cria header se não existir)
            file_exists = os.path.exists(HISTORY_FILE)
            with open(HISTORY_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['version', 'log'])
                writer.writerow([version_label, output])

    return render_template(
        "screen-update.html",
        output=output,
        versions=executed_versions
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
