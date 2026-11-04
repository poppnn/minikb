#pragma once
#include <Arduino.h>
#include "config.h"

// Deep sleep après inactivité (cfg.sleepMin, 0 = désactivé), réveil par les touches sur WAKE_PINS.
void powerActivity(uint32_t now);
void powerLoop(const Config& cfg, uint32_t now, bool busy);
