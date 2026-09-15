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
from watson_service import WatsonAssistantService

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
def index():
    """
    Renderiza a interface web do chat caso o template exista,
    ou retorna o status da API em JSON.
    """
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
    Endpoint de Health Check para verificar a saúde da API e status da conexão com Watson.
    """
    return jsonify({
        "status": "online",
        "service": "CardioIA Conversational API",
        "watson_connected": watson_service is not None,
        "api_version": "v2"
    }), 200


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


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Iniciando servidor CardioIA Flask na porta {port}...")
    print(f"\n=======================================================")
    print(f" Servidor CardioIA Chatbot Online: http://localhost:{port}")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)
