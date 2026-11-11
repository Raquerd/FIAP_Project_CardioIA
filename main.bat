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
echo [0] Iniciar Solucao Completa (Backend + Hub Web + Simulador IoT)
echo [1] Iniciar Backend Integrador em Janela Separada (Fase 7)
echo [2] Executar Testes Automatizados de Integracao (Fase 7)
echo [3] Executar Simulador IoT MicroPython (Fase 7)
echo [4] Gerar Relatorio Tecnico em PDF (Fase 7 - 5 Paginas)
echo [5] Abrir Hub Web da Solucao no Navegador (http://localhost:5000)
echo [6] Executar Sistema Multiagente no Terminal (Fase 6 - CLI)
echo [7] Abrir Dashboard Web Interativo da Fase 6 (Navegador)
echo [8] Executar Testes Automatizados do Multiagente (Fase 6)
echo [9] Iniciar Chatbot Conversacional (Fase 5 - Flask ^& Web)
echo [10] Iniciar Prototipo de Diagnostico ECG (Fase 4 - Streamlit)
echo [11] Sair
echo =======================================================
set /p OPT="Escolha uma opcao (0-11): "

if "%OPT%"=="0" goto AUTO_COMPLETO
if "%OPT%"=="1" goto BACKEND_FASE7
if "%OPT%"=="2" goto TESTES_FASE7
if "%OPT%"=="3" goto SIMULADOR_IOT
if "%OPT%"=="4" goto RELATORIO_PDF_FASE7
if "%OPT%"=="5" goto ABRIR_HUB_WEB
if "%OPT%"=="6" goto MULTIAGENTE
if "%OPT%"=="7" goto DASHBOARD_FASE6
if "%OPT%"=="8" goto TESTES_FASE6
if "%OPT%"=="9" goto CHATBOT
if "%OPT%"=="10" goto STREAMLIT
if "%OPT%"=="11" goto FIM
echo Opcao invalida! Tente novamente.
pause
cls
goto MENU

:AUTO_COMPLETO
cls
echo =======================================================
echo Inicializando Ecossistema CardioIA Completo (Fase 7)...
echo =======================================================
echo 1. Iniciando Backend Integrador em janela dedicada...
start "CardioIA - Backend Integrador (Fase 7)" cmd /k "chcp 65001 > nul && python backend/app.py"
timeout /t 3 > nul
echo 2. Abrindo Hub Web da Solucao no Navegador...
start http://localhost:5000
echo 3. Disparando Simulador IoT de Sinais Vitais...
echo =======================================================
python iot/simulador_iot.py --qtd 10 --intervalo 2
pause
cls
goto MENU

:BACKEND_FASE7
cls
echo =======================================================
echo Iniciando Backend Integrador CardioIA em janela dedicada...
echo Acesso Web: http://localhost:5000
echo API Status: http://localhost:5000/api/status
echo =======================================================
start "CardioIA - Backend Integrador (Fase 7)" cmd /k "chcp 65001 > nul && python backend/app.py"
timeout /t 2 > nul
start http://localhost:5000
echo.
echo Backend iniciado com sucesso na porta 5000!
echo O servidor continuara rodando na janela aberta em segundo plano.
echo.
pause
cls
goto MENU

:ABRIR_HUB_WEB
cls
echo Abrindo Hub Web Integrador do CardioIA no navegador...
start http://localhost:5000
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

