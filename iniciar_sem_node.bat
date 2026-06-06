@echo off
title Simulador de Automatos - Sem Node.js
echo ====================================================================
echo   SIMULADOR DE AUTOMATOS - AMBIENTE SEM NODE.JS
echo ====================================================================
echo.
echo [1/3] Instalando dependencias do Python (FastAPI, Uvicorn, Pydantic)...
python -m pip install fastapi uvicorn pydantic

echo.
echo [2/3] Inicializando o motor de calculo (Backend na porta 8000)...
start /B python -m uvicorn interface.api.app:app --host 127.0.0.1 --port 8000

echo.
echo [3/3] Inicializando o servidor web estatico do Python (Porta 3000)...
echo Abrindo o navegador em http://127.0.0.1:3000...
timeout /t 2 /nobreak > nul
start http://127.0.0.1:3000
python -m http.server 3000 --directory web/dist

echo.
echo Pressione qualquer tecla para encerrar...
pause > nul
