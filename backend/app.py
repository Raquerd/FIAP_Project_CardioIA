#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Flask - Backend Integrador da Plataforma CardioIA (Fase 7 - MVP Final)
Unifica os módulos de:
  - Telemetria de Sensores (ESP32 MicroPython / Wokwi)
  - Visão Computacional de ECG (CNN e ResNet50 da Fase 4)
  - Assistente Conversacional (IBM Watson Assistant / LLMs da Fase 5)
  - Sistema Preditivo e Multiagente (Random Forest e OpenAI Agents da Fase 6)
  - Suporte à aplicação Web (Vercel) e Mobile (Expo / APK)
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("CardioIA.Backend")

# Diretórios base
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
TEMPLATES_DIR = ROOT_DIR / "templates"
STATIC_DIR = ROOT_DIR / "static"

# Adicionar caminhos para importação
for p in [str(BACKEND_DIR), str(SCRIPTS_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Importar o serviço integrador
from integrador_service import integrador

# Inicializar aplicação Flask
app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
    static_url_path='/static'
)

# Habilitar CORS irrestrito para endpoints de API
CORS(app, resources={r"/api/*": {"origins": "*"}})


# ==============================================================================
# ROTAS DE HEALTH CHECK & STATUS INTEGRADO
# ==============================================================================
@app.route('/')
@app.route('/fase7')
def index():
    """Retorna o Hub Integrador da Fase 7 ou o template padrão."""
    fase7_html = TEMPLATES_DIR / 'fase7_hub.html'
    if fase7_html.exists():
        return render_template('fase7_hub.html')
    index_html = TEMPLATES_DIR / 'index.html'
    if index_html.exists():
        return render_template('index.html')
    return jsonify({
        "plataforma": "CardioIA - MVP Final Integrado",
        "versao": "7.0",
        "status": "online",
        "documentacao_api": "/api/status"
    }), 200


@app.route('/api/status', methods=['GET'])
def get_status():
    """Endpoint de Health Check unificado consultado pelo Frontend Web e Mobile."""
    status_completo = integrador.obter_status_geral()
    return jsonify({
        "status": "online",
        "service": "CardioIA Integrated Ecosystem API",
        "api_version": "v7.0",
        "watson_connected": status_completo["modulos"]["ia_conversacional_fase5"]["watson_conectado"],
        "modelo_risco_carregado": status_completo["modulos"]["ia_preditiva_fase6"]["modelo_carregado"],
        "iot_conectado": status_completo["modulos"]["iot_micropython"]["dispositivo_conectado"],
        "detalhes": status_completo
    }), 200


@app.route('/api/integracao/resumo', methods=['GET'])
def get_integracao_resumo():
    """Resumo técnico em tempo real de todo o ecossistema integrado."""
    return jsonify(integrador.obter_status_geral()), 200


# ==============================================================================
# ROTAS DE TELEMETRIA IOT (MICROPYTHON / WOKWI)
# ==============================================================================
@app.route('/api/telemetria', methods=['GET', 'POST'])
@app.route('/api/sensores', methods=['GET', 'POST'])
def registrar_telemetria():
    """
    POST: Recebe os sinais vitais coletados pelo ESP32 com MicroPython.
    GET:  Retorna o último sinal vital capturado (para visualização no navegador).
    """
    if request.method == 'GET':
        return jsonify(integrador.obter_ultimo_sinal()), 200

    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Payload JSON ausente ou mal formatado."}), 400

    try:
        leitura_processada = integrador.registrar_telemetria_iot(dados)
        return jsonify({
            "status": "sucesso",
            "mensagem": "Sinais vitais processados com sucesso pelo backend integrador.",
            "registro": leitura_processada
        }), 201
    except Exception as e:
        logger.exception("Erro ao processar telemetria IoT")
        return jsonify({"erro": f"Falha interna: {str(e)}"}), 500


@app.route('/api/telemetria/atual', methods=['GET'])
def get_telemetria_atual():
    """Retorna o sinal vital mais recente registrado para alimentar a UI."""
    return jsonify(integrador.obter_ultimo_sinal()), 200


@app.route('/api/telemetria/historico', methods=['GET'])
def get_telemetria_historico():
    """Retorna os últimos N sinais vitais para gráficos em tempo real."""
    limite = int(request.args.get('limite', 20))
    historico = integrador.obter_historico_iot(limite)
    return jsonify({"total": len(historico), "leituras": historico}), 200


# ==============================================================================
# ROTAS DO MODELO PREDITIVO E MULTIAGENTE (FASE 6)
# ==============================================================================
@app.route('/api/predicao/risco', methods=['POST'])
def avaliar_risco_preditivo():
    """
    Avalia o risco de crise cardiovascular a partir de sinais vitais recebidos
    ou a partir da última telemetria registrada pelo sensor IoT.
    """
    dados = request.get_json(silent=True) or {}
    bpm = dados.get('bpm')
    temp = dados.get('temperatura')

    # Se não forem informados, usar o último sinal capturado pelo sensor
    if bpm is None or temp is None:
        ultimo = integrador.obter_ultimo_sinal()
        bpm = bpm if bpm is not None else ultimo.get('bpm', 75)
        temp = temp if temp is not None else ultimo.get('temperatura', 36.5)

    try:
        resultado = integrador.avaliar_risco_sinais_vitais(
            bpm=int(bpm),
            temp=float(temp),
            **dados
        )
        return jsonify(resultado), 200
    except Exception as e:
        logger.exception("Erro ao avaliar risco preditivo")
        return jsonify({"erro": str(e)}), 500


@app.route('/api/multiagente/executar', methods=['POST'])
def executar_multiagente_fase6():
    """Aciona a orquestração multiagente da Fase 6 com os 4 agentes."""
    dados = request.get_json(silent=True)
    resultado = integrador.executar_multiagente(dados)
    return jsonify(resultado), 200


@app.route('/fase6')
def dashboard_fase6():
    """Renderiza a rota legada do dashboard da Fase 6."""
    from app import fase6_dashboard
    return fase6_dashboard()


@app.route('/api/fase6/simular', methods=['GET', 'POST'])
def api_fase6_simular():
    """Rota da simulação multiagente da Fase 6."""
    from app import api_fase6_simular as fase6_sim
    return fase6_sim()


@app.route('/api/fase6/testes', methods=['GET', 'POST'])
def api_fase6_testes():
    """Rota dos testes da Fase 6."""
    from app import api_fase6_testes as fase6_tst
    return fase6_tst()


# ==============================================================================
# ROTA DE VISÃO COMPUTACIONAL (FASE 4 - CNN / RESNET50)
# ==============================================================================
@app.route('/api/ecg/analisar', methods=['POST'])
def analyze_ecg():
    """Classifica imagens de ECG utilizando CNN ou ResNet50."""
    if 'image' not in request.files:
        return jsonify({"erro": "Nenhuma imagem foi enviada."}), 400

    image_file = request.files['image']
    if not image_file.filename:
        return jsonify({"erro": "Selecione uma imagem para análise."}), 400

    if not image_file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return jsonify({"erro": "Formato inválido. Envie PNG ou JPEG."}), 400

    model_type = request.form.get('model', 'resnet50')

    try:
        from ecg_inference import analyze_ecg_image
        result = analyze_ecg_image(image_file, model_type)
        return jsonify({"result": result}), 200
    except Exception as e:
        logger.exception("Erro ao analisar imagem de ECG")
        return jsonify({"erro": str(e)}), 500


# ==============================================================================
# ROTAS DE ASSISTENTE CONVERSACIONAL (FASE 5 - WATSON / LLM)
# ==============================================================================
@app.route('/api/session', methods=['POST'])
def create_session():
    """Cria nova sessão no Watson Assistant ou mock local."""
    try:
        if integrador._watson_service:
            session_id = integrador._watson_service.create_session()
        else:
            session_id = "session-cardioia-local"
        return jsonify({"status": "success", "session_id": session_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/message', methods=['POST'])
def send_message():
    """Envia mensagem ao assistente de saúde."""
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id')

    if not user_message:
        return jsonify({"status": "error", "message": "Mensagem vazia."}), 400

    try:
        resposta = integrador.processar_mensagem_chat(session_id, user_message)
        return jsonify(resposta), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Encerra sessão do assistente."""
    try:
        if integrador._watson_service:
            integrador._watson_service.delete_session(session_id)
        return jsonify({"status": "success", "message": f"Sessão {session_id} encerrada."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ==============================================================================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"\n=======================================================")
    print(f" CARDIOIA - BACKEND INTEGRADOR (FASE 7)")
    print(f" Endereço Principal: http://localhost:{port}")
    print(f" Health Check Geral: http://localhost:{port}/api/status")
    print(f" Telemetria Atual:   http://localhost:{port}/api/telemetria/atual")
    print(f" Dashboard Fase 6:   http://localhost:{port}/fase6")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)
