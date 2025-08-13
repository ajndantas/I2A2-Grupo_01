# seguranca/gestao_usuario_secure.py (v2)
# Mantém a MESMA assinatura e retornos (True/False), com reforços de segurança.
# Produção: trocar os dicionários por DB (e.g., PostgreSQL) e mover rate limit para Redis.
# Requer: pip install argon2-cffi

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import os, time, hmac, secrets, random

# Argon2id com parâmetros seguros padrão (argon2-cffi já usa Argon2id)
ph = PasswordHasher()
PEPPER = os.environ.get("APP_PEPPER", "")  # definir em variável de ambiente segura

# Armazenamento em memória (trocar por DB/Redis em produção)
USERS = {}  # {login: {"hash": str, "nome": str, "created_at": float, "updated_at": float}}
FAILS = {}  # {(login, ip): [timestamps]}

# Política mínima de senha: >= 12 chars (mesmo se a UI já validar)
def _policy_ok(password: str) -> bool:
    return bool(password) and len(password.strip()) >= 12

def _rate_limited(login: str, ip: str, window=900, limit=5) -> bool:
    now = time.time()
    key = (login, ip or "")
    FAILS.setdefault(key, [])
    FAILS[key] = [t for t in FAILS[key] if now - t < window]
    return len(FAILS[key]) >= limit

def _add_fail(login: str, ip: str):
    FAILS.setdefault((login, ip or ""), []).append(time.time())

def _soft_jitter_delay():
    # Pequeno atraso aleatório para não dar dica de timing (anti-enumeração/brute-force)
    time.sleep(random.uniform(0.15, 0.35))

def gestao_usuario(login, senha, nome=None, novo_usuario=False, esqueci_senha=False, autenticacao=False, ip=None):
    """
    Assinatura padronizada do projeto. Sempre retorna True/False.
    - login normalizado (lowercase), sem vazar detalhes sensíveis.
    - hash seguro Argon2id + pepper (APP_PEPPER)
    - rate limit por login/IP (5 falhas/15min), com pequeno atraso (jitter)
    - regras de senha aplicadas no servidor (>= 12 chars) para criar/resetar
    - mensagens devem ser NEUTRAS na UI (não indicar se usuário existe)
    """
    login = (login or "").strip().lower()
    senha = (senha or "").strip()
    if not login or not senha:
        _soft_jitter_delay()
        return False

    # Autenticação
    if autenticacao:
        if _rate_limited(login, ip):
            _soft_jitter_delay()
            return False
        try:
            h = USERS[login]["hash"]
            # Argon2 verify já é resistente a timing attacks
            ph.verify(h, senha + PEPPER)
            return True
        except (KeyError, VerifyMismatchError):
            _add_fail(login, ip)
            _soft_jitter_delay()
            return False

    # Criar usuário
    if novo_usuario and nome:
        if not _policy_ok(senha):
            _soft_jitter_delay()
            return False
        # Não revelar se existe: apenas falhar genericamente
        if login in USERS:
            _soft_jitter_delay()
            return False
        USERS[login] = {
            "hash": ph.hash(senha + PEPPER),
            "nome": (nome or "").strip(),
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        return True

    # Reset de senha (ideal: token de reset fora de banda; manter assinatura retornando bool)
    if esqueci_senha:
        if not _policy_ok(senha):
            _soft_jitter_delay()
            return False
        if login not in USERS:
            _soft_jitter_delay()
            return False
        USERS[login]["hash"] = ph.hash(senha + PEPPER)
        USERS[login]["updated_at"] = time.time()
        return True

    _soft_jitter_delay()
    return False
