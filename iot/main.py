# ==============================================================================
# FIAP - PROJETO CARDIOIA - FASE 7 (MVP FINAL)
# MODULO IOT: CAPTURA DE SINAIS, PROCESSAMENTO EM MICROPYTHON & FEEDBACK VISUAL
#
# Hardware simulado no Wokwi / ESP32:
#   - ESP32 DevKit v4
#   - Sensor DHT22 (Temperatura e Umidade) -> Pino GPIO 15
#   - Potenciometro (Simulador de Frequencia Cardiaca 40-200 BPM) -> ADC GPIO 34
#   - Display OLED SSD1306 I2C (128x64) -> SDA: GPIO 21 | SCL: GPIO 22
#   - LED de Alerta Critico -> Pino GPIO 2 (ou 21/4 com resistor)
#   - Conectividade: Wi-Fi (Wokwi-GUEST) + MQTT (HiveMQ) + HTTP Fallback
# ==============================================================================

import time
import json
import network
import machine
import dht

# Tentar importar driver OLED SSD1306 local
try:
    import ssd1306
    HAS_OLED = True
except ImportError:
    HAS_OLED = False

# Tentar importar cliente MQTT do MicroPython
try:
    from umqtt.simple import MQTTClient
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

# Tentar importar urequests para envio HTTP REST direto
try:
    import urequests
    HAS_UREQUESTS = True
except ImportError:
    HAS_UREQUESTS = False


# ==============================================================================
# CONFIGURACOES DE HARDWARE E PINOUT
# ==============================================================================
PIN_DHT = 15          # DHT22 no GPIO 15
PIN_POT_BPM = 34      # Potenciometro (ADC) no GPIO 34
PIN_LED_ALERTA = 2    # LED interno / externo de alerta critico no GPIO 2
PIN_I2C_SDA = 21      # SDA do display OLED SSD1306
PIN_I2C_SCL = 22      # SCL do display OLED SSD1306

OLED_WIDTH = 128
OLED_HEIGHT = 64

# Limiares clinicos de alerta (triagem de borda - Edge Computing)
LIMIAR_BPM_ALERTA = 120
LIMIAR_TEMP_ALERTA = 38.0
LIMIAR_BPM_BRADICARDIA = 50

# Configuracoes de rede e telemetria
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_TELEMETRIA = "fiap/cardioia/telemetria"
MQTT_TOPIC_ALERTAS = "fiap/cardioia/alertas"
MQTT_CLIENT_ID = "ESP32_CardioIA_MicroPython"

# URL do Backend Integrador em Python (ajuste conforme o IP local ou nuvem)
BACKEND_HTTP_URL = "http://localhost:5000/api/telemetria"

# ==============================================================================
# BUFFER CIRCULAR DE BORDA (RESILIENCIA / OFFLINE FIRST)
# ==============================================================================
BUFFER_CAPACIDADE_MAXIMA = 20
buffer_edge = []


# ==============================================================================
# INICIALIZACAO DE PERIFERICOS
# ==============================================================================
print("\n" + "=" * 60)
print(" FIAP CARDIOIA - INICIANDO SISTEMA IOT MICROPYTHON (ESP32)")
print("=" * 60)

# Inicializar LED de Alerta
led_alerta = machine.Pin(PIN_LED_ALERTA, machine.Pin.OUT)
led_alerta.value(0)

# Inicializar Leitor ADC do Potenciometro (0-4095)
adc_bpm = machine.ADC(machine.Pin(PIN_POT_BPM))
try:
    adc_bpm.atten(machine.ADC.ATTN_11DB)  # Range completo de 0 a 3.3V
except AttributeError:
    pass

# Inicializar Sensor DHT22
sensor_dht = dht.DHT22(machine.Pin(PIN_DHT))

# Inicializar Display OLED via I2C
oled = None
if HAS_OLED:
    try:
        i2c = machine.I2C(0, scl=machine.Pin(PIN_I2C_SCL), sda=machine.Pin(PIN_I2C_SDA))
        oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
        oled.fill(0)
        oled.text("CARDIOIA - ESP32", 0, 4)
        oled.text("MicroPython v1.0", 0, 18)
        oled.text("Iniciando...", 0, 34)
        oled.show()
        print("[OLED] Display SSD1306 inicializado com sucesso (I2C SDA=21, SCL=22).")
    except Exception as e:
        print(f"[OLED] Aviso: Display nao detectado ou falha I2C: {e}")
        oled = None
else:
    print("[OLED] Driver ssd1306 nao disponivel.")


# ==============================================================================
# FUNCOES DE INTERFACE VISUAL (OLED)
# ==============================================================================
def atualizar_oled(bpm, temp, status_clinico, wifi_ok, buffer_qtd=0):
    """
    Renderiza na tela OLED de 128x64 o laudo instantaneo de sinais vitais.
    """
    if not oled:
        return
    try:
        oled.fill(0)
        # Header
        oled.text("CARDIOIA MONITOR", 0, 0)
        oled.hline(0, 10, 128, 1)

        # Dados Vitais
        oled.text(f"BPM: {bpm:3d} bpm", 0, 15)
        oled.text(f"Temp: {temp:.1f} C", 0, 27)

        # Status Clinico com Alerta
        if status_clinico == "CRITICO":
            oled.text("STATUS: ! ALERTA !", 0, 40)
        elif status_clinico == "ATENCAO":
            oled.text("STATUS: ATENCAO", 0, 40)
        else:
            oled.text("STATUS: ESTAVEL", 0, 40)

        # Rodape com status da conexao e buffer de borda
        oled.hline(0, 52, 128, 1)
        rede_txt = "NET:OK" if wifi_ok else "NET:OFF"
        buf_txt = f"BUF:{buffer_qtd}" if buffer_qtd > 0 else "SINCRONIZADO"
        oled.text(f"{rede_txt} {buf_txt}", 0, 55)
        oled.show()
    except Exception as e:
        print(f"[OLED] Erro ao renderizar tela: {e}")


# ==============================================================================
# CONECTIVIDADE: WI-FI & MQTT
# ==============================================================================
wlan = network.WLAN(network.STA_IF)
mqtt_client = None


def conectar_wifi():
    """Conecta ao Wi-Fi (compativel com Wokwi-GUEST)."""
    global wlan
    wlan.active(True)
    if not wlan.isconnected():
        print(f"[WIFI] Conectando a {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        tentativas = 0
        while not wlan.isconnected() and tentativas < 10:
            time.sleep(0.5)
            tentativas += 1
    if wlan.isconnected():
        print(f"[WIFI] Conectado! IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("[WIFI] Falha na conexao Wi-Fi.")
        return False


def conectar_mqtt():
    """Inicializa e conecta ao Broker MQTT."""
    global mqtt_client
    if not HAS_MQTT:
        return False
    try:
        print(f"[MQTT] Conectando ao Broker {MQTT_BROKER}:{MQTT_PORT}...")
        mqtt_client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, keepalive=60)
        mqtt_client.connect()
        print("[MQTT] Conexao estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"[MQTT] Falha na conexao com broker: {e}")
        mqtt_client = None
        return False


# ==============================================================================
# EDGE COMPUTING: CAPTURA, TRIAGEM LOCAL & RESILIENCIA
# ==============================================================================
def ler_sensores():
    """
    Realiza a leitura do sensor DHT22 e a conversao do ADC do potenciometro
    para frequencia cardiaca fisiologica (40 a 200 BPM).
    """
    # 1. Leitura do Potenciometro e mapeamento para BPM
    raw_val = adc_bpm.read()
    # Formula linear: 40 + (raw / 4095.0) * 160
    bpm = int(40 + (raw_val / 4095.0) * 160)

    # 2. Leitura do Sensor DHT22
    temp = 36.5
    umid = 60.0
    try:
        sensor_dht.measure()
        temp = sensor_dht.temperature()
        umid = sensor_dht.humidity()
    except Exception as e:
        # Fallback de leitura suave em caso de atraso de leitura fisica
        print(f"[SENSOR] Aviso leitura DHT22: {e}")

    # 3. Triagem de Borda (Edge Analytics)
    status = "ESTAVEL"
    alerta_ativo = False

    if bpm > LIMIAR_BPM_ALERTA or temp > LIMIAR_TEMP_ALERTA:
        status = "CRITICO"
        alerta_ativo = True
    elif bpm < LIMIAR_BPM_BRADICARDIA:
        status = "ATENCAO"
        alerta_ativo = True

    # 4. Ativacao do Feedback Visual Fisico (LED)
    led_alerta.value(1 if alerta_ativo else 0)

    payload = {
        "dispositivo_id": "esp32-cardioia-01",
        "timestamp_ms": time.ticks_ms(),
        "bpm": bpm,
        "temperatura": round(temp, 1),
        "umidade": round(umid, 1),
        "status_clinico": status,
        "alerta_critico": alerta_ativo,
        "edge_decision": "Acionamento de triagem hospitalar" if alerta_ativo else "Monitoramento de rotina"
    }

    return payload


def enviar_telemetria(payload):
    """
    Envia a telemetria via MQTT e/ou HTTP. Caso nao haja conexao,
    salva no buffer de borda local para resiliencia (Edge Computing).
    """
    global buffer_edge, mqtt_client

    mensagem_json = json.dumps(payload)
    enviado = False

    # Tentativa 1: Envio via MQTT
    if wlan.isconnected() and mqtt_client:
        try:
            mqtt_client.publish(MQTT_TOPIC_TELEMETRIA, mensagem_json)
            if payload.get("alerta_critico"):
                mqtt_client.publish(MQTT_TOPIC_ALERTAS, mensagem_json)
            enviado = True
        except Exception as e:
            print(f"[MQTT] Falha no envio da mensagem: {e}")
            mqtt_client = None

    # Tentativa 2: Envio via HTTP REST (se MQTT falhou ou nao esta conectado)
    if not enviado and wlan.isconnected() and HAS_UREQUESTS:
        try:
            res = urequests.post(
                BACKEND_HTTP_URL,
                headers={"Content-Type": "application/json"},
                data=mensagem_json
            )
            if res.status_code in (200, 201):
                enviado = True
            res.close()
        except Exception:
            enviado = False

    # Lógica de Resiliência: salvar no Buffer de Borda se a rede falhou
    if enviado:
        print(f"[ONLINE] Enviado: BPM={payload['bpm']} | Temp={payload['temperatura']}C | Status={payload['status_clinico']}")
        # Se ha dados offline represados, descarrega o buffer em lote
        if buffer_edge:
            sincronizar_buffer()
    else:
        if len(buffer_edge) < BUFFER_CAPACIDADE_MAXIMA:
            buffer_edge.append(payload)
            print(f"[OFFLINE] Dados salvos no Buffer Edge ({len(buffer_edge)}/{BUFFER_CAPACIDADE_MAXIMA})")
        else:
            print("[OFFLINE] Aviso: Buffer de borda cheio. Sobrescrevendo registro mais antigo.")
            buffer_edge.pop(0)
            buffer_edge.append(payload)


def sincronizar_buffer():
    """
    Descarrega ordenadamente os sinais vitais que foram retidos no buffer offline
    quando a conexao com a rede for restabelecida.
    """
    global buffer_edge, mqtt_client
    print(f"[SYNC] >>> Restabelecida conexao! Sincronizando {len(buffer_edge)} registros do buffer edge...")
    while buffer_edge and (mqtt_client or HAS_UREQUESTS):
        dado = buffer_edge[0]
        try:
            msg = json.dumps(dado)
            if mqtt_client:
                mqtt_client.publish(MQTT_TOPIC_TELEMETRIA, msg)
            elif HAS_UREQUESTS:
                res = urequests.post(BACKEND_HTTP_URL, headers={"Content-Type": "application/json"}, data=msg)
                res.close()
            buffer_edge.pop(0)
            time.sleep(0.1)
        except Exception as e:
            print(f"[SYNC] Interrupcao durante sincronizacao: {e}")
            break
    print(f"[SYNC] Sincronizacao concluida. Registros pendentes: {len(buffer_edge)}")


# ==============================================================================
# LOOP PRINCIPAL DO MICROPYTHON
# ==============================================================================
def executar():
    print("[INIT] Inicializando rotina principal do ESP32...")
    wifi_ok = conectar_wifi()
    if wifi_ok:
        conectar_mqtt()

    print("[EXEC] Monitoramento continuo iniciado. Pressione Ctrl+C para encerrar.\n")

    ciclos = 0
    while True:
        try:
            # 1. Captura e processamento local dos sensores
            telemetria = ler_sensores()

            # 2. Verificacao de reconexao periodica a cada 10 ciclos (~20s)
            ciclos += 1
            if ciclos % 10 == 0:
                wifi_ok = wlan.isconnected()
                if not wifi_ok:
                    wifi_ok = conectar_wifi()
                if wifi_ok and (not mqtt_client):
                    conectar_mqtt()

            # 3. Atualizacao da interface visual OLED
            atualizar_oled(
                bpm=telemetria["bpm"],
                temp=telemetria["temperatura"],
                status_clinico=telemetria["status_clinico"],
                wifi_ok=wlan.isconnected(),
                buffer_qtd=len(buffer_edge)
            )

            # 4. Transmissao ou armazenamento no buffer
            enviar_telemetria(telemetria)

            # 5. Manter conexao MQTT viva
            if mqtt_client:
                try:
                    mqtt_client.check_msg()
                except Exception:
                    pass

            # Pausa de amostragem (2 segundos)
            time.sleep(2)

        except KeyboardInterrupt:
            print("\n[STOP] Encerrando sistema IoT CardioIA...")
            if oled:
                oled.fill(0)
                oled.text("CARDIOIA", 0, 10)
                oled.text("Sistema Parado", 0, 25)
                oled.show()
            led_alerta.value(0)
            break
        except Exception as e:
            print(f"[ERRO] Erro inesperado no loop principal: {e}")
            time.sleep(2)


if __name__ == "__main__":
    executar()
