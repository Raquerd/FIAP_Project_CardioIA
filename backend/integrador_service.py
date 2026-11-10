#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço Central Integrador da Plataforma CardioIA (Fase 7 - MVP Final)
Conecta as interfaces (Web e Mobile) aos motores técnicos do ecossistema:
  - Telemetria de Sensores IoT (ESP32 MicroPython / Wokwi)
  - Motores Preditivos e Protocolos Clínicos da Fase 6 (Random Forest + Multiagentes)
  - Assistente Conversacional e NLP da Fase 5 (IBM Watson Assistant / LLMs)
  - Visão Computacional da Fase 4 (Classificação de ECG com CNN e ResNet50)
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("CardioIA.Integrador")

# Diretórios base do projeto
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
CONFIG_DIR = ROOT_DIR / "config"
SCRIPTS_DIR = ROOT_DIR / "scripts"

# Garantir que a pasta scripts esteja no sys.path para importação dos módulos anteriores
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


FEATURES_MODELO = [
    "idade_media",
    "carga_sistema",
    "tempo_espera",
    "fc_media",
    "spo2_media",
    "pa_sistolica",
    "temperatura",
    "densidade_eventos",
    "eventos_24h",
    "disponibilidade_recursos",
]


class CardioIAIntegrador:
    def __init__(self):
        self._modelo_risco = None
        self._colunas_modelo = FEATURES_MODELO
        self._protocolos_clinicos = []
        self._watson_service = None
        self._ultimo_sinal_iot: Optional[Dict[str, Any]] = None
        self._historico_iot: List[Dict[str, Any]] = []
        self._max_historico = 50

        # Carregar componentes
        self._carregar_modelo_preditivo()
        self._carregar_protocolos()
        self._carregar_watson()

    # --------------------------------------------------------------------------
    # 1. Carregamento dos Motores de IA
    # --------------------------------------------------------------------------
    def _carregar_modelo_preditivo(self):
        """Carrega o modelo Random Forest treinado na Fase 6."""
        caminho_modelo = CONFIG_DIR / "modelo_risco_cardiaco.joblib"
        if not caminho_modelo.exists():
            logger.warning(f"Modelo preditivo nao encontrado em: {caminho_modelo}")
            return

        try:
            import joblib
            dados = joblib.load(caminho_modelo)
            if isinstance(dados, dict) and "modelo" in dados:
                self._modelo_risco = dados["modelo"]
            else:
                self._modelo_risco = dados
            self._colunas_modelo = FEATURES_MODELO
            logger.info("Modelo Preditivo Random Forest (Fase 6) carregado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo preditivo: {e}")
            self._modelo_risco = None

    def _carregar_protocolos(self):
        """Carrega os 10 protocolos clínicos estruturados em JSON."""
        caminho_proto = CONFIG_DIR / "protocolos_emergencia.json"
        if not caminho_proto.exists():
            logger.warning(f"Arquivo de protocolos nao encontrado em: {caminho_proto}")
            return

        try:
            with open(caminho_proto, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if isinstance(dados, list):
                    self._protocolos_clinicos = dados
                elif isinstance(dados, dict) and "protocolos" in dados:
                    self._protocolos_clinicos = dados["protocolos"]
                else:
                    self._protocolos_clinicos = []
            logger.info(f"{len(self._protocolos_clinicos)} protocolos clinicos carregados.")
        except Exception as e:
            logger.error(f"Erro ao carregar protocolos clinicos: {e}")
            self._protocolos_clinicos = []

    def _carregar_watson(self):
        """Inicializa o servico Watson Assistant (Fase 5) se configurado."""
        try:
            from watson_service import WatsonAssistantService
            self._watson_service = WatsonAssistantService()
            logger.info("Servico Watson Assistant (Fase 5) inicializado.")
        except Exception as e:
            logger.warning(f"Watson Assistant indisponivel: {e}")
            self._watson_service = None

    # --------------------------------------------------------------------------
    # 2. Gerenciamento de Telemetria IoT (MicroPython / Wokwi)
    # --------------------------------------------------------------------------
    def registrar_telemetria_iot(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recebe pacote de telemetria do ESP32 MicroPython,
        executa inferência do modelo preditivo e atualiza o estado em tempo real.
        """
        agora = datetime.now()
        leitura = {
            "dispositivo_id": dados.get("dispositivo_id", "esp32-cardioia-01"),
            "timestamp": agora.strftime("%Y-%m-%d %H:%M:%S"),
            "hora": agora.strftime("%H:%M:%S"),
            "timestamp_ms": dados.get("timestamp_ms", int(agora.timestamp() * 1000)),
            "bpm": int(dados.get("bpm", 75)),
            "temperatura": float(dados.get("temperatura", 36.5)),
            "umidade": float(dados.get("umidade", 55.0)),
            "status_edge": dados.get("status_clinico", "ESTAVEL"),
            "alerta_critico_edge": bool(dados.get("alerta_critico", False)),
            "edge_decision": dados.get("edge_decision", "Monitoramento continuo"),
        }

        # Avaliar Risco Clínico Preditivo (Fase 6) a partir dos dados do sensor
        predicao = self.avaliar_risco_sinais_vitais(
            bpm=leitura["bpm"],
            temp=leitura["temperatura"]
        )
        leitura["predicao_risco"] = predicao

        # Armazenar no cache de estado
        self._ultimo_sinal_iot = leitura
        self._historico_iot.append(leitura)
        if len(self._historico_iot) > self._max_historico:
            self._historico_iot.pop(0)

        logger.info(
            f"[TELEMETRIA RECEBIDA] BPM: {leitura['bpm']} | Temp: {leitura['temperatura']}C | "
            f"Edge: {leitura['status_edge']} | IA Risco: {predicao['categoria_risco']}"
        )

        return leitura

    def obter_ultimo_sinal(self) -> Dict[str, Any]:
        """Retorna o último sinal vital registrado ou um estado padrão."""
        if self._ultimo_sinal_iot:
            return self._ultimo_sinal_iot

        # Fallback de inicialização suave
        return {
            "dispositivo_id": "esp32-cardioia-01",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hora": datetime.now().strftime("%H:%M:%S"),
            "bpm": 72,
            "temperatura": 36.6,
            "umidade": 55.0,
            "status_edge": "ESTAVEL",
            "alerta_critico_edge": False,
            "edge_decision": "Aguardando primeiro pacote do MicroPython",
            "predicao_risco": {
                "categoria_risco": "BAIXO",
                "probabilidade": 0.05,
                "score_risco": 0.05,
                "pico_risco": 0,
                "recomendacao": "Paciente em faixa fisiológica estável."
            }
        }

    def obter_historico_iot(self, limite: int = 20) -> List[Dict[str, Any]]:
        """Retorna o histórico recente de telemetria para gráficos de tendência."""
        return self._historico_iot[-limite:]

    # --------------------------------------------------------------------------
    # 3. Inferência do Modelo Preditivo (Fase 6)
    # --------------------------------------------------------------------------
    def avaliar_risco_sinais_vitais(self, bpm: int, temp: float, **kwargs) -> Dict[str, Any]:
        """
        Executa a predição probabilística de risco cardiovascular cruzando os dados
        dos sensores físicos do ESP32 com o modelo Random Forest da Fase 6.
        """
        alerta = (bpm > 120) or (temp > 38.0) or (bpm < 50)

        # Mapeamento dinâmico inteligente com fallback para os 10 parâmetros exatos do modelo Fase 6
        features_dict = {
            "idade_media": float(kwargs.get("idade_media", kwargs.get("idade", 62))),
            "carga_sistema": float(kwargs.get("carga_sistema", 92.0 if alerta else 50.0)),
            "tempo_espera": float(kwargs.get("tempo_espera", 75.0 if alerta else 28.0)),
            "fc_media": float(kwargs.get("fc_media", kwargs.get("frequencia_cardiaca", bpm))),
            "spo2_media": float(kwargs.get("spo2_media", kwargs.get("saturacao_o2", 89.0 if alerta else 97.0))),
            "pa_sistolica": float(kwargs.get("pa_sistolica", kwargs.get("pressao_sistolica", 100.0 if alerta else 122.0))),
            "temperatura": float(kwargs.get("temperatura", temp)),
            "densidade_eventos": float(kwargs.get("densidade_eventos", 7.0 if alerta else 2.0)),
            "eventos_24h": float(kwargs.get("eventos_24h", 5.0 if alerta else 1.0)),
            "disponibilidade_recursos": float(kwargs.get("disponibilidade_recursos", kwargs.get("disponibilidade recursos", 25.0 if alerta else 84.0))),
        }

        # Inferência se o modelo Random Forest estiver carregado
        probabilidade = 0.05
        pico_risco = 0
        if self._modelo_risco:
            try:
                import pandas as pd
                df = pd.DataFrame([features_dict], columns=FEATURES_MODELO)
                pico_risco = int(self._modelo_risco.predict(df)[0])
                if hasattr(self._modelo_risco, "predict_proba"):
                    probs = self._modelo_risco.predict_proba(df)[0]
                    probabilidade = float(probs[1]) if len(probs) > 1 else float(probs[0])
                else:
                    probabilidade = 0.95 if pico_risco == 1 else 0.05
            except Exception as e:
                logger.error(f"Erro ao inferir modelo de risco: {e}")
                # Heurística clínica de fallback
                probabilidade = 0.96 if alerta else 0.05
                pico_risco = 1 if probabilidade >= 0.5 else 0
        else:
            probabilidade = 0.96 if alerta else 0.05
            pico_risco = 1 if probabilidade >= 0.5 else 0

        # Categorização
        if probabilidade >= 0.70 or pico_risco == 1:
            categoria = "ALTO"
        elif probabilidade >= 0.40:
            categoria = "MEDIO"
        else:
            categoria = "BAIXO"

        # Protocolos acionados baseados em sinais vitais e risco
        protocolos_disparados = self._identificar_protocolos(features_dict, pico_risco, probabilidade)

        return {
            "pico_risco": pico_risco,
            "probabilidade": round(probabilidade, 4),
            "score_risco": round(probabilidade, 2),
            "categoria_risco": categoria,
            "features_utilizadas": features_dict,
            "protocolos_acionados": protocolos_disparados,
            "recomendacao": (
                "Alerta Vermelho: Acionamento imediato da equipe de hemodinâmica e reserva de UTI."
                if categoria == "ALTO"
                else "Paciente monitorado: Sinais estáveis, manter protocolo ambulatorial."
            )
        }

    def _identificar_protocolos(self, cenario: Dict[str, float], pico_risco: int, prob_risco: float) -> List[str]:
        """Avalia os 10 protocolos da Fase 6 frente aos sinais e risco predito."""
        if not self._protocolos_clinicos:
            return ["Monitoramento clínico ambulatorial contínuo."]

        acionados = []
        p = self._protocolos_clinicos

        # Regras diretas da Fase 6
        if len(p) >= 1 and cenario.get("spo2_media", 97) < 88:
            acionados.append(p[0])
        if len(p) >= 2 and cenario.get("carga_sistema", 50) > 85:
            acionados.append(p[1])
        if len(p) >= 3 and cenario.get("fc_media", 75) > 120:
            acionados.append(p[2])
        if len(p) >= 4 and cenario.get("eventos_24h", 1) > 5:
            acionados.append(p[3])
        if len(p) >= 5 and cenario.get("disponibilidade_recursos", 80) < 30:
            acionados.append(p[4])
        if len(p) >= 6 and cenario.get("tempo_espera", 30) > 90:
            acionados.append(p[5])
        if len(p) >= 7 and cenario.get("temperatura", 36.5) > 38.0:
            acionados.append(p[6])
        if len(p) >= 8 and cenario.get("densidade_eventos", 2) > 6:
            acionados.append(p[7])
        if len(p) >= 9 and cenario.get("pa_sistolica", 120) < 90:
            acionados.append(p[8])
        if len(p) >= 10 and (pico_risco == 1 or prob_risco >= 0.70):
            acionados.append(p[9])

        if not acionados:
            acionados.append("Protocolo de Observação: Sinais vitais dentro dos limiares de segurança.")

        return acionados

    # --------------------------------------------------------------------------
    # 4. Orquestração do Sistema Multiagente da Fase 6
    # --------------------------------------------------------------------------
    def executar_multiagente(self, cenario_custom: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executa a orquestração completa dos 4 agentes autônomos da Fase 6."""
        try:
            from sistema_multiagente_fase6 import (
                CENARIO_NOVO_CASO_FIAP,
                executar_sistema_multiagente,
                normalizar_cenario
            )
            cenario = cenario_custom or CENARIO_NOVO_CASO_FIAP
            res = executar_sistema_multiagente(cenario=cenario, modo="local", verbose=False)
            rec_dict = res["recomendacao_final"].model_dump()
            rec_dict["texto_formatado_fiap"] = res["saida_formatada_fiap"]
            rec_dict["handoffs_realizados"] = res["handoffs_realizados"]
            rec_dict["cenario_normalizado"] = res["cenario_normalizado"]
            return rec_dict
        except Exception as e:
            logger.error(f"Erro ao executar pipeline multiagente: {e}")
            return {
                "erro": str(e),
                "mensagem": "Falha na orquestração multiagente. Consulte logs do sistema."
            }

    # --------------------------------------------------------------------------
    # 5. Integração Conversacional (Fase 5 - Watson / LLMs)
    # --------------------------------------------------------------------------
    def processar_mensagem_chat(self, session_id: Optional[str], texto: str) -> Dict[str, Any]:
        """Encaminha mensagem ao IBM Watson Assistant ou fallback com contexto de saúde."""
        if not self._watson_service:
            # Fallback inteligente contextualizado com os sinais vitais atuais
            sinal = self.obter_ultimo_sinal()
            return {
                "response": (
                    f"Olá! Sou o assistente CardioIA. Estou monitorando seus sinais vitais em tempo real: "
                    f"Frequência Cardíaca em {sinal['bpm']} BPM e Temperatura em {sinal['temperatura']}°C. "
                    f"Em caso de dor aguda no peito ou falta de ar, procure atendimento médico imediato."
                ),
                "watson_connected": False,
                "session_id": session_id or "local-session-fallback"
            }

        return self._watson_service.send_message(session_id, texto)

    # --------------------------------------------------------------------------
    # 6. Status Global de Integração
    # --------------------------------------------------------------------------
    def obter_status_geral(self) -> Dict[str, Any]:
        """Retorna o diagnóstico de integração de todos os pilares do CardioIA."""
        return {
            "status": "online",
            "versao": "CardioIA MVP Integrado v7.0",
            "timestamp": datetime.now().isoformat(),
            "modulos": {
                "iot_micropython": {
                    "dispositivo_conectado": self._ultimo_sinal_iot is not None,
                    "ultimo_sinal": self.obter_ultimo_sinal(),
                    "total_leituras_em_memoria": len(self._historico_iot)
                },
                "ia_preditiva_fase6": {
                    "modelo_carregado": self._modelo_risco is not None,
                    "algoritmo": "Random Forest Classifier (Acuracia 99.90%)",
                    "total_protocolos": len(self._protocolos_clinicos)
                },
                "ia_conversacional_fase5": {
                    "watson_conectado": self._watson_service is not None,
                    "service": "IBM Watson Assistant v2 / LLM"
                },
                "ia_visao_computacional_fase4": {
                    "modelos_disponiveis": ["CNN do Zero (Scratch)", "ResNet50 Transfer Learning"]
                }
            }
        }


# Instância singleton do serviço integrador
integrador = CardioIAIntegrador()
