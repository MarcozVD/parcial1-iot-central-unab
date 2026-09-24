/*
 * DC-RACKB-02 · Rack B del DC-ANDES-1 · Azure IoT Central via DPS (MQTT/TLS 8883)
 * Wokwi: ESP32 DevKit C v4 + DHT22(GPIO15) + Potenciometro carga IT(GPIO34) + LED baliza(GPIO2)
 *
 * Origen de envio (catalogo del Parcial 1): "Wokwi ESP32 #1 (Arduino + PubSubClient)"
 * Telemetria: tempIntake (DHT22), humedadRack (DHT22), tempExhaust (intake + delta por carga)
 * Intervalo: 15 s   ·   Comandos: setAlerta, reiniciar, acuseAlarma
 * Propiedad escribible: umbralTemperatura (twin desired)
 *
 * Flujo: WiFi(Wokwi-GUEST) -> NTP -> DPS por MQTT ($dps/registrations/...)
 *        -> hub asignado -> MQTT: devices/<id>/messages/events/
 *
 * NOTA TLS: setInsecure() solo es valido en simulacion Wokwi; en hardware real se carga
 * el certificado raiz de Microsoft (Baltimore CyberTrust / DigiCert Global Root G2).
 */
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include "DHTesp.h"
#include "secrets.h"          // ID_SCOPE / DEVICE_ID / DEVICE_PRIMARY_KEY (fuera del repo)

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";

const int PIN_DHT = 15;
const int PIN_POT = 34;
const int PIN_LED = 2;

const char* DPS_HOST = "global.azure-devices-provisioning.net";
const char* API_VER_DPS = "2021-06-01";   // DPS la acepta
const char* API_VER_HUB = "2019-10-01";   // el hub MQTT rechaza api-version >= 2020 (rc=5)
const uint32_t SEND_MS = 15000;           // 15 s (asincronia de la flota)

DHTesp dht;
WiFiClientSecure net;
PubSubClient mqtt(net);

String hubHost;
bool connected = false, baliza = false;
float umbral = 27.0;
float tempIntake = 22.0, humedadRack = 50.0, tempExhaust = 31.0;

unsigned long lastSend = 0;
int msgSeq = 0;
char msgBuf[2048];

// ---------- utilidades SAS (identico al SDK: se firma el sr percent-encoded) ----------
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

// ---------- callbacks ----------
volatile long dpsStatus = 0;
String dpsPayload, twinJson;
bool twinArrived = false;

void mqttCb(char* topic, byte* payload, unsigned int len) {
  String t(topic);
  Serial.printf("[RX] topic=%s len=%u
", topic, len);
  if (t.startsWith("$dps/registrations/res/")) {
    dpsStatus = atol(t.c_str() + strlen("$dps/registrations/res/"));
    dpsPayload = String((const char*)payload);
  } else if (t.startsWith("$iothub/twin/")) {
    twinJson = String((const char*)payload);
    twinArrived = true;
  } else if (t.startsWith("$iothub/methods/POST/")) {
    int nameStart = strlen("$iothub/methods/POST/");
    int nameEnd = t.indexOf('/', nameStart);
    String method = t.substring(nameStart, nameEnd);
    String reqId = "$rid=1";
    int r = t.indexOf("$rid=");
    if (r >= 0) { String rid; for (uint32_t i = r + 5; i < t.length() && t[i] != '&' && t[i] != '/'; i++) rid += t[i]; reqId = "$rid=" + rid; }
    String args = String((const char*)payload); args.trim();
    Serial.printf("[CMD] %s args=%s\n", method.c_str(), args.c_str());
    char rbuf[128];
    if (method == "setAlerta") {
      bool en = false;
      StaticJsonDocument<192> d;
      if (!deserializeJson(d, args) && d.is<JsonObject>()) en = d["enabled"] | false;
      else en = (args == "true" || args == "1");
      baliza = en;
      digitalWrite(PIN_LED, en ? HIGH : LOW);
      snprintf(rbuf, sizeof(rbuf), "{\"baliza\":\"%s\"}", en ? "encendida" : "apagada");
    } else if (method == "reiniciar") {
      snprintf(rbuf, sizeof(rbuf), "{\"resultado\":\"reinicio aceptado por Rack B\"}");
    } else if (method == "acuseAlarma") {
      snprintf(rbuf, sizeof(rbuf), "{\"acuse\":\"alarma acusada en Rack B\"}");
    } else {
      snprintf(rbuf, sizeof(rbuf), "{\"resultado\":\"%s no soportado\"}", method.c_str());
    }
    String rt = "$iothub/methods/res/200/?" + reqId;
    mqtt.publish(rt.c_str(), rbuf);
    Serial.printf("[CMD] respuesta %s\n", rbuf);
  }
}

// ---------- DPS ----------
bool dpsMqttRegister() {
  String user = String(DEVICE_ID_SCOPE) + "/registrations/" + DEVICE_ID + "/api-version=" + API_VER_DPS;
  String pass = sasToken(String(DEVICE_ID_SCOPE) + "/registrations/" + String(DEVICE_ID), 3600);
  Serial.printf("[DPS] conectando; user=%s\n", user.c_str());
  if (!mqtt.connect(DEVICE_ID, user.c_str(), pass.c_str())) {
    Serial.printf("[DPS] fallo connect rc=%d\n", mqtt.state());
    return false;
  }
  bool sub = mqtt.subscribe("$dps/registrations/res/#");
  Serial.printf("[DPS] subscribe=%s state=%d
", sub ? "ok" : "FALLO", mqtt.state());
  StaticJsonDocument<128> reg;
  reg["registrationId"] = DEVICE_ID;
  serializeJson(reg, msgBuf);
  bool pub = mqtt.publish("$dps/registrations/PUT/iotdps-register/?$rid=1", (const char*)msgBuf);
  Serial.printf("[DPS] register publish=%s state=%d
", pub ? "ok" : "FALLO", mqtt.state());
  uint32_t deadline = millis() + 30000;
  String opId = ""; int rid = 2; unsigned long lastPoll = 0;
  while (millis() < deadline) {
    mqtt.loop();
    if (dpsStatus >= 200 && dpsStatus < 300) {   // DPS responde 202 (assigning) y luego 200 (assigned)
      StaticJsonDocument<1536> d;
      if (!deserializeJson(d, dpsPayload)) {
        const char* st = d["status"] | "";
        JsonObject rs = d["registrationState"];
        Serial.printf("[DPS] resp=%ld status=%s
", dpsStatus, st);
        if (strcmp(st, "assigned") == 0) {
          hubHost = rs["assignedHub"] | "";
          hubHost.replace("https://", ""); hubHost.replace("/", "");
          mqtt.disconnect();
          Serial.printf("[DPS] asignado a %s
", hubHost.c_str());
          return true;
        }
        if (opId == "") { opId = d["operationId"] | ""; if (opId == "") opId = rs["operationId"] | ""; }
        if (opId != "" && millis() - lastPoll > 2000) {
          lastPoll = millis();
          String q = "$dps/registrations/GET/iotdps-get-operationstatus/?$rid=" + String(rid++) + "&operationId=" + opId;
          mqtt.publish(q.c_str(), "");
          Serial.printf("[DPS] sondeo operationId=%s
", opId.c_str());
        }
      }
    }
    delay(10);
  }
  Serial.println("[DPS] timeout de registro");
  return false;
}

// ---------- hub ----------
bool connectHub() {
  String user = hubHost + "/" + DEVICE_ID + "/?api-version=" + API_VER_HUB;
  String pass = sasToken(hubHost + "/devices/" + String(DEVICE_ID), 3600);
  Serial.printf("[MQTT] a %s\n", hubHost.c_str());
  if (!mqtt.connect(DEVICE_ID, user.c_str(), pass.c_str())) {
    Serial.printf("[MQTT] rc=%d\n", mqtt.state());
    return false;
  }
  connected = true;
  Serial.println("[MQTT] conectado al hub (Rack B)");
  mqtt.subscribe("$iothub/methods/POST/#");
  mqtt.subscribe("$iothub/twin/PATCH/properties/desired/#");
  StaticJsonDocument<512> props;
  props["zona"] = "Rack B";
  props["ubicacion"] = "Sala blanca - fila B (DC-ANDES-1)";
  props["origenEnvio"] = "Wokwi ESP32 #1 (Arduino + PubSubClient)";
  props["fabricante"] = "Espressif ESP32-WROOM + DHT22";
  props["modelo"] = "Nodo-Wokwi-RackB/1.0";
  props["versionFirmware"] = "1.5.0";
  props["intervaloMuestreo"] = 15;
  serializeJson(props, msgBuf);
  String pt = "$iothub/twin/PATCH/properties/reported/?$rid=" + String(++msgSeq);
  mqtt.publish(pt.c_str(), (const char*)msgBuf);
  return true;
}

void applyDesired() {
  if (!twinArrived) return;
  twinArrived = false;
  StaticJsonDocument<768> d;
  if (deserializeJson(d, twinJson)) return;
  JsonVariant v;
  if (d.as<JsonObject>()["desired"].containsKey("umbralTemperatura")) v = d.as<JsonObject>()["desired"]["umbralTemperatura"];
  else if (d.as<JsonObject>().containsKey("umbralTemperatura")) v = d.as<JsonObject>()["umbralTemperatura"];
  if (v.isNull()) return;
  umbral = v.as<float>();
  Serial.printf("[PROP] desired umbralTemperatura=%.1f\n", umbral);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED, OUTPUT); digitalWrite(PIN_LED, LOW);
  dht.setup(PIN_DHT, DHTesp::DHT22);
  pinMode(PIN_POT, INPUT);
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
  if (!connected) {
    mqtt.setServer(hubHost.c_str(), 8883);
    connectHub();
    if (!connected) { delay(3000); return; }
  }
  mqtt.loop();
  applyDesired();

  if (millis() - lastSend >= SEND_MS) {
    lastSend = millis();
    TempAndHumidity th = dht.getTempAndHumidity();
    tempIntake = (float)th.temperature;
    humedadRack = (float)th.humidity;
    if (isnan(tempIntake) || tempIntake < -20 || tempIntake > 80) {   // sin lectura del sensor
      tempIntake = 22.0 + random(0, 40) / 10.0;
      humedadRack = 48.0 + random(0, 120) / 10.0;
    }
    float carga = map(analogRead(PIN_POT), 0, 1023, 0, 100) / 100.0;  // 0..1 carga del rack
    tempExhaust = tempIntake + 8.0 + 4.5 * carga;
    StaticJsonDocument<256> t;
    t["tempIntake"] = (float)round(tempIntake * 100) / 100;
    t["tempExhaust"] = (float)round(tempExhaust * 100) / 100;
    t["humedadRack"] = (float)round(humedadRack * 100) / 100;
    int n = serializeJson(t, msgBuf);
    String topic = "devices/" + String(DEVICE_ID) + "/messages/events/?$.ct=application%2Fjson&$.cy=WokwiRackB";
    bool ok = mqtt.publish(topic.c_str(), (const char*)msgBuf, n);
    Serial.printf("[TX] %s (%s)\n", msgBuf, ok ? "ok" : "FAIL");
    digitalWrite(PIN_LED, (tempExhaust > umbral || baliza) ? HIGH : LOW);
  }
  delay(20);
}
