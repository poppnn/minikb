#pragma once
#include <Arduino.h>

enum class ButtonEvent : uint8_t { None, Pressed, Released, LongPress };

// Bouton actif bas (INPUT_PULLUP), debounce non bloquant + appui long.
struct Button {
    uint8_t pin = 0xFF;
    bool raw = false;
    bool pressed = false;
    bool longFired = false;
    uint32_t changedAt = 0;
    uint32_t pressedAt = 0;

    void begin(uint8_t p);
    // longMs = 0 : pas d'événement LongPress.
    ButtonEvent update(uint32_t now, uint16_t debounceMs, uint32_t longMs = 0);
};
