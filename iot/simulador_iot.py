#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador de Telemetria IoT MicroPython (CardioIA - Fase 7)
Envia pacotes de sinais vitais para o Backend Integrador em Python,
simulando o comportamento do firmware ESP32 no Wokwi.
"""

import time
import random
import requests
import argparse

DEFAULT_URL = "http://localhost:5000/api/telemetria"


def gerar_leitura(cenario="aleatorio"):
    if cenario == "normal":
        bpm = random.randint(65, 80)
        temp = round(random.uniform(36.2, 36.9), 1)
        umid = round(random.uniform(50.0, 65.0), 1)
        status = "ESTAVEL"
        alerta = False
    elif cenario == "critico":
        bpm = random.randint(125, 160)
        temp = round(random.uniform(38.2, 39.5), 1)
        umid = round(random.uniform(45.0, 70.0), 1)
        status = "CRITICO"
        alerta = True
    elif cenario == "bradicardia":
        bpm = random.randint(40, 48)
        temp = round(random.uniform(36.0, 36.8), 1)
        umid = round(random.uniform(50.0, 60.0), 1)
        status = "ATENCAO"
        alerta = True
    else:
        # Alterna dinamicamente
        bpm = random.randint(55, 140)
        temp = round(random.uniform(36.0, 39.0), 1)
        umid = round(random.uniform(45.0, 70.0), 1)
        alerta = bpm > 120 or temp > 38.0
        status = "CRITICO" if alerta else ("ATENCAO" if bpm < 50 else "ESTAVEL")

    return {
        "dispositivo_id": "esp32-cardioia-simulador",
        "timestamp_ms": int(time.time() * 1000),
        "bpm": bpm,
        "temperatura": temp,
        "umidade": umid,
        "status_clinico": status,
        "alerta_critico": alerta,
        "edge_decision": "Acionamento de triagem hospitalar" if alerta else "Monitoramento de rotina"
    }


def executar_simulador(url=DEFAULT_URL, qtd=10, intervalo=2.0, cenario="aleatorio"):
    print(f"\n=======================================================")
    print(f" SIMULADOR IOT MICROPYTHON -> BACKEND CARDIOIA")
    print(f" Destino: {url}")
    print(f" Cenario: {cenario} | Pacotes: {qtd} | Intervalo: {intervalo}s")
    print(f"=======================================================\n")

    sucessos = 0
    for i in range(1, qtd + 1):
        payload = gerar_leitura(cenario)
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code in (200, 201):
                sucessos += 1
                dados_retornados = res.json()
                risco_predito = dados_retornados.get("predicao_risco", {}).get("categoria_risco", "N/A")
                print(f"[{i:02d}/{qtd}] OK -> BPM: {payload['bpm']} | Temp: {payload['temperatura']}C | Edge: {payload['status_clinico']} | IA Risco: {risco_predito}")
            else:
                print(f"[{i:02d}/{qtd}] Erro HTTP {res.status_code}: {res.text}")
        except Exception as e:
            print(f"[{i:02d}/{qtd}] Falha de conexao com o backend ({url}): {e}")

        if i < qtd:
            time.sleep(intervalo)

    print(f"\nSimulacao concluida: {sucessos}/{qtd} pacotes entregues com sucesso.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador IoT MicroPython CardioIA")
    parser.add_argument("--url", default=DEFAULT_URL, help="Endpoint de telemetria da API")
    parser.add_argument("--qtd", type=int, default=5, help="Quantidade de pacotes para enviar")
    parser.add_argument("--intervalo", type=float, default=2.0, help="Intervalo em segundos entre pacotes")
    parser.add_argument("--cenario", choices=["aleatorio", "normal", "critico", "bradicardia"], default="aleatorio", help="Cenario clinico")
    args = parser.parse_args()

    executar_simulador(url=args.url, qtd=args.qtd, intervalo=args.intervalo, cenario=args.cenario)
