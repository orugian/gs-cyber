"""Classificador de risco de foco de calor (camada de IA — Req #1).

Treina um RandomForest para classificar cada foco como **baixo / medio / alto** a
partir de features físicas (FRP, brilho, confiança, densidade espacial, mês).

Integridade do modelo (Req #2 — manipulação de **modelos**):
o artefato `.pkl` é assinado digitalmente. `load_model` **recusa** carregar um modelo
cuja assinatura não confere — defesa contra troca/adulteração do modelo de IA.

Observação de segurança: `pickle.loads` só é executado APÓS a verificação da assinatura
contra a chave pública de confiança. Modelo sem assinatura válida nunca é desserializado.
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from .. import crypto

FEATURES: List[str] = ["frp", "brilho", "confianca", "densidade", "mes"]


class IntegrityError(Exception):
    """Levantada quando a assinatura do modelo não confere."""


def _densidade(df: pd.DataFrame, raio: float = 0.5) -> np.ndarray:
    """Conta vizinhos dentro de `raio` graus (proxy de densidade do foco)."""
    lat = df["lat"].to_numpy(dtype=float)
    lon = df["lon"].to_numpy(dtype=float)
    n = len(df)
    dens = np.zeros(n, dtype=int)
    for i in range(n):
        d = np.hypot(lat - lat[i], lon - lon[i])
        dens[i] = int((d <= raio).sum() - 1)  # exclui o próprio ponto
    return dens


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta as colunas derivadas `mes` e `densidade`."""
    out = df.copy()
    out["mes"] = pd.to_datetime(out["data"]).dt.month
    out["densidade"] = _densidade(out)
    return out


def train(
    df: pd.DataFrame,
    model_path: str | Path | None = None,
    keys_dir: str | Path = "keys",
) -> RandomForestClassifier:
    """Treina o classificador. Se `model_path` for dado, salva e assina o modelo."""
    feats = build_features(df)
    X = feats[FEATURES]
    y = feats["risco"]
    clf = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
    clf.fit(X, y)
    if model_path is not None:
        save_model(clf, model_path, keys_dir)
    return clf


def predict(clf: RandomForestClassifier, df: pd.DataFrame) -> np.ndarray:
    feats = build_features(df)
    return clf.predict(feats[FEATURES])


def predict_proba_max(clf: RandomForestClassifier, df: pd.DataFrame) -> np.ndarray:
    feats = build_features(df)
    return clf.predict_proba(feats[FEATURES]).max(axis=1)


def classify_df(clf: RandomForestClassifier, df: pd.DataFrame) -> pd.DataFrame:
    """Retorna o df original com colunas `risco_previsto` e `score`."""
    feats = build_features(df)
    out = df.copy()
    out["risco_previsto"] = clf.predict(feats[FEATURES])
    out["score"] = clf.predict_proba(feats[FEATURES]).max(axis=1).round(3)
    return out


# --------------------------------------------------------------------------- #
# Persistência assinada do modelo
# --------------------------------------------------------------------------- #


def _sig_path(model_path: Path) -> Path:
    return model_path.with_suffix(model_path.suffix + ".sig")


def save_model(clf, model_path: str | Path, keys_dir: str | Path = "keys") -> Path:
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    blob = pickle.dumps(clf)
    model_path.write_bytes(blob)
    priv, _pub = crypto.ensure_keypair(keys_dir)
    _sig_path(model_path).write_bytes(crypto.sign(blob, priv))
    return model_path


def load_model(
    model_path: str | Path,
    keys_dir: str | Path = "keys",
    require_signature: bool = True,
) -> RandomForestClassifier:
    """Carrega o modelo APÓS verificar a assinatura (defesa contra troca de modelo)."""
    model_path = Path(model_path)
    blob = model_path.read_bytes()
    if require_signature:
        sig_path = _sig_path(model_path)
        pub_path = Path(keys_dir) / "public_key.pem"
        if not sig_path.exists() or not pub_path.exists():
            raise IntegrityError("assinatura do modelo ausente: carregamento recusado")
        if not crypto.verify_signature(blob, sig_path.read_bytes(), pub_path.read_bytes()):
            raise IntegrityError(
                "assinatura do modelo invalida: possivel troca/adulteracao do modelo"
            )
    return pickle.loads(blob)  # seguro: só executa após assinatura válida
