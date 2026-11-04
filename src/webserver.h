#pragma once
#include "config.h"

// Mode config : AP Wi-Fi + web UI + API REST. Le BLE est coupé dans ce mode.
void webBegin(Config& cfg);
// Gère les redémarrages différés et le timeout d'inactivité (10 min).
void webLoop(uint32_t now);
