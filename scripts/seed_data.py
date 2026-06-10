"""Gera um dataset de amostra determinístico de focos de calor (queimadas).

Simula dados que viriam do NASA FIRMS / INPE BDQueimadas (tabular).
Usa apenas a biblioteca padrão para rodar antes da instalação das dependências.

Saída: data/sample_focos.csv com colunas:
    lat, lon, brilho, confianca, frp, data, satelite, nome, risco

O rótulo `risco` (baixo/medio/alto) é derivado das features com ruído, simulando
um histórico de focos confirmados — é o que o classificador aprende a prever.

Uso:
    python scripts/seed_data.py
"""
from __future__ import annotations

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
N_FOCOS = 320

# Regiões reais de bioma brasileiro (nome, lat base, lon base)
REGIOES = [
    ("Floresta Amazonica - PA", -3.5, -52.0),
    ("Cerrado - MT", -12.5, -56.0),
    ("Amazonia - RO", -10.0, -63.0),
    ("Amazonia - AM", -4.0, -65.0),
    ("Cerrado - TO", -10.0, -48.5),
    ("Pantanal - MS", -18.0, -56.5),
    ("Amazonia - AC", -9.5, -69.0),
    ("Maranhao (MATOPIBA) - MA", -5.5, -45.5),
]
SATELITES = ["VIIRS_NOAA20", "VIIRS_SNPP", "MODIS_AQUA", "MODIS_TERRA"]


def _gerar_pontos(rng: random.Random):
    pontos = []
    inicio = date(2025, 8, 1)  # estação seca
    for _ in range(N_FOCOS):
        nome, lat0, lon0 = rng.choice(REGIOES)
        # cluster em torno da região
        lat = lat0 + rng.uniform(-1.2, 1.2)
        lon = lon0 + rng.uniform(-1.2, 1.2)
        # alguns clusters quentes (alta intensidade)
        quente = rng.random() < 0.30
        if quente:
            frp = rng.uniform(120, 300)
            brilho = rng.uniform(360, 420)
            confianca = rng.uniform(70, 100)
        else:
            frp = rng.uniform(2, 130)
            brilho = rng.uniform(300, 365)
            confianca = rng.uniform(20, 90)
        dia = inicio + timedelta(days=rng.randint(0, 90))
        sat = rng.choice(SATELITES)
        pontos.append(
            {
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "brilho": round(brilho, 1),
                "confianca": int(confianca),
                "frp": round(frp, 1),
                "data": dia.isoformat(),
                "satelite": sat,
                "nome": nome,
            }
        )
    return pontos


def _densidade(pontos, i, raio=0.5):
    """Conta vizinhos dentro de `raio` graus (proxy de densidade do foco)."""
    p = pontos[i]
    n = 0
    for j, q in enumerate(pontos):
        if i == j:
            continue
        d = math.hypot(p["lat"] - q["lat"], p["lon"] - q["lon"])
        if d <= raio:
            n += 1
    return n


def _derivar_risco(brilho, confianca, frp, densidade, rng: random.Random):
    score = (
        0.40 * (frp / 300.0)
        + 0.30 * (confianca / 100.0)
        + 0.20 * ((brilho - 300.0) / 120.0)
        + 0.10 * min(densidade / 12.0, 1.0)
    )
    score += rng.uniform(-0.07, 0.07)  # ruído: rótulo não é função perfeita das features
    if score >= 0.60:
        return "alto"
    if score >= 0.34:
        return "medio"
    return "baixo"


def main() -> None:
    rng = random.Random(SEED)
    pontos = _gerar_pontos(rng)
    for i, p in enumerate(pontos):
        dens = _densidade(pontos, i)
        p["densidade"] = dens
        p["risco"] = _derivar_risco(p["brilho"], p["confianca"], p["frp"], dens, rng)

    out = Path(__file__).resolve().parents[1] / "data" / "sample_focos.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    campos = ["lat", "lon", "brilho", "confianca", "frp", "data", "satelite", "nome", "risco"]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for p in pontos:
            w.writerow(p)

    dist = {"baixo": 0, "medio": 0, "alto": 0}
    for p in pontos:
        dist[p["risco"]] += 1
    print(f"OK: {len(pontos)} focos gravados em {out}")
    print(f"Distribuicao de risco: {dist}")


if __name__ == "__main__":
    main()
