"""Gera figuras reais (a partir dos dados classificados) para o PDF/slides.

Saídas em docs/apresentacao/img/: mapa.png, distribuicao.png, features.png

Uso:  python scripts/gerar_figuras.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from sentinelia import crypto  # noqa: E402
from sentinelia.ai import risk_model  # noqa: E402

CORES = {"alto": "#d62728", "medio": "#ff7f0e", "baixo": "#2ca02c"}
IMG = ROOT / "docs" / "apresentacao" / "img"


def main() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    crypto.ensure_keypair(ROOT / "keys")
    df = pd.read_csv(ROOT / "data" / "sample_focos.csv")
    mp = ROOT / "models" / "risk.pkl"
    try:
        clf = risk_model.load_model(mp, keys_dir=ROOT / "keys")
    except Exception:
        clf = risk_model.train(df, model_path=mp, keys_dir=ROOT / "keys")
    dfc = risk_model.classify_df(clf, df)

    # Figura 1 — mapa de focos por risco
    fig, ax = plt.subplots(figsize=(7, 6), dpi=130)
    for risco, cor in CORES.items():
        sub = dfc[dfc["risco_previsto"] == risco]
        ax.scatter(sub["lon"], sub["lat"], c=cor, s=18, alpha=0.75, label=risco, edgecolors="none")
    ax.set_title("SentinelIA — Focos de calor classificados por risco (IA)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(title="Risco")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(IMG / "mapa.png")
    plt.close(fig)

    # Figura 2 — distribuição de risco
    dist = dfc["risco_previsto"].value_counts().reindex(["alto", "medio", "baixo"]).fillna(0)
    fig, ax = plt.subplots(figsize=(6, 4), dpi=130)
    ax.bar(dist.index, dist.values, color=[CORES[k] for k in dist.index])
    ax.set_title("Distribuicao de risco dos focos")
    ax.set_ylabel("Quantidade")
    for i, v in enumerate(dist.values):
        ax.text(i, v + 1, str(int(v)), ha="center")
    fig.tight_layout()
    fig.savefig(IMG / "distribuicao.png")
    plt.close(fig)

    # Figura 3 — importância das features do modelo
    imp = pd.Series(clf.feature_importances_, index=risk_model.FEATURES).sort_values()
    fig, ax = plt.subplots(figsize=(6, 4), dpi=130)
    ax.barh(imp.index, imp.values, color="#1f77b4")
    ax.set_title("Importancia das features (modelo de risco)")
    ax.set_xlabel("Importancia")
    fig.tight_layout()
    fig.savefig(IMG / "features.png")
    plt.close(fig)

    print("OK — figuras geradas em", IMG)


if __name__ == "__main__":
    main()
