#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o PDF de Entrega Oficial da Fase 7 (CardioIA - Da Construção de Módulos à Solução Integrada: MVP Final)
Gera os arquivos:
  - Entrega_Final_Fase6_CardioIA.pdf (atualizado com a entrega atual)
  - docs/Entrega_Final_Fase6_CardioIA.pdf
  - Entrega_Final_Fase7_CardioIA.pdf
  - docs/Entrega_Final_Fase7_CardioIA.pdf
"""

from pathlib import Path
from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent.parent

DESTINOS = [
    BASE_DIR / "Entrega_Final_Fase6_CardioIA.pdf",
    BASE_DIR / "docs" / "Entrega_Final_Fase6_CardioIA.pdf",
    BASE_DIR / "Entrega_Final_Fase7_CardioIA.pdf",
    BASE_DIR / "docs" / "Entrega_Final_Fase7_CardioIA.pdf",
]


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
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")


class EntregaPDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 26, "F")
        self.set_y(5.5)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(255, 255, 255)
        self.cell(0, 6.5, _latin1("FIAP - 2TIAOA | PROJETO CARDIOIA - FASE 7 (MVP FINAL)"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(148, 163, 184)
        self.cell(
            0,
            5,
            _latin1("Da Construção de Módulos à Solução Integrada: IoT MicroPython, IAs, Backend e Web/Mobile"),
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )

    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(100, 116, 139)
        self.cell(
            0,
            6,
            _latin1("CardioIA Fase 7 - Entrega Oficial | Integrantes: Davi Santos Ferreira e Lais Kurahashi | Turma 2TIAOA"),
            align="C",
        )


def desenhar_card_link_duplo(pdf, y, x1, w1, tit1, url1, cor_borda1, cor_fundo1, cor_link1,
                             x2, w2, tit2, url2, cor_borda2, cor_fundo2, cor_link2, h=11.2):
    # Card 1
    pdf.set_fill_color(*cor_fundo1)
    pdf.set_draw_color(*cor_borda1)
    pdf.rect(x1, y, w1, h, "DF")
    pdf.set_xy(x1 + 3, y + 1.2)
    pdf.set_font("Helvetica", "B", 7.8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w1 - 6, 4, _latin1(tit1), new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(x1 + 3, y + 5.2)
    pdf.set_font("Helvetica", "BU", 7.3)
    pdf.set_text_color(*cor_link1)
    pdf.cell(w1 - 6, 4, url1, link=url1, new_x="LMARGIN", new_y="NEXT")

    # Card 2
    if x2 is not None:
        pdf.set_fill_color(*cor_fundo2)
        pdf.set_draw_color(*cor_borda2)
        pdf.rect(x2, y, w2, h, "DF")
        pdf.set_xy(x2 + 3, y + 1.2)
        pdf.set_font("Helvetica", "B", 7.8)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(w2 - 6, 4, _latin1(tit2), new_x="LMARGIN", new_y="NEXT")
        pdf.set_xy(x2 + 3, y + 5.2)
        pdf.set_font("Helvetica", "BU", 7.3)
        pdf.set_text_color(*cor_link2)
        pdf.cell(w2 - 6, 4, url2, link=url2, new_x="LMARGIN", new_y="NEXT")


def gerar_pdf_entrega():
    pdf = EntregaPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # Bloco de Integrantes
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(12, 29, 186, 14.5, "DF")
    pdf.set_xy(15, 30.5)
    pdf.set_font("Helvetica", "B", 8.8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(38, 5, _latin1("Integrantes do Grupo:"), new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "", 8.8)
    pdf.cell(0, 5, _latin1("Davi Santos Ferreira  &  Lais Kurahashi   |   Turma: 2TIAOA - 2026"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 8.8)
    pdf.cell(38, 5, _latin1("Disciplina / Fase:"), new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "", 8.8)
    pdf.cell(0, 5, _latin1("Fase 7 - Cap 1: Da Construção de Módulos à Solução Integrada (MVP Final CardioIA)"), new_x="LMARGIN", new_y="NEXT")

    # Bloco de Links Oficiais (Clicáveis)
    pdf.set_xy(12, 46)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 5.5, _latin1("1. Links Oficiais da Solução Integrada (Clicáveis)"), new_x="LMARGIN", new_y="NEXT")

    # Link 1: Vídeo de Demonstração (Destaque Red)
    desenhar_card_link_duplo(
        pdf, 52.5,
        12, 186, "1. Vídeo de Demonstração Oficial da Solução (YouTube - Não Listado):",
        "https://youtu.be/BRGNv5NzkT0",
        (220, 38, 38), (254, 242, 242), (185, 28, 28),
        None, 0, "", "", (), (), (),
        h=11
    )

    # Links 2 e 3 (Duas colunas: Web Vercel e App Mobile APK)
    desenhar_card_link_duplo(
        pdf, 65,
        12, 91.5, "2. Aplicação Web em Produção (Vercel SPA):",
        "https://fiap-project-cardio-ia-delta.vercel.app",
        (59, 130, 246), (239, 246, 255), (37, 99, 235),
        106.5, 91.5, "3. Aplicativo Android (APK via EAS Build):",
        "https://expo.dev/artifacts/eas/5-zVREEnJZ6c7p0Ryhjkn65hlqBnIuC4IfWS9qX_5JI.apk",
        (16, 185, 129), (240, 253, 244), (5, 150, 105),
        h=11
    )

    # Links 4 e 5 (Duas colunas: Wokwi MicroPython e GitHub)
    desenhar_card_link_duplo(
        pdf, 77.5,
        12, 91.5, "4. Simulação IoT MicroPython (Wokwi ESP32):",
        "https://wokwi.com/projects/480358266952735745",
        (245, 158, 11), (254, 243, 199), (180, 83, 9),
        106.5, 91.5, "5. Repositório Oficial no GitHub:",
        "https://github.com/Raquerd/FIAP_Project_CardioIA",
        (139, 92, 246), (245, 243, 255), (109, 40, 217),
        h=11
    )

    # Seção 2: Resumo do que foi trabalhado na Fase 7
    pdf.set_xy(12, 91)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 5.5, _latin1("2. Resumo Executivo da Solução Integrada na Fase 7"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 8.1)
    pdf.set_text_color(30, 41, 59)
    intro_text = (
        "Nesta Fase 7, consolidamos o MVP completo do ecossistema CardioIA, orquestrando hardware IoT com firmware em "
        "MicroPython, inteligência preditiva de risco cardiovascular, visão computacional de ECG, chatbot conversacional, "
        "backend em nuvem e aplicações cliente (Web e Mobile) totalmente conectadas."
    )
    pdf.multi_cell(0, 3.8, _latin1(intro_text), new_x="LMARGIN", new_y="NEXT")

    # Parte 1
    pdf.set_y(pdf.get_y() + 1.2)
    pdf.set_font("Helvetica", "B", 8.8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, _latin1("Parte 1 - Deploy em Nuvem, Aplicação Web e Aplicativo Mobile (Lais Kurahashi):"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 7.8)
    pdf.set_text_color(51, 65, 85)
    itens_p1 = [
        "Deploy da aplicação Web em React + Vite na Vercel com suporte a rotas SPA (web/vercel.json) e automação de CI/CD via GitHub.",
        "Backend Flask hospedado no AWS Elastic Beanstalk (cardioia-env na região us-east-2) configurado com Gunicorn e rotas protegidas.",
        "Desenvolvimento do aplicativo mobile Android com React Native e Expo, permitindo login, upload de exames e laudo de ECG.",
        "Geração de build de produção Android (.apk) distribuído via Expo Application Services (EAS Build) para instalação em dispositivos reais.",
        "Configuração de autenticação e persistência de sessões com o Supabase.",
    ]
    for item in itens_p1:
        pdf.set_x(15)
        pdf.multi_cell(182, 3.5, _latin1(f"- {item}"), new_x="LMARGIN", new_y="NEXT")

    # Parte 2
    pdf.set_y(pdf.get_y() + 1.2)
    pdf.set_font("Helvetica", "B", 8.8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, _latin1("Parte 2 - MicroPython, Núcleo Integrador, Hub Local e Arquitetura Final (Davi Santos Ferreira):"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 7.8)
    pdf.set_text_color(51, 65, 85)
    itens_p2 = [
        "Transição completa do firmware do ESP32 para MicroPython (iot/main.py, iot/ssd1306.py e iot/diagram.json): sensoriamento clínico (ADC 40-200 BPM e DHT22), duplo feedback visual (display OLED SSD1306 I2C e LED de alerta em tempo de máquina <5ms) e buffer circular local de borda de 20 medições para resiliência offline.",
        "Desenvolvimento do Backend Integrador em Python (backend/app.py e backend/integrador_service.py) que unifica: ingestão de telemetria, inferência instantânea com o modelo Random Forest da Fase 6, avaliação automática dos 10 protocolos clínicos de emergência, classificação de ECG por CNN/ResNet50 da Fase 4 e chat com Watson Assistant da Fase 5.",
        "Implementação do Hub Web Local de telemetria e controle (templates/fase7_hub.html) em http://localhost:5000, simulador IoT resiliente (iot/simulador_iot.py com auto-inicialização do backend) e nova tela 'Telemetria & Risco' na aplicação React da Vercel.",
        "Criação da suíte de 7 testes de integração automatizados (backend/test_integrador.py) com 100% de aprovação e do script inicializador (main.bat).",
        "Elaboração do Relatório Técnico Oficial da Arquitetura Final de 5 páginas (docs/Relatorio_Integracao_Arquitetura_Final_Fase7.pdf).",
    ]
    for item in itens_p2:
        pdf.set_x(15)
        pdf.multi_cell(182, 3.5, _latin1(f"- {item}"), new_x="LMARGIN", new_y="NEXT")

    # Seção 3: Mapa Rápido de Arquivos no GitHub
    pdf.set_y(pdf.get_y() + 1.5)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 5, _latin1("3. Localização dos Principais Entregáveis no Repositório"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Courier", "", 7.3)
    pdf.set_text_color(15, 23, 42)
    arquivos = [
        "docs/Relatorio_Integracao_Arquitetura_Final_Fase7.pdf -> Relatorio Tecnico da Arquitetura (5 pags)",
        "iot/main.py & iot/ssd1306.py                         -> Firmware ESP32 MicroPython e driver OLED I2C",
        "iot/diagram.json & iot/simulador_iot.py              -> Esquema Wokwi e Simulador IoT Resiliente",
        "backend/app.py & backend/integrador_service.py       -> Backend Integrador e Orquestrador de IA",
        "backend/test_integrador.py                           -> Bateria de 7 Testes de Integracao (100% OK)",
        "templates/fase7_hub.html                             -> Hub Web Local de Telemetria e Simulação",
        "web/src/App.jsx & web/vercel.json                    -> Frontend Web React SPA (Vercel CI/CD)",
        "mobile/app.json & mobile/eas.json                    -> App Mobile React Native / Expo EAS Build",
        "main.bat                                             -> Menu e Inicializador Rapido da Solucao",
    ]
    for arq in arquivos:
        pdf.set_x(15)
        pdf.cell(0, 3.6, _latin1(arq), new_x="LMARGIN", new_y="NEXT")

    print(f"Y final no PDF: {pdf.get_y():.1f} mm (Limite: 285 mm)")

    for destino in DESTINOS:
        destino.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(destino))
        print(f" - Salvo em: {destino}")


if __name__ == "__main__":
    gerar_pdf_entrega()
