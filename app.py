from flask import Flask, render_template, request
import paramiko

# importa a configuração SSH e script
from config import SSH_HOST, SSH_USER, SSH_KEY_PATH, SCRIPT_PATH

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    if request.method == "POST":
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=SSH_HOST,
                username=SSH_USER,
                key_filename=SSH_KEY_PATH,
            )
            stdin, stdout, stderr = ssh.exec_command(f"sh {SCRIPT_PATH}")
            out = stdout.read().decode("utf-8", errors="ignore")
            err = stderr.read().decode("utf-8", errors="ignore")
            ssh.close()
            output = out + ("\n--- ERRORS ---\n" + err if err else "")
        except Exception as e:
            output = f"❌ Erro ao executar via SSH: {e}"
    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)