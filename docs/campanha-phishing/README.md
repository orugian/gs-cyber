# Engenharia Social: Ataque (OSINT → Phishing) e Campanha de Conscientização

> **Requisito #4** — Conteúdos estudados: **OSINT, Phishing, Engenharia Social**.
> Material educacional/defensivo para a SentinelIA (contexto acadêmico autorizado).

A defesa técnica mais forte falha se um analista entregar a própria senha. Esta seção mostra
**como o ataque acontece** e entrega uma **campanha de conscientização e proteção**.

---

## Parte 1 — Como o ataque é realizado

### Etapa 1 — Reconhecimento (OSINT)
O atacante coleta informações públicas, sem invadir nada:
- **LinkedIn / sites institucionais**: nomes, cargos e e-mails dos analistas da plataforma
  ("Analista de Monitoramento Ambiental — SentinelIA").
- **Vazamentos de dados** (have-i-been-pwned, combolists): e-mails e senhas reaproveitadas.
- **Metadados** de PDFs/relatórios públicos: padrão de e-mail (`nome.sobrenome@empresa`),
  software usado, nomes de servidores.
- **Redes sociais**: rotina, viagens, fornecedores, vocabulário interno — para criar um pretexto
  convincente.

> Resultado do OSINT: uma lista de alvos + um **pretexto** plausível ("auditoria de segurança",
> "atualização urgente do sistema").

### Etapa 2 — Pretexto e isca (Phishing)
O atacante envia um e-mail que imita a TI da SentinelIA, criando **urgência** e **autoridade**,
com um link para uma **página de login clonada** que captura as credenciais.

### Etapa 3 — Coleta de credenciais
A vítima digita usuário e senha na página falsa. O atacante captura e, se não houver **MFA**,
acessa o painel real — podendo **adulterar alertas**, **silenciar focos de queimada** ou
**exfiltrar dados**.

### Etapa 4 — Impacto
- Decisões erradas em emergências ambientais (focos reais "sumindo" do painel);
- Vazamento de dados sensíveis;
- Uso do acesso como ponte para ataques internos (movimento lateral).

### Exemplo de e-mail malicioso (anotado)

```
De:  suporte-sentinelia@sentinel1a-seguranca.com      ← (1) domínio falso (sentinel1a, com "1")
Para: ana.souza@sentinelia.gov.br
Assunto: [URGENTE] Sua conta SentinelIA será bloqueada em 24h   ← (2) urgência artificial

Prezada Ana Souza,                                     ← (3) personalizado (veio do OSINT)

Detectamos um acesso suspeito à sua conta. Por segurança,
confirme suas credenciais em até 24 horas ou seu acesso
ao painel de monitoramento será suspenso.

>> Confirmar minha conta agora <<                      ← (4) link para página clonada
   (https://sentinel1a-seguranca.com/login)            ← (5) URL não-oficial

Atenciosamente,
Equipe de Segurança SentinelIA                         ← (6) assina como "TI", sem canal verificável
```

**Sinais de fraude:** (1) domínio parecido mas falso; (2) urgência/ameaça; (3) personalização
obtida por OSINT; (4)(5) link/URL fora do domínio oficial; (6) remetente não verificável.

---

## Parte 2 — Campanha de Conscientização e Proteção

### Mensagem central
> **"A SentinelIA NUNCA pede sua senha por e-mail. Na dúvida, não clique — verifique e denuncie."**

### Como reconhecer um phishing (treinar todos os analistas)
1. **Cheque o remetente e o domínio** (passe o mouse — não clique). Domínios "quase iguais" são
   o sinal nº 1.
2. **Desconfie de urgência e ameaça** ("em 24h", "será bloqueado").
3. **Confira o link antes de clicar** — o texto pode ser diferente do destino real.
4. **Nunca digite senha** a partir de link de e-mail; acesse o sistema pela URL oficial salva.
5. **Anexos inesperados** = perigo (macros, .html, .zip).
6. **Erros sutis** de português, saudação genérica, pedido fora do processo normal.

### Defesas técnicas que quebram a cadeia do ataque
- **MFA (autenticação multifator)** — mesmo com a senha roubada, o atacante não entra.
- **Gestor de senhas** — não preenche credenciais em domínio falso (detecta a URL errada).
- **Menor privilégio** — analista só acessa o necessário; reduz o impacto de uma conta comprometida.
- **DMARC/DKIM/SPF** — dificulta a falsificação do domínio oficial.
- **Alertas de "e-mail externo"** e bloqueio de domínios *lookalike*.

### Programa contínuo (não é evento único)
- **Phishing simulado** trimestral, com métrica de cliques e feedback imediato (sem punir; educar).
- **Microtreinamentos** de 5 min e cartaz/【1-pager】fixado (abaixo).
- **Canal de denúncia fácil**: botão "Reportar phishing" no e-mail + e-mail `abuse@sentinelia`.
- **Resposta a incidente**: quem clicou troca a senha, revoga sessões e avisa a equipe — **sem
  medo de punição** (cultura de reporte).

### 1-pager (cartão de bolso)
```
┌──────────────────────────────────────────────┐
│  PAROU? PENSOU? CLICOU NÃO!                    │
│  ✔ Confira o DOMÍNIO do remetente              │
│  ✔ Urgência/ameaça = DESCONFIE                 │
│  ✔ NUNCA digite senha vinda de link de e-mail  │
│  ✔ Ative o MFA                                 │
│  ✔ Na dúvida: REPORTE (botão / abuse@sentinelia)│
│  A SentinelIA nunca pede sua senha por e-mail. │
└──────────────────────────────────────────────┘
```

### Indicadores de sucesso da campanha
- Queda na **taxa de cliques** do phishing simulado;
- Aumento das **denúncias** (sinal de vigilância ativa);
- 100% das contas com **MFA** habilitado.
