# 📹 Roteiro de Gravação do Vídeo Demonstrativo – CardioIA (Fase 5)

> **Objetivo do Vídeo:** Demonstrar em até 5 minutos o funcionamento do Assistente Conversacional em Saúde, a integração técnica entre a Interface Web, o Backend Flask e a inteligência do IBM Watson Assistant v2, além da execução da bateria de testes automatizados.

---

## ⏱️ Linha do Tempo Sugerida (Duração: 4 a 5 Minutos)

| Bloco | Tempo Estimado | O que mostrar na tela | O que falar (Script) |
| :--- | :---: | :--- | :--- |
| **1. Introdução & Contexto** | 0:00 - 0:45 | Câmera aberta ou slide inicial do CardioIA no VS Code | Apresentar os integrantes (Davi Ferreira e Lais Kurahashi), turma 2TIAOA-2026, e introduzir o objetivo da Fase 5: conectar a prática clínica com um agente conversacional inteligente para triagem preliminar e orientação de exames. |
| **2. Modelagem Conversacional (Watson)** | 0:45 - 1:45 | Abrir brevemente a tela do IBM Watson Assistant ou o arquivo config/watson_assistant_skill.json | Explicar a estrutura desenvolvida pela Lais Kurahashi: as 12 intenções (#relatar_sintoma, #preparo_exame, #agendamento), as 6 entidades (@tipo_exame, @sintomas, @sys-date, @sys-time), e a preocupação ética e médica de não emitir diagnósticos definitivos. |
| **3. Demonstração Prática do Chatbot** | 1:45 - 3:15 | Navegador em http://localhost:5000 interagindo em tempo real | **Demonstrar 4 cenários práticos:**<br>1. *Boas-Vindas:* Mostrar mensagem inicial de acolhimento e o alerta ético no topo.<br>2. *Preparo de Exame:* Clicar no chip **'🩺 Preparo do Holter'** e mostrar a orientação personalizada.<br>3. *Triagem Crítica:* Clicar em **'🚨 Sinto dor no peito'** e mostrar o alerta de emergência.<br>4. *Agendamento:* Digitar *'Quero agendar ecocardiograma amanhã às 14h'* e mostrar a confirmação formatada.<br>5. *Transbordo:* Mostrar o direcionamento humano ao solicitar atendente. |
| **4. Arquitetura Backend & Testes** | 3:15 - 4:15 | Terminal / PowerShell no VS Code executando python scripts/test_watson_api.py | Mostrar a arquitetura em Flask (scripts/app.py e scripts/watson_service.py) e rodar a bateria de testes automatizados ao vivo, demonstrando a aprovação de todos os 7 testes clínicos e o status 200/201 da API. |
| **5. Conclusão & Encerramento** | 4:15 - 4:45 | Página do repositório GitHub ou tela inicial do CardioIA | Fechar destacando a integração do assistente ao ecossistema hospitalar do CardioIA e os próximos passos. Agradecer a atenção do professor Caique Bezerra e da banca avaliadora. |

---

## 🎯 Dicas de Apresentação
* **Resolução recomendada:** 1080p (Full HD) com áudio claro.
* **Antes de iniciar a gravação:** Deixe o servidor já rodando ou inicie pelo main.bat para demonstrar a facilidade de inicialização em 1 clique.
* **Destaque de Governança:** Mencione a presença do banner ético e o uso de variáveis de ambiente (.env) para proteção das credenciais em nuvem.
