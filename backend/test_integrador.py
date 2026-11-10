#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados do Backend Integrador CardioIA (Fase 7)
Valida a integração dos sensores MicroPython, motor preditivo de risco,
protocolos clínicos e rotas unificadas da API REST.
"""

import sys
import unittest
import json
from pathlib import Path

# Ajustar sys.path
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"

for p in [str(BACKEND_DIR), str(SCRIPTS_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app import app
from integrador_service import integrador


class TestCardioIABackendIntegrador(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.testing = True
        cls.client = app.test_client()

    def test_01_health_check_status(self):
        """Testa se o endpoint /api/status está online e reporta os módulos."""
        res = self.client.get('/api/status')
        self.assertEqual(res.status_code, 200)
        dados = res.get_json()
        self.assertEqual(dados.get("status"), "online")
        self.assertEqual(dados.get("api_version"), "v7.0")
        self.assertIn("detalhes", dados)

    def test_02_recebimento_telemetria_micropython_normal(self):
        """Testa o envio de sinais normais simulando o ESP32 MicroPython."""
        payload = {
            "dispositivo_id": "esp32-teste-01",
            "bpm": 76,
            "temperatura": 36.6,
            "umidade": 55.0,
            "status_clinico": "ESTAVEL",
            "alerta_critico": False,
            "edge_decision": "Monitoramento de rotina"
        }
        res = self.client.post('/api/telemetria', json=payload)
        self.assertEqual(res.status_code, 201)
        dados = res.get_json()
        self.assertEqual(dados.get("status"), "sucesso")
        registro = dados.get("registro", {})
        self.assertEqual(registro.get("bpm"), 76)
        self.assertEqual(registro.get("status_edge"), "ESTAVEL")
        self.assertIn("predicao_risco", registro)
        self.assertEqual(registro["predicao_risco"]["categoria_risco"], "BAIXO")

    def test_03_recebimento_telemetria_micropython_alerta_critico(self):
        """Testa o envio de sinais com taquicardia (>120 BPM) e febre."""
        payload = {
            "dispositivo_id": "esp32-teste-01",
            "bpm": 138,
            "temperatura": 38.6,
            "umidade": 60.0,
            "status_clinico": "CRITICO",
            "alerta_critico": True,
            "edge_decision": "Acionamento de triagem hospitalar"
        }
        res = self.client.post('/api/telemetria', json=payload)
        self.assertEqual(res.status_code, 201)
        dados = res.get_json()
        registro = dados.get("registro", {})
        self.assertEqual(registro.get("bpm"), 138)
        self.assertEqual(registro.get("status_edge"), "CRITICO")
        self.assertTrue(registro.get("alerta_critico_edge"))
        self.assertIn("predicao_risco", registro)
        # O modelo da Fase 6 deve classificar como ALTO risco
        self.assertEqual(registro["predicao_risco"]["categoria_risco"], "ALTO")
        self.assertEqual(registro["predicao_risco"]["pico_risco"], 1)
        self.assertGreaterEqual(registro["predicao_risco"]["probabilidade"], 0.70)

    def test_04_consulta_ultimo_sinal_iot(self):
        """Testa a rota /api/telemetria/atual que alimenta os cards da UI."""
        res = self.client.get('/api/telemetria/atual')
        self.assertEqual(res.status_code, 200)
        dados = res.get_json()
        self.assertIn("bpm", dados)
        self.assertIn("temperatura", dados)
        self.assertIn("status_edge", dados)
        self.assertIn("predicao_risco", dados)

    def test_05_consulta_historico_iot(self):
        """Testa a rota de histórico de telemetria para gráficos."""
        res = self.client.get('/api/telemetria/historico?limite=10')
        self.assertEqual(res.status_code, 200)
        dados = res.get_json()
        self.assertIn("leituras", dados)
        self.assertGreater(len(dados["leituras"]), 0)

    def test_06_predicao_risco_personalizada(self):
        """Testa o endpoint /api/predicao/risco da Fase 6 com parâmetros arbitrários."""
        payload = {
            "idade": 65,
            "frequencia_cardiaca": 135,
            "temperatura": 38.5,
            "dor_peito_escala": 8,
            "historico_infarto": 1
        }
        res = self.client.post('/api/predicao/risco', json=payload)
        self.assertEqual(res.status_code, 200)
        dados = res.get_json()
        self.assertIn("categoria_risco", dados)
        self.assertIn("probabilidade", dados)
        self.assertIn("protocolos_acionados", dados)
        self.assertEqual(dados["categoria_risco"], "ALTO")

    def test_07_resumo_integracao_completa(self):
        """Testa a rota executiva /api/integracao/resumo."""
        res = self.client.get('/api/integracao/resumo')
        self.assertEqual(res.status_code, 200)
        dados = res.get_json()
        self.assertEqual(dados.get("status"), "online")
        self.assertIn("modulos", dados)
        self.assertIn("iot_micropython", dados["modulos"])
        self.assertIn("ia_preditiva_fase6", dados["modulos"])
        self.assertIn("ia_conversacional_fase5", dados["modulos"])
        self.assertIn("ia_visao_computacional_fase4", dados["modulos"])


if __name__ == '__main__':
    print("\n=======================================================")
    print(" INICIANDO TESTES DO BACKEND INTEGRADOR (FASE 7)")
    print("=======================================================\n")
    unittest.main(verbosity=2)
