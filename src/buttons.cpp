#include "buttons.h"

void Button::begin(uint8_t p) {
    pin = p;
    pinMode(pin, INPUT_PULLUP);
    raw = pressed = digitalRead(pin) == LOW;
    longFired = pressed;  // un bouton déjà enfoncé au démarrage ne déclenche rien
    changedAt = pressedAt = millis();
}

ButtonEvent Button::update(uint32_t now, uint16_t debounceMs, uint32_t longMs) {
    bool r = digitalRead(pin) == LOW;
    if (r != raw) {
        raw = r;
        changedAt = now;
    }
    if (raw != pressed && now - changedAt >= debounceMs) {
        pressed = raw;
        if (pressed) {
            pressedAt = now;
            longFired = false;
            return ButtonEvent::Pressed;
        }
        return ButtonEvent::Released;
    }
    if (pressed && longMs && !longFired && now - pressedAt >= longMs) {
        longFired = true;
        return ButtonEvent::LongPress;
    }
    return ButtonEvent::None;
}
