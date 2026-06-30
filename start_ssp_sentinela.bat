@echo off
title SENTINELA - Sistema de Inteligência Policial
echo ============================================================
echo      SENTINELA - INICIANDO AMBIENTE DE AUDITORIA DE MVI
echo ============================================================
echo.

echo [1/3] Verificando sementeira de dados...
if not exist sentinela.db (
    echo Banco sentinela.db nao encontrado! Rodando sementeira...
    python scripts\db_seeder.py
) else (
    echo Banco sentinela.db ja existe.
)
echo.

echo [2/3] Iniciando Backend FastAPI na porta 8000...
start "SENTINELA - Backend API" cmd /k "python -m uvicorn api.main:app --host 0.0.0.0 --port 8000"

echo [3/3] Iniciando Frontend Next.js na porta 3000...
cd app
start "SENTINELA - Frontend UI" cmd /c "npm run dev"

echo Aguardando 5 segundos para a inicializacao dos servidores...
timeout /t 5 >nul

echo Abrindo o painel visual no seu navegador...
start http://localhost:3000
start http://localhost:8000/docs

echo.
echo ============================================================
echo   SENTINELA PRONTO PARA USO!
echo   - Backend API (Swagger): http://localhost:8000/docs
echo   - Painel do Analista UI: http://localhost:3000
echo ============================================================
echo.
pause
