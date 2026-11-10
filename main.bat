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
echo [1] Iniciar Backend Integrador CardioIA (Fase 7 - Flask REST)
echo [2] Executar Testes Automatizados de Integracao (Fase 7)
echo [3] Executar Simulador IoT MicroPython (Fase 7)
echo [4] Gerar Relatorio Tecnico em PDF (Fase 7 - 5 Paginas)
echo [5] Executar Sistema Multiagente no Terminal (Fase 6 - CLI)
echo [6] Abrir Dashboard Web Interativo da Fase 6 (Navegador)
echo [7] Executar Testes Automatizados do Multiagente (Fase 6)
echo [8] Iniciar Chatbot Conversacional (Fase 5 - Flask ^& Web)
echo [9] Iniciar Prototipo de Diagnostico ECG (Fase 4 - Streamlit)
echo [10] Sair
echo =======================================================
set /p OPT="Escolha uma opcao (1-10): "

if "%OPT%"=="1" goto BACKEND_FASE7
if "%OPT%"=="2" goto TESTES_FASE7
if "%OPT%"=="3" goto SIMULADOR_IOT
if "%OPT%"=="4" goto RELATORIO_PDF_FASE7
if "%OPT%"=="5" goto MULTIAGENTE
if "%OPT%"=="6" goto DASHBOARD_FASE6
if "%OPT%"=="7" goto TESTES_FASE6
if "%OPT%"=="8" goto CHATBOT
if "%OPT%"=="9" goto STREAMLIT
if "%OPT%"=="10" goto FIM
echo Opcao invalida! Tente novamente.
pause
cls
goto MENU

:BACKEND_FASE7
cls
echo =======================================================
echo Iniciando Backend Integrador CardioIA (Fase 7)...
echo Acesso: http://localhost:5000
echo Telemetria: http://localhost:5000/api/telemetria/atual
echo =======================================================
start http://localhost:5000/api/status
python backend/app.py
pause
cls
goto MENU

:TESTES_FASE7
cls
echo =======================================================
echo Executando Bateria de Testes do Backend Integrador (Fase 7)...
echo =======================================================
python backend/test_integrador.py
pause
cls
goto MENU

:SIMULADOR_IOT
cls
echo =======================================================
echo Executando Simulador IoT MicroPython (ESP32)...
echo =======================================================
python iot/simulador_iot.py --qtd 10 --intervalo 2
pause
cls
goto MENU

:RELATORIO_PDF_FASE7
cls
echo =======================================================
echo Gerando Relatorio Tecnico Oficial da Fase 7 (PDF 5 Pags)...
echo =======================================================
python scripts/gerar_pdf_arquitetura_final_fase7.py
pause
cls
goto MENU

:MULTIAGENTE
cls
echo =======================================================
echo Executando Sistema Multiagente CardioIA (Fase 6)...
echo =======================================================
echo [1] Cenario Oficial FIAP (novo_caso - Risco Alto 0.96)
echo [2] Cenario Normalidade (Baixo Risco)
echo [3] Cenario Colapso Hospitalar (Risco Critico)
echo =======================================================
set /p CEN="Escolha o cenario (1-3, Enter para 1): "
if "%CEN%"=="2" (
    python scripts/sistema_multiagente_fase6.py --cenario baixo_risco
) else if "%CEN%"=="3" (
    python scripts/sistema_multiagente_fase6.py --cenario critico
) else (
    python scripts/sistema_multiagente_fase6.py --cenario padrao
)
pause
cls
goto MENU

:DASHBOARD_FASE6
cls
echo =======================================================
echo Iniciando Dashboard Web Interativo da Fase 6...
echo Acesso: http://localhost:5000/fase6
echo =======================================================
start http://localhost:5000/fase6
python scripts/app.py
pause
cls
goto MENU


:TESTES_FASE6
cls
echo =======================================================
echo Executando Bateria de Testes do Sistema Multiagente (Fase 6)...
echo =======================================================
python scripts/test_multiagente_fase6.py
pause
cls
goto MENU

:CHATBOT
cls
echo =======================================================
echo Iniciando Servidor Flask do Chatbot CardioIA...
echo Acesso: http://localhost:5000
echo =======================================================
start http://localhost:5000
python scripts/app.py
pause
cls
goto MENU

:STREAMLIT
cls
echo =======================================================
echo Iniciando Prototipo de Visao Computacional / ECG...
echo =======================================================
python -m streamlit run scripts/cardioia_prototype.py
pause
cls
goto MENU

:TESTES_FASE5
cls
echo =======================================================
echo Executando Bateria de Testes Automatizados (Fase 5)...
echo =======================================================
python scripts/test_watson_api.py
pause
cls
goto MENU

:FIM
exit

