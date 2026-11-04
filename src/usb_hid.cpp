// USB HID natif (ESP32-S3 uniquement). Fichier séparé : les en-têtes TinyUSB et
// NimBLE définissent les mêmes macros HID et ne compilent pas ensemble.
#ifdef MINIKB_USB_HID
#include <USB.h>
#include <USBHIDKeyboard.h>

static USBHIDKeyboard usbKeyboard;

void usbHidBegin() {
    usbKeyboard.begin();
    USB.begin();
}

void usbHidSend(uint8_t mod, uint8_t key) {
    KeyReport r = {mod, 0, {key, 0, 0, 0, 0, 0}};
    usbKeyboard.sendReport(&r);
}
#endif
