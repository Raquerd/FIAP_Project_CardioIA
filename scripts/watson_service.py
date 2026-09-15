import os
import logging
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

class WatsonAssistantService:
    """
    Serviço responsável pela comunicação com o IBM Watson Assistant v2.
    Gerencia o ciclo de vida das sessões e a troca de mensagens com o assistente.
    """
    
    def __init__(self, api_key=None, service_url=None, assistant_id=None, api_version=None):
        self.api_key = api_key or os.getenv('WATSON_API_KEY') or os.getenv('WATSON_APIKEY')
        self.service_url = (service_url or os.getenv('WATSON_SERVICE_URL') or os.getenv('WATSON_URL') or '').rstrip('/')
        self.assistant_id = assistant_id or os.getenv('WATSON_ASSISTANT_ID')
        self.api_version = api_version or os.getenv('WATSON_API_VERSION') or os.getenv('WATSON_VERSION') or '2021-06-14'
        
        if not self.api_key or not self.service_url or not self.assistant_id:
            raise ValueError("Credenciais do Watson Assistant incompletas no arquivo de configuração (.env).")
            
        self.auth = HTTPBasicAuth('apikey', self.api_key)
        self.base_url = f"{self.service_url}/v2/assistants/{self.assistant_id}"
        logger.info("WatsonAssistantService inicializado com sucesso.")

    def create_session(self):
        """
        Cria uma nova sessão com o Watson Assistant.
        Retorna o session_id gerado pela IBM Cloud.
        """
        url = f"{self.base_url}/sessions?version={self.api_version}"
        try:
            response = requests.post(url, auth=self.auth, timeout=15)
            response.raise_for_status()
            data = response.json()
            session_id = data.get('session_id')
            logger.info(f"Nova sessão criada: {session_id}")
            return session_id
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao criar sessão no Watson: {str(e)}")
            raise RuntimeError(f"Falha ao conectar ao Watson Assistant: {str(e)}")

    def send_message(self, session_id, message_text):
        """
        Envia uma mensagem de texto do usuário para o assistente.
        Se a sessão tiver expirado (HTTP 404), recria uma nova sessão automaticamente.
        """
        if not session_id:
            logger.info("Session ID ausente. Criando nova sessão automaticamente...")
            session_id = self.create_session()
            
        url = f"{self.base_url}/sessions/{session_id}/message?version={self.api_version}"
        payload = {
            'input': {
                'message_type': 'text',
                'text': message_text or '',
                'options': {
                    'return_context': True
                }
            }
        }
        
        try:
            response = requests.post(url, auth=self.auth, json=payload, timeout=20)
            
            # Se a sessão expirou na IBM Cloud (404), recria e tenta novamente
            if response.status_code == 404:
                logger.warning(f"Sessão {session_id} expirada ou inválida. Gerando nova sessão...")
                session_id = self.create_session()
                url = f"{self.base_url}/sessions/{session_id}/message?version={self.api_version}"
                response = requests.post(url, auth=self.auth, json=payload, timeout=20)
                
            response.raise_for_status()
            raw_data = response.json()
            
            # Extrair e formatar respostas do Watson
            output = raw_data.get('output', {})
            generic_responses = output.get('generic', [])
            intents = output.get('intents', [])
            entities = output.get('entities', [])
            
            formatted_messages = []
            for item in generic_responses:
                resp_type = item.get('response_type', 'text')
                if resp_type == 'text':
                    text_val = item.get('text', '')
                    if text_val:
                        formatted_messages.append({'type': 'text', 'text': text_val})
                elif resp_type == 'option':
                    formatted_messages.append({
                        'type': 'option',
                        'title': item.get('title', ''),
                        'description': item.get('description', ''),
                        'options': [opt.get('label') for opt in item.get('options', [])]
                    })
                elif resp_type == 'image':
                    formatted_messages.append({
                        'type': 'image',
                        'source': item.get('source', ''),
                        'title': item.get('title', '')
                    })
                    
            # Fallback caso não haja mensagens genéricas retornadas
            if not formatted_messages:
                formatted_messages.append({
                    'type': 'text',
                    'text': 'Desculpe, não compreendi sua mensagem. Poderia reformular?'
                })
                
            return {
                'status': 'success',
                'session_id': session_id,
                'messages': formatted_messages,
                'detected_intents': [i.get('intent') for i in intents],
                'detected_entities': [{'entity': e.get('entity'), 'value': e.get('value')} for e in entities]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar mensagem ao Watson: {str(e)}")
            raise RuntimeError(f"Falha na comunicação com o assistente: {str(e)}")

    def delete_session(self, session_id):
        """
        Encerra e limpa a sessão no Watson Assistant.
        """
        if not session_id:
            return False
        url = f"{self.base_url}/sessions/{session_id}?version={self.api_version}"
        try:
            response = requests.delete(url, auth=self.auth, timeout=10)
            if response.status_code in [200, 204]:
                logger.info(f"Sessão {session_id} finalizada com sucesso.")
                return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"Não foi possível deletar sessão {session_id}: {str(e)}")
        return False


if __name__ == '__main__':
    print("=== TESTANDO CLIENTE WATSON ASSISTANT ===")
    service = WatsonAssistantService()
    sess_id = service.create_session()
    print("Sessão criada:", sess_id)
    
    resp = service.send_message(sess_id, "Olá, bom dia!")
    print("Resposta recebida:", resp)
    
    deleted = service.delete_session(sess_id)
    print("Sessão encerrada com sucesso:", deleted)
