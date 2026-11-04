#include "ble_hid.h"
#include <NimBLEDevice.h>
#include <NimBLEHIDDevice.h>
#include <deque>

#ifdef MINIKB_USB_HID
void usbHidBegin();  // usb_hid.cpp
void usbHidSend(uint8_t mod, uint8_t key);
#endif

// Descripteur clavier standard (boot keyboard) avec Report ID 1 et LED en sortie.
static const uint8_t REPORT_MAP[] = {
    0x05, 0x01, 0x09, 0x06, 0xA1, 0x01, 0x85, 0x01,  // Usage Page Desktop, Keyboard, Report ID 1
    0x05, 0x07, 0x19, 0xE0, 0x29, 0xE7, 0x15, 0x00,  // Modificateurs
    0x25, 0x01, 0x75, 0x01, 0x95, 0x08, 0x81, 0x02,
    0x95, 0x01, 0x75, 0x08, 0x81, 0x01,              // Octet réservé
    0x95, 0x05, 0x75, 0x01, 0x05, 0x08, 0x19, 0x01,  // LED (sortie)
    0x29, 0x05, 0x91, 0x02, 0x95, 0x01, 0x75, 0x03,
    0x91, 0x01,
    0x95, 0x06, 0x75, 0x08, 0x15, 0x00, 0x25, 0x73,  // 6 touches
    0x05, 0x07, 0x19, 0x00, 0x29, 0x73, 0x81, 0x00,
    0xC0,
};

static NimBLEHIDDevice* hid = nullptr;
static NimBLECharacteristic* inputReport = nullptr;
static volatile bool connected = false;

static std::deque<Stroke> queue;
static bool keyDown = false;
static uint32_t lastStepAt = 0;

class ServerCallbacks : public NimBLEServerCallbacks {
    void onConnect(NimBLEServer*) override {
        connected = true;
        Serial.println("[ble] connecté");
    }
    void onDisconnect(NimBLEServer*) override {
        connected = false;
        Serial.println("[ble] déconnecté, réannonce");
        NimBLEDevice::startAdvertising();
    }
};

static void sendReport(uint8_t mod, uint8_t key) {
    uint8_t r[8] = {mod, 0, key, 0, 0, 0, 0, 0};
    if (connected) {
        inputReport->setValue(r, sizeof(r));
        inputReport->notify();
    }
#ifdef MINIKB_USB_HID
    usbHidSend(mod, key);
#endif
}

void hidBegin(const char* bleName) {
    NimBLEDevice::init(bleName);
    NimBLEDevice::setSecurityAuth(true, false, true);  // bonding, pas de MITM, Secure Connections
    NimBLEDevice::setSecurityIOCap(BLE_HS_IO_NO_INPUT_OUTPUT);

    NimBLEServer* server = NimBLEDevice::createServer();
    server->setCallbacks(new ServerCallbacks());

    hid = new NimBLEHIDDevice(server);
    inputReport = hid->inputReport(1);
    hid->outputReport(1);  // LED : ignorées, mais attendues par certains hôtes
    hid->manufacturer()->setValue("DIY");
    hid->pnp(0x02, 0xE502, 0xA111, 0x0210);
    hid->hidInfo(0x00, 0x01);
    hid->reportMap((uint8_t*)REPORT_MAP, sizeof(REPORT_MAP));
    hid->startServices();
    hid->setBatteryLevel(100);

    NimBLEAdvertising* adv = server->getAdvertising();
    adv->setAppearance(HID_KEYBOARD);
    adv->addServiceUUID(hid->hidService()->getUUID());
    adv->setScanResponse(true);
    adv->start();
    Serial.printf("[ble] annonce sous le nom \"%s\"\n", bleName);

#ifdef MINIKB_USB_HID
    usbHidBegin();
#endif
}

bool hidConnected() { return connected; }

bool hidBusy() { return keyDown || !queue.empty(); }

void hidQueue(const std::vector<Stroke>& strokes) {
#ifndef MINIKB_USB_HID
    if (!connected) {
        Serial.println("[ble] non connecté, frappe ignorée");
        return;
    }
#endif
    queue.insert(queue.end(), strokes.begin(), strokes.end());
}

void hidLoop(uint32_t now, uint16_t keyDelayMs) {
    if (!hidBusy() || now - lastStepAt < keyDelayMs) return;
    lastStepAt = now;
    if (keyDown) {
        sendReport(0, 0);  // relâchement, indispensable entre deux frappes identiques
        keyDown = false;
        return;
    }
    Stroke s = queue.front();
    queue.pop_front();
    sendReport(s.mod, s.key);
    keyDown = true;
}
