import api from "./api";

/**
 * Consulta a última leitura telemétrica do sensor ESP32 MicroPython e a predição de risco em tempo real.
 */
export async function getLatestTelemetry() {
  const response = await api.get("/api/telemetria/atual");
  return response.data;
}

/**
 * Consulta o histórico de leituras de sinais vitais para gráficos e tabelas de tendência.
 */
export async function getTelemetryHistory(limit = 20) {
  const response = await api.get(`/api/telemetria/historico?limite=${limit}`);
  return response.data;
}

/**
 * Envia um pacote de sinais vitais simulando o ESP32 MicroPython diretamente pela UI.
 */
export async function sendTelemetryReading(reading) {
  const response = await api.post("/api/telemetria", reading);
  return response.data;
}

/**
 * Executa a predição de risco da Fase 6 com parâmetros arbitrários.
 */
export async function evaluateRiskPrediction(params) {
  const response = await api.post("/api/predicao/risco", params);
  return response.data;
}

/**
 * Obtém o resumo executivo dos 4 pilares do ecossistema integrado CardioIA.
 */
export async function getIntegrationSummary() {
  const response = await api.get("/api/integracao/resumo");
  return response.data;
}
