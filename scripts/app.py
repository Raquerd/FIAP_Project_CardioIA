import os
import sys
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar caminhos para importar módulos locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

from watson_service import WatsonAssistantService
try:
    from integrador_service import integrador
except Exception as e:
    integrador = None

# Inicializar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

# Configurar diretório de templates e arquivos estáticos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, '..', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, '..', 'static')

app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR,
    static_url_path='/static'
)

# Habilitar CORS para permitir conexões de qualquer origem local ou externa
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Inicializar o serviço do Watson Assistant
try:
    watson_service = WatsonAssistantService()
except Exception as e:
    logger.error(f"Erro ao inicializar WatsonAssistantService: {str(e)}")
    watson_service = None


@app.route('/')
@app.route('/fase7')
def index():
    """
    Renderiza o Hub Integrador da Fase 7 ou o chat da Fase 5.
    """
    fase7_html = os.path.join(TEMPLATES_DIR, 'fase7_hub.html')
    if os.path.exists(fase7_html):
        return render_template('fase7_hub.html')
    index_html = os.path.join(TEMPLATES_DIR, 'index.html')
    if os.path.exists(index_html):
        return render_template('index.html')
    return jsonify({
        "name": "CardioIA Assistant API",
        "version": "1.0.0",
        "status": "online",
        "description": "API intermediária Flask integrada ao IBM Watson Assistant (Fase 5)"
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Endpoint de Health Check para verificar a saúde da API e status da conexão com Watson e Motores de IA.
    """
    detalhes = integrador.obter_status_geral() if integrador else {}
    return jsonify({
        "status": "online",
        "service": "CardioIA Integrated API",
        "watson_connected": watson_service is not None,
        "api_version": "v7.0",
        "iot_conectado": detalhes.get("modulos", {}).get("iot_micropython", {}).get("dispositivo_conectado", False),
        "modelo_risco_carregado": detalhes.get("modulos", {}).get("ia_preditiva_fase6", {}).get("modelo_carregado", False),
        "detalhes": detalhes
    }), 200


@app.route('/api/telemetria', methods=['GET', 'POST'])
@app.route('/api/sensores', methods=['GET', 'POST'])
def registrar_telemetria():
    """Recebe sinais vitais do ESP32 MicroPython (POST) ou retorna o último sinal (GET)."""
    if not integrador:
        return jsonify({"erro": "Servico integrador indisponivel"}), 503
    if request.method == 'GET':
        return jsonify(integrador.obter_ultimo_sinal()), 200
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "JSON ausente"}), 400
    try:
        res = integrador.registrar_telemetria_iot(dados)
        return jsonify({"status": "sucesso", "registro": res}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/telemetria/atual', methods=['GET'])
def get_telemetria_atual():
    """Retorna o último sinal vital registrado."""
    if not integrador:
        return jsonify({"erro": "Servico integrador indisponivel"}), 503
    return jsonify(integrador.obter_ultimo_sinal()), 200


@app.route('/api/telemetria/historico', methods=['GET'])
def get_telemetria_historico():
    """Retorna histórico de leituras de telemetria."""
    if not integrador:
        return jsonify({"total": 0, "leituras": []}), 200
    limite = int(request.args.get('limite', 20))
    return jsonify({"total": len(integrador.obter_historico_iot(limite)), "leituras": integrador.obter_historico_iot(limite)}), 200


@app.route('/api/predicao/risco', methods=['POST'])
def avaliar_risco_preditivo():
    """Avalia o risco de crise cardiovascular a partir de sinais vitais."""
    if not integrador:
        return jsonify({"erro": "Servico integrador indisponivel"}), 503
    dados = request.get_json(silent=True) or {}
    bpm = dados.get('bpm')
    temp = dados.get('temperatura')
    if bpm is None or temp is None:
        ultimo = integrador.obter_ultimo_sinal()
        bpm = bpm if bpm is not None else ultimo.get('bpm', 75)
        temp = temp if temp is not None else ultimo.get('temperatura', 36.5)
    try:
        resultado = integrador.avaliar_risco_sinais_vitais(bpm=int(bpm), temp=float(temp), **dados)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/integracao/resumo', methods=['GET'])
def get_integracao_resumo():
    """Resumo técnico em tempo real de todo o ecossistema integrado."""
    if not integrador:
        return jsonify({"erro": "Servico integrador indisponivel"}), 503
    return jsonify(integrador.obter_status_geral()), 200


@app.route('/api/ecg/analisar', methods=['POST'])
def analyze_ecg():
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


@app.route('/api/session', methods=['POST'])
def create_session():
    """
    Cria uma nova sessão no Watson Assistant e devolve o session_id.
    """
    if not watson_service:
        return jsonify({
            "status": "error",
            "message": "Serviço Watson Assistant não configurado no servidor."
        }), 503

    try:
        session_id = watson_service.create_session()
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "message": "Sessão criada com sucesso."
        }), 201
    except Exception as e:
        logger.error(f"Falha ao criar sessão: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erro ao criar sessão no Watson Assistant: {str(e)}"
        }), 500


@app.route('/api/message', methods=['POST'])
def send_message():
    """
    Recebe a mensagem do usuário e encaminha para o Watson Assistant.
    Payload esperado:
    {
        "session_id": "...",       # Opcional (cria automaticamente se não informado)
        "message": "texto digitado" # Obrigatório
    }
    """
    if not watson_service:
        return jsonify({
            "status": "error",
            "message": "Serviço Watson Assistant não configurado no servidor."
        }), 503

    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({
            "status": "error",
            "message": "Corpo da requisição inválido. Envie um JSON contendo o campo 'message'."
        }), 400

    user_message = data.get('message', '').strip()
    session_id = data.get('session_id')

    try:
        result = watson_service.send_message(session_id, user_message)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erro na comunicação com o assistente: {str(e)}"
        }), 500


@app.route('/api/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Encerra e limpa uma sessão existente no Watson Assistant.
    """
    if not watson_service:
        return jsonify({"status": "error", "message": "Serviço não inicializado"}), 503

    try:
        deleted = watson_service.delete_session(session_id)
        return jsonify({
            "status": "success" if deleted else "warning",
            "message": f"Sessão {session_id} encerrada."
        }), 200
    except Exception as e:
        logger.error(f"Erro ao deletar sessão {session_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/fase6')
def fase6_dashboard():
    """
    Renderiza o Dashboard Interativo da Fase 6 (Sistema Preditivo Multiagente).
    """
    import json
    from sistema_multiagente_fase6 import (
        CENARIO_NOVO_CASO_FIAP,
        CENARIO_BAIXO_RISCO,
        CENARIO_COLAPSO_CRITICO,
        executar_sistema_multiagente,
        normalizar_cenario,
    )
    cenarios = {
        "padrao": normalizar_cenario(CENARIO_NOVO_CASO_FIAP),
        "baixo_risco": normalizar_cenario(CENARIO_BAIXO_RISCO),
        "critico": normalizar_cenario(CENARIO_COLAPSO_CRITICO),
    }
    results = {}
    for key, cenario in cenarios.items():
        res = executar_sistema_multiagente(cenario=cenario, modo="local", verbose=False)
        rec_dict = res["recomendacao_final"].model_dump()
        rec_dict["texto_formatado_fiap"] = res["saida_formatada_fiap"]
        rec_dict["handoffs_realizados"] = res["handoffs_realizados"]
        rec_dict["historico_mensagens"] = res["historico_mensagens"]
        rec_dict["cenario_normalizado"] = res["cenario_normalizado"]
        results[key] = rec_dict

    test_summary = (
        "Clique em '▶️ Executar 7 Testes ao Vivo' para rodar a bateria real via Python unittest..."
    )
    return render_template(
        'fase6_dashboard.html',
        scenarios_json=json.dumps(cenarios, ensure_ascii=False),
        results_json=json.dumps(results, ensure_ascii=False),
        test_output_json=json.dumps(test_summary, ensure_ascii=False),
    )


@app.route('/api/fase6/simular', methods=['GET', 'POST'])
def api_fase6_simular():
    """
    Executa ao vivo o pipeline multiagente da Fase 6 para o cenário selecionado
    ou com os parâmetros customizados enviados pelo usuário no formulário.
    """
    from datetime import datetime
    from sistema_multiagente_fase6 import (
        CENARIO_NOVO_CASO_FIAP,
        CENARIO_BAIXO_RISCO,
        CENARIO_COLAPSO_CRITICO,
        executar_sistema_multiagente,
    )
    cenarios = {
        "padrao": CENARIO_NOVO_CASO_FIAP,
        "baixo_risco": CENARIO_BAIXO_RISCO,
        "critico": CENARIO_COLAPSO_CRITICO,
    }
    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        cenario = payload.get('parametros') or cenarios.get(payload.get('cenario', 'padrao'), CENARIO_NOVO_CASO_FIAP)
    else:
        cenario_nome = request.args.get('cenario', 'padrao')
        cenario = cenarios.get(cenario_nome, CENARIO_NOVO_CASO_FIAP)

    inicio = datetime.now()
    res = executar_sistema_multiagente(cenario=cenario, modo="local", verbose=False)
    duracao_ms = round((datetime.now() - inicio).total_seconds() * 1000, 1)

    rec_dict = res["recomendacao_final"].model_dump()
    rec_dict["texto_formatado_fiap"] = res["saida_formatada_fiap"]
    rec_dict["handoffs_realizados"] = res["handoffs_realizados"]
    rec_dict["historico_mensagens"] = res["historico_mensagens"]
    rec_dict["cenario_normalizado"] = res["cenario_normalizado"]
    rec_dict["executado_em"] = datetime.now().strftime("%H:%M:%S")
    rec_dict["duracao_ms"] = duracao_ms
    return jsonify(rec_dict), 200


@app.route('/api/fase6/testes', methods=['POST', 'GET'])
def api_fase6_testes():
    """
    Executa ao vivo o script scripts/test_multiagente_fase6.py e retorna o log real.
    """
    import subprocess
    from datetime import datetime
    script_testes = os.path.join(BASE_DIR, 'test_multiagente_fase6.py')
    inicio = datetime.now()
    proc = subprocess.run(
        [sys.executable, script_testes],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=30
    )
    duracao_s = round((datetime.now() - inicio).total_seconds(), 2)
    output_completo = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return jsonify({
        "sucesso": proc.returncode == 0,
        "returncode": proc.returncode,
        "duracao_s": duracao_s,
        "executado_em": datetime.now().strftime("%H:%M:%S"),
        "output": output_completo.strip()
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Iniciando servidor CardioIA Flask na porta {port}...")
    print(f"\n=======================================================")
    print(f" Servidor CardioIA Chatbot Online: http://localhost:{port}")
    print(f" Dashboard Fase 6 Multiagente:     http://localhost:{port}/fase6")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)

