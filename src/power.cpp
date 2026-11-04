#include "power.h"
#include <driver/gpio.h>
#include <esp_sleep.h>
#if CONFIG_IDF_TARGET_ESP32S3
#include <driver/rtc_io.h>
#endif

static uint32_t lastActivity = 0;
static bool warnedNoWakePin = false;

void powerActivity(uint32_t now) { lastActivity = now; }

void powerLoop(const Config& cfg, uint32_t now, bool busy) {
    if (cfg.sleepMin == 0 || busy) return;
    if (now - lastActivity < uint32_t(cfg.sleepMin) * 60000UL) return;

    uint64_t mask = 0;
    for (const KeyConfig& k : cfg.keys)
        if (isWakePin(k.pin) && digitalRead(k.pin) == HIGH) mask |= 1ULL << k.pin;
    if (!mask) {
        // Sans touche de réveil, on ne pourrait sortir de veille qu'en débranchant.
        if (!warnedNoWakePin) Serial.println("[power] aucune touche sur un pin de réveil, veille annulée");
        warnedNoWakePin = true;
        return;
    }

    Serial.println("[power] inactivité, deep sleep");
    Serial.flush();
    digitalWrite(LED_PIN, LED_ACTIVE_LOW ? HIGH : LOW);
#if CONFIG_IDF_TARGET_ESP32S3
    // shortcut: ext1 sur IDF 4.4 ne sait pas « n'importe quel pin bas », on réveille sur la 1re touche RTC ; passer à ESP-IDF 5 (ext1 ANY_LOW) pour toutes.
    int first = __builtin_ctzll(mask);
    rtc_gpio_pullup_en((gpio_num_t)first);
    esp_sleep_enable_ext0_wakeup((gpio_num_t)first, 0);
#else
    for (int pin = 0; pin < 6; pin++) {
        if (!(mask & (1ULL << pin))) continue;
        gpio_pullup_en((gpio_num_t)pin);  // garde le pull-up pendant la veille
        gpio_pulldown_dis((gpio_num_t)pin);
    }
    esp_deep_sleep_enable_gpio_wakeup(mask, ESP_GPIO_WAKEUP_GPIO_LOW);
#endif
    esp_deep_sleep_start();
}
