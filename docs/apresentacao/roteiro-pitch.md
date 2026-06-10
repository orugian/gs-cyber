# Roteiro do Pitch — SentinelIA (Vídeo de até 5 minutos)

> **Objetivo:** Gravar um vídeo fluido, demonstrando a solução e conectando os controles de segurança.
> **Duração Alvo:** ~4 minutos e 45 segundos.
> **Cadência:** Fala natural, sem pressa. Em média, 130 palavras por minuto.

---

## 🎬 Resumo do Cronograma

| Bloco | Duração | Tema Abordado | Requisito do Desafio |
| :--- | :--- | :--- | :--- |
| **01** | 0:00 - 0:45 | Introdução e Alinhamento | Req #1 (IA + Espacial) |
| **02** | 0:45 - 1:45 | Integridade (Dados e Modelos) | Req #2 (Manipulação) |
| **03** | 1:45 - 2:30 | Inovação (Prompt Injection) | Req Inovação |
| **04** | 2:30 - 3:15 | Abuso e Rate Limiting | Req #3 (Rate Limit) |
| **05** | 3:15 - 4:00 | O Fator Humano (Phishing) | Req #4 (Eng. Social) |
| **06** | 4:00 - 4:45 | Resiliência (Backup 3-2-1) e Fim | Req #5 (Perda de dados) |

---

## 📝 Detalhamento das Passagens (Cena a Cena)

### 🔴 Bloco 1: Introdução à Nova Economia Espacial (0:00 - 0:45)
**Visão da Tela (O que gravar):**
*   Inicie com a sua webcam (rosto).
*   Depois de 10 segundos, transição para mostrar a tela inicial do **Dashboard (Streamlit)** da SentinelIA rodando (mapa ou painel de análise).

**Áudio (O que falar):**
> "Olá! Sejam bem-vindos à apresentação da **SentinelIA**. 
> Na Nova Economia Espacial, informações orbitais deixaram de ser exclusividade da ciência e passaram a ditar decisões críticas aqui na Terra. A nossa plataforma ingere dados de satélite sobre focos de calor e desmatamento, e utiliza Inteligência Artificial para classificar o risco e emitir alertas por meio de um Copiloto cognitivo.
> Mas se a nossa solução ajuda a coordenar times de emergência, ela precisa ser 100% confiável. Se um atacante adulterar os dados orbitais ou a nossa IA, as decisões tomadas serão catastróficas. Por isso, construímos a SentinelIA com segurança desde a concepção."

---

### 🔴 Bloco 2: Proteção contra Manipulação de Dados e Modelos (0:45 - 1:45)
**Visão da Tela (O que gravar):**
*   Mostrar o terminal. Executar o script de integridade: `python scripts/demo_integridade.py`
*   Mostrar o código `crypto.py` rapidamente, destacando a função de assinatura.

**Áudio (O que falar):**
> "O primeiro vetor de ataque é a manipulação dos dados em trânsito. Como garantimos que o foco de queimada não foi alterado? 
> Nós implementamos **Hash SHA-256 em conjunto com Assinatura Digital RSA e certificados X.509**. Quando ingerimos os dados ou carregamos nosso modelo de IA treinado, o sistema confere a integridade. 
> *[Aponte para o terminal rodando]* Vejam a demonstração: quando simulamos a alteração de apenas um bit no arquivo de focos de incêndio, ou tentamos injetar um modelo de Inteligência Artificial malicioso, a assinatura digital é invalidada imediatamente e o sistema recusa o carregamento. Nenhuma informação corrompida entra na plataforma."

---

### 🔴 Bloco 3: Inovação - Proteção Cognitiva contra Prompt Injection (1:45 - 2:30)
**Visão da Tela (O que gravar):**
*   Terminal rodando o script: `python scripts/demo_prompt_injection.py`
*   Mostrar o log do terminal bloqueando um ataque.

**Áudio (O que falar):**
> "Como diferencial e inovação, protegemos a camada cognitiva da nossa IA. Como o Copiloto processa texto gerado por usuários e relatórios externos, ele é vulnerável a **Prompt Injection**.
> Um atacante poderia tentar sequestrar as instruções do nosso bot inserindo comandos escondidos para ignorar o seu papel e revelar dados sensíveis. Para impedir isso, implementamos um *Prompt Guard* estrutural. Ele separa rigorosamente o que é *dado* do que é *instrução*, filtra caracteres de controle e possui uma heurística para detecção. Como vemos no terminal, o ataque é identificado e o comando malicioso é neutralizado."

---

### 🔴 Bloco 4: Proteção da API contra Abuso (2:30 - 3:15)
**Visão da Tela (O que gravar):**
*   Tela dividida ou navegador. Mostrar uma ferramenta (como Postman/Thunder Client) ou script tentando fazer vários logins/buscas seguidas.
*   Focar no status **HTTP 429 Too Many Requests**.

**Áudio (O que falar):**
> "A SentinelIA expõe seus dados via API, o que atrai entes externos: bots, scrapers copiando nossa base de dados, concorrentes minerando inteligência e tentativas de ataques de força-bruta para roubo de senhas. 
> Para proteger contra esse abuso, implementamos **Rate Limiting** rigoroso atrelado a autenticação JWT. 
> Se um bot tenta inundar nossa API para esgotar nossos recursos, ele atinge o limite instantaneamente e recebe um erro *429 Too Many Requests*, como demonstrado aqui. Isso previne o esgotamento da nossa conta de nuvem e ataques de Negação de Serviço."

---

### 🔴 Bloco 5: Engenharia Social e Conscientização (3:15 - 4:00)
**Visão da Tela (O que gravar):**
*   Mostrar o PDF/Slide ou a marcação em Markdown do **Cartão de Bolso (1-pager)** da campanha de conscientização.
*   Mostrar brevemente a estrutura do ataque no `README` de phishing.

**Áudio (O que falar):**
> "Nenhuma defesa técnica funciona se o atacante conseguir a senha dos nossos analistas.
> Modelamos um ataque onde o cibercriminoso utiliza **OSINT** nas redes sociais e em vazamentos públicos para criar um pretexto convincente. A partir disso, ele envia um e-mail de **Phishing** exigindo uma atualização urgente de credenciais em um site falso. 
> Para combater isso, desenvolvemos uma **Campanha de Conscientização contínua**. Nossos analistas são treinados a checar domínios, desconfiar do senso de urgência, não usar links de e-mail e utilizar o botão de denúncia. Além disso, exigimos o uso de **Múltiplos Fatores de Autenticação (MFA)** para que, mesmo com a senha vazada, o acesso seja negado."

---

### 🔴 Bloco 6: Resiliência, Perda de Dados e Conclusão (4:00 - 4:45)
**Visão da Tela (O que gravar):**
*   Mostrar o código `backup.py` rodando os testes (`pytest tests/test_backup.py`).
*   Voltar para sua imagem na webcam (rosto) para finalizar.

**Áudio (O que falar):**
> "Por fim, projetamos estratégias robustas caso a plataforma sofra perda de dados, seja por falhas no provedor, exclusão acidental ou ataques de **Ransomware**. 
> Operamos com a arquitetura de **Backup 3-2-1**: três cópias, em duas mídias distintas, com uma *off-site*. Crucialmente, nosso script de restauração não aceita qualquer arquivo; ele verifica novamente a **hash e a assinatura** do backup antes do *restore*.
>
> Assim, a SentinelIA entrega inovação espacial guiada por IA, mas com a resiliência e a blindagem necessárias para o mundo real. Muito obrigado por assistir!"

---

## 💡 Dicas de Execução para o Apresentador:
1. **Ambiente:** Deixe todos os scripts (`demo_integridade.py`, `demo_prompt_injection.py`, API e Dashboard) abertos e prontos em abas do VS Code/Terminal antes de iniciar a gravação.
2. **Edição:** Você pode gravar o áudio e a tela separadamente e juntar depois, ou usar o OBS Studio para transitar entre a sua webcam e a tela fluidamente.
3. **Naturalidade:** Não precisa ler o texto de forma engessada. Use as falas propostas acima como guia e use suas próprias palavras mantendo o "cerne" da mensagem de segurança.
