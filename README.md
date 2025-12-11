Notificador de Mudanças em Repositórios GitHub

Serviço FastAPI para receber e validar webhooks do GitHub

Este projeto implementa um endpoint HTTP para receber webhooks do GitHub, validar a assinatura HMAC usando um segredo compartilhado (GITHUB_WEBHOOK_SECRET) e registrar eventos em log local.
Ele não grava em arquivo, não usa banco de dados e não envia para o Telegram. O fluxo atual é simples, direto e ideal para fins educacionais ou integrações locais.


# 1. Funcionalidades

- Endpoint: POST /webhook/github

- Validação da assinatura X-Hub-Signature-256 (HMAC-SHA256).

- Suporte aos eventos:

    - push

    - pull_request

- Processamento do payload e registro da notificação via logging local.

- Script auxiliar para simular uma requisição assinada (teste_signed.py).

- Integração real com GitHub via ngrok (opcional).

# 2. Requisitos

- Python 3.10+

- Git

- (Opcional) ngrok para testar webhooks reais


# 3. Instalação
- 3.1 Clonar o repositório
    - git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
    - cd SEU_REPOSITORIO

- 3.2 Criar virtualenv e instalar dependências

- Linux/macOS:

    - python3 -m venv .venv
    - source .venv/bin/activate
    - pip install -r requirements.txt


- Windows:

    - python -m venv .venv
    - .venv\Scripts\Activate.ps1
    - pip install -r requirements.txt


- 3.3 Configurar o arquivo .env

    - Crie a partir do exemplo:

    - cp .env.example .env
    - Conteúdo do .env:
        - GITHUB_WEBHOOK_SECRET=secret

Esse valor deve ser o mesmo configurado no GitHub Webhook.


# 4. Executando o Servidor Local

- Com a virtualenv ativa, digite no terminal:
  -     uvicorn app.main:app --reload --port 8000


- Saída esperada:
  -     Uvicorn running on http://127.0.0.1:8000
  
Logs do processamento aparecerão nesse terminal.


# 5. Testando com GitHub

- 5.1 Abrir túnel com ngrok, digite em um novo terminal:
  -     ngrok http 8000


Copie a URL mostrada (ex.: https://xxxx.ngrok-free.dev)

- 5.2 Criar Webhook no GitHub
  -    No repositório → Settings → Webhooks → Add Webhook

- Preencha:

- Payload URL: https://SEU_NGROK_URL/webhook/github

- Content type: application/json

- Secret: o mesmo do .env

- Events: selecione push (ou outros)

Após salvar, faça um git push no repositório => o evento aparece em Recent Deliveries e nos logs do seu servidor.

# 6. Solução de Problemas
- 6.1 401 Unauthorized
  - O GitHub está usando um secret diferente do .env.

-   Verifique GITHUB_WEBHOOK_SECRET.

-   Confirme que o payload chega com header X-Hub-Signature-256.


- 6.2 500 Internal Server Error

- Veja o traceback no terminal onde roda o uvicorn.

Normalmente indica problema de formatação de payload ou erro interno no processamento.

- 6.3 Variáveis não carregam

  - Execute:
    -       python -c "from app.config import GITHUB_WEBHOOK_SECRET; print(repr(GITHUB_WEBHOOK_SECRET))"


# 7. Extensões Futuras

Este projeto será expandido para:

- Persistência em arquivo JSON/JSONL.

- Persistência em SQLite ou PostgreSQL.

- Notificações em Telegram, Discord ou Slack.

- Dashboard web com histórico de eventos.

- Execução Dockerizada.