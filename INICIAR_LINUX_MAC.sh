#!/bin/bash
echo "===================================================================="
echo "  SIMULADOR DE AUTOMATOS - MODO PORTATIL (LINUX/MAC)"
echo "===================================================================="
echo ""

echo "[1/3] Criando ambiente virtual isolado para nao conflitar com o OS..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo ""
echo "[2/3] Instalando dependencias do projeto..."
python3 -m pip install fastapi uvicorn pydantic

echo ""
echo "[3/3] Inicializando o Servidor..."
python3 interface/run_server.py
