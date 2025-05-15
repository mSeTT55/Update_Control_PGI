from flask import Flask, render_template, request
import paramiko
import logging
from config import SSH_HOST, SSH_USER, SSH_KEY_PATH, SCRIPT_PATH

# Configura o logger do Flask para imprimir INFO no console
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

def ssh_login():
    app.logger.info(f"🔌 Conectando em {SSH_HOST} como {SSH_USER} usando chave {SSH_KEY_PATH!r}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=SSH_HOST,
        username=SSH_USER,
        key_filename=SSH_KEY_PATH,
        timeout=10
    )
    app.logger.info("✅ Conexão SSH estabelecida")
    return ssh

def run_update(ssh):
    cmd = f"sudo {SCRIPT_PATH}"
    app.logger.info(f"▶️ Executando comando remoto: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

    app.logger.info("⏳ Aguardando saída do comando...")
    # Lê o stdout
    out = stdout.read().decode("utf-8", errors="ignore")
    app.logger.info(f"🖨️ Stdout recebido ({len(out)} bytes)")
    # Lê o stderr (se houver)
    err = stderr.read().decode("utf-8", errors="ignore")
    if err:
        app.logger.warning(f"⚠️ Stderr recebido ({len(err)} bytes)")
    # Pega o exit status
    status = stdout.channel.recv_exit_status()
    app.logger.info(f"📋 Exit status do comando: {status}")

    app.logger.info("🔒 Fechando conexão SSH")
    ssh.close()

    return out + ("\n--- ERRORS ---\n" + err if err else "")

@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    if request.method == "POST":
        try:
            ssh = ssh_login()
            output = run_update(ssh)
        except Exception as e:
            app.logger.error(f"❌ Erro durante o processo: {e}")
            output = f"❌ Erro: {e}"
    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)