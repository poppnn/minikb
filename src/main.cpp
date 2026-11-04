// MiniKB : clavier de macros BLE. Mode normal = BLE HID, mode config = Wi-Fi AP + web UI.
#include <Arduino.h>
#include <esp_attr.h>
#include "ble_hid.h"
#include "buttons.h"
#include "config.h"
#include "power.h"
#include "webserver.h"

static constexpr uint32_t BOOT_LONG_PRESS_MS = 3000;
static constexpr uint32_t CONFIG_MAGIC = 0xC0F16A11;

// Survit à ESP.restart() : demande de démarrage en mode config.
RTC_NOINIT_ATTR static uint32_t bootRequest;

static Config cfg;
static bool configMode = false;
static std::vector<Button> keys;
static Button bootButton;

static void setLed(bool on) { digitalWrite(LED_PIN, on != LED_ACTIVE_LOW); }

static void updateLed(uint32_t now) {
    if (configMode) setLed((now / 100) % 2);          // flash rapide
    else if (hidConnected()) setLed(true);             // fixe
    else setLed((now / 500) % 2);                      // clignote
}

static void sendKey(const KeyConfig& k) {
    std::vector<uint32_t> bad;
    auto strokes = textToStrokes(k.send.c_str(), cfg.layout, &bad);
    for (uint32_t cp : bad)
        Serial.printf("[keymap] caractère non supporté U+%04X \"%s\" ignoré\n", unsigned(cp), codepointToUtf8(cp).c_str());
    if (k.enter) strokes.push_back({0, KEY_ENTER});
    hidQueue(strokes);
}

// Envoyer n'importe quel caractère sur le port série affiche l'état (les logs de boot sont souvent perdus en USB CDC).
static void printStatus() {
    Serial.printf("[status] mode %s, BLE %s, %u touche(s), layout %s, AP \"%s\" %s\n",
                  configMode ? "config" : "normal", hidConnected() ? "connecté" : "en attente",
                  unsigned(cfg.keys.size()), cfg.layout == Layout::FR ? "fr" : "us", AP_SSID,
                  cfg.apPass.isEmpty() ? "ouvert" : ("mot de passe \"" + cfg.apPass + "\"").c_str());
}

void setup() {
    Serial.begin(115200);
    // L'USB CDC se réénumère au reset : laisse 2 s au terminal pour se reconnecter, sinon les logs (et le mot de passe AP) sont perdus.
    while (!Serial && millis() < 2000) {}
    pinMode(LED_PIN, OUTPUT);
    setLed(false);

    configMode = bootRequest == CONFIG_MAGIC;
    bootRequest = 0;

    if (!loadConfig(cfg)) Serial.println("[config] config par défaut utilisée");
    printStatus();

    if (configMode) {
        webBegin(cfg);
        return;
    }
    hidBegin(cfg.bleName.c_str());
    // Seuls les pins déclarés sont configurés ; les autres restent en entrée flottante.
    for (const KeyConfig& k : cfg.keys) {
        keys.emplace_back();
        keys.back().begin(k.pin);
    }
    bootButton.begin(BOOT_PIN);
    powerActivity(millis());
}

void loop() {
    uint32_t now = millis();
    updateLed(now);
    if (Serial.available()) {
        while (Serial.available()) Serial.read();
        printStatus();
    }
    if (configMode) {
        webLoop(now);
        return;
    }

    if (bootButton.update(now, cfg.debounceMs, BOOT_LONG_PRESS_MS) == ButtonEvent::LongPress) {
        Serial.println("[main] BOOT maintenu 3 s : redémarrage en mode config");
        bootRequest = CONFIG_MAGIC;
        ESP.restart();
    }
    for (size_t i = 0; i < keys.size(); i++) {
        if (keys[i].update(now, cfg.debounceMs) == ButtonEvent::Pressed) {
            powerActivity(now);
            sendKey(cfg.keys[i]);
        }
    }
    hidLoop(now, cfg.keyDelayMs);
    powerLoop(cfg, now, hidBusy());
}
