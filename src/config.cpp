#include "config.h"
#include <LittleFS.h>

static constexpr const char* CONFIG_PATH = "/config.json";

template <size_t N>
static bool contains(const uint8_t (&arr)[N], int v) {
    for (uint8_t p : arr)
        if (p == v) return true;
    return false;
}

bool isAllowedPin(int pin) { return contains(ALLOWED_PINS, pin); }
bool isWakePin(int pin) { return contains(WAKE_PINS, pin); }

Config defaultConfig() {
    Config c;
    const size_t n = min<size_t>(8, sizeof(ALLOWED_PINS));
    for (size_t i = 0; i < n; i++) {
        String idx(i + 1);
        c.keys.push_back({ALLOWED_PINS[i], idx, ";k" + idx, false});
    }
    return c;
}

static bool readUInt(JsonVariantConst v, const char* name, uint16_t lo, uint16_t hi,
                     uint16_t& out, String& err) {
    if (v.isNull()) return true;
    if (!v.is<int>() || v.as<int>() < lo || v.as<int>() > hi) {
        err = String(name) + " doit être un entier entre " + lo + " et " + hi;
        return false;
    }
    out = v.as<uint16_t>();
    return true;
}

static bool readString(JsonVariantConst v, const char* name, size_t minLen, size_t maxLen,
                       String& out, String& err) {
    if (v.isNull() && minLen == 0) return true;
    if (!v.is<const char*>()) {
        err = String(name) + " doit être une chaîne";
        return false;
    }
    String s = v.as<const char*>();
    if (s.length() < minLen || s.length() > maxLen) {
        err = String(name) + " : longueur " + minLen + " à " + maxLen;
        return false;
    }
    out = s;
    return true;
}

bool configFromJson(JsonVariantConst src, Config& out, String& err) {
    if (!src.is<JsonObjectConst>()) { err = "objet JSON attendu"; return false; }
    Config c = out;

    if (!src["layout"].isNull()) {
        if (!src["layout"].is<const char*>() || !parseLayout(src["layout"].as<const char*>(), c.layout)) {
            err = "layout doit être \"fr\" ou \"us\"";
            return false;
        }
    }
    if (!src["ble_name"].isNull() && !readString(src["ble_name"], "ble_name", 1, 29, c.bleName, err)) return false;
    for (size_t i = 0; i < c.bleName.length(); i++) {
        if (c.bleName[i] < 0x20 || c.bleName[i] > 0x7E) { err = "ble_name : ASCII imprimable uniquement"; return false; }
    }
    // Vide = réseau ouvert ; sinon WPA2 impose 8 à 63 caractères.
    if (!readString(src["ap_pass"], "ap_pass", 0, 63, c.apPass, err)) return false;
    if (!c.apPass.isEmpty() && c.apPass.length() < 8) { err = "ap_pass : vide (réseau ouvert) ou 8 à 63 caractères"; return false; }
    if (!readUInt(src["key_delay_ms"], "key_delay_ms", 1, 200, c.keyDelayMs, err)) return false;
    if (!readUInt(src["debounce_ms"], "debounce_ms", 5, 200, c.debounceMs, err)) return false;
    if (!readUInt(src["sleep_min"], "sleep_min", 0, 1440, c.sleepMin, err)) return false;

    JsonArrayConst keys = src["keys"];
    if (keys.isNull() || keys.size() < 1 || keys.size() > MAX_KEYS) {
        err = String("keys : 1 à ") + MAX_KEYS + " touches";
        return false;
    }
    c.keys.clear();
    for (JsonVariantConst k : keys) {
        String where = String("touche ") + (c.keys.size() + 1) + " : ";
        if (!k["pin"].is<int>() || !isAllowedPin(k["pin"].as<int>())) {
            err = where + "pin interdit ou absent";
            return false;
        }
        KeyConfig kc{k["pin"].as<uint8_t>(), "", "", false};
        for (const KeyConfig& other : c.keys) {
            if (other.pin == kc.pin) { err = where + "pin " + kc.pin + " déjà utilisé"; return false; }
        }
        if (!readString(k["label"], "label", 0, 16, kc.label, err) ||
            !readString(k["send"], "send", 0, 256, kc.send, err)) {
            err = where + err;
            return false;
        }
        if (!k["enter"].isNull() && !k["enter"].is<bool>()) { err = where + "enter doit être un booléen"; return false; }
        kc.enter = k["enter"] | false;
        if (kc.send.isEmpty() && !kc.enter) { err = where + "rien à envoyer"; return false; }
        c.keys.push_back(kc);
    }
    out = c;
    return true;
}

void configToJson(const Config& c, JsonDocument& doc) {
    doc.clear();
    doc["layout"] = c.layout == Layout::FR ? "fr" : "us";
    doc["ble_name"] = c.bleName;
    doc["ap_pass"] = c.apPass;
    doc["key_delay_ms"] = c.keyDelayMs;
    doc["debounce_ms"] = c.debounceMs;
    doc["sleep_min"] = c.sleepMin;
    JsonArray keys = doc["keys"].to<JsonArray>();
    for (const KeyConfig& k : c.keys) {
        JsonObject o = keys.add<JsonObject>();
        o["pin"] = k.pin;
        o["label"] = k.label;
        o["send"] = k.send;
        o["enter"] = k.enter;
    }
}

bool loadConfig(Config& cfg) {
    cfg = defaultConfig();
    if (!LittleFS.begin(true)) {
        Serial.println("[config] LittleFS indisponible, config par défaut en RAM");
        return false;
    }
    File f = LittleFS.open(CONFIG_PATH, "r");
    if (!f) {
        Serial.println("[config] pas de config.json, création des valeurs par défaut");
        saveConfig(cfg);
        return false;
    }
    JsonDocument doc;
    DeserializationError jerr = deserializeJson(doc, f);
    f.close();
    String err = jerr ? String("JSON illisible : ") + jerr.c_str() : String();
    if (!jerr && configFromJson(doc.as<JsonVariantConst>(), cfg, err)) return true;

    // Conserve le fichier fautif pour diagnostic, puis repart des valeurs par défaut.
    Serial.printf("[config] %s -> sauvegardé en /config.bad, valeurs par défaut\n", err.c_str());
    LittleFS.remove("/config.bad");
    LittleFS.rename(CONFIG_PATH, "/config.bad");
    cfg = defaultConfig();
    saveConfig(cfg);
    return false;
}

bool saveConfig(const Config& cfg) {
    JsonDocument doc;
    configToJson(cfg, doc);
    File f = LittleFS.open("/config.tmp", "w");
    if (!f) return false;
    bool ok = serializeJson(doc, f) > 0;
    f.close();
    // Écriture puis renommage : une coupure pendant l'écriture ne corrompt pas l'ancienne config.
    if (ok) {
        LittleFS.remove(CONFIG_PATH);
        ok = LittleFS.rename("/config.tmp", CONFIG_PATH);
    }
    if (!ok) Serial.println("[config] échec d'écriture de config.json");
    return ok;
}
