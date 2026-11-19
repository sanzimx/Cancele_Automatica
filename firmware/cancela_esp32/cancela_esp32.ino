#include <Arduino.h>
#include <esp_system.h>

// Mesmos pinos do projeto original.
constexpr uint8_t LED_VERMELHO=4, BUZZER=5, BOTAO=19, SENSOR_IR=21;
constexpr uint8_t LED_VERDE=22, LED_AMARELO=23, RELE=25;
constexpr uint8_t RELE_LIGADO=HIGH, RELE_DESLIGADO=LOW;
constexpr unsigned long TEMPO_RELE=3000, TEMPO_MAX_OCR=30000;
enum Estado { OCIOSO, AGUARDANDO, ABERTO, NEGADO };
Estado estado=OCIOSO;
unsigned long inicioEstado=0, ultimoBotao=0, ultimoSensor=0;
bool sensorArmado=false, botaoLido=HIGH, botaoEstavel=HIGH;
bool sensorLido=HIGH, sensorEstavel=HIGH;
uint32_t bootId=0, sequencia=0;
String pedido;
char bufferSerial[100];
size_t tamanhoSerial=0;
bool descartarLinha=false;

void leds(bool vermelho,bool amarelo,bool verde) {
  digitalWrite(LED_VERMELHO,vermelho);
  digitalWrite(LED_AMARELO,amarelo);
  digitalWrite(LED_VERDE,verde);
}
void som(bool ligado) { digitalWrite(BUZZER,ligado?LOW:HIGH); }
void cancelarPedido() {
  if(estado==AGUARDANDO && pedido.length()) Serial.println("CANCELADO:"+pedido);
  pedido="";
}
void abrir(bool manual=false) {
  cancelarPedido();
  estado=ABERTO; inicioEstado=millis();
  digitalWrite(RELE,RELE_LIGADO);
  leds(false,false,true); som(true);
  Serial.println(manual?"ABERTURA_MANUAL":"RELE_LIGADO");
  // Estado físico da cancela não é medido: não declarar CANCELA_ABERTA.
}
void negar() {
  pedido="";
  estado=NEGADO; inicioEstado=millis();
  digitalWrite(RELE,RELE_DESLIGADO);
  leds(true,false,false); som(true);
  Serial.println("ACESSO_NEGADO");
}
void tratarComando(String linha) {
  linha.trim();
  if(linha=="PING") { Serial.println("PROTOCOLO:2"); return; }
  int separador=linha.indexOf(':');
  if(separador<0) return;
  String comando=linha.substring(0,separador);
  String id=linha.substring(separador+1);
  // Toda resposta precisa coincidir com a detecção ainda pendente.
  if(estado!=AGUARDANDO || id!=pedido || millis()-inicioEstado>=TEMPO_MAX_OCR) {
    Serial.println("RESPOSTA_DESCARTADA:"+id);
    return;
  }
  if(comando=="AUTORIZADO") {
    Serial.println("ACESSO_AUTORIZADO:"+id);
    pedido=""; // autorização já consumida, não é cancelamento
    abrir();
  } else if(comando=="NEGADO") negar();
}
void lerSerial() {
  while(Serial.available()>0) {
    char c=char(Serial.read());
    if(c=='\n') {
      if(!descartarLinha) {
        bufferSerial[tamanhoSerial]='\0';
        tratarComando(String(bufferSerial));
      }
      tamanhoSerial=0; descartarLinha=false;
    } else if(c!='\r') {
      if(tamanhoSerial<sizeof(bufferSerial)-1 && !descartarLinha)
        bufferSerial[tamanhoSerial++]=c;
      else descartarLinha=true;
    }
  }
}
void setup() {
  digitalWrite(RELE,RELE_DESLIGADO); pinMode(RELE,OUTPUT);
  digitalWrite(BUZZER,HIGH); pinMode(BUZZER,OUTPUT);
  pinMode(LED_VERMELHO,OUTPUT); pinMode(LED_VERDE,OUTPUT);
  pinMode(LED_AMARELO,OUTPUT);
  pinMode(BOTAO,INPUT_PULLUP); pinMode(SENSOR_IR,INPUT);
  leds(false,false,false); som(false);
  Serial.begin(115200);
  bootId=esp_random();
  botaoLido=botaoEstavel=digitalRead(BOTAO);
  sensorLido=sensorEstavel=digitalRead(SENSOR_IR);
  sensorArmado=sensorEstavel==HIGH;
  Serial.println("PROTOCOLO:2");
}
void loop() {
  unsigned long agora=millis();
  // Expirar antes de interpretar mensagens disponíveis.
  if(estado==AGUARDANDO && agora-inicioEstado>=TEMPO_MAX_OCR) {
    Serial.println("TEMPO_ESGOTADO:"+pedido);
    negar();
  }
  lerSerial();
  bool botao=digitalRead(BOTAO);
  if(botao!=botaoLido) { botaoLido=botao; ultimoBotao=agora; }
  if(agora-ultimoBotao>=30 && botaoEstavel!=botaoLido) {
    botaoEstavel=botaoLido;
    if(botaoEstavel==LOW) abrir(true);
  }
  bool sensor=digitalRead(SENSOR_IR);
  if(sensor!=sensorLido) { sensorLido=sensor; ultimoSensor=agora; }
  if(agora-ultimoSensor>=60) sensorEstavel=sensorLido;

  if(estado==ABERTO) {
    unsigned long decorrido=agora-inicioEstado;
    // Início de estado pode ter ocorrido após a leitura de "agora".
    if((long)decorrido<0) return;
    som(decorrido<150 || (decorrido>=270 && decorrido<420));
    if(decorrido>=TEMPO_RELE) {
      digitalWrite(RELE,RELE_DESLIGADO); som(false);
      leds(false,false,false); estado=OCIOSO;
      // Exige liberação do sensor após o ciclo.
      sensorArmado=false;
      Serial.println("RELE_DESLIGADO");
    }
  } else if(estado==NEGADO) {
    unsigned long decorrido=agora-inicioEstado;
    if((long)decorrido<0) return;
    som(decorrido<1000);
    if(decorrido>=2500) {
      som(false); leds(false,false,false); estado=OCIOSO;
      sensorArmado=false;
    }
  }
  if(estado==OCIOSO) {
    if(sensorEstavel==HIGH) sensorArmado=true;
    if(sensorEstavel==LOW && sensorArmado) {
      sensorArmado=false;
      pedido=String(bootId,HEX)+"-"+String(++sequencia);
      estado=AGUARDANDO; inicioEstado=millis();
      leds(false,true,false);
      Serial.println("VEICULO_DETECTADO:"+pedido);
    }
  }
}
