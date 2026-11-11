# CardioIA - Módulo IoT em MicroPython (Fase 7 - MVP Integrado)

Este diretório contém a evolução da camada de sensoriamento e computação de borda (*Edge Computing*) do projeto **CardioIA**, com a transição completa da base anterior em C/C++ (`skecth_esp32.ino`) para **MicroPython** executando no microcontrolador **ESP32 DevKit v4** simulado no ambiente **Wokwi**.

---

## 🎯 Objetivos Deste Módulo

1. **Transição para MicroPython:** Código modular em Python de baixo nível para microcontroladores (`main.py` e driver `ssd1306.py`).
2. **Sensoriamento Clínico Contínuo:**
   - **Frequência Cardíaca (BPM):** Leitura analógica via ADC (Pino 34 - Potenciômetro) mapeada dinamicamente para o intervalo clínico de **40 a 200 BPM**.
   - **Temperatura e Umidade:** Leitura digital via sensor **DHT22** (Pino 15).
3. **Feedback Visual Duplo:**
   - **Display OLED SSD1306 (I2C):** Resolução 128x64 exibindo BPM, Temperatura, Status Clínico (`ESTÁVEL`, `ATENÇÃO` ou `! ALERTA !`) e estado da conexão/buffer.
   - **LED de Alerta Físico (GPIO 2):** Acionamento imediato por hardware ao detectar taquicardia (>120 BPM) ou febre (>38,0°C).
4. **Resiliência e Edge Computing (Offline-First):**
   - Buffer circular de borda com retenção de até **20 medições** caso o Wi-Fi ou Broker MQTT fiquem inacessíveis.
   - Sincronização automática em lote assim que a conectividade for restabelecida.
5. **Transmissão de Telemetria:**
   - Publicação assíncrona em MQTT no tópico `fiap/cardioia/telemetria` (Broker HiveMQ).
   - Envio HTTP REST direto para o endpoint `/api/telemetria` do Backend Integrador em Python.

---

## 🔌 Pinout e Mapeamento de Conexões (ESP32)

| Periférico | Pino no ESP32 | Protocolo / Tipo | Finalidade Clínica |
| :--- | :--- | :--- | :--- |
| **Sensor DHT22** | `GPIO 15` | Digital (1-Wire) | Monitoramento de Temperatura (°C) e Umidade |
| **Potenciômetro** | `GPIO 34` | Analógico (ADC 11dB) | Simulação de Batimentos Cardíacos (40 a 200 BPM) |
| **Display OLED (SDA)** | `GPIO 21` | I2C Data | Barramento de dados do display SSD1306 |
| **Display OLED (SCL)** | `GPIO 22` | I2C Clock | Clock de sincronização do display SSD1306 |
| **LED Vermelho de Alerta** | `GPIO 2` | Digital Output | Alerta visual de taquicardia/febre crítica |
| **Alimentação** | `3V3` e `5V` | Alimentação | Linhas de tensão do ESP32 |
| **Aterramento** | `GND` | Ground | Referência comum de aterramento |

---

## 🌐 Como Executar a Simulação no Wokwi

### Link do Projeto no Wokwi:
🔗 **[Simulação MicroPython CardioIA no Wokwi](https://wokwi.com/projects/480358266952735745)**

### Passo a Passo para Criar ou Rodar a Simulação:
1. Acesse o [Wokwi ESP32 MicroPython](https://wokwi.com/projects/new/micropython-esp32).
2. Na aba **`diagram.json`**, cole o conteúdo do arquivo [`iot/diagram.json`](./diagram.json).
3. Na aba **`main.py`**, cole o código de [`iot/main.py`](./main.py).
4. Crie um novo arquivo com o nome **`ssd1306.py`** e cole o conteúdo de [`iot/ssd1306.py`](./ssd1306.py).
5. Clique no botão verde **Play / Iniciar Simulação**.
6. No console serial e na tela OLED você verá o laudo dos sinais vitais sendo atualizado a cada 2 segundos.
7. Mova o controle deslizante do potenciômetro ou altere a temperatura no DHT22 para verificar o acionamento do LED de alerta e o aviso `! ALERTA !` no display OLED.

---

## 📦 Formato da Mensagem de Telemetria (JSON)

```json
{
  "dispositivo_id": "esp32-cardioia-01",
  "timestamp_ms": 142850,
  "bpm": 135,
  "temperatura": 38.4,
  "umidade": 62.0,
  "status_clinico": "CRITICO",
  "alerta_critico": true,
  "edge_decision": "Acionamento de triagem hospitalar"
}
```

---

## 🛠️ Script Utilitário de Teste / Simulação Local

Para testar o fluxo de telemetria sem depender do simulador Wokwi aberto, você pode executar o script utilitário:
```bash
python iot/simulador_iot.py
```
Ele simula o comportamento do ESP32 enviando pacotes aleatórios e cenários clínicos diretamente para a API REST do Backend Integrador em Python.
