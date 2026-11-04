#pragma once
#include <Arduino.h>
#include <vector>
#include "keymap_fr_us.h"

// Clavier HID BLE (NimBLE). Sur S3 avec MINIKB_USB_HID, les rapports partent aussi en USB.
void hidBegin(const char* bleName);
bool hidConnected();
bool hidBusy();
// Met des frappes en file ; elles sont envoyées par hidLoop() sans bloquer.
void hidQueue(const std::vector<Stroke>& strokes);
void hidLoop(uint32_t now, uint16_t keyDelayMs);
