import uvicorn
import os
import sys
import webbrowser
import threading
import time

import socket

def find_available_port(start_port=8000):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Se não conseguir conectar, a porta está livre
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        port += 1

def open_browser(port):
    time.sleep(2)
    webbrowser.open(f"http://127.0.0.1:{port}")

# Ajustar o path para o PyInstaller localizar os arquivos embutidos
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
    os.chdir(application_path)
else:
    # Subir um diretório já que o script agora está dentro de interface/
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(application_path)

from interface.api.app import app

if __name__ == "__main__":
    port = find_available_port(8000)
    print("======================================================")
    print("  SIMULADOR DE AUTOMATOS - SERVIDOR LOCAL             ")
    print("======================================================")
    print(f"Iniciando motor Python e interface React na porta {port}...")
    
    # Abre o navegador em background
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    # Inicia o servidor uvicorn (não usamos auto-reload no executável)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
