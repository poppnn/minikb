#include "webserver.h"
#include <AsyncJson.h>
#include <ESPAsyncWebServer.h>
#include <LittleFS.h>
#include <WiFi.h>

static constexpr uint32_t CONFIG_TIMEOUT_MS = 10UL * 60UL * 1000UL;

static AsyncWebServer server(80);
static Config* config = nullptr;
static volatile uint32_t lastRequestAt = 0;
static volatile uint32_t rebootAt = 0;

static void sendJson(AsyncWebServerRequest* req, int code, const JsonDocument& doc) {
    String body;
    serializeJson(doc, body);
    req->send(code, "application/json", body);
}

static void sendError(AsyncWebServerRequest* req, int code, const String& msg) {
    JsonDocument doc;
    doc["ok"] = false;
    doc["error"] = msg;
    sendJson(req, code, doc);
}

static void touch() { lastRequestAt = millis(); }

static void scheduleReboot() { rebootAt = millis() + 500; }

void webBegin(Config& cfg) {
    config = &cfg;
    WiFi.mode(WIFI_AP);
    // Mot de passe vide = réseau ouvert (nullptr pour softAP).
    WiFi.softAP(AP_SSID, cfg.apPass.isEmpty() ? nullptr : cfg.apPass.c_str());
    Serial.printf("[web] AP \"%s\" %s -> http://%s\n", AP_SSID,
                  cfg.apPass.isEmpty() ? "ouvert" : ("mot de passe \"" + cfg.apPass + "\"").c_str(),
                  WiFi.softAPIP().toString().c_str());

    server.on("/", HTTP_GET, [](AsyncWebServerRequest* req) {
        touch();
        if (LittleFS.exists("/index.html")) req->send(LittleFS, "/index.html", "text/html");
        else req->send(500, "text/plain", "index.html absent : lancer pio run -t uploadfs");
    });

    server.on("/api/config", HTTP_GET, [](AsyncWebServerRequest* req) {
        touch();
        JsonDocument doc;
        configToJson(*config, doc);
        sendJson(req, 200, doc);
    });

    auto* post = new AsyncCallbackJsonWebHandler("/api/config", [](AsyncWebServerRequest* req, JsonVariant& json) {
        touch();
        Config next = *config;
        String err;
        if (!configFromJson(json, next, err)) return sendError(req, 400, err);
        if (!saveConfig(next)) return sendError(req, 500, "écriture LittleFS impossible");
        *config = next;
        JsonDocument doc;
        doc["ok"] = true;
        sendJson(req, 200, doc);
        scheduleReboot();
    });
    post->setMethod(HTTP_POST);
    post->setMaxContentLength(8192);
    server.addHandler(post);

    // BLE et Wi-Fi sont exclusifs sur C3 : on vérifie la conversion sans rien envoyer.
    auto* test = new AsyncCallbackJsonWebHandler("/api/test", [](AsyncWebServerRequest* req, JsonVariant& json) {
        touch();
        if (!json["text"].is<const char*>()) return sendError(req, 400, "text attendu");
        std::vector<uint32_t> bad;
        auto strokes = textToStrokes(json["text"].as<const char*>(), config->layout, &bad);
        JsonDocument doc;
        doc["ok"] = bad.empty();
        doc["ble"] = false;
        doc["strokes"] = strokes.size() + ((json["enter"] | false) ? 1 : 0);
        JsonArray arr = doc["unsupported"].to<JsonArray>();
        for (uint32_t cp : bad) arr.add(codepointToUtf8(cp));
        sendJson(req, 200, doc);
    });
    test->setMethod(HTTP_POST);
    server.addHandler(test);

    server.on("/api/reboot", HTTP_POST, [](AsyncWebServerRequest* req) {
        JsonDocument doc;
        doc["ok"] = true;
        sendJson(req, 200, doc);
        scheduleReboot();
    });

    server.on("/api/pins", HTTP_GET, [](AsyncWebServerRequest* req) {
        touch();
        JsonDocument doc;
        JsonArray allowed = doc["allowed"].to<JsonArray>();
        for (uint8_t p : ALLOWED_PINS) allowed.add(p);
        JsonArray wake = doc["wake"].to<JsonArray>();
        for (uint8_t p : WAKE_PINS) wake.add(p);
        doc["max_keys"] = MAX_KEYS;
        sendJson(req, 200, doc);
    });

    server.onNotFound([](AsyncWebServerRequest* req) { req->send(404, "text/plain", "introuvable"); });
    server.begin();
    touch();
}

void webLoop(uint32_t now) {
    if (rebootAt && int32_t(now - rebootAt) >= 0) ESP.restart();
    if (now - lastRequestAt > CONFIG_TIMEOUT_MS) {
        Serial.println("[web] 10 min sans activité, retour au mode normal");
        ESP.restart();
    }
}
