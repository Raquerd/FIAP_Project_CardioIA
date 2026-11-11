#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador de Telemetria IoT MicroPython (CardioIA - Fase 7)
Envia pacotes de sinais vitais para o Backend Integrador em Python,
simulando o comportamento do firmware ESP32 no Wokwi.
Possui inicialização automática do backend caso esteja desligado.
"""

import sys
import time
import random
import argparse
import subprocess
from pathlib import Path
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_SCRIPT = ROOT_DIR / "backend" / "app.py"

DEFAULT_LOCAL_URL = "http://localhost:5000/api/telemetria"
DEFAULT_CLOUD_URL = "http://cardioia-env.eba-unfydca4.us-east-2.elasticbeanstalk.com/api/telemetria"


def verificar_e_iniciar_backend(url: str) -> str:
    """
    Verifica se o backend está respondendo. Se estiver desligado e for localhost,
    inicia o servidor backend automaticamente em segundo plano.
    """
    if "localhost" not in url and "127.0.0.1" not in url:
        return url

    status_url = url.replace("/api/telemetria", "/api/status")
    try:
        res = requests.get(status_url, timeout=1.5)
        if res.status_code == 200:
            return url
    except Exception:
        pass

    # Backend local não está respondendo. Tentar iniciá-lo automaticamente
    print("[INIT] Backend local (localhost:5000) não detectado.")
    if BACKEND_SCRIPT.exists():
        print(f"[INIT] Iniciando Backend Integrador automaticamente ({BACKEND_SCRIPT.name})...")
        try:
            # Iniciar em processo independente no Windows
            subprocess.Popen(
                [sys.executable, str(BACKEND_SCRIPT)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP") else 0
            )
            # Aguardar até 5 segundos para o servidor subir
            for tentativa in range(1, 6):
                time.sleep(1)
                try:
                    res = requests.get(status_url, timeout=1.5)
                    if res.status_code == 200:
                        print(f"[INIT] Backend Integrador iniciado com sucesso na porta 5000!")
                        return url
                except Exception:
                    pass
        except Exception as e:
            print(f"[AVISO] Não foi possível iniciar o backend local automaticamente: {e}")

    # Fallback para nuvem se localhost não subir
    try:
        print("[INIT] Testando conexão com a nuvem AWS Elastic Beanstalk...")
        res = requests.get(DEFAULT_CLOUD_URL.replace("/api/telemetria", "/api/status"), timeout=3)
        if res.status_code == 200:
            print(f"[INIT] Conectado à API na nuvem: {DEFAULT_CLOUD_URL}")
            return DEFAULT_CLOUD_URL
    except Exception:
        pass

    return url


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


def executar_simulador(url=DEFAULT_LOCAL_URL, qtd=10, intervalo=2.0, cenario="aleatorio"):
    print("\n" + "=" * 60)
    print(" SIMULADOR IOT MICROPYTHON -> BACKEND CARDIOIA (FASE 7)")
    print("=" * 60)

    url_ativa = verificar_e_iniciar_backend(url)

    print(f" Destino Ativo: {url_ativa}")
    print(f" Cenario: {cenario} | Pacotes: {qtd} | Intervalo: {intervalo}s")
    print("=" * 60 + "\n")

    sucessos = 0
    for i in range(1, qtd + 1):
        payload = gerar_leitura(cenario)
        try:
            res = requests.post(url_ativa, json=payload, timeout=5)
            if res.status_code in (200, 201):
                sucessos += 1
                dados_retornados = res.json()
                risco_predito = (
                    dados_retornados.get("registro", {})
                    .get("predicao_risco", {})
                    .get("categoria_risco")
                    or dados_retornados.get("predicao_risco", {}).get("categoria_risco", "OK")
                )
                print(f"[{i:02d}/{qtd}] OK -> BPM: {payload['bpm']:3d} | Temp: {payload['temperatura']}C | Edge: {payload['status_clinico']:7s} | IA Risco: {risco_predito}")
            else:
                print(f"[{i:02d}/{qtd}] Resposta HTTP {res.status_code}: {res.text[:120]}")
        except requests.exceptions.ConnectionError:
            print(f"[{i:02d}/{qtd}] [ERRO DE CONEXAO] O servidor backend em {url_ativa} nao respondeu.")
            print("        Dica: Execute o backend com: python backend/app.py (opcao 1 do main.bat).")
            break
        except Exception as e:
            print(f"[{i:02d}/{qtd}] Falha de envio: {e}")

        if i < qtd:
            time.sleep(intervalo)

    print("\n" + "=" * 60)
    if sucessos > 0:
        print(f" Simulacao concluida com sucesso! ({sucessos}/{qtd} pacotes entregues)")
        print(f" Acesse os dados em tempo real em: http://localhost:5000/api/telemetria/atual")
    else:
        print(f" Simulacao interrompida. Inicie o backend antes de transmitir.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador IoT MicroPython CardioIA")
    parser.add_argument("--url", default=DEFAULT_LOCAL_URL, help="Endpoint de telemetria da API")
    parser.add_argument("--qtd", type=int, default=10, help="Quantidade de pacotes para enviar")
    parser.add_argument("--intervalo", type=float, default=2.0, help="Intervalo em segundos entre pacotes")
    parser.add_argument("--cenario", choices=["aleatorio", "normal", "critico", "bradicardia"], default="aleatorio", help="Cenario clinico")
    args = parser.parse_args()

    executar_simulador(url=args.url, qtd=args.qtd, intervalo=args.intervalo, cenario=args.cenario)
