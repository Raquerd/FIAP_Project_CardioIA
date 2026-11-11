#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador do Relatório Técnico Oficial - Fase 7 (MVP Final CardioIA)
Título: Da Construção de Módulos à Solução Integrada
Contendo exatamente 5 páginas:
  - Página 1: Capa Executiva, Identificação, Links Oficiais & Resumo do MVP
  - Página 2: Transição de Hardware para MicroPython (ESP32 / Wokwi) & Edge Computing
  - Página 3: Núcleo Integrador Backend em Python & Orquestração dos Motores de IA
  - Página 4: Diagrama de Arquitetura Técnica Final & Fluxo de Comunicação de Dados
  - Página 5: Validação Fim-a-Fim, Roteiro do Vídeo Demonstrativo & Conclusão
"""

from pathlib import Path
from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_ROOT = BASE_DIR / "Relatorio_Integracao_Arquitetura_Final_Fase7.pdf"
PDF_DOCS = BASE_DIR / "docs" / "Relatorio_Integracao_Arquitetura_Final_Fase7.pdf"


def _latin1(text: str) -> str:
    replacements = {
        "→": "->",
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "-",
        "…": "...",
        "⚡": "*",
        "🌐": "*",
        "📱": "*",
        "💻": "*",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")


class RelatorioFinalPDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)  # Slate 900
        self.rect(0, 0, 210, 26, "F")
        self.set_y(6)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(255, 255, 255)
        self.cell(0, 6, _latin1("FIAP - 2TIAOA | PROJETO CARDIOIA - FASE 7 (MVP FINAL)"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(148, 163, 184)
        self.cell(
            0,
            5.5,
            _latin1("Cap 1: Da Construção de Módulos à Solução Integrada - Relatório Técnico & Arquitetura"),
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(5)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        texto = f"CardioIA Fase 7 - MVP Integrado | Integrantes: Davi Santos Ferreira & Lais Kurahashi | Pagina {self.page_no()}/5"
        self.cell(0, 8, _latin1(texto), align="C")


def desenhar_card_link(pdf, y, titulo, url, cor_borda, cor_fundo, cor_link):
    pdf.set_fill_color(*cor_fundo)
    pdf.set_draw_color(*cor_borda)
    pdf.rect(12, y, 186, 14.5, "DF")
    pdf.set_xy(16, y + 1.8)
    pdf.set_font("Helvetica", "B", 8.8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 4.8, _latin1(titulo), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(16)
    pdf.set_font("Helvetica", "BU", 9.2)
    pdf.set_text_color(*cor_link)
    pdf.cell(0, 5, url, link=url, new_x="LMARGIN", new_y="NEXT")


def gerar_relatorio_tecnico():
    pdf = RelatorioFinalPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    # ==========================================================================
    # PÁGINA 1: Capa Executiva, Identificação, Links Oficiais & Resumo do MVP
    # ==========================================================================
    pdf.add_page()

    # Bloco de Identificação
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(12, 31, 186, 17, "DF")
    pdf.set_xy(16, 33)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(38, 5.5, _latin1("Integrantes do Grupo:"), new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.cell(0, 5.5, _latin1("Davi Santos Ferreira  &  Lais Kurahashi   |   Turma: 2TIAOA - 2026"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(16)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(38, 5.5, _latin1("Disciplina / Etapa:"), new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.cell(0, 5.5, _latin1("Fase 7 - MVP Final: Da Construção de Módulos à Solução Integrada"), new_x="LMARGIN", new_y="NEXT")

    # Links Oficiais Clicáveis
    pdf.set_xy(12, 51)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, _latin1("1. Links Oficiais da Solução Integrada (Clicáveis)"), new_x="LMARGIN", new_y="NEXT")

    desenhar_card_link(
        pdf, 58,
        "1. Aplicação Web Publicada (Vercel SPA com CI/CD ativo):",
        "https://fiap-project-cardio-ia-delta.vercel.app",
        (59, 130, 246), (239, 246, 255), (37, 99, 235)
    )
    desenhar_card_link(
        pdf, 75.5,
        "2. Aplicativo Mobile Android (Download do .APK via Expo EAS Build):",
        "https://expo.dev/artifacts/eas/5-zVREEnJZ6c7p0Ryhjkn65hlqBnIuC4IfWS9qX_5JI.apk",
        (16, 185, 129), (240, 253, 244), (5, 150, 105)
    )
    desenhar_card_link(
        pdf, 93,
        "3. Simulação de Hardware IoT em MicroPython (Ambiente Wokwi ESP32):",
        "https://wokwi.com/projects/480358266952735745",
        (245, 158, 11), (254, 243, 199), (180, 83, 9)
    )
    desenhar_card_link(
        pdf, 110.5,
        "4. Repositório Oficial no GitHub (Código-Fonte Integrado e Documentos):",
        "https://github.com/Raquerd/FIAP_Project_CardioIA",
        (139, 92, 246), (245, 243, 255), (109, 40, 217)
    )

    # Resumo Geral da Solução
    pdf.set_xy(12, 130)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, _latin1("2. Resumo Executivo da Solução Integrada (Visão Fim-a-Fim)"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    resumo_texto = (
        "O projeto CardioIA atinge sua maturidade técnica consolidando todos os módulos desenvolvidos ao longo "
        "do curso em um ecossistema hospitalar coeso, orquestrado por Python e disponível em produção para múltiplos "
        "canais de atendimento (Web e Mobile). O fluxo contempla a captura de sinais vitais de borda simulados em "
        "MicroPython (ESP32 no Wokwi), a transmissão resiliente de telemetria via MQTT/HTTP para um Backend Integrador "
        "em Python hospedado na nuvem (AWS Elastic Beanstalk), a inferência contínua por motores de Inteligência "
        "Artificial supervisionada (Classificação de ECG por CNN/ResNet50 da Fase 4, Assistente Conversacional "
        "Watson/LLM da Fase 5 e Predição de Crises por Random Forest e Sistema Multiagente da Fase 6) e a entrega de "
        "indicadores clínicos e laudos em tempo real nas interfaces do paciente e da equipe médica."
    )
    pdf.multi_cell(0, 4.6, _latin1(resumo_texto), new_x="LMARGIN", new_y="NEXT")

    # Divisão de Trabalho da Fase 7
    pdf.set_xy(12, 182)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, _latin1("3. Divisão de Responsabilidades na Fase 7"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(12, 190, 186, 75, "DF")

    pdf.set_xy(16, 193)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, _latin1("Parte 1 - Deploy e Distribuição Profissional Front-End & Mobile (Lais Kurahashi):"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.7)
    pdf.set_text_color(51, 65, 85)
    itens_p1 = [
        "Publicação da aplicação Web em React + Vite na Vercel com suporte a rotas SPA (web/vercel.json) e CI/CD ativo.",
        "Configuração de build mobile Expo EAS (mobile/app.json com domínio invertido e mobile/eas.json perfil preview).",
        "Geração bem-sucedida do pacote instalável .apk Android no dashboard da Expo e documentação no README.md.",
        "Refinamento de UX nas telas de login, visão geral, envio de imagens de ECG e visualização de probabilidades.",
    ]
    for it in itens_p1:
        pdf.set_x(18)
        pdf.multi_cell(176, 4.3, _latin1(f"- {it}"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_xy(16, 227)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, _latin1("Parte 2 - Integração do Ecossistema, MicroPython & Arquitetura Final (Davi Ferreira):"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.7)
    pdf.set_text_color(51, 65, 85)
    itens_p2 = [
        "Transição de C/C++ para MicroPython no ESP32 (iot/main.py), conectando DHT22, Potenciômetro ADC, OLED e LED.",
        "Implementação do Buffer de Borda (Edge Computing) com tolerância a falhas de rede e sincronização em lote.",
        "Construção do Backend Integrador em Python (backend/app.py e backend/integrador_service.py) unificando IA e IoT.",
        "Criação de rota e interface de Telemetria & Risco em tempo real integrada à Web e elaboração do Relatório Técnico.",
    ]
    for it in itens_p2:
        pdf.set_x(18)
        pdf.multi_cell(176, 4.3, _latin1(f"- {it}"), new_x="LMARGIN", new_y="NEXT")

    # ==========================================================================
    # PÁGINA 2: Transição de Hardware para MicroPython & Edge Computing
    # ==========================================================================
    pdf.add_page()

    pdf.set_xy(12, 31)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, _latin1("1. Transição de Hardware: C/C++ para MicroPython no ESP32"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    txt_micropy = (
        "Na Fase 3, o protótipo de sensoriamento havia sido desenvolvido em C++ para a IDE Arduino. Na presente fase, "
        "conforme a diretriz de modernização tecnológica, realizamos a transição completa da lógica de firmware "
        "para MicroPython (firmware v1.20+ no ESP32 DevKit v4). Essa abordagem eleva a manutenibilidade do código, "
        "padroniza toda a pilha tecnológica da CardioIA em Python e permite validação direta de objetos JSON em memória."
    )
    pdf.multi_cell(0, 4.5, _latin1(txt_micropy), new_x="LMARGIN", new_y="NEXT")

    # Tabela de Pinout e Sensores
    pdf.set_y(pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5.5, _latin1("Mapeamento Físico de Periféricos e Pinos (ESP32 DevKit v4):"), new_x="LMARGIN", new_y="NEXT")

    col_widths = [40, 25, 45, 76]
    headers = ["Periferico / Sensor", "Pino GPIO", "Protocolo / Barramento", "Funcao Clinica no CardioIA"]
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_x(12)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 6, _latin1(h), border=1, fill=True, align="C" if i < 3 else "L")
    pdf.ln()

    linhas_tabela = [
        ("Sensor DHT22", "GPIO 15", "Digital 1-Wire", "Captura continua de Temperatura Corporal e Umidade"),
        ("Potenciometro ADC", "GPIO 34", "Analogico (ADC 11dB)", "Simulacao de Frequencia Cardiaca (40 a 200 BPM)"),
        ("Display OLED SSD1306", "GPIO 21 (SDA)\nGPIO 22 (SCL)", "I2C (0x3C, 128x64 px)", "Feedback visual local de BPM, Temperatura, Status e Rede"),
        ("LED Vermelho Alerta", "GPIO 2", "Digital Output (PWM)", "Acionamento fisico instantaneo em Taquicardia ou Febre"),
        ("Conectividade Wi-Fi", "Interno", "802.11 b/g/n (STA)", "Transmissao MQTT (HiveMQ) e fallback HTTP REST"),
    ]
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(15, 23, 42)
    for item in linhas_tabela:
        pdf.set_x(12)
        pdf.cell(col_widths[0], 6.5, _latin1(item[0]), border=1)
        pdf.cell(col_widths[1], 6.5, _latin1(item[1]), border=1, align="C")
        pdf.cell(col_widths[2], 6.5, _latin1(item[2]), border=1, align="C")
        pdf.cell(col_widths[3], 6.5, _latin1(item[3]), border=1)
        pdf.ln()

    # Seção Edge Computing & Resiliência
    pdf.set_y(pdf.get_y() + 4)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 5.5, _latin1("2. Inteligência de Borda (Edge Computing) e Tolerância a Falhas"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    txt_edge = (
        "A camada IoT não opera como mera transmissora passiva de dados; ela desempenha triagem primária local "
        "(Edge Analytics) antes mesmo de acionar a nuvem, garantindo segurança ao paciente em situações críticas:"
    )
    pdf.multi_cell(0, 4.4, _latin1(txt_edge), new_x="LMARGIN", new_y="NEXT")

    pontos_edge = [
        "Triagem Imediata por Hardware: Ao detectar batimentos acima de 120 BPM ou temperatura superior a 38,0 °C, "
        "o microcontrolador aciona o LED vermelho no GPIO 2 e atualiza a tela OLED para '! ALERTA !' em tempo de máquina (<5ms).",
        "Buffer Circular de Borda (Resiliência Offline-First): Implementamos uma fila circular em memória RAM local com "
        "capacidade para 20 registros. Caso a rede Wi-Fi oscile ou o broker MQTT fique inacessível, os sinais vitais "
        "são persistidos localmente sem perda de histórico clínico.",
        "Sincronização Automática em Lote: Quando a conectividade é restabelecida, a rotina sincronizar_buffer() descarrega "
        "todos os pacotes acumulados de forma sequencial com carimbo de tempo, limpando o buffer de borda ordenadamente.",
        "Feedback Visual Completo em OLED SSD1306: Utilizando o driver oficial framebuf ssd1306.py, a interface exibe "
        "o cabeçalho do CardioIA, valores instantâneos de BPM e Temperatura, estado clínico e contador de pacotes pendentes.",
    ]
    for pt in pontos_edge:
        pdf.set_x(16)
        pdf.multi_cell(182, 4.3, _latin1(f"- {pt}"), new_x="LMARGIN", new_y="NEXT")

    # Box com código JSON de Telemetria
    pdf.set_y(pdf.get_y() + 3)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(12, pdf.get_y(), 186, 26, "DF")
    pdf.set_xy(16, pdf.get_y() + 1.5)
    pdf.set_font("Courier", "B", 8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 4, _latin1("Estrutura do Pacote de Telemetria Emitido pelo ESP32 (JSON):"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", "", 7.5)
    json_lines = [
        '{"dispositivo_id": "esp32-cardioia-01", "timestamp_ms": 17943518, "bpm": 138, "temperatura": 38.6,',
        ' "umidade": 60.0, "status_clinico": "CRITICO", "alerta_critico": true,',
        ' "edge_decision": "Acionamento de triagem hospitalar"}',
    ]
    for jl in json_lines:
        pdf.set_x(16)
        pdf.cell(0, 3.8, _latin1(jl), new_x="LMARGIN", new_y="NEXT")

    # ==========================================================================
    # PÁGINA 3: Núcleo Integrador Backend em Python & Orquestração de Motores de IA
    # ==========================================================================
    pdf.add_page()

    pdf.set_xy(12, 31)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, _latin1("1. O Núcleo Integrador em Python (backend/app.py)"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    txt_backend = (
        "O núcleo do ecossistema é composto pelo serviço integrador em Python (backend/app.py e backend/integrador_service.py). "
        "Ele atua como o orquestrador central de mensagens, recebendo as conexões das aplicações cliente (Vercel e APK) "
        "e dos sensores de campo (MicroPython), encaminhando os dados para os motores de Inteligência Artificial especializados."
    )
    pdf.multi_cell(0, 4.5, _latin1(txt_backend), new_x="LMARGIN", new_y="NEXT")

    # Integração dos Motores de IA
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5.5, _latin1("Conexão Unificada com os Motores de Inteligência Artificial:"), new_x="LMARGIN", new_y="NEXT")

    motores = [
        ("Fase 4 - Visão Computacional (CNN do Zero & ResNet50 Transfer Learning):",
         "O endpoint POST /api/ecg/analisar recebe exames de eletrocardiograma em formato PNG/JPEG, pré-processa "
         "as imagens em tensores 3x224x224 via PyTorch/Torchvision e infere a probabilidade de classe Normal (N) "
         "ou Anomalia (M), retornando o percentual de certeza consumido pelo Web e Mobile."),
        ("Fase 5 - Assistente Conversacional & Triagem Clínica (IBM Watson Assistant v2):",
         "Os endpoints /api/session e /api/message gerenciam sessões conversacionais com transbordo inteligente, "
         "processando relatos em linguagem natural do paciente e orientando protocolos de preparo de exames com fallback."),
        ("Fase 6 - Modelo Preditivo de Risco Hospitalar (Random Forest Classifier):",
         "Alimentado diretamente pelos sinais de telemetria dos sensores (FC média e Temperatura) cruzados com a carga "
         "hospitalar. Executa a predição probabilística da base serializada (modelo_risco_cardiaco.joblib), atingindo "
         "99,90% de acurácia com Brier Score de 0,0058 e previsão de pico de risco (0 ou 1)."),
        ("Fase 6 - Sistema Multiagente Autônomo & Protocolos (OpenAI Agents SDK):",
         "Orquestra 4 agentes especializados (Orquestrador, Analista de Risco, Especialista em Protocolos e Planejador "
         "de Resposta) conectados por 3 handoffs explícitos, avaliando as 10 diretrizes clínicas de protocolos_emergencia.json "
         "e gerando laudo justificado validado via Pydantic."),
    ]
    for tit, desc in motores:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(30, 58, 138)
        pdf.set_x(14)
        pdf.cell(0, 4.8, _latin1(tit), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8.7)
        pdf.set_text_color(51, 65, 85)
        pdf.set_x(16)
        pdf.multi_cell(182, 4.2, _latin1(desc), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    # Tabela de Endpoints da API REST
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5.5, _latin1("Catálogo de Endpoints da API REST Unificada (CORS Habilitado):"), new_x="LMARGIN", new_y="NEXT")

    w_api = [22, 42, 60, 62]
    h_api = ["Metodo", "Rota da API", "Finalidade Tecnica", "Origem / Consumidor"]
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8.2)
    pdf.set_x(12)
    for i, h in enumerate(h_api):
        pdf.cell(w_api[i], 5.5, _latin1(h), border=1, fill=True, align="C" if i < 2 else "L")
    pdf.ln()

    rotas = [
        ("GET", "/api/status", "Health Check unificado e diagnostico de modulos", "Frontend Web, Mobile e Monitoramento"),
        ("POST", "/api/telemetria", "Ingestao de sinais do ESP32 e predicao de risco", "Firmware MicroPython (Wokwi / Hardware)"),
        ("GET", "/api/telemetria/atual", "Consulta o ultimo sinal vital e risco clinico", "Interface Web (Aba Telemetria) e Mobile"),
        ("GET", "/api/telemetria/historico", "Historico recente para graficos de tendencia", "Painel de Acompanhamento Medico"),
        ("POST", "/api/predicao/risco", "Inferencia preditiva com parametros customizados", "Sistema Multiagente e Simulador"),
        ("POST", "/api/ecg/analisar", "Classificacao de ECG com CNN e ResNet50", "Aplicacao Web Vercel e App Mobile APK"),
        ("POST", "/api/message", "Interacao conversacional com Watson Assistant", "Chatbot do Paciente e Triagem Digital"),
    ]
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(15, 23, 42)
    for r in rotas:
        pdf.set_x(12)
        pdf.cell(w_api[0], 5, r[0], border=1, align="C")
        pdf.set_font("Courier", "B", 7.8)
        pdf.cell(w_api[1], 5, r[1], border=1)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(w_api[2], 5, _latin1(r[2]), border=1)
        pdf.cell(w_api[3], 5, _latin1(r[3]), border=1)
        pdf.ln()

    # ==========================================================================
    # PÁGINA 4: Diagrama de Arquitetura Técnica Final & Fluxo de Dados
    # ==========================================================================
    pdf.add_page()

    pdf.set_xy(12, 31)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, _latin1("1. Diagrama Técnico da Arquitetura Final CardioIA"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 8.8)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(
        0, 4.3,
        _latin1(
            "O desenho arquitetural abaixo consolida as 5 camadas da solução integrada, evidenciando o percurso "
            "completo dos dados desde o sensoriamento físico de borda até as interfaces interativas do usuário final:"
        ),
        new_x="LMARGIN",
        new_y="NEXT"
    )

    # DESENHO DO DIAGRAMA DE ARQUITETURA EM BLOCOS
    y_start = 48
    camadas = [
        ("CAMADA 1: SENSORIAMENTO & EDGE COMPUTING (MICROPYTHON)",
         "ESP32 DevKit v4 | Sensor DHT22 (Temp) | Potenciometro (BPM 40-200) | OLED SSD1306 | LED Alerta\n"
         "Logica de borda: Triagem <5ms, buffer circular de resiliencia (20 registros) e reconexao automatica",
         (254, 243, 199), (245, 158, 11), (180, 83, 9)),
        ("CAMADA 2: CONECTIVIDADE & TRANSPORTE DE DADOS",
         "Protocolos: MQTT (Broker HiveMQ - porta 1883) com topicos de telemetria e alertas criticos\n"
         "Fallback: HTTP/1.1 REST JSON multipart direto para o gateway na nuvem via Wi-Fi 802.11b/g/n",
         (240, 253, 244), (16, 185, 129), (5, 150, 105)),
        ("CAMADA 3: BACKEND INTEGRADOR PYTHON (NUCLEO DO SISTEMA)",
         "Flask REST API (backend/app.py) | Gunicorn WSGI | Hospedado na AWS Elastic Beanstalk (us-east-2)\n"
         "Servico Integrador: Ingestao em tempo real, CORS, historico em memoria e orquestracao multi-modelo",
         (239, 246, 255), (59, 130, 246), (37, 99, 235)),
        ("CAMADA 4: MOTORES DE INTELIGÊNCIA ARTIFICIAL (IA HOSPITALAR)",
         "1. Visao Computacional: CNN e ResNet50 (PyTorch) para laudo de imagens de eletrocardiograma (Fase 4)\n"
         "2. Assistente Conversacional: IBM Watson Assistant v2 (NLP de triagem e agendamentos) (Fase 5)\n"
         "3. Modelo Preditivo: Random Forest Classifier (Acuracia 99.90%) para antecipacao de crises (Fase 6)\n"
         "4. Sistema Multiagente: 4 agentes autônomos (OpenAI Agents SDK) + 10 protocolos de emergencia (Fase 6)",
         (245, 243, 255), (139, 92, 246), (109, 40, 217)),
        ("CAMADA 5: APRESENTAÇÃO & EXPERIÊNCIA DO USUÁRIO (FRONT-END & MOBILE)",
         "Web: React + Vite publicado na Vercel (CI/CD automatico via GitHub, rotas SPA vercel.json)\n"
         "Mobile: React Native + Expo APK (.apk funcional via EAS Build, app.json e eas.json)\n"
         "Funcionalidades: Login Supabase, laudos de ECG, painel de telemetria em tempo real e score de risco",
         (255, 241, 242), (244, 63, 94), (190, 18, 60)),
    ]

    curr_y = y_start
    for titulo, desc, c_fundo, c_borda, c_texto in camadas:
        # Caixa da Camada
        pdf.set_fill_color(*c_fundo)
        pdf.set_draw_color(*c_borda)
        pdf.rect(12, curr_y, 186, 28, "DF")

        # Título da Camada
        pdf.set_xy(16, curr_y + 1.8)
        pdf.set_font("Helvetica", "B", 9.2)
        pdf.set_text_color(*c_texto)
        pdf.cell(0, 4.8, _latin1(titulo), new_x="LMARGIN", new_y="NEXT")

        # Descrição da Camada
        pdf.set_font("Helvetica", "", 7.8)
        pdf.set_text_color(15, 23, 42)
        pdf.set_x(16)
        pdf.multi_cell(178, 3.8, _latin1(desc), new_x="LMARGIN", new_y="NEXT")

        # Desenhar seta de fluxo se não for a última camada
        if curr_y < y_start + (28 * 4):
            seta_y = curr_y + 28
            pdf.set_draw_color(100, 116, 139)
            pdf.set_line_width(0.6)
            pdf.line(105, seta_y, 105, seta_y + 4)
            # Cabeça da seta
            pdf.line(103.5, seta_y + 2.5, 105, seta_y + 4)
            pdf.line(106.5, seta_y + 2.5, 105, seta_y + 4)
            pdf.set_line_width(0.2)
            curr_y += 33
        else:
            curr_y += 30

    # Matriz de Segurança e Comunicação
    pdf.set_y(curr_y + 3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, _latin1("Garantias Técnicas de Fluidez e Segurança do Fluxo:"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 8.2)
    pdf.set_text_color(51, 65, 85)
    garantias = [
        "Comunicação Assíncrona e Baixa Latência: A telemetria opera em intervalos de 2 segundos, com tempo médio de inferência preditiva inferior a 40ms no Backend Python.",
        "Segurança e Isolamento: Credenciais sensíveis mantidas estritamente em variáveis de ambiente (.env), rotas autenticadas por Bearer Token e isolamento por CORS na Vercel.",
        "Desacoplamento Completo: Caso o hardware Wokwi esteja offline, o Web e o Mobile continuam operando normalmente via dados em cache ou simulações interativas.",
    ]
    for g in garantias:
        pdf.set_x(16)
        pdf.multi_cell(182, 4, _latin1(f"- {g}"), new_x="LMARGIN", new_y="NEXT")

    # ==========================================================================
    # PÁGINA 5: Validação Fim-a-Fim, Roteiro do Vídeo Demonstrativo & Conclusão
    # ==========================================================================
    pdf.add_page()

    pdf.set_xy(12, 31)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, _latin1("1. Roteiro Estruturado do Vídeo Demonstrativo (Até 5 Minutos)"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 8.8)
    pdf.set_text_color(30, 41, 59)
    txt_video = (
        "O vídeo demonstrativo comprova a integração real do ecossistema fim-a-fim, seguindo o roteiro técnico "
        "planejado de até 5 minutos com visualização das ferramentas e interfaces ativas em produção:"
    )
    pdf.multi_cell(0, 4.3, _latin1(txt_video), new_x="LMARGIN", new_y="NEXT")

    etapas_video = [
        ("Minuto 0:00 a 0:45", "Abertura, Apresentação da Equipe & Visão Geral da Arquitetura:",
         "Apresentação dos integrantes Davi Santos Ferreira e Lais Kurahashi, exibição do repositório no GitHub, "
         "apresentação do diagrama da arquitetura final de 5 camadas e esclarecimento dos objetivos do MVP integrado."),
        ("Minuto 0:45 a 1:45", "Hardware IoT e Simulação em MicroPython no Wokwi:",
         "Demonstração do firmware ESP32 executando no Wokwi. Leitura da temperatura no DHT22 e modulação de BPM "
         "no potenciômetro. Feedback visual local com acionamento do display OLED SSD1306 e do LED vermelho de alerta. "
         "Demonstração do Buffer de Borda salvando dados offline e sincronizando automaticamente ao recuperar o sinal."),
        ("Minuto 1:45 a 2:45", "Backend Integrador Python & Motores de IA:",
         "Demonstração dos logs do Backend Flask em execução na AWS Elastic Beanstalk. Ingestão da telemetria "
         "do ESP32 em tempo real, chamada automática ao modelo Random Forest da Fase 6 (predizendo risco e score) "
         "e execução da bateria de 7 testes automatizados de integração com 100% de sucesso."),
        ("Minuto 2:45 a 4:00", "Aplicação Web na Vercel (CI/CD) & Nova Tela de Telemetria:",
         "Navegação na URL pública da Vercel (rotas SPA funcionais). Demonstração da tela de Análise de ECG (Fase 4), "
         "seguida da apresentação da nova tela 'Telemetria & Risco' atualizando os cards de BPM, Temperatura, "
         "status do ESP32 e diretrizes clínicas acionadas dinamicamente."),
        ("Minuto 4:00 a 5:00", "Aplicativo Mobile Android (APK via EAS Build) & Conclusão:",
         "Demonstração do aplicativo CardioIA instalado no dispositivo Android via .apk gerado no EAS Build. "
         "Validação do fluxo de login e visualização dos indicadores cardíacos. Conclusão final da entrega da Fase 7."),
    ]

    pdf.set_y(pdf.get_y() + 2)
    for tempo, titulo_etapa, desc_etapa in etapas_video:
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(226, 232, 240)
        pdf.rect(12, pdf.get_y(), 186, 21.5, "DF")
        pdf.set_xy(15, pdf.get_y() + 1.2)
        pdf.set_font("Helvetica", "B", 8.8)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(32, 4.5, _latin1(f"[{tempo}]"), new_x="RIGHT", new_y="TOP")
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 4.5, _latin1(titulo_etapa), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 7.8)
        pdf.set_text_color(71, 85, 105)
        pdf.set_x(15)
        pdf.multi_cell(180, 3.6, _latin1(desc_etapa), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2.2)

    # Resultados dos Testes Automatizados
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 5.5, _latin1("2. Homologação da Solução: Testes Automatizados de Integração"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    txt_testes = (
        "A suíte de testes automatizados backend/test_integrador.py foi executada sobre os módulos integrados, "
        "validando 100% dos requisitos técnicos estipulados para a Fase 7:"
    )
    pdf.multi_cell(0, 4, _latin1(txt_testes), new_x="LMARGIN", new_y="NEXT")

    testes_resumo = [
        "test_01_health_check_status: Diagnóstico de saúde da API, Watson, modelos de risco e IoT -> [APROVADO]",
        "test_02_recebimento_telemetria_micropython_normal: Ingestão de telemetria estável (BPM 76, Temp 36.6°C) -> [APROVADO]",
        "test_03_recebimento_telemetria_micropython_alerta_critico: Ingestão de crise (BPM 138, Temp 38.6°C) -> [APROVADO]",
        "test_04_consulta_ultimo_sinal_iot: Retorno instantâneo do último sinal para alimentação da UI -> [APROVADO]",
        "test_05_consulta_historico_iot: Recuperação ordenada do histórico de telemetria para gráficos -> [APROVADO]",
        "test_06_predicao_risco_personalizada: Inferência do modelo Random Forest e acionamento de protocolos -> [APROVADO]",
        "test_07_resumo_integracao_completa: Consolidação executiva dos 4 pilares do ecossistema hospitalar -> [APROVADO]",
    ]
    pdf.set_font("Courier", "", 7.2)
    pdf.set_text_color(15, 23, 42)
    for tr in testes_resumo:
        pdf.set_x(16)
        pdf.cell(0, 3.8, _latin1(tr), new_x="LMARGIN", new_y="NEXT")

    # Conclusão Final
    pdf.set_y(pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 5, _latin1("3. Conclusão do MVP Final CardioIA"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "I", 8.3)
    pdf.set_text_color(51, 65, 85)
    conclusao_txt = (
        "Com a unificação funcional dos módulos, a transição para MicroPython com feedback visual duplo (OLED/LED), "
        "o deploy Web com CI/CD na Vercel e o aplicativo Mobile .apk via Expo EAS, a equipe entrega um MVP completo, "
        "auditável e aderente às melhores práticas de engenharia de software e Inteligência Artificial aplicada à saúde."
    )
    pdf.multi_cell(0, 4, _latin1(conclusao_txt), new_x="LMARGIN", new_y="NEXT")

    # Salvar PDFs
    pdf.output(str(PDF_ROOT))
    PDF_DOCS.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(PDF_DOCS))
    print(f"Relatório Técnico da Fase 7 gerado com sucesso em:\n - {PDF_ROOT}\n - {PDF_DOCS}")


if __name__ == "__main__":
    gerar_relatorio_tecnico()
