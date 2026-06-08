@echo off
title Simulador de Automatos - Ambiente Integrado
echo ====================================================================
echo   SIMULADOR DE AUTOMATOS - MODO PORTATIL (WINDOWS)
echo ====================================================================
echo.

echo [1/3] Criando ambiente virtual isolado para nao sujar seu Python...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo.
echo [2/3] Instalando dependencias do projeto...
python -m pip install fastapi uvicorn pydantic

echo.
echo [3/3] Inicializando o Servidor...
python interface\run_server.py

pause
