"""DEMO (Req #2): detecção de adulteração de dados em trânsito via hash + assinatura.

Uso:  python scripts/demo_integridade.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sentinelia import ingest  # noqa: E402


def main() -> None:
    sample = ROOT / "data" / "sample_focos.csv"
    print("=" * 64)
    print(" DEMO — Integridade de dados (hash SHA-256 + assinatura digital)")
    print("=" * 64)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        manifest = ingest.ingest_csv(sample, keys_dir=tmp / "keys", out_dir=tmp / "batches")
        print(f"\n[1] Lote ingerido: {manifest['n_records']} focos de calor")
        print(f"    SHA-256  : {manifest['sha256']}")
        print(f"    Algoritmo: {manifest['algorithm']}")

        ok, motivo = ingest.verify_batch(manifest["batch_dir"], keys_dir=tmp / "keys")
        print(f"\n[2] Verificacao inicial : {'INTEGRO' if ok else 'FALHA'} -> {motivo}")

        focos = Path(manifest["batch_dir"]) / "focos.csv"
        dados = focos.read_text(encoding="utf-8").replace("alto", "baixo", 1)
        focos.write_text(dados, encoding="utf-8")
        print("\n[3] ATAQUE: um foco de risco 'alto' foi alterado para 'baixo' no arquivo.")

        ok, motivo = ingest.verify_batch(manifest["batch_dir"], keys_dir=tmp / "keys")
        status = "INTEGRO" if ok else ">>> ADULTERACAO DETECTADA <<<"
        print(f"\n[4] Verificacao pos-ataque: {status}")
        print(f"    Motivo: {motivo}")

    print("\n=> Resultado: dados adulterados em transito sao REJEITADOS pela plataforma.\n")


if __name__ == "__main__":
    main()
