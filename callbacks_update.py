# callbacks_update.py

import paramiko
from config import SSH_HOST, SSH_USER, SSH_KEY_PATH, SCRIPT_PATH

def ssh_login(logger):
    """
    Faz login SSH e retorna o client conectado.
    Usa logger (por exemplo, app.logger) para debugar.
    """
    logger.info(f"🔌 Conectando em {SSH_HOST} como {SSH_USER}…")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=SSH_HOST,
        username=SSH_USER,
        key_filename=SSH_KEY_PATH,
        timeout=10
    )
    logger.info("✅ SSH conectado")
    return ssh

def run_update(ssh, logger):
    """
    Executa o SCRIPT_PATH via sudo e retorna todo o output.
    Recebe o client SSH já conectado e o mesmo logger.
    """
    cmd = f"sudo -n {SCRIPT_PATH}"
    logger.info(f"▶️ Executando comando remoto: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    status = stdout.channel.recv_exit_status()
    logger.info(f"📋 Código de saída: {status}")

    ssh.close()
    return out + ("\n--- ERRORS ---\n" + err if err else "")
