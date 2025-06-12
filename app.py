import os
import csv
from datetime import timedelta
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

# carrega as variáveis do .env
load_dotenv()
secret = os.getenv("FLASK_SECRET", os.urandom(24).hex())

app = Flask(__name__)
app.secret_key = secret
# Sessão permanente: expira em 1 horas
app.permanent_session_lifetime = timedelta(hours=1)
logging.basicConfig(level=logging.INFO)

# —————— Carrega histórico do CSV ——————
executed_versions = []
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reversed(list(reader)):
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
            session.permanent = True
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
    # PRG: pega do session (pop) se veio de um POST
    output = session.pop('last_output', None)
    current_version = session.pop('current_version', None)

    if request.method == "POST":
        version = request.form.get("version", "").strip()
        if version:
            current_version = f"Git v{version}"
            # executa o update via SSH
            ssh = ssh_login(app.logger)
            output = run_update(ssh, app.logger)

            # atualiza histórico em memória e no CSV
            executed_versions.insert(0, {
                'version': current_version,
                'log': output
            })
            new_file = not os.path.exists(HISTORY_FILE)
            with open(HISTORY_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if new_file:
                    writer.writerow(['version', 'log'])
                writer.writerow([current_version, output])

            # armazena na session para exibir no próximo GET
            session['last_output'] = output
            session['current_version'] = current_version

        # redireciona para evitar reexecução no F5
        return redirect(url_for('index'))

    # GET: renderiza normalmente
    return render_template(
        "screen-update.html",
        output=output,
        versions=executed_versions,
        current_version=current_version
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8054, debug=False)