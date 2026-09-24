/*
 * DC-AGUA-07 · Deteccion de agua bajo piso del DC-ANDES-1 · Azure IoT Central via DPS (MQTT)
 * Wokwi: ESP32 DevKit C v4 + Potenciometro humedad de piso(GPIO34) + Pulsador fuga(GPIO27)
 *        + LED indicador de fuga(GPIO2)
 *
 * Origen de envio (catalogo del Parcial 1): "Wokwi ESP32 #2 (sketch propio, sensor analogico)"
 * Telemetria: fugaAgua (bool), humedadPiso (%)
 * Intervalo: 30 s   ·   El pulsador simula la prueba funcional de la sonda de fuga.
 */
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include "secrets.h"          // ID_SCOPE / DEVICE_ID / DEVICE_PRIMARY_KEY (fuera del repo)

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";

const int PIN_SONDA = 34;     // potenciometro = humedad de piso 30-90 %
const int PIN_FUGA = 27;      // pulsador = simular fuga de agua
const int PIN_LED = 2;        // baliza de fuga

const char* DPS_HOST = "global.azure-devices-provisioning.net";
const char* API_VER_DPS = "2021-06-01";
const char* API_VER_HUB = "2019-10-01";
const uint32_t SEND_MS = 30000;   // 30 s

WiFiClientSecure net;
PubSubClient mqtt(net);

String hubHost;
bool connected = false, fuga = false, baliza = false;
float humedadPiso = 38.0;
unsigned long lastSend = 0, fugaHasta = 0;
int msgSeq = 0;
char msgBuf[2048];

String urlEncode(const char* s) {
  static const char* HEXD = "0123456789ABCDEF";
  char out[224]; int j = 0;
  for (const char* p = s; *p && j < 210; p++) {
    if (isalnum(*p) || *p == '.' || *p == '-' || *p == '_' || *p == '~') out[j++] = *p;
    else { out[j++] = '%'; out[j++] = HEXD[(*p >> 4) & 0xF]; out[j++] = HEXD[*p & 0xF]; }
  }
  out[j] = 0;
  return String(out);
}

static int b64val(char c) {
  if (c >= 'A' && c <= 'Z') return c - 'A';
  if (c >= 'a' && c <= 'z') return c - 'a' + 26;
  if (c >= '0' && c <= '9') return c - '0' + 52;
  if (c == '+') return 62;
  if (c == '/') return 63;
  return -1;
}

static size_t b64decode(const char* in, unsigned char* out, size_t cap) {
  size_t o = 0; int acc = 0, bits = 0;
  for (const char* p = in; *p; p++) {
    if (*p == '=' || *p == '\n' || *p == '\r') continue;
    int v = b64val(*p); if (v < 0) continue;
    acc = (acc << 6) | v; bits += 6;
    if (bits >= 8) { bits -= 8; if (o < cap) out[o++] = (acc >> bits) & 0xFF; }
  }
  return o;
}

String sasToken(const String& rawResource, uint32_t ttlSec) {
  unsigned char decoded[64];
  size_t dlen = b64decode(DEVICE_PRIMARY_KEY, decoded, sizeof(decoded));
  uint32_t expiry = (uint32_t)time(nullptr) + ttlSec;
  String srEnc = urlEncode(rawResource.c_str());
  char toSign[320];
  snprintf(toSign, sizeof(toSign), "%s\n%lu", srEnc.c_str(), (unsigned long)expiry);
  unsigned char sig[32];
  mbedtls_md_context_t ctx;
  mbedtls_md_init(&ctx);
  mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(MBEDTLS_MD_SHA256), 1);
  mbedtls_md_hmac_starts(&ctx, decoded, dlen);
  mbedtls_md_hmac_update(&ctx, (const unsigned char*)toSign, strlen(toSign));
  mbedtls_md_hmac_finish(&ctx, sig);
  mbedtls_md_free(&ctx);
  static const char* AB = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  char b64[48]; size_t o = 0;
  for (size_t i = 0; i < 32; i += 3) {
    unsigned nn = ((unsigned)sig[i]) << 16;
    if (i + 1 < 32) nn |= ((unsigned)sig[i + 1]) << 8;
    if (i + 2 < 32) nn |= ((unsigned)sig[i + 2]);
    b64[o++] = AB[(nn >> 18) & 63]; b64[o++] = AB[(nn >> 12) & 63];
    b64[o++] = (i + 1 < 32) ? AB[(nn >> 6) & 63] : '=';
    b64[o++] = (i + 2 < 32) ? AB[nn & 63] : '=';
  }
  b64[o] = '\0';
  char sigEnc[96];
  strcpy(sigEnc, urlEncode(b64).c_str());
  char sas[640];
  snprintf(sas, sizeof(sas), "SharedAccessSignature sr=%s&sig=%s&se=%lu",
           srEnc.c_str(), sigEnc, (unsigned long)expiry);
  return String(sas);
}

volatile long dpsStatus = 0;
String dpsPayload;

void mqttCb(char* topic, byte* payload, unsigned int len) {
  String t(topic);
  if (t.startsWith("$dps/registrations/res/")) {
    dpsStatus = atol(t.c_str() + strlen("$dps/registrations/res/"));
    dpsPayload = String((const char*)payload);
  } else if (t.startsWith("$iothub/methods/POST/")) {
    int nameStart = strlen("$iothub/methods/POST/");
    int nameEnd = t.indexOf('/', nameStart);
    String method = t.substring(nameStart, nameEnd);
    String reqId = "$rid=1";
    int r = t.indexOf("$rid=");
    if (r >= 0) { String rid; for (uint32_t i = r + 5; i < t.length() && t[i] != '&' && t[i] != '/'; i++) rid += t[i]; reqId = "$rid=" + rid; }
    char rbuf[128];
    if (method == "setAlerta") {
      String args = String((const char*)payload); args.trim();
      baliza = (args.indexOf("true") >= 0);
      snprintf(rbuf, sizeof(rbuf), "{\"baliza\":\"%s\"}", baliza ? "encendida" : "apagada");
    } else if (method == "acuseAlarma") {
      fuga = false; fugaHasta = 0;
      snprintf(rbuf, sizeof(rbuf), "{\"acuse\":\"fuga acusada en nodo de agua\"}");
    } else {
      snprintf(rbuf, sizeof(rbuf), "{\"resultado\":\"%s atendido por nodo de agua\"}", method.c_str());
    }
    Serial.printf("[CMD] %s -> %s\n", method.c_str(), rbuf);
    String rt = "$iothub/methods/res/200/?" + reqId;
    mqtt.publish(rt.c_str(), rbuf);
  }
}

bool dpsMqttRegister() {
  String user = String(DEVICE_ID_SCOPE) + "/registrations/" + DEVICE_ID + "/api-version=" + API_VER_DPS;
  String pass = sasToken(String(DEVICE_ID_SCOPE) + "/registrations/" + String(DEVICE_ID), 3600);
  if (!mqtt.connect(DEVICE_ID, user.c_str(), pass.c_str())) {
    Serial.printf("[DPS] fallo connect rc=%d\n", mqtt.state());
    return false;
  }
  mqtt.subscribe("$dps/registrations/res/#");
  mqtt.publish("$dps/registrations/PUT/iotdps-register/?$rid=1", "{\"registrationId\":\"" DEVICE_ID "\"}");
  uint32_t deadline = millis() + 30000;
  String opId = ""; int rid = 2; unsigned long lastPoll = 0;
  while (millis() < deadline) {
    mqtt.loop();
    if (dpsStatus >= 200 && dpsStatus < 300) {   // DPS responde 202 (assigning) y luego 200 (assigned)
      StaticJsonDocument<1536> d;
      if (!deserializeJson(d, dpsPayload)) {
        const char* st = d["status"] | "";
        JsonObject rs = d["registrationState"];
        Serial.printf("[DPS] resp=%ld status=%s\n", dpsStatus, st);
        if (strcmp(st, "assigned") == 0) {
          hubHost = rs["assignedHub"] | "";
          hubHost.replace("https://", ""); hubHost.replace("/", "");
          mqtt.disconnect();
          Serial.printf("[DPS] asignado a %s\n", hubHost.c_str());
          return true;
        }
        if (opId == "") { opId = d["operationId"] | ""; if (opId == "") opId = rs["operationId"] | ""; }
        if (opId != "" && millis() - lastPoll > 2000) {
          lastPoll = millis();
          String q = "$dps/registrations/GET/iotdps-get-operationstatus/?$rid=" + String(rid++) + "&operationId=" + opId;
          mqtt.publish(q.c_str(), "");
          Serial.printf("[DPS] sondeo operationId=%s\n", opId.c_str());
        }
      }
    }
    delay(10);
  }
  return false;
}

bool connectHub() {
  String user = hubHost + "/" + DEVICE_ID + "/?api-version=" + API_VER_HUB;
  String pass = sasToken(hubHost + "/devices/" + String(DEVICE_ID), 3600);
  if (!mqtt.connect(DEVICE_ID, user.c_str(), pass.c_str())) {
    Serial.printf("[MQTT] rc=%d\n", mqtt.state());
    return false;
  }
  connected = true;
  Serial.println("[MQTT] conectado al hub (nodo de agua)");
  mqtt.subscribe("$iothub/methods/POST/#");
  StaticJsonDocument<512> props;
  props["zona"] = "Deteccion de agua bajo piso";
  props["ubicacion"] = "Sala blanca - piso tecnico bajo el CRAC 2";
  props["origenEnvio"] = "Wokwi ESP32 #2 (sketch propio, sensor analogico)";
  props["fabricante"] = "Espressif ESP32-WROOM + sonda resistiva RLE LD2100";
  props["modelo"] = "Nodo-Wokwi-Agua/1.0";
  props["versionFirmware"] = "1.3.0";
  props["intervaloMuestreo"] = 30;
  serializeJson(props, msgBuf);
  String pt = "$iothub/twin/PATCH/properties/reported/?$rid=" + String(++msgSeq);
  mqtt.publish(pt.c_str(), (const char*)msgBuf);
  return true;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED, OUTPUT); digitalWrite(PIN_LED, LOW);
  pinMode(PIN_FUGA, INPUT_PULLUP);
  pinMode(PIN_SONDA, INPUT);
  analogReadResolution(10);

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int guard = 0;
  while (WiFi.status() != WL_CONNECTED && guard++ < 60) { delay(500); Serial.print("."); }
  Serial.println("\n[WIFI] conectado");

  configTime(0, 0, "pool.ntp.org", "time.google.com");
  uint32_t ntpGuard = 0;
  while (time(nullptr) < 1700000000UL && ntpGuard++ < 100) delay(200);
  Serial.printf("[NTP] epoch=%lu\n", (unsigned long)time(nullptr));

  net.setInsecure();
  mqtt.setKeepAlive(60);
  mqtt.setBufferSize(2048);
  mqtt.setCallback(mqttCb);
  mqtt.setServer(DPS_HOST, 8883);
  while (!dpsMqttRegister()) { delay(3000); mqtt.setServer(DPS_HOST, 8883); }
  mqtt.setServer(hubHost.c_str(), 8883);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) { Serial.println("[WIFI] perdido, reinicio"); ESP.restart(); }
  // el SAS caduca cada hora: si el hub corta la sesion, se reconecta con un token nuevo
  if (!connected || !mqtt.connected()) {
    connected = false;
    Serial.println("[MQTT] sesion caida o sin conectar: reconectando");
    mqtt.setServer(hubHost.c_str(), 8883);
    connectHub();
    if (!connected) { delay(3000); return; }
  }
  mqtt.loop();

  // pulsador = prueba de fuga (mantiene la fuga 3 ciclos)
  if (digitalRead(PIN_FUGA) == LOW) { fuga = true; fugaHasta = millis() + 90000UL; Serial.println("[PRUEBA] fuga simulada por pulsador"); }
  if (fuga && millis() > fugaHasta) { fuga = false; Serial.println("[PRUEBA] fuga finalizada"); }
  digitalWrite(PIN_LED, (fuga || baliza) ? HIGH : LOW);

  if (millis() - lastSend >= SEND_MS) {
    lastSend = millis();
    float hora2 = (millis() / 1000.0) / 3600.0;
    humedadPiso = map(analogRead(PIN_SONDA), 0, 1023, 30, 90)
                  + 1.5 * sin(hora2 * 0.7) + ((random(0, 21) - 10) / 10.0) + (fuga ? 8 : 0);
    if (humedadPiso > 99) humedadPiso = 99;
    StaticJsonDocument<256> t;
    t["fugaAgua"] = fuga;
    t["humedadPiso"] = (float)(round(humedadPiso * 10) / 10.0);
    int n = serializeJson(t, msgBuf);
    String topic = "devices/" + String(DEVICE_ID) + "/messages/events/?$.ct=application%2Fjson&$.cy=WokwiAgua";
    bool ok = mqtt.publish(topic.c_str(), (const char*)msgBuf, n);
    Serial.printf("[TX] %s (%s)\n", msgBuf, ok ? "ok" : "FAIL");
  }
  delay(20);
}
