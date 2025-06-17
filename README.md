# 🛠️ Update PGI – Controle de Atualizações

Aplicação Flask para execução remota de atualizações do sistema PGI via SSH com autenticação Active Directory (LDAP).
Todo o histórico de execuções e logs é persistente mesmo após reinícios de container Docker.

---

## 📋 Funcionalidades

- ✅ Login via Active Directory (LDAP)
- ✅ Controle de acesso por grupo de segurança do AD
- ✅ Execução remota de script via SSH com sudo
- ✅ Wizard de confirmação (validação de atualização de banco + versão Git)
- ✅ Registro da versão, usuário e data/hora de cada execução
- ✅ Histórico persistente em CSV
- ✅ Exibição dos logs por versão (modal)
- ✅ Proteção contra reexecução em F5 (Post → Redirect → Get)
- ✅ Dockerized

## 🎨 Screenshots 

### Tela de Login
![image](https://github.com/user-attachments/assets/67162b13-3853-4c07-9392-baca2bfb28dd)

### Tela Principal
![image](https://github.com/user-attachments/assets/69459d73-39c2-42d5-b59b-7a532a0ee929)

### Wizard de Confirmação
![image](https://github.com/user-attachments/assets/d3da214e-5d0e-4afb-a66c-9f22c502d857)

### Modal de Log
![image](https://github.com/user-attachments/assets/e023aec7-4034-4bbc-91cf-d434fa9182fd)

### Histórico de execução com Log
![image](https://github.com/user-attachments/assets/edab0a47-9837-4347-9725-63e7741f581d)



## ⚙️ Requisitos

- Docker
- Docker Compose
- Servidor com acesso SSH ao PGI
- LDAP ativo com um grupo para validação de acesso
- Service Account de leitura no AD
- Chave SSH válida (sem senha)

## 🐳 Executando via Docker Compose

### 1. Crie o arquivo `.env` com as configurações:

```
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
```

### 2. Estrutura do `docker-compose.yml`

```yaml
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
      - "port:port"            # ajuste conforme necessário
    volumes:
      - /dados/update_control_PGI:/button_update_PGI/data
    restart: unless-stopped
```

### 3. Build e inicialização:

```bash
docker compose up --build -d
```

## 📂 Estrutura de Pastas

```
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
```

## ✅ Segurança

- ✅ O `.env` está ignorado no Git (`.gitignore`)
- ✅ O `history.csv` também está ignorado
- ✅ Uso de **SSH Key** + **NOPASSWD** via sudoers para execução remota
- ✅ Sessões Flask expiram após **1 hora**
- ✅ Nenhuma credencial sensível dentro da imagem Docker (tudo via `.env`)
