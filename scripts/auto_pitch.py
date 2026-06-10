import os
import sys
import time
import subprocess
from textwrap import dedent

def get_python_exe():
    """Obtém o executável python do ambiente virtual do projeto, se existir."""
    venv_path = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_path):
        return venv_path
    return "python"

PYTHON_EXE = get_python_exe()

def clear_screen():
    # Limpa a tela do terminal dependendo do SO (Windows ou Unix)
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    clear_screen()
    print("=" * 80)
    print(f" 🛰️  SENTINELIA - {title}")
    print("=" * 80)
    print("\n")

def main():
    clear_screen()
    print("=" * 80)
    print(" PREPARAÇÃO PARA GRAVAÇÃO DO PITCH ".center(80))
    print("=" * 80)
    print("\nInstruções:")
    print("1. Abra o OBS Studio e configure para gravar a Tela/Janela inteira.")
    print("2. Pegue o seu roteiro (roteiro-pitch.md).")
    print("3. Quando estiver pronto, ative a gravação no OBS.")
    print(f"\n[Aviso] Usando Python do projeto: {PYTHON_EXE}")
    print("\nIniciando a Automação do Pitch em 10 segundos...")
    
    for i in range(10, 0, -1):
        print(f"Começando em {i}...")
        time.sleep(1)
        
    # ---------------------------------------------------------
    # Bloco 1: Tema e Dashboard (0:45)
    # ---------------------------------------------------------
    print_header("Bloco 1: Introdução à Nova Economia Espacial")
    print(">>> Iniciando o Dashboard Streamlit (o navegador abrirá em instantes)...\n")
    
    # Subprocesso rodando o streamlit. Ele abre o navegador na porta padrão (8501).
    streamlit_cmd = [PYTHON_EXE, "-m", "streamlit", "run", "src/sentinelia/dashboard.py"]
    streamlit_proc = subprocess.Popen(streamlit_cmd)
    
    # Aguarda o tempo de carregamento do servidor antes de contar o tempo da apresentação
    print(">>> [Aguardando 10 segundos para o servidor carregar a tela...]")
    time.sleep(10)
    
    print(">>> [Dashboard no ar! Valendo 45 segundos para a locução do Bloco 1]")
    time.sleep(45)
    
    # Encerra o Streamlit
    print("\n>>> Encerrando o Dashboard e restaurando o foco ao Terminal...")
    streamlit_proc.terminate()
    try:
        streamlit_proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        streamlit_proc.kill()
        
    # MÁGICA: Automação no Windows para fechar a aba e voltar a tela pro terminal
    if os.name == 'nt':
        try:
            import ctypes
            # Ctrl+W (Fechar a aba do navegador)
            ctypes.windll.user32.keybd_event(0x11, 0, 0, 0) # Ctrl
            ctypes.windll.user32.keybd_event(0x57, 0, 0, 0) # W
            ctypes.windll.user32.keybd_event(0x57, 0, 2, 0)
            ctypes.windll.user32.keybd_event(0x11, 0, 2, 0)
            time.sleep(0.5)
            # Alt+Esc (Enviar a janela do navegador para o fundo do Windows, trazendo o Terminal de volta)
            ctypes.windll.user32.keybd_event(0x12, 0, 0, 0) # Alt
            ctypes.windll.user32.keybd_event(0x1B, 0, 0, 0) # Esc
            ctypes.windll.user32.keybd_event(0x1B, 0, 2, 0)
            ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
        except Exception:
            pass
            
    time.sleep(3)
    
    # ---------------------------------------------------------
    # Bloco 2: Integridade (0:45)
    # ---------------------------------------------------------
    print_header("Bloco 2: Integridade de Dados e Modelos")
    print(">>> Executando simulação de adulteração de focos e IA...\n")
    subprocess.run([PYTHON_EXE, "scripts/demo_integridade.py"])
    print("\n[Aguardando 25 segundos para a locução...]")
    time.sleep(25)
    
    # ---------------------------------------------------------
    # Bloco 3: Prompt Injection (0:45)
    # ---------------------------------------------------------
    print_header("Bloco 3: Inovação e Proteção Cognitiva")
    print(">>> Testando a defesa estrutural contra Prompt Injection no Copiloto...\n")
    subprocess.run([PYTHON_EXE, "scripts/demo_prompt_injection.py"])
    print("\n[Aguardando 25 segundos para a locução...]")
    time.sleep(25)
    
    # ---------------------------------------------------------
    # Bloco 4: Rate Limiting (0:45)
    # ---------------------------------------------------------
    print_header("Bloco 4: Proteção da API (Rate Limiting)")
    print(">>> Executando teste de abuso de requisições (Status HTTP 429)...\n")
    subprocess.run([PYTHON_EXE, "-m", "pytest", "tests/test_api.py::test_rate_limit_retorna_429", "-v", "--tb=short"])
    print("\n[Aguardando 25 segundos para a locução...]")
    time.sleep(25)
    
    # ---------------------------------------------------------
    # Bloco 5: Engenharia Social (0:45)
    # ---------------------------------------------------------
    print_header("Bloco 5: O Fator Humano (Engenharia Social e Phishing)")
    print(dedent("""
    [CARTÃO DE BOLSO - CAMPANHA DE CONSCIENTIZAÇÃO CONTINUADA]
    
    ┌──────────────────────────────────────────────┐
    │  PAROU? PENSOU? CLICOU NÃO!                  │
    │  ✔ Confira o DOMÍNIO do remetente            │
    │  ✔ Urgência/ameaça = DESCONFIE               │
    │  ✔ NUNCA digite senha vinda de link de e-mail│
    │  ✔ Ative o MFA                               │
    │  ✔ Na dúvida: REPORTE (botão / abuse@sentinelia)│
    │                                              │
    │  A SentinelIA nunca pede sua senha por e-mail. │
    └──────────────────────────────────────────────┘
    """))
    print("\n[Aguardando 25 segundos para a locução...]")
    time.sleep(25)
    
    # ---------------------------------------------------------
    # Bloco 6: Resiliência (0:45)
    # ---------------------------------------------------------
    print_header("Bloco 6: Resiliência e Recuperação de Dados")
    print(">>> Testando fluxo de Backup 3-2-1 e Restore Seguro Verificado...\n")
    subprocess.run([PYTHON_EXE, "-m", "pytest", "tests/test_backup.py", "-v", "--tb=short"])
    print("\n[Aguardando 25 segundos para a locução final...]")
    time.sleep(25)
    
    # ---------------------------------------------------------
    # Encerramento
    # ---------------------------------------------------------
    print_header("GRAVAÇÃO CONCLUÍDA")
    print("Você pode parar a gravação no OBS Studio agora.")
    print("Muito obrigado e sucesso na entrega da sua Global Solution!")

if __name__ == "__main__":
    # O set PYTHONIOENCODING garante emojis no windows terminal se aplicável
    os.environ["PYTHONIOENCODING"] = "utf-8"
    # Adiciona a pasta src ao PYTHONPATH para que os imports do pacote 'sentinelia' funcionem nos subprocessos
    os.environ["PYTHONPATH"] = os.path.abspath("src")
    main()
