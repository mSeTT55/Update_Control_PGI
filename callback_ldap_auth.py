# ldap_auth.py

from ldap3 import Server, Connection, ALL
from config import (
    LDAP_SERVER,
    LDAP_BIND_DN,
    LDAP_BIND_PASSWORD,
    LDAP_BASE_DN,
    LDAP_USER_SEARCH_FILTER,
    LDAP_GROUP_DN,
)

def authenticate_and_authorize(username: str, password: str) -> bool:
    """
    1) Faz bind simples com a conta de serviço para buscar o DN do usuário
    2) Faz bind simples com o DN do usuário e senha fornecida (autentica)
    3) Verifica se o DN do usuário consta como membro do grupo
    """
    # 1) Conecta ao servidor LDAP
    server = Server(LDAP_SERVER, get_info=ALL)

    # Bind da conta de serviço (SIMPLE)
    svc_conn = Connection(
        server,
        user=LDAP_BIND_DN,
        password=LDAP_BIND_PASSWORD,
        auto_bind=True
    )

    # Busca o DN completo do usuário
    search_filter = LDAP_USER_SEARCH_FILTER.format(username=username)
    svc_conn.search(
        search_base=LDAP_BASE_DN,
        search_filter=search_filter,
        attributes=['distinguishedName']
    )
    if not svc_conn.entries:
        svc_conn.unbind()
        return False

    user_dn = svc_conn.entries[0].distinguishedName.value

    # 2) Tenta bind com o usuário real (SIMPLE)
    try:
        user_conn = Connection(
            server,
            user=user_dn,
            password=password,
            auto_bind=True
        )
        user_conn.unbind()
    except Exception:
        svc_conn.unbind()
        return False

    # 3) Verifica se o usuário está no grupo
    svc_conn.search(
        search_base=LDAP_GROUP_DN,
        search_filter=f"(member={user_dn})",
        attributes=['member']
    )
    is_member = bool(svc_conn.entries)
    svc_conn.unbind()
    return is_member
