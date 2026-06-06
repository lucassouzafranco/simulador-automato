import os
import sys
import time
import subprocess
import platform

def kill_process_on_port(port):
    try:
        if platform.system() == "Windows":
            # Executa netstat para encontrar conexões na porta correspondente
            output = subprocess.check_output("netstat -ano", shell=True).decode("utf-8", errors="ignore")
            pids = set()
            for line in output.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit() and int(pid) > 0:
                            pids.add(int(pid))
            
            for pid in pids:
                print(f"[Sistema] Detectado processo antigo ativo (PID {pid}) na porta {port}. Liberando porta...")
                subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Linux / macOS (Codespaces)
            try:
                output = subprocess.check_output(f"lsof -t -i:{port}", shell=True).decode("utf-8", errors="ignore")
                pids = [int(pid) for pid in output.strip().split() if pid.isdigit()]
                for pid in pids:
                    print(f"[Sistema] Detectado processo antigo ativo (PID {pid}) na porta {port}. Liberando porta...")
                    subprocess.run(f"kill -9 {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                # lsof retorna status != 0 se não encontrar nenhum processo ouvindo
                pass
    except Exception as e:
        print(f"[Sistema] Erro ao verificar/liberar porta {port}: {e}")

def main():
    print("[Sistema] Iniciando ambiente integrado de desenvolvimento...")
    
    # 1. Verificação e instalação automática de dependências Python (Auto-healing)
    try:
        import fastapi
        import uvicorn
        import pydantic
    except ImportError:
        print("[Sistema] Dependencias Python ausentes. Instalando via pip...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        except Exception as e:
            print(f"[Sistema] Erro ao instalar dependencias Python: {e}")
            
    # 2. Verificação e instalação automática de dependências npm (Auto-healing)
    import shutil
    has_npm = shutil.which('npm') is not None
    if has_npm:
        web_node_modules = os.path.join("web", "node_modules")
        if not os.path.exists(web_node_modules):
            print("[Sistema] Pasta web/node_modules ausente. Instalando dependencias npm...")
            try:
                subprocess.run("npm install", cwd="web", shell=True, check=True)
            except Exception as e:
                print(f"[Sistema] Erro ao instalar dependencias npm: {e}")
                
    # 3. Liberar portas se estiverem em uso para evitar conflito de inicialização
    kill_process_on_port(8000)  # FastAPI
    kill_process_on_port(5173)  # Vite
    
    backend_proc = None
    frontend_proc = None
    
    try:
        # 2. Iniciar o servidor Backend (FastAPI com Uvicorn)
        print("[Sistema] Iniciando Backend (FastAPI) na porta 8000...")
        backend_cmd = [
            sys.executable, "-m", "uvicorn", 
            "interface.api.app:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ]
        backend_proc = subprocess.Popen(backend_cmd)
        
        # Pequeno delay para permitir que a API comece a subir antes do frontend
        time.sleep(1.5)
        
        # 3. Iniciar o servidor Frontend (Vite ou Fallback Python)
        import shutil
        import webbrowser
        
        has_npm = shutil.which('npm') is not None
        
        if has_npm:
            print("[Sistema] Detectado Node.js/npm. Iniciando Frontend (React/Vite) na porta 5173...")
            # No Windows, precisamos usar shell=True porque npm é um comando em lote (.cmd)
            frontend_cmd = "npm --prefix web run dev"
            frontend_proc = subprocess.Popen(frontend_cmd, shell=True)
        else:
            print("[Sistema] Node.js/npm NAO detectado. Servindo build de producao com Python na porta 3000...")
            frontend_cmd = [
                sys.executable, "-m", "http.server", "3000",
                "--directory", "web/dist"
            ]
            frontend_proc = subprocess.Popen(frontend_cmd)
            
            # Pequeno delay e abre o navegador
            time.sleep(1.0)
            webbrowser.open("http://127.0.0.1:3000")
        
        # 4. Monitoramento contínuo
        while True:
            if backend_proc.poll() is not None:
                print("[Sistema] O servidor Backend encerrou inesperadamente.")
                break
            if frontend_proc.poll() is not None:
                print("[Sistema] O servidor Frontend encerrou inesperadamente.")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[Sistema] Encerrando servidores por solicitação do usuário (Ctrl+C)...")
    finally:
        # 5. Encerramento limpo e completo (limpeza de árvore de processos do Windows)
        for name, proc in [("Backend", backend_proc), ("Frontend", frontend_proc)]:
            if proc and proc.poll() is None:
                print(f"[Sistema] Encerrando processos vinculados ao {name} (PID {proc.pid})...")
                try:
                    subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception as e:
                    print(f"[Sistema] Erro ao limpar {name}: {e}")
        
        print("[Sistema] Todos os servidores foram encerrados. Ambiente limpo.")

if __name__ == "__main__":
    main()
