"""Copiloto LLM cognitivo (Req #1) protegido contra prompt injection (Req #2).

Transforma os alertas de risco em um *briefing* de decisão em linguagem natural.
O cliente de LLM é **plugável**:
  - `StubLLM`  — determinístico e offline (padrão), garante demo confiável;
  - `RealLLM`  — integra um provedor real se `SENTINELIA_LLM=real` e houver chave.

Toda entrada passa por `prompt_guard` ANTES de chegar ao modelo: tentativas de injeção
são bloqueadas e registradas, e o dado entra sempre delimitado como não confiável.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional, Protocol

import pandas as pd

from .. import prompt_guard


@dataclass
class BriefResult:
    texto: str
    bloqueado: bool = False
    motivo: str = ""
    prompt_usado: str = ""


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...


class StubLLM:
    """LLM determinístico local: extrai o resumo do prompt e devolve um briefing."""

    name = "stub-local"

    def complete(self, prompt: str) -> str:
        def num(chave: str, default: str = "0") -> str:
            m = re.search(rf"{chave}=([0-9.]+)", prompt)
            return m.group(1) if m else default

        total, alto, medio, baixo = num("total"), num("alto"), num("medio"), num("baixo")
        frp = num("frp_max")
        m_reg = re.search(r"regioes_alto=([^\n<>]*)", prompt)
        regioes = (m_reg.group(1).strip() if m_reg else "") or "nenhuma"
        return "\n".join(
            [
                "BRIEFING DE DECISAO — SentinelIA",
                f"- Focos analisados: {total} (alto={alto}, medio={medio}, baixo={baixo}).",
                f"- FRP maximo observado: {frp} MW.",
                f"- Regioes criticas (alto risco): {regioes}.",
                "- Recomendacao: acionar brigadas nas regioes de alto risco e priorizar "
                "sobrevoo onde o FRP for mais elevado; monitorar evolucao nas proximas 24h.",
            ]
        )


class RealLLM:
    """Cliente para provedor real de LLM (placeholder). Sem chave, levanta erro controlado."""

    name = "real"

    def __init__(self, model: str = "claude-haiku-4-5") -> None:
        self.model = model

    def complete(self, prompt: str) -> str:  # pragma: no cover - exige rede/chave
        raise RuntimeError("Provedor de LLM real nao configurado (use o StubLLM para a demo).")


def get_llm() -> LLMClient:
    """Retorna o LLM real se configurado e com chave; senão o stub determinístico."""
    if os.getenv("SENTINELIA_LLM") == "real" and os.getenv("ANTHROPIC_API_KEY"):
        try:
            return RealLLM()
        except Exception:
            return StubLLM()
    return StubLLM()


def summarize_alerts(df: pd.DataFrame, risco_col: str = "risco_previsto") -> dict:
    """Resume um DataFrame classificado em métricas para o briefing."""
    col = risco_col if risco_col in df.columns else "risco"
    counts = df[col].value_counts().to_dict()
    regioes_alto: List[str] = []
    if "nome" in df.columns:
        regioes_alto = df.loc[df[col] == "alto", "nome"].value_counts().index.tolist()[:5]
    return {
        "total": int(len(df)),
        "alto": int(counts.get("alto", 0)),
        "medio": int(counts.get("medio", 0)),
        "baixo": int(counts.get("baixo", 0)),
        "frp_max": round(float(df["frp"].max()), 1) if "frp" in df.columns else 0.0,
        "regioes_alto": regioes_alto,
    }


@dataclass
class Copilot:
    llm: Optional[LLMClient] = None
    bloqueios: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.llm is None:
            self.llm = get_llm()

    def brief(self, summary: dict, question: str = "") -> BriefResult:
        # Vetores de injeção: pergunta do usuário + nomes vindos dos dados de satélite.
        suspeito = " ".join(
            [question or ""] + [str(r) for r in summary.get("regioes_alto", [])]
        )
        detectado, motivo = prompt_guard.detect_injection(suspeito)
        if detectado:
            self.bloqueios.append(motivo)
            return BriefResult(
                texto=(
                    "Solicitacao BLOQUEADA pela defesa anti prompt-injection. "
                    "Conteudo suspeito neutralizado; nenhum dado sensivel foi exposto."
                ),
                bloqueado=True,
                motivo=motivo,
            )

        dados = (
            f"total={summary.get('total', 0)}; alto={summary.get('alto', 0)}; "
            f"medio={summary.get('medio', 0)}; baixo={summary.get('baixo', 0)}; "
            f"frp_max={summary.get('frp_max', 0)}; "
            f"regioes_alto={', '.join(map(str, summary.get('regioes_alto', []))) or 'nenhuma'}\n"
            f"pergunta={question}"
        )
        safe = prompt_guard.build_safe_prompt(dados)
        texto = self.llm.complete(safe)
        return BriefResult(texto=texto, bloqueado=False, prompt_usado=safe)
