# Checklist de Conformidade — SentinelIA × Global Solution 2026.1

Mapeia cada **requisito** e **critério de avaliação** do desafio à **evidência** concreta na
solução (arquivo, teste, script ou tela). Base para a avaliação macro final.

## Requisitos técnicos (enunciado)

| # | Requisito | Atendido? | Evidência |
|---|---|:---:|---|
| 1 | Aplicação alinhada ao tema (IA + dados espaciais + segurança) | ✅ | `risk_model.py` (IA), `data/sample_focos.csv` (focos orbitais), `dashboard.py`, `copilot.py` |
| 2a | Proteção contra manipulação de **dados** em trânsito | ✅ | `crypto.py` + `ingest.py`; `demo_integridade.py`; `test_crypto.py`, `test_ingest.py` |
| 2b | Proteção contra manipulação de **modelos** | ✅ | `risk_model.load_model` (recusa modelo adulterado); `test_risk_model.py` |
| 2c | Verificação de integridade (em trânsito) | ✅ | endpoint `GET /verify`; hash SHA-256 + assinatura RSA-PSS + X.509 |
| 3 | Proteção contra abuso (rate limiting) + entes externos + importância | ✅ | `api.py` (slowapi, 429); `test_api.py::test_rate_limit_retorna_429`; doc técnico §3.4 |
| 4 | Engenharia Social: ataque + campanha de conscientização | ✅ | `docs/campanha-phishing/README.md` (OSINT→Phishing + campanha) |
| 5 | Perda de dados: cenários + estratégias de recuperação | ✅ | `backup.py` (3-2-1); `test_backup.py`; doc técnico §3.6 |
| 6 | Apresentação em PDF + pitch (vídeo ≤5 min) com encadeamento | ✅ | `docs/apresentacao/` (roteiro, slides, PDF) |

## Critérios de avaliação (pontuação)

| Critério | Pts | Como a solução pontua |
|---|:---:|---|
| Alinhamento ao tema (dados espaciais + IA + Nova Economia Espacial) | 2 | Plataforma de queimadas com IA + copiloto cognitivo, narrativa ambiental |
| Implementação dos controles de segurança | 3 | 5 controles **funcionais e testados** (49 testes verdes) |
| Qualidade técnica e justificativa | 2 | `documento-tecnico.md` (modelo de ameaças + justificativa por controle) |
| Inovação | 2 | Defesa contra **Prompt Injection** no copiloto + modelo de IA assinado |
| Apresentação/Pitch | 1 | Roteiro cronometrado + slides + PDF, encadeando os 6 requisitos |

## Conteúdos estudados (cobertura)

| Conteúdo | Coberto? | Onde |
|---|:---:|---|
| OSINT | ✅ | campanha (etapa de reconhecimento) |
| Prompt Injection | ✅ | `prompt_guard.py`, `demo_prompt_injection.py` |
| Phishing | ✅ | campanha (e-mail anotado + defesas) |
| Engenharia Social | ✅ | campanha (ataque + conscientização) |
| hash | ✅ | `crypto.sha256_*` em ingestão/modelo/backup |
| certificado digital | ✅ | `crypto.generate_self_signed_cert` + assinatura/verificação |

## Verificação executável (como o avaliador confirma)

```powershell
pytest -q                                   # 49 testes dos controles
python scripts/demo_integridade.py          # adulteração detectada
python scripts/demo_prompt_injection.py     # prompt injection bloqueado
streamlit run src/sentinelia/dashboard.py   # evidência visual (3 painéis)
$env:PYTHONPATH="src"; uvicorn sentinelia.api:app  # API + /docs + 429
```

**Status global:** todos os requisitos e critérios atendidos com evidência reproduzível.
