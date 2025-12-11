import requests
import hmac
import hashlib
import json
import sys

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

# Substitua pela URL pública do ngrok OU localhost
URL = "http://localhost:8000/webhook/github"
# Exemplo:
# URL = "https://xxxx-yyy.ngrok-free.dev/webhook/github"

# Secret deve ser exatamente o mesmo do .env
SECRET = "secret"

# Payload de teste simulando evento push do GitHub
payload = {
    "repository": {"full_name": "meu/repo"},
    "pusher": {"name": "Arthur"},
    "commits": [
        {"message": "Commit de teste", "id": "abc123"},
        {"message": "Segundo commit", "id": "def456"},
    ],
}

# ==========================================================
# GERA ASSINATURA IGUAL À DO GITHUB
# ==========================================================

body = json.dumps(payload).encode("utf-8")

signature = "sha256=" + hmac.new(
    SECRET.encode(),
    body,
    hashlib.sha256
).hexdigest()

print("URL:", URL)
print("Signature (calculated):", signature)
print("Payload bytes len:", len(body))

headers = {
    "Content-Type": "application/json",
    "X-Hub-Signature-256": signature,
    "X-GitHub-Event": "push",
}

# ==========================================================
# ENVIA REQUISIÇÃO
# ==========================================================

try:
    response = requests.post(URL, headers=headers, data=body, timeout=10)
    print("STATUS:", response.status_code)
    print("BODY:", response.text)
except Exception as e:
    print("Erro ao enviar:", e)
    sys.exit(1)
