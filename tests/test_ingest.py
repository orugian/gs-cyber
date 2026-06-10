"""Testes de ingestão íntegra (Req #2)."""
from pathlib import Path

from sentinelia import crypto, ingest

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_focos.csv"


def test_ingest_gera_manifesto_e_verifica(tmp_path):
    res = ingest.ingest_csv(SAMPLE, keys_dir=tmp_path / "keys", out_dir=tmp_path / "batches")
    assert res["n_records"] == 320
    assert res["algorithm"] == "RSA-PSS-SHA256"
    ok, motivo = ingest.verify_batch(res["batch_dir"], keys_dir=tmp_path / "keys")
    assert ok is True, motivo


def test_verify_detecta_adulteracao_de_conteudo(tmp_path):
    res = ingest.ingest_csv(SAMPLE, keys_dir=tmp_path / "keys", out_dir=tmp_path / "batches")
    focos = Path(res["batch_dir"]) / "focos.csv"
    # atacante esconde uma queimada de alto risco
    dados = focos.read_text(encoding="utf-8").replace("alto", "baixo", 1)
    focos.write_text(dados, encoding="utf-8")
    ok, motivo = ingest.verify_batch(res["batch_dir"], keys_dir=tmp_path / "keys")
    assert ok is False
    assert "alterado" in motivo or "adulterado" in motivo


def test_verify_detecta_chave_de_origem_diferente(tmp_path):
    # lote assinado com um conjunto de chaves, verificado com OUTRA âncora -> rejeita
    res = ingest.ingest_csv(SAMPLE, keys_dir=tmp_path / "keysA", out_dir=tmp_path / "batches")
    crypto.ensure_keypair(tmp_path / "keysB")  # âncora de confiança diferente
    ok, motivo = ingest.verify_batch(res["batch_dir"], keys_dir=tmp_path / "keysB")
    assert ok is False
    assert "assinatura" in motivo
