"""Ingestão de dados espaciais com integridade e autenticidade (Req #2).

Cada lote ingerido (CSV de focos de calor vindo do FIRMS/INPE) é:
  1. copiado para um diretório versionado por timestamp;
  2. resumido por **hash SHA-256**;
  3. **assinado digitalmente** (RSA-PSS) com a chave privada da plataforma.

A verificação (`verify_batch`) recomputa o hash e confere a assinatura contra a
**âncora de confiança** (chave pública em `keys/`) — separada do artefato, como manda
o modelo de certificado digital. Assim, adulteração de dado em trânsito é detectada.
"""
from __future__ import annotations

import base64
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from . import crypto

DEFAULT_KEYS = "keys"
DEFAULT_BATCHES = "data/batches"


def _contar_registros(content: bytes) -> int:
    linhas = [l for l in content.splitlines() if l.strip()]
    return max(len(linhas) - 1, 0)  # menos o cabeçalho


def ingest_csv(
    csv_path: str | Path,
    keys_dir: str | Path = DEFAULT_KEYS,
    out_dir: str | Path = DEFAULT_BATCHES,
) -> dict:
    """Ingere um CSV, gera o lote versionado + manifesto assinado. Retorna o manifesto."""
    csv_path = Path(csv_path)
    content = csv_path.read_bytes()

    priv, _pub = crypto.ensure_keypair(keys_dir)
    digest = crypto.sha256_bytes(content)
    signature = crypto.sign(content, priv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    batch_dir = Path(out_dir) / ts
    batch_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(csv_path, batch_dir / "focos.csv")

    manifest = {
        "source_filename": csv_path.name,
        "sha256": digest,
        "signature_b64": base64.b64encode(signature).decode(),
        "algorithm": "RSA-PSS-SHA256",
        "n_records": _contar_registros(content),
        "ingested_at": ts,
    }
    (batch_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return {"batch_dir": str(batch_dir), **manifest}


def verify_batch(
    batch_dir: str | Path, keys_dir: str | Path = DEFAULT_KEYS
) -> Tuple[bool, str]:
    """Verifica integridade (hash) e autenticidade (assinatura) de um lote."""
    batch_dir = Path(batch_dir)
    try:
        manifest = json.loads((batch_dir / "manifest.json").read_text(encoding="utf-8"))
        content = (batch_dir / "focos.csv").read_bytes()
    except FileNotFoundError:
        return False, "lote incompleto: arquivo ou manifesto ausente"

    if crypto.sha256_bytes(content) != manifest["sha256"]:
        return False, "hash divergente: o conteudo foi alterado/adulterado"

    pub_path = Path(keys_dir) / "public_key.pem"
    if not pub_path.exists():
        return False, "chave publica de confianca ausente"
    pub = pub_path.read_bytes()
    sig = base64.b64decode(manifest["signature_b64"])
    if not crypto.verify_signature(content, sig, pub):
        return False, "assinatura invalida: origem nao confiavel ou dado adulterado"

    return True, "lote integro e autentico"


def latest_batch(out_dir: str | Path = DEFAULT_BATCHES) -> Optional[Path]:
    base = Path(out_dir)
    if not base.exists():
        return None
    subs = sorted(p for p in base.iterdir() if p.is_dir())
    return subs[-1] if subs else None


def load_batch_df(batch_dir: str | Path) -> pd.DataFrame:
    return pd.read_csv(Path(batch_dir) / "focos.csv")
