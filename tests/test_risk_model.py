"""Testes do classificador de risco (Req #1) e da integridade do modelo (Req #2)."""
from pathlib import Path

import pandas as pd
import pytest

from sentinelia.ai import risk_model

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_focos.csv"


def _df():
    return pd.read_csv(SAMPLE)


def test_acuracia_treino_razoavel():
    clf = risk_model.train(_df())
    preds = risk_model.predict(clf, _df())
    acc = (preds == _df()["risco"]).mean()
    assert acc > 0.80


def test_alto_tem_frp_medio_maior_que_baixo():
    df = _df()
    clf = risk_model.train(df)
    classificado = risk_model.classify_df(clf, df)
    frp_alto = classificado.loc[classificado["risco_previsto"] == "alto", "frp"].mean()
    frp_baixo = classificado.loc[classificado["risco_previsto"] == "baixo", "frp"].mean()
    assert frp_alto > frp_baixo


def test_modelo_salvo_assinado_carrega(tmp_path):
    mp = tmp_path / "model.pkl"
    risk_model.train(_df(), model_path=mp, keys_dir=tmp_path / "keys")
    clf = risk_model.load_model(mp, keys_dir=tmp_path / "keys")
    assert clf is not None


def test_modelo_adulterado_e_recusado(tmp_path):
    mp = tmp_path / "model.pkl"
    risk_model.train(_df(), model_path=mp, keys_dir=tmp_path / "keys")
    # atacante substitui/adultera o artefato do modelo
    mp.write_bytes(mp.read_bytes() + b"payload-malicioso")
    with pytest.raises(risk_model.IntegrityError):
        risk_model.load_model(mp, keys_dir=tmp_path / "keys")
