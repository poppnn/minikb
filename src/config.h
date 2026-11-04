#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include <vector>
#include "keymap_fr_us.h"

constexpr size_t MAX_KEYS = 10;
constexpr const char* AP_SSID = "MiniKB-Config";

#if CONFIG_IDF_TARGET_ESP32S3
// Exclus : 0 (BOOT), 3/45/46 (strapping), 19/20 (USB), 26-37 (flash/PSRAM), 48 (LED RGB)
constexpr uint8_t ALLOWED_PINS[] = {1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21};
constexpr uint8_t WAKE_PINS[] = {1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21};
constexpr uint8_t LED_PIN = LED_BUILTIN;
constexpr bool LED_ACTIVE_LOW = false;
constexpr uint8_t BOOT_PIN = 0;
#else
// ESP32-C3 SuperMini. Exclus : 2/8/9 (strapping, LED, BOOT), 18/19 (USB)
constexpr uint8_t ALLOWED_PINS[] = {0, 1, 3, 4, 5, 6, 7, 10, 20, 21};
constexpr uint8_t WAKE_PINS[] = {0, 1, 3, 4, 5};  // GPIO0-5 réveillent du deep sleep (2 exclu)
constexpr uint8_t LED_PIN = 8;
constexpr bool LED_ACTIVE_LOW = true;
constexpr uint8_t BOOT_PIN = 9;
#endif

struct KeyConfig {
    uint8_t pin;
    String label;
    String send;
    bool enter;
};

struct Config {
    Layout layout = Layout::FR;
    String bleName = "MiniKB";
    String apPass;
    uint16_t keyDelayMs = 8;
    uint16_t debounceMs = 30;
    uint16_t sleepMin = 0;
    std::vector<KeyConfig> keys;
};

bool isAllowedPin(int pin);
bool isWakePin(int pin);

Config defaultConfig();
// Valide strictement `src` et remplit `out` (les champs absents gardent la valeur de `out`).
bool configFromJson(JsonVariantConst src, Config& out, String& err);
void configToJson(const Config& cfg, JsonDocument& doc);

// Monte LittleFS et charge /config.json. Retourne false si fallback sur la config par défaut.
bool loadConfig(Config& cfg);
bool saveConfig(const Config& cfg);
