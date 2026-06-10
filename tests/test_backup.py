"""Testes de resiliência e recuperação (Req #5)."""
from pathlib import Path

import pytest

from sentinelia import backup


def test_backup_cria_tres_copias_integras(tmp_path):
    src = tmp_path / "dados.csv"
    src.write_text("a,b\n1,2\n", encoding="utf-8")
    m = backup.backup_3_2_1(src, base_dir=tmp_path / "bk")
    assert len(m["copies"]) == 3
    intact = backup.list_intact_copies(tmp_path / "bk")
    assert all(intact.values())


def test_restore_recupera_apos_exclusao(tmp_path):
    src = tmp_path / "dados.csv"
    src.write_text("conteudo importante", encoding="utf-8")
    backup.backup_3_2_1(src, base_dir=tmp_path / "bk")
    src.unlink()  # exclusão acidental / perda do original
    dest = backup.restore(tmp_path / "restaurado.csv", base_dir=tmp_path / "bk")
    assert dest.read_text(encoding="utf-8") == "conteudo importante"


def test_restore_usa_copia_integra_quando_uma_corrompe(tmp_path):
    src = tmp_path / "dados.csv"
    src.write_text("original", encoding="utf-8")
    m = backup.backup_3_2_1(src, base_dir=tmp_path / "bk")
    # ransomware corrompe a cópia local; secundário/off-site permanecem
    Path(m["copies"]["local"]).write_text("corrompido", encoding="utf-8")
    dest = backup.restore(tmp_path / "out.csv", base_dir=tmp_path / "bk")
    assert dest.read_text(encoding="utf-8") == "original"


def test_restore_recusa_quando_tudo_corrompido(tmp_path):
    src = tmp_path / "dados.csv"
    src.write_text("x", encoding="utf-8")
    m = backup.backup_3_2_1(src, base_dir=tmp_path / "bk")
    for p in m["copies"].values():  # todas as cópias corrompidas
        Path(p).write_text("corrompido", encoding="utf-8")
    with pytest.raises(backup.RecoveryError):
        backup.restore(tmp_path / "out.csv", base_dir=tmp_path / "bk")
