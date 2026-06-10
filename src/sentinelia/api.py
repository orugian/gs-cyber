"""API da plataforma (FastAPI) — superfície de acesso com controles de segurança.

Reúne os requisitos:
  - #1: serve alertas classificados pela IA e o copiloto cognitivo;
  - #2: endpoint `/verify` confere integridade (hash+assinatura) de dados e modelo;
  - #3: **rate limiting** (slowapi) por IP nos endpoints sensíveis + login (anti brute force);
        autenticação por **JWT**.

Inicialização é preguiçosa (`get_state`) para funcionar tanto em produção quanto em testes.
"""
from __future__ import annotations

import hmac
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import jwt
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from . import crypto, ingest
from .ai import copilot as copilot_mod
from .ai import risk_model

# --------------------------------------------------------------------------- #
# Configuração
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "sample_focos.csv"
KEYS = ROOT / "keys"
MODEL_PATH = ROOT / "models" / "risk.pkl"
BATCHES = ROOT / "data" / "batches"

JWT_SECRET = os.getenv("SENTINELIA_JWT_SECRET", "segredo-de-demo-troque-em-producao")
JWT_ALGO = "HS256"
JWT_TTL_MIN = 30

# Credenciais de demonstração (em produção: store + Argon2/bcrypt, nunca em código).
DEMO_USER = os.getenv("SENTINELIA_USER", "analista")
DEMO_PASS = os.getenv("SENTINELIA_PASS", "sentinela2026")

limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer(auto_error=False)
STATE: dict = {}


# --------------------------------------------------------------------------- #
# Inicialização do estado (dados + modelo + alertas)
# --------------------------------------------------------------------------- #
def init_state() -> dict:
    crypto.ensure_keypair(KEYS)
    manifest = ingest.ingest_csv(DATA, keys_dir=KEYS, out_dir=BATCHES)
    df = pd.read_csv(DATA)
    try:
        clf = risk_model.load_model(MODEL_PATH, keys_dir=KEYS)
    except Exception:
        clf = risk_model.train(df, model_path=MODEL_PATH, keys_dir=KEYS)
    classified = risk_model.classify_df(clf, df)
    summary = copilot_mod.summarize_alerts(classified, risco_col="risco_previsto")
    STATE.update(
        clf=clf,
        df=classified,
        summary=summary,
        batch_dir=manifest["batch_dir"],
        copilot=copilot_mod.Copilot(),
    )
    return STATE


def get_state() -> dict:
    if not STATE:
        init_state()
    return STATE


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_state()
    yield


app = FastAPI(title="SentinelIA API", version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --------------------------------------------------------------------------- #
# Autenticação JWT
# --------------------------------------------------------------------------- #
def _make_token(sub: str) -> str:
    payload = {
        "sub": sub,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_TTL_MIN),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    if creds is None:
        raise HTTPException(status_code=401, detail="token ausente")
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="token invalido ou expirado")
    return payload["sub"]


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #
class LoginIn(BaseModel):
    username: str
    password: str


class CopilotIn(BaseModel):
    question: str = ""


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
@app.get("/health")
def health():
    return {"status": "ok", "servico": "SentinelIA"}


@app.post("/auth/login")
@limiter.limit("20/minute")  # anti credential stuffing / brute force
def login(request: Request, body: LoginIn):
    user_ok = hmac.compare_digest(body.username, DEMO_USER)
    pass_ok = hmac.compare_digest(body.password, DEMO_PASS)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="credenciais invalidas")
    return {"access_token": _make_token(body.username), "token_type": "bearer"}


@app.get("/alerts")
@limiter.limit("60/minute")
def alerts(request: Request, user: str = Depends(current_user)):
    st = get_state()
    df = st["df"]
    top = (
        df[df["risco_previsto"] == "alto"]
        .sort_values("frp", ascending=False)
        .head(10)[["lat", "lon", "frp", "confianca", "nome", "risco_previsto", "score"]]
        .to_dict(orient="records")
    )
    return {"resumo": st["summary"], "top_alertas": top}


@app.post("/copilot")
@limiter.limit("30/minute")
def copilot_endpoint(request: Request, body: CopilotIn, user: str = Depends(current_user)):
    st = get_state()
    result = st["copilot"].brief(st["summary"], question=body.question)
    return {
        "briefing": result.texto,
        "bloqueado": result.bloqueado,
        "motivo": result.motivo,
    }


@app.get("/verify")
def verify(request: Request, user: str = Depends(current_user)):
    st = get_state()
    dados_ok, dados_motivo = ingest.verify_batch(st["batch_dir"], keys_dir=KEYS)
    try:
        risk_model.load_model(MODEL_PATH, keys_dir=KEYS)
        modelo_ok, modelo_motivo = True, "assinatura do modelo confere"
    except Exception as exc:  # IntegrityError ou ausência
        modelo_ok, modelo_motivo = False, str(exc)
    return {
        "dados_integros": dados_ok,
        "dados_motivo": dados_motivo,
        "modelo_integro": modelo_ok,
        "modelo_motivo": modelo_motivo,
    }


@app.get("/demo/rate-limit")
@limiter.limit("3/minute")  # endpoint dedicado para demonstrar o rate limiting
def demo_rate_limit(request: Request):
    return {"ok": True, "dica": "chame varias vezes para ver o 429 (Too Many Requests)"}
