@echo off
setlocal
title Compre - Homologacao local
cd /d "%~dp0"

rem ===== Configuracao =====
set VPS_IP=200.234.218.138
set TUNEL_PORTA=3307
rem Usuario SSH da VPS (deixe vazio para ser perguntado)
set SSH_USER=

echo ============================================
echo   COMPRE - homologacao local
echo ============================================
echo.

rem ----- Backend: ambiente virtual e dependencias -----
if not exist "backend\.venv\Scripts\activate.bat" (
    echo [1/5] Criando ambiente virtual do backend...
    py -m venv backend\.venv || goto :erro
    call backend\.venv\Scripts\activate.bat
    pip install -r backend\requirements.txt || goto :erro
) else (
    echo [1/5] Ambiente virtual do backend OK.
)

rem ----- Backend: arquivo .env -----
if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env" >nul
    echo.
    echo O arquivo backend\.env foi criado. Preencha DB_PASSWORD, SECRET_KEY e FERNET_KEY.
    notepad "backend\.env"
    echo Depois de salvar o arquivo, rode este script de novo.
    pause
    exit /b 0
)

rem ----- Seguranca: nunca roda contra a base de PRODUCAO (compre) -----
set DB_OK=
findstr /R /C:"^DB_NAME=compre_hml" "backend\.env" >nul && set DB_OK=1
findstr /R /C:"^DB_NAME=compre_dev" "backend\.env" >nul && set DB_OK=1
if not defined DB_OK (
    echo.
    echo PARADO: DB_NAME no backend\.env deve ser compre_hml ^(homologacao^) ou compre_dev.
    echo Este script aplica migrations automaticamente e nao deve tocar na base de producao ^(compre^).
    pause
    exit /b 1
)
for /f "tokens=2 delims== " %%A in ('findstr /R /C:"^DB_NAME=" "backend\.env"') do set BASE_ATUAL=%%A
echo [2/5] Configuracao do backend OK ^(base %BASE_ATUAL%^).

rem ----- Frontend: dependencias -----
if not exist "frontend\node_modules" (
    echo [3/5] Instalando dependencias do painel...
    pushd frontend
    call npm install || (popd & goto :erro)
    popd
) else (
    echo [3/5] Dependencias do painel OK.
)

rem ----- Tunel SSH para o MySQL da VPS -----
netstat -ano | findstr /R /C:":%TUNEL_PORTA% .*LISTENING" >nul
if errorlevel 1 (
    echo [4/5] Tunel SSH nao esta ativo.
    if "%SSH_USER%"=="" set /p SSH_USER=Usuario SSH da VPS ^(ENTER para pular^): 
    if not "%SSH_USER%"=="" (
        start "Tunel SSH - MySQL" ssh -N -L %TUNEL_PORTA%:127.0.0.1:3306 %SSH_USER%@%VPS_IP%
        echo Informe a senha na janela "Tunel SSH - MySQL" ^(se pedir^).
        echo Quando o tunel estiver conectado, pressione uma tecla para continuar.
        pause >nul
    ) else (
        echo Tunel ignorado. O backend so conecta se o banco estiver acessivel em 127.0.0.1:%TUNEL_PORTA%.
    )
) else (
    echo [4/5] Tunel SSH ativo na porta %TUNEL_PORTA%.
)

rem ----- Sobe backend e painel em janelas separadas -----
echo [5/5] Iniciando backend e painel...
start "Compre API (porta 8000)" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && alembic upgrade head && uvicorn app.main:app --reload"
start "Compre Painel (porta 5173)" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 6 >nul
start "" http://localhost:5173
start "" http://localhost:8000/api/docs

echo.
echo Pronto. Para encerrar, feche as janelas "Compre API", "Compre Painel" e "Tunel SSH".
echo Primeiro acesso? Rode uma vez: backend\.venv\Scripts\python -m app.scripts.seed  ^(dentro da pasta backend^)
timeout /t 5 >nul
exit /b 0

:erro
echo.
echo ERRO durante a preparacao do ambiente. Veja a mensagem acima.
pause
exit /b 1