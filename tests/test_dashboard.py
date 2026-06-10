"""Verificação headless do dashboard Streamlit (não deve levantar exceção ao renderizar)."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "src" / "sentinelia" / "dashboard.py")


def test_dashboard_renderiza_sem_excecao():
    at = AppTest.from_file(APP).run(timeout=90)
    assert not at.exception, at.exception


def test_dashboard_tem_titulo():
    at = AppTest.from_file(APP).run(timeout=90)
    titulos = [t.value for t in at.title]
    assert any("SentinelIA" in t for t in titulos)
