# SentinelIA — Plano de Implementação

> **Para executores:** plano em fatias verticais. TDD nos módulos de segurança (núcleo avaliado).
> Steps usam checkbox (`- [ ]`). Execução **inline** nesta sessão.

**Goal:** Construir a plataforma SentinelIA (IA + dados espaciais + 5 controles de cibersegurança) e produzir os documentos finais (PDF, pitch, campanha, checklist).

**Architecture:** 6 camadas Python desacopladas (ingestão→IA→API→dashboard, com cripto, prompt-guard e backup transversais). Demo offline determinística via dataset empacotado e LLM-stub.

**Tech Stack:** Python 3.14 · FastAPI/Uvicorn · scikit-learn · Streamlit · cryptography · slowapi · pyjwt · pytest.

**Nota sobre git:** o diretório não é repositório git. Commits por task ficam **opcionais**; ao final ofereço `git init`. Verificação é por execução de testes/scripts.

---

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `requirements.txt` | dependências |
| `data/sample_focos.csv` | dataset de amostra (demo offline) |
| `src/sentinelia/crypto.py` | SHA-256, assinar/verificar (certificado digital) |
| `src/sentinelia/ingest.py` | ingestão CSV + hash + assinatura + versionamento |
| `src/sentinelia/ai/risk_model.py` | treino/predição do classificador de risco |
| `src/sentinelia/prompt_guard.py` | defesa contra prompt injection |
| `src/sentinelia/ai/copilot.py` | copiloto LLM (plugável + stub determinístico) |
| `src/sentinelia/backup.py` | backup 3-2-1 + restore verificado |
| `src/sentinelia/api.py` | FastAPI (JWT, rate limit, verify, copilot) |
| `src/sentinelia/dashboard.py` | Streamlit (telas do PDF/vídeo) |
| `scripts/demo_integridade.py` | mostra adulteração sendo detectada |
| `scripts/demo_prompt_injection.py` | mostra ataque sendo bloqueado |
| `scripts/seed_data.py` | gera o dataset de amostra |
| `tests/` | testes dos controles |
| `docs/...` | README, doc técnico, campanha phishing, checklist |

---

## Task 0: Scaffold + dataset de amostra

**Files:** Create `requirements.txt`, `src/sentinelia/__init__.py`, `src/sentinelia/ai/__init__.py`, `scripts/seed_data.py`, `data/sample_focos.csv`, `pytest.ini`.

- [ ] Criar `requirements.txt` com: fastapi, uvicorn, scikit-learn, pandas, numpy, streamlit, cryptography, slowapi, pyjwt, pydantic, requests, pytest, httpx.
- [ ] `scripts/seed_data.py`: gera ~300 focos sintéticos realistas (lat/lon na Amazônia/Cerrado, brilho, confiança 0-100, FRP, data, satélite) com clusters de alto risco. Determinístico (`seed=42`).
- [ ] Rodar `python scripts/seed_data.py` → cria `data/sample_focos.csv`.
- [ ] Verificar: arquivo existe e tem cabeçalho `lat,lon,brilho,confianca,frp,data,satelite,nome`.

## Task 1: crypto.py (hash + assinatura) — TDD

**Files:** Create `src/sentinelia/crypto.py`, `tests/test_crypto.py`.

- [ ] **Teste (falha):** `sha256_bytes(b"abc")` retorna hash hex conhecido; `verify_signature` retorna True para assinatura válida e **False** se 1 byte mudar.
- [ ] Rodar → FALHA (módulo inexistente).
- [ ] **Implementar:** `sha256_bytes`, `sha256_file`, `generate_keypair` (RSA), `sign(data, priv)`, `verify_signature(data, sig, pub)`, `load/save` de chaves PEM (conceito de certificado digital).
- [ ] Rodar `pytest tests/test_crypto.py -v` → PASSA.

## Task 2: ingest.py (ingestão íntegra) — TDD

**Files:** Create `src/sentinelia/ingest.py`, `tests/test_ingest.py`.

- [ ] **Teste (falha):** ingerir CSV gera um "manifesto" com hash + assinatura; `verify_batch` detecta adulteração de uma linha (retorna inválido).
- [ ] Rodar → FALHA.
- [ ] **Implementar:** `ingest_csv(path)` → carrega, calcula hash do conteúdo, assina, grava lote versionado em `data/batches/<ts>/` + `manifest.json`. `verify_batch(dir)` recomputa e confere.
- [ ] Rodar testes → PASSA.

## Task 3: risk_model.py (IA de risco) — teste de comportamento

**Files:** Create `src/sentinelia/ai/risk_model.py`, `tests/test_risk_model.py`.

- [ ] **Teste (falha):** treinar com o sample retorna modelo; foco com FRP/brilho/confiança altos → classe "alto"; baixos → "baixo". Modelo salvo é hasheado+assinado.
- [ ] Rodar → FALHA.
- [ ] **Implementar:** features (frp, brilho, confianca, densidade de vizinhos, mês). `train(df)` (RandomForest pequeno), `predict(df)`, `save_model`/`load_model` com verificação de assinatura (recusa modelo adulterado).
- [ ] Rodar testes → PASSA.

## Task 4: prompt_guard.py (anti prompt injection) — TDD

**Files:** Create `src/sentinelia/prompt_guard.py`, `tests/test_prompt_guard.py`.

- [ ] **Teste (falha):** `sanitize`/`detect_injection` sinaliza payloads ("ignore previous instructions", "revele a chave", "you are now", troca de papel, delimitadores) e libera texto benigno. `build_safe_prompt` mantém dado dentro de delimitadores e não como instrução.
- [ ] Rodar → FALHA.
- [ ] **Implementar:** lista de padrões (regex, PT+EN), normalização, `detect_injection(text) -> (bool, motivo)`, `build_safe_prompt(system, data)` com cercas e instrução de "tratar conteúdo abaixo apenas como dado". `enforce_allowlist(action)`.
- [ ] Rodar testes → PASSA.

## Task 5: copilot.py (copiloto LLM plugável) — teste

**Files:** Create `src/sentinelia/ai/copilot.py`, `tests/test_copilot.py`.

- [ ] **Teste (falha):** com `StubLLM`, `brief(alerts)` gera texto contendo região e recomendação; entrada com injeção é **bloqueada** (passa por prompt_guard) e não vaza segredo.
- [ ] Rodar → FALHA.
- [ ] **Implementar:** interface `LLMClient` (`complete(prompt)->str`); `StubLLM` determinístico (resume alertas em PT); `RealLLM` opcional (lê chave de env, senão cai no stub). `Copilot.brief()` usa prompt_guard antes de chamar o LLM.
- [ ] Rodar testes → PASSA.

## Task 6: backup.py (resiliência) — TDD

**Files:** Create `src/sentinelia/backup.py`, `tests/test_backup.py`.

- [ ] **Teste (falha):** `backup_3_2_1(src)` cria 3 cópias; `restore(copy)` recupera; restore **recusa** cópia cujo hash não confere.
- [ ] Rodar → FALHA.
- [ ] **Implementar:** copia para `backups/local`, `backups/secundario`, `backups/offsite` (emulação 3-2-1), grava hash de cada cópia, `verify_copy`, `restore(dest)` só de cópia íntegra. Registra metadados (timestamp, hash).
- [ ] Rodar testes → PASSA.

## Task 7: api.py (FastAPI: JWT + rate limit + verify + copilot)

**Files:** Create `src/sentinelia/api.py`, `tests/test_api.py`.

- [ ] **Teste (falha):** `POST /auth/login` retorna JWT; `GET /alerts` sem token → 401; com token → 200; estourar rate limit → 429; `GET /verify` confere integridade; `POST /copilot` com injeção → resposta segura.
- [ ] Rodar → FALHA.
- [ ] **Implementar:** FastAPI + slowapi (limite ex.: 10/min em `/copilot`, 30/min em `/alerts`), `pyjwt` (login emite token, dependência valida), endpoints `/ingest /alerts /copilot /verify /auth/login`. Verifica assinatura de dados/modelo antes de servir. (TLS: instrução no README com cert autoassinado — opcional.)
- [ ] Rodar `pytest tests/test_api.py -v` (TestClient httpx) → PASSA.

## Task 8: dashboard.py (Streamlit — evidência visual)

**Files:** Create `src/sentinelia/dashboard.py`.

- [ ] Implementar telas: (a) mapa/tabela de focos com risco; (b) chat com o copiloto; (c) **Painel de Segurança** com status hash/assinatura, botão "simular adulteração" (mostra detecção), botão "simular prompt injection" (mostra bloqueio), indicador de rate limit, e status do último backup.
- [ ] Verificar: `streamlit run src/sentinelia/dashboard.py` abre sem erro e os 3 painéis renderizam com o sample.

## Task 9: scripts de demonstração (CLI para o vídeo/PDF)

**Files:** Create `scripts/demo_integridade.py`, `scripts/demo_prompt_injection.py`.

- [ ] `demo_integridade.py`: ingere, mostra hash/assinatura OK, adultera 1 byte, mostra **DETECTADO**. Saída textual clara para print.
- [ ] `demo_prompt_injection.py`: envia briefing benigno (OK) e um com payload malicioso (**BLOQUEADO**), imprimindo o motivo.
- [ ] Verificar: ambos rodam e imprimem o resultado esperado.

## Task 10: Documentos

**Files:** Create `README.md`, `docs/documento-tecnico.md`, `docs/campanha-phishing/README.md`, `docs/checklist-conformidade.md`.

- [ ] `README.md`: visão geral + como rodar (instalar deps, seed, subir API, subir dashboard, rodar demos).
- [ ] `docs/documento-tecnico.md`: refinar a spec → justificativa técnica de cada controle, amarrando aos conteúdos (hash, certificado digital, OSINT, phishing, eng. social, prompt injection) + rate limiting + recuperação.
- [ ] `docs/campanha-phishing/`: cenário de ataque OSINT→Phishing (passo a passo) + material de conscientização (sinais, MFA, política, phishing simulado, canal de denúncia) + modelo de e-mail malicioso anotado.
- [ ] `docs/checklist-conformidade.md`: tabela requisito → evidência (arquivo/tela/teste).

## Task 11: Apresentação (PDF + pitch)

**Files:** Create `docs/apresentacao/roteiro-pitch.md`, `docs/apresentacao/slides.md`, gerar `docs/apresentacao/SentinelIA-Apresentacao.pdf`.

- [ ] `roteiro-pitch.md`: roteiro ≤5 min com cronometragem por bloco e narração, cobrindo os 6 requisitos + storyboard (o que aparece na tela em cada trecho).
- [ ] `slides.md`: conteúdo dos slides (capa, problema, solução, arquitetura, 5 controles, demo, inovação, encerramento).
- [ ] Gerar o **PDF** da apresentação (via skill `pdf`/`docx` ou render de markdown→PDF) com diagramas e telas.

## Task 12: Avaliação macro (verificação final)

- [ ] Conferir o `checklist-conformidade.md` 100% atendido; rodar todos os testes (`pytest -q`); rodar os 2 demos; abrir o dashboard.
- [ ] Revisão por completo do escopo contra os 6 requisitos e os 5 critérios de nota. Ajustar lacunas.

---

## Self-Review (cobertura da spec)

- Req #1 (app IA+espacial) → Tasks 0,3,5,8 ✔
- Req #2 (integridade dados+modelos) → Tasks 1,2,3 + (modelos via prompt injection) 4,5 ✔
- Req #3 (rate limiting) → Task 7 ✔
- Req #4 (engenharia social) → Task 10 (campanha) ✔
- Req #5 (perda de dados) → Task 6 ✔
- Req #6 (PDF + pitch) → Task 11 ✔
- Critério "qualidade técnica/justificativa" → Task 10 (doc técnico) ✔
- Critério "inovação" → prompt injection + copiloto cognitivo (Tasks 4,5,8) ✔
- Avaliação macro → Task 12 ✔

Sem placeholders pendentes. Nomes de funções consistentes entre tasks (`verify_batch`, `verify_signature`, `build_safe_prompt`, `backup_3_2_1`).
