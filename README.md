# SentinelIA — Inteligência Espacial Cognitiva + Cibersegurança

> **Global Solution 2026.1 — Cognitive Cybersecurity**
> Disciplina: Cybersecurity | Curso: Tecnólogo em IA — 1TIAPZ-2026
> Tema: *Soluções Cognitivas para a Nova Economia Espacial*

---

## Para o Professor — Guia de Avaliação

Este repositório contém a entrega completa do desafio Global Solution 2026.1.
A plataforma **SentinelIA** ingere **dados espaciais de focos de calor** (queimadas/desmatamento — padrão NASA FIRMS/INPE), classifica o **risco** com IA e oferece um **copiloto cognitivo** que gera *briefings* de decisão automatizada.

Toda a solução foi construída com foco em **cibersegurança**: cada requisito do enunciado é implementado como código funcional e coberto por testes automatizados.

---

## Mapa Rápido: Requisito → Evidência

| # | Requisito do Enunciado | Onde encontrar | Como verificar |
|---|---|---|---|
| 1 | Aplicação com IA + dados espaciais | `src/sentinelia/ai/`, `data/sample_focos.csv` | `streamlit run src/sentinelia/dashboard.py` |
| 2a | Proteção contra manipulação de **dados** | `src/sentinelia/crypto.py`, `ingest.py` | `python scripts/demo_integridade.py` |
| 2b | Proteção contra manipulação de **modelos** de IA | `src/sentinelia/ai/risk_model.py` | `pytest tests/test_risk_model.py -v` |
| 2c | Verificação em trânsito (SHA-256 + RSA + X.509) | `src/sentinelia/crypto.py` | `pytest tests/test_crypto.py -v` |
| 3 | Rate limiting + JWT + entes externos | `src/sentinelia/api.py` | `pytest tests/test_api.py -v` |
| 4 | Engenharia Social: ataque OSINT→Phishing + campanha | `docs/campanha-phishing/README.md` | Leitura direta |
| 5 | Perda de dados: cenários + estratégia 3-2-1 | `src/sentinelia/backup.py` | `pytest tests/test_backup.py -v` |
| 6 | Defesa contra Prompt Injection (inovação) | `src/sentinelia/prompt_guard.py` | `python scripts/demo_prompt_injection.py` |
| — | Apresentação / Pitch | `docs/apresentacao/` | Leitura direta |

Para um mapa detalhado com todos os critérios de avaliação e pontuação, ver [`docs/checklist-conformidade.md`](docs/checklist-conformidade.md).

---

## Como Executar (Passo a Passo)

> **Pré-requisito:** Python 3.11. As dependências têm *wheels* garantidas nessa versão.

```powershell
# 1. Ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Gerar o dataset de amostra (determinístico, offline)
python scripts/seed_data.py
```

### Rodar todos os testes (49 testes dos controles de segurança)

```powershell
pytest -q
```

Resultado esperado: **49 passed** — cobre todos os controles de segurança.

### Subir o dashboard (evidência visual)

```powershell
streamlit run src/sentinelia/dashboard.py
```

Abre em `http://localhost:8501` — painel de focos, risco por IA e copiloto cognitivo.

### Subir a API REST

```powershell
$env:PYTHONPATH = "src"
uvicorn sentinelia.api:app --port 8000
```

Documentação interativa: `http://localhost:8000/docs` | Login demo: `analista / sentinela2026`

### Demonstrações para o vídeo/PDF

```powershell
# Adulteração de dados é detectada automaticamente
python scripts/demo_integridade.py

# Prompt injection é bloqueado pelo copiloto
python scripts/demo_prompt_injection.py
```

---

## Estrutura do Repositório

```
GS-Cyber/
├── README.md                        ← este arquivo
├── GS.md                            ← enunciado original do desafio
├── GS.pdf                           ← PDF do enunciado
├── requirements.txt
├── pytest.ini
│
├── src/sentinelia/                  ← código-fonte principal
│   ├── crypto.py                    ← SHA-256, assinatura RSA-PSS, certificado X.509
│   ├── ingest.py                    ← ingestão de dados orbitais com verificação de hash
│   ├── prompt_guard.py              ← defesa contra Prompt Injection
│   ├── api.py                       ← FastAPI + rate limiting (slowapi) + JWT
│   ├── backup.py                    ← estratégia de backup 3-2-1
│   ├── dashboard.py                 ← visualização Streamlit (3 painéis)
│   └── ai/
│       ├── risk_model.py            ← modelo de risco + verificação de integridade do .pkl
│       └── copilot.py               ← copiloto cognitivo (gera briefings)
│
├── scripts/
│   ├── seed_data.py                 ← gera dataset de amostra offline
│   ├── demo_integridade.py          ← demonstra detecção de adulteração
│   └── demo_prompt_injection.py     ← demonstra bloqueio de prompt injection
│
├── tests/                           ← 49 testes automatizados
│   ├── test_crypto.py
│   ├── test_ingest.py
│   ├── test_risk_model.py
│   ├── test_api.py
│   ├── test_backup.py
│   ├── test_prompt_guard.py
│   ├── test_copilot.py
│   └── test_dashboard.py
│
├── data/
│   └── sample_focos.csv             ← 320 focos rotulados (gerados offline)
│
├── models/
│   ├── risk.pkl                     ← modelo treinado (Random Forest)
│   └── risk.pkl.sig                 ← assinatura digital do modelo
│
└── docs/
    ├── documento-tecnico.md         ← justificativa técnica de cada controle
    ├── checklist-conformidade.md    ← mapa requisito → evidência → pontuação
    ├── campanha-phishing/
    │   └── README.md                ← ataque OSINT→Phishing + campanha de conscientização
    ├── apresentacao
    │   ├── slides.md
    │   └── img/                     ← figuras geradas (distribuição, features, mapa)
    ├── spec/
    │   └── 2026-06-07-sentinelia-design.md
    └── plan/
        └── 2026-06-07-sentinelia-implementacao.md
```

---

## Controles de Segurança Implementados

### 1. Integridade de Dados e Modelos (Requisito #2)

- **SHA-256** de cada lote de dados orbitais na ingestão
- **Assinatura RSA-PSS** com chave de 2048 bits
- **Certificado X.509** auto-assinado (estrutura real; em produção, emitido por CA)
- **Modelo `.pkl` assinado** — só é desserializado após verificação (defesa contra RCE por pickle)
- Qualquer adulteração levanta `DataIntegrityError` antes de qualquer processamento

### 2. Rate Limiting + Autenticação (Requisito #3)

- **JWT (HS256)** com expiração em 30 minutos
- **Rate limiting** com `slowapi`: 30 req/min no endpoint de análise
- Ultrapassar o limite retorna **HTTP 429** com header `Retry-After`
- Justificativa dos entes externos e importância: [`docs/documento-tecnico.md`](docs/documento-tecnico.md)

### 3. Engenharia Social (Requisito #4)

Conteúdo em [`docs/campanha-phishing/README.md`](docs/campanha-phishing/README.md):
- **Ataque completo**: OSINT → Pretexto → Phishing → Coleta de credenciais → Impacto
- **E-mail malicioso** anotado (sinaliza cada técnica de manipulação)
- **Campanha de conscientização**: treino, 1-pager, defesas técnicas (MFA, DMARC, etc.)

### 4. Backup e Recuperação (Requisito #5)

- Estratégia **3-2-1**: 3 cópias, 2 mídias distintas, 1 offsite
- Backup versionado com **hash de verificação** (detecta corrompimento)
- Cenários de perda cobertos: falha de hardware, ransomware, exclusão acidental, desastre físico

### 5. Defesa contra Prompt Injection (Inovação)

- Módulo `prompt_guard.py` filtra o input do copiloto antes de passar ao LLM
- Detecta padrões de *jailbreak* e instruções de sistema embutidas
- O LLM é **plugável**: usa stub offline por padrão; `SENTINELIA_LLM=real` + `ANTHROPIC_API_KEY` ativa provedor real

---

## Documentos da Entrega

| Documento | Caminho | Finalidade |
|---|---|---|
| Documento Técnico | [`docs/documento-tecnico.md`](docs/documento-tecnico.md) | Justificativa de cada controle de segurança |
| Checklist de Conformidade | [`docs/checklist-conformidade.md`](docs/checklist-conformidade.md) | Mapa requisito → evidência → critério de avaliação |
| Campanha Anti-Phishing | [`docs/campanha-phishing/README.md`](docs/campanha-phishing/README.md) | Ataque completo + conscientização (Req #4) |
| Enunciado | [`GS.md`](GS.md) / [`GS.pdf`](GS.pdf) | Desafio original |

---

## Integrantes

| Nome completo | RM |
|---|:---:|
| Guilherme Orugian | 572882 |
| Rodrigo Bettio | 573725 |
| Rafael Jun Aita Hirata | 569708 |


---

## Notas Técnicas (Honestidade Acadêmica)

- O certificado X.509 é **auto-assinado** (válido para demonstração; em produção, emitido por CA confiável como Let's Encrypt ou PKI corporativa).
- As senhas de demo estão em texto claro apenas para fins de avaliação — em produção, usaria **Argon2/bcrypt** e segredos em cofre (Vault, AWS Secrets Manager).
- O `pickle` do modelo só é desserializado **após** verificação de assinatura, mitigando RCE.
- `data/batches/` e `backups/` ficam no `.gitignore` (artefatos de runtime); as chaves privadas (`keys/`) também não são versionadas.
