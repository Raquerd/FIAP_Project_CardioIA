@echo off
title CardioIA - Sistema Inteligente
chcp 65001 > nul
cd /d "%~dp0"

echo =======================================================
echo          CARDIOIA - ECOSSISTEMA HOSPITALAR
echo =======================================================
echo Verificando e instalando dependencias...
pip install -r requirements.txt
cls

:MENU
echo =======================================================
echo          CARDIOIA - MENU PRINCIPAL
echo =======================================================
echo [1] Iniciar Chatbot Conversacional (Fase 5 - Flask & Web)
echo [2] Iniciar Prototipo de Diagnostico ECG (Fase 4 - Streamlit)
echo [3] Executar Testes Automatizados da API (Fase 5)
echo [4] Sair
echo =======================================================
set /p OPT="Escolha uma opcao (1-4): "

if "%OPT%"=="1" goto CHATBOT
if "%OPT%"=="2" goto STREAMLIT
if "%OPT%"=="3" goto TESTES
if "%OPT%"=="4" goto FIM
echo Opcao invalida! Tente novamente.
pause
cls
goto MENU

:CHATBOT
cls
echo =======================================================
echo Iniciando Servidor Flask do Chatbot CardioIA...
echo Abrindo automaticamente no navegador em: http://localhost:5000
echo =======================================================
python scripts/app.py
pause
cls
goto MENU

:STREAMLIT
cls
echo =======================================================
echo Iniciando Prototipo de Visao Computacional / ECG...
echo =======================================================
streamlit run scripts/cardioia_prototype.py
pause
cls
goto MENU

:TESTES
cls
echo =======================================================
echo Executando Bateria de Testes Automatizados...
echo =======================================================
python scripts/test_watson_api.py
pause
cls
goto MENU

:FIM
exit
