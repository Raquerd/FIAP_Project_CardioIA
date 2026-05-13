// IMPORTAÇÃO DE LIBS
#include <DHT.h>
#include <WiFi.h>        
#include <PubSubClient.h> 

// Definição dos pinos físicos no ESP32
#define DHTPIN 15         // DHT22
#define DHTTYPE DHT22     // Define o modelo do sensor DHT22
#define POT_PIN 34        // Pino analógico para o potenciômetro
#define LED_ALERTA 21     // Pino do LED de alerta visual

// Inicializa o objeto do sensor DHT
DHT dht(DHTPIN, DHTTYPE);

// Configurações de rede e comunicação
const char* ssid = "Sandra";      
const char* password = "040814sandrA@";     
const char* mqtt_server = "broker.hivemq.com"; // Endereço do servidor MQTT

// Objetos para gerenciar a internet e o protocolo de mensagens
WiFiClient espClient;
PubSubClient client(espClient);

// ------------- ESTRUTURA DE DADOS -------------
// Criamos um modelo de "caixa" que guarda temperatura e batimento juntos
struct DadoMedico {
  float temp;
  int bpm;
};

// ------------- BUFFER DE EDGE COMPUTING -------------
// Lista para salvar os dados caso a internet caia
const int TAMANHO_BUFFER = 20; 
DadoMedico buffer[TAMANHO_BUFFER]; // Reserva de espaço para 20 registros
int itensNoBuffer = 0;             // Contador para saber quantos dados foram salvos offline

void setup() {
  Serial.begin(115200);
  dht.begin();            // Liga o sensor de temperatura
  pinMode(LED_ALERTA, OUTPUT); // Configura o pino do LED como saída de sinal
  pinMode(POT_PIN, INPUT);     // Configura o pino do potenciômetro como entrada

  setup_wifi();           // função para conectar ao Wi-Fi
  client.setServer(mqtt_server, 1883); // Informa ao MQTT qual é o servidor e a porta
  Serial.println("Inicializado...");
}

void setup_wifi() {
  delay(10);
  Serial.println("Conectando ao WiFi...");
  WiFi.begin(ssid, password); // Inicia a tentativa de conexão
}

// Função de Edge Computing: guarda o dado na memória se não houver rede
void armazenarLocalmente(float t, int b) {
  if (itensNoBuffer < TAMANHO_BUFFER) {
    buffer[itensNoBuffer] = {t, b}; // Salva os valores na posição atual da lista
    itensNoBuffer++;                // Pula para a próxima posição livre
    Serial.printf("Offline: Dados armazenados em edge (%d/%d)\n", itensNoBuffer, TAMANHO_BUFFER);
  } else {
    Serial.println("Erro: Memória local cheia!"); // Proteção para não estourar a memória
  }
}

// Função de Cloud Computing: envia o dado formatado para a nuvem
void enviarParaNuvem(float t, int b) {
  char msg[50];
  // Cria um texto no formato JSON
  snprintf(msg, 50, "{\"temp\": %.2f, \"bpm\": %d}", t, b);
  client.publish("fiap/cardioia/dados/davi", msg); // Publica no "tópico" do MQTT
  Serial.print("Online: Enviado -> ");
  Serial.println(msg);
}

// Função de Sincronização: descarrega o que foi salvo offline quando a rede volta
void sincronizarDados() {
  Serial.println(">>> Sincronizando dados pendentes...");
  for (int i = 0; i < itensNoBuffer; i++) {
    enviarParaNuvem(buffer[i].temp, buffer[i].bpm); // Envia os dados guardados
    delay(200); // Pausa curta para não atropelar a conexão
  }
  itensNoBuffer = 0; // Zera o contador após enviar tudo
  Serial.println(">>> Sincronização concluída. Buffer limpo.");
}

// Função para reconectar ao MQTT se a conexão cair
void reconnect() {
  if (!client.connected()) {
    Serial.print("Tentando conexão MQTT...");
    if (client.connect("ESP32_CardioIA_Davi_Client")) {
      Serial.println("conectado!");
    } else {
      Serial.print("falhou, rc=");
      Serial.print(client.state());

    }
  }
}

void loop() {
  // 1. LEITURA DOS SENSORES
  float tempAtual = dht.readTemperature(); // Lê a temperatura real do DHT22
  int valorPot = analogRead(POT_PIN);      // Lê a posição do potenciômetro (0 a 4095)
  int bpmAtual = map(valorPot, 0, 4095, 40, 200); // Transforma o valor em batimentos (40 a 200 BPM)

  // 2. SEGURANÇA LOCAL
  // Se os batimentos ou temperatura forem perigosos, acende o LED na hora
  if (bpmAtual > 120 || tempAtual > 38) {
    digitalWrite(LED_ALERTA, HIGH);
  } else {
    digitalWrite(LED_ALERTA, LOW);
  }

  // 3. LÓGICA DE CONEXÃO E RESILIÊNCIA
  if (WiFi.status() == WL_CONNECTED) { // Se o Wi-Fi estiver funcionando:
    if (!client.connected()) {
      reconnect(); // Garante que o MQTT também esteja conectado
    }
    client.loop(); // Mantém a comunicação MQTT ativa

    // Se existirem dados salvos do período que estava sem internet:
    if (itensNoBuffer > 0) {
      sincronizarDados(); // Envia os dados acumulados (Backlog)
    }
    
    enviarParaNuvem(tempAtual, bpmAtual); // Envia a leitura atual em tempo real
  } 
  else {
    // Se o Wi-Fi caiu (Modo Offline / Edge Computing):
    armazenarLocalmente(tempAtual, bpmAtual);
  }

  delay(5000); // Espera 5 segundos para a próxima leitura (Ciclo de monitoramento)
}