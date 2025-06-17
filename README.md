🛠️ Update PGI – Controle de Atualizações
Aplicação Flask para gestão e execução remota de atualizações do sistema PGI via SSH com autenticação por Active Directory (LDAP).
Todo o histórico de versões e logs é persistente, mesmo após reinícios de container Docker.

---

📋 Funcionalidades
✅ Login com autenticação via Active Directory (LDAP)

✅ Verificação de grupo no Active Directory antes de liberar acesso a aplicação

✅ Execução de script remoto via SSH e sudo (sem senha)

✅ Wizard de confirmação com múltiplas perguntas antes da atualização

✅ Registro de versão, usuário e data/hora de cada execução

✅ Histórico de execuções persistido em CSV (com bind-mount para persistência)

✅ Visualização do log de cada versão via modal na interface

✅ Proteção contra reexecução ao dar F5 (Post → Redirect → Get)

✅ Containerizado com Docker e Docker Compose

🎨 Screenshots
Aqui você pode adicionar imagens do layout. Exemplo:

Tela de Login:
(adicione aqui seu print da tela de login com o fundo e form bonitos)

Tela de Atualização:
(adicione aqui print do header gradiente com o botão “Atualizar PGI” e o histórico de versões)

Wizard de Confirmação:
(print do wizard com as perguntas antes de executar)

Modal de Log:
(print do modal mostrando o log + versão + usuário + data/hora)

⚙️ Requisitos
Docker e Docker Compose

Acesso à rede com o Active Directory

Acesso via SSH ao servidor PGI

Service Account com permissão de bind LDAP

Chave privada SSH com permissão de execução remota

🐳 Executando via Docker Compose
1. Crie o arquivo .env com as configurações:

FLASK_SECRET=uma_chave_secreta
SSH_HOST=ip_do_servidor_pgi
SSH_USER=pgi.service
SSH_KEY_PATH=/caminho/dentro/do/container/.ssh/pgi.service
SCRIPT_PATH=/dados/.pgi-update.sh
LDAP_SERVER=ldap://ip_ou_dns_ad
LDAP_BIND_DN=CN=...,OU=...,DC=...
LDAP_BIND_PASSWORD=sua_senha_ldap
LDAP_BASE_DN=DC=...
LDAP_USER_SEARCH_FILTER=(sAMAccountName={username})
LDAP_GROUP_DN=CN=Update-PGI,OU=...,DC=...
HISTORY_FILE=data/history.csv

2. Estrutura do Docker Compose:
version: '3.8'

services:
  app:
    build:
      context: .
    image: button_update_pgi:latest
    container_name: button_update_pgi
    env_file:
      - .env
    ports:
      - "port:port"
    volumes:
      - /dados/update_control_PGI:/button_update_PGI/data
    restart: unless-stopped

3. Build e subida:
docker compose up --build -d

📂 Estrutura de Pastas
button_update_PGI/
├── app.py
├── callback_ldap_auth.py
├── callbacks_update.py
├── config.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env
├── .gitignore
├── README.md
├── /templates
│   ├── login.html
│   └── screen-update.html
├── /static
│   └── /css
│       └── screen-update.css
└── /data
    └── history.csv
✅ Segurança
O .env não vai para o Git (está no .gitignore)

O history.csv também ignorado no Git

Uso de SSH Key + NOPASSWD no sudoers

Sessões expiram após 1 hora
