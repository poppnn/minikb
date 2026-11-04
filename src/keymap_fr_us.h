#pragma once
// Conversion caractère Unicode -> frappes HID (keycode + modificateurs).
// Sans dépendance Arduino pour pouvoir être testé en natif.
#include <stdint.h>
#include <string>
#include <vector>

enum class Layout : uint8_t { US, FR };

struct Stroke {
    uint8_t mod;
    uint8_t key;
};

constexpr uint8_t MOD_SHIFT = 0x02;
constexpr uint8_t MOD_ALTGR = 0x40;  // Right Alt
constexpr uint8_t KEY_ENTER = 0x28;
constexpr uint8_t KEY_TAB = 0x2B;
constexpr uint8_t KEY_SPACE = 0x2C;

bool parseLayout(const std::string& name, Layout& out);

// Ajoute à `out` les frappes du caractère `cp` (1 ou 2 pour une touche morte).
// Retourne false si le caractère n'est pas tapable dans ce layout.
bool appendCodepoint(uint32_t cp, Layout layout, std::vector<Stroke>& out);

// Décode l'UTF-8 et convertit tout le texte. Les caractères non supportés
// sont ignorés et ajoutés à `unsupported` si fourni.
std::vector<Stroke> textToStrokes(const std::string& utf8, Layout layout,
                                  std::vector<uint32_t>* unsupported = nullptr);

// Encode un codepoint en UTF-8 (pour les messages d'erreur).
std::string codepointToUtf8(uint32_t cp);
