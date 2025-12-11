from fastapi import FastAPI, Header, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import hmac, hashlib, json, logging, traceback
from .notifier import send_telegram_message
from .config import GITHUB_WEBHOOK_SECRET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compute_hmac_sha256(secret: str, body: bytes) -> str:
    mac = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha256)
    return "sha256=" + mac.hexdigest()

def compute_hmac_sha1(secret: str, body: bytes) -> str:
    mac = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha1)
    return "sha1=" + mac.hexdigest()

def verify_signature(request_body: bytes, signature_header: str | None, secret: str) -> bool:
    if not signature_header:
        return False
    signature_header = signature_header.strip()
    expected_sha256 = compute_hmac_sha256(secret, request_body)
    expected_sha1 = compute_hmac_sha1(secret, request_body)
    if hmac.compare_digest(signature_header, expected_sha256):
        return True
    if hmac.compare_digest(signature_header, expected_sha1):
        return True
    logger.info("Signature mismatch. Received: %s | Expected sha256: %s | Expected sha1: %s",
                signature_header, expected_sha256, expected_sha1)
    return False

app = FastAPI()

# CORS — permite que o frontend (Vite) faça requests durante o desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],  # "*" aceitável em dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento em memória (dev). Mantemos apenas últimos N eventos.
MAX_EVENTS = 200
events_log: list[dict] = []

@app.post("/webhook/github")
async def github_webhook(request: Request,
                         x_hub_signature_256: str | None = Header(None),
                         x_hub_signature: str | None = Header(None),
                         x_github_event: str | None = Header(None),
                         x_github_delivery: str | None = Header(None)):
    body = await request.body()
    logger.info("Delivery: %s Event: %s Sig256: %s Sig1: %s", x_github_delivery, x_github_event, x_hub_signature_256, x_hub_signature)
    signature_to_check = x_hub_signature_256 or x_hub_signature

    if not verify_signature(body, signature_to_check, GITHUB_WEBHOOK_SECRET):
        logger.warning("Unauthorized webhook call - signature verification failed.")
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(body.decode("utf-8"))
        event = x_github_event or "unknown"

        # montar texto (mantive sua lógica)
        if event == "push":
            repo = payload.get("repository", {}).get("full_name")
            pusher = payload.get("pusher", {}).get("name")
            commits = payload.get("commits", [])
            commit_msgs = "\n".join(f"- {c.get('message')} ({c.get('id')[:7]})" for c in commits[:5])
            text = f"📌 Push em {repo}\nPor: {pusher}\nCommits:\n{commit_msgs}"
            await send_telegram_message(text)

        elif event == "pull_request":
            action = payload.get("action")
            pr = payload.get("pull_request", {})
            title = pr.get("title")
            number = pr.get("number")
            user = pr.get("user", {}).get("login")
            text = f"🔀 PR {action}: #{number} — {title} por {user}"
            await send_telegram_message(text)

        else:
            logger.info("Evento não tratado: %s", event)

        # --- salvar no log em memória para o frontend ---
        try:
            events_log.append({
                "event": event,
                "payload": payload
            })
            # manter tamanho do buffer
            if len(events_log) > MAX_EVENTS:
                del events_log[0: len(events_log) - MAX_EVENTS]
        except Exception:
            logger.exception("Falha ao adicionar evento ao events_log")

        return {"status": "ok"}

    except Exception as exc:
        tb = traceback.format_exc()
        logger.error("Erro ao processar webhook: %s\nTraceback:\n%s", exc, tb)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/events")
def get_events():

    return events_log
