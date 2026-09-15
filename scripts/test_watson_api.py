import os
import sys
import json

# Garantir que o diretório scripts está no path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from app import app

def run_tests():
    print("=" * 65)
    print("   CARDIOIA - BATERIA DE TESTES DE FLUXOS CONVERSACIONAIS")
    print("=" * 65)
    
    client = app.test_client()
    
    # 1. Health Check
    print("\n[1/7] Testando Health Check da API (/api/status)...")
    res = client.get('/api/status')
    assert res.status_code == 200, f"Status esperado 200, recebido {res.status_code}"
    status_data = res.get_json()
    assert status_data.get('status') == 'online'
    assert status_data.get('watson_connected') is True
    print("  -> OK: API online e conectada ao Watson Assistant.")
    
    # 2. Criar Sessão
    print("\n[2/7] Criando sessão no Watson Assistant (/api/session)...")
    res = client.post('/api/session')
    assert res.status_code == 201, f"Status esperado 201, recebido {res.status_code}"
    session_data = res.get_json()
    session_id = session_data.get('session_id')
    assert session_id, "Session ID não retornado"
    print(f"  -> OK: Sessão criada: {session_id}")
    
    # Casos de Teste de Conversação Clínica
    test_cases = [
        {
            "num": "3/7",
            "nome": "Boas-vindas e Saudação",
            "mensagem": "Olá, bom dia!",
            "expected_intent": "sauda",
            "check_content": "CardioIA"
        },
        {
            "num": "4/7",
            "nome": "Triagem Clínica: Relato de Dor no Peito (Crítico)",
            "mensagem": "Estou sentindo uma forte dor no peito e aperto",
            "expected_intent": "relatar_sintoma",
            "check_content": "Dor no peito"
        },
        {
            "num": "5/7",
            "nome": "Orientação de Exame: Preparo de Holter",
            "mensagem": "Preciso fazer jejum para fazer o exame de Holter?",
            "expected_intent": "preparo_exame",
            "check_content": "Holter"
        },
        {
            "num": "6/7",
            "nome": "Agendamento de Exame Cardiológico",
            "mensagem": "Gostaria de agendar um ecocardiograma",
            "expected_intent": "agendamento",
            "check_content": "Ecocardiograma"
        },
        {
            "num": "7/7",
            "nome": "Transbordo para Atendente Humano",
            "mensagem": "Preciso de ajuda de uma pessoa real, falar com atendente",
            "expected_intent": "falar_com_atendente",
            "check_content": "atendente"
        }
    ]
    
    for tc in test_cases:
        print(f"\n[{tc['num']}] Testando Fluxo: {tc['nome']}...")
        print(f"  Usuário: '{tc['mensagem']}'")
        res = client.post('/api/message', json={
            "session_id": session_id,
            "message": tc['mensagem']
        })
        assert res.status_code == 200, f"Status esperado 200, recebido {res.status_code}"
        data = res.get_json()
        
        intents = data.get('detected_intents', [])
        messages = data.get('messages', [])
        bot_texts = " ".join([m.get('text', '') for m in messages if m.get('type') == 'text'])
        
        print(f"  Intenções Detectadas: {intents}")
        print(f"  CardioIA: {bot_texts[:100]}...")
        
        # Validação da intenção
        intent_match = any(tc['expected_intent'] in i.lower() for i in intents)
        assert intent_match, f"Intenção esperada contendo '{tc['expected_intent']}', detectadas: {intents}"
        
        # Validação do conteúdo
        assert tc['check_content'].lower() in bot_texts.lower(), f"Palavra chave '{tc['check_content']}' não encontrada na resposta."
        print("  -> OK: Fluxo validado com assertividade.")
        
    # Encerramento de Sessão
    print("\n[Final] Encerrando sessão de testes (/api/session/<id>)...")
    res = client.delete(f'/api/session/{session_id}')
    assert res.status_code == 200
    print("  -> OK: Sessão encerrada.")
    
    print("\n" + "=" * 65)
    print("   TODOS OS 7 TESTES DOS FLUXOS CONVERSACIONAIS FORAM APROVADOS!")
    print("=" * 65)

if __name__ == '__main__':
    run_tests()
