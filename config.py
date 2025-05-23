# config.py

import os
from dotenv import load_dotenv

load_dotenv()  # carrega as variáveis do .env

# —————— CONFIGURAÇÃO SSH ——————
SSH_HOST     = os.getenv("SSH_HOST")
SSH_USER     = os.getenv("SSH_USER")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")

# —————— PATH DO SCRIPT ——————
SCRIPT_PATH  = os.getenv("SCRIPT_PATH")

# —————— CONFIGURAÇÃO LDAP ——————
LDAP_SERVER             = os.getenv("LDAP_SERVER")
LDAP_BIND_DN            = os.getenv("LDAP_BIND_DN")
LDAP_BIND_PASSWORD      = os.getenv("LDAP_BIND_PASSWORD")
LDAP_BASE_DN            = os.getenv("LDAP_BASE_DN")
LDAP_USER_SEARCH_FILTER = os.getenv("LDAP_USER_SEARCH_FILTER")
LDAP_GROUP_DN           = os.getenv("LDAP_GROUP_DN")