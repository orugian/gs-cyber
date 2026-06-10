"""Resiliência e recuperação de dados (Req #5).

Implementa a estratégia **3-2-1** (3 cópias, em destinos distintos, sendo uma "off-site"
— aqui emulada por diretórios separados). Cada cópia é verificada por **hash SHA-256**.

Situações de perda cobertas: ransomware, corrupção de disco, exclusão acidental, falha de
hardware. A restauração (`restore`) só aceita uma cópia cujo hash confere — se todas
estiverem corrompidas, falha de forma segura (não restaura lixo).
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from . import crypto

# 3 cópias em 2 "mídias" lógicas + 1 off-site (emulação da regra 3-2-1)
DEST_NAMES = ["local", "secundario", "offsite"]


class RecoveryError(Exception):
    """Levantada quando não há cópia íntegra para restaurar."""


def backup_3_2_1(src_file: str | Path, base_dir: str | Path = "backups") -> dict:
    """Cria 3 cópias do arquivo e registra o manifesto com o hash de referência."""
    src_file = Path(src_file)
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    content_hash = crypto.sha256_file(src_file)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    copies: Dict[str, str] = {}
    for nome in DEST_NAMES:
        dst_dir = base / nome
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / src_file.name
        shutil.copyfile(src_file, dst)
        copies[nome] = str(dst)

    manifest = {
        "source": src_file.name,
        "sha256": content_hash,
        "timestamp": ts,
        "strategy": "3-2-1",
        "copies": copies,
    }
    (base / "backup_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return manifest


def _load_manifest(base_dir: str | Path) -> dict:
    return json.loads((Path(base_dir) / "backup_manifest.json").read_text(encoding="utf-8"))


def verify_copy(copy_path: str | Path, expected_hash: str) -> bool:
    copy_path = Path(copy_path)
    if not copy_path.exists():
        return False
    return crypto.sha256_file(copy_path) == expected_hash


def list_intact_copies(base_dir: str | Path = "backups") -> Dict[str, bool]:
    """Retorna, por cópia, se ela está íntegra (hash confere)."""
    manifest = _load_manifest(base_dir)
    return {nome: verify_copy(p, manifest["sha256"]) for nome, p in manifest["copies"].items()}


def restore(dest_path: str | Path, base_dir: str | Path = "backups") -> Path:
    """Restaura a partir da primeira cópia íntegra encontrada. Falha se todas corrompidas."""
    manifest = _load_manifest(base_dir)
    expected = manifest["sha256"]
    for nome in DEST_NAMES:
        p = manifest["copies"].get(nome)
        if p and verify_copy(p, expected):
            dest_path = Path(dest_path)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest_path)
            return dest_path
    raise RecoveryError("nenhuma copia integra disponivel para restauracao")
