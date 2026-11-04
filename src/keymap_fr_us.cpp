#include "keymap_fr_us.h"

namespace {

constexpr uint8_t S = MOD_SHIFT;
constexpr uint8_t G = MOD_ALTGR;

struct Entry {
    uint32_t cp;
    uint8_t mod;
    uint8_t key;
};

// Touche morte suivie d'un caractère de base (ex. ^ puis e = ê).
struct DeadEntry {
    uint32_t cp;
    uint8_t mod;
    uint8_t key;
    char base;
};

// Codes HID = positions physiques d'un clavier US (HID Usage Tables, page 0x07).
const Entry US_TABLE[] = {
    {' ', 0, 0x2C},  {'!', S, 0x1E},  {'@', S, 0x1F},  {'#', S, 0x20},  {'$', S, 0x21},
    {'%', S, 0x22},  {'^', S, 0x23},  {'&', S, 0x24},  {'*', S, 0x25},  {'(', S, 0x26},
    {')', S, 0x27},  {'-', 0, 0x2D},  {'_', S, 0x2D},  {'=', 0, 0x2E},  {'+', S, 0x2E},
    {'[', 0, 0x2F},  {'{', S, 0x2F},  {']', 0, 0x30},  {'}', S, 0x30},  {'\\', 0, 0x31},
    {'|', S, 0x31},  {';', 0, 0x33},  {':', S, 0x33},  {'\'', 0, 0x34}, {'"', S, 0x34},
    {'`', 0, 0x35},  {'~', S, 0x35},  {',', 0, 0x36},  {'<', S, 0x36},  {'.', 0, 0x37},
    {'>', S, 0x37},  {'/', 0, 0x38},  {'?', S, 0x38},
};

// AZERTY français (Windows / Linux "fr").
const Entry FR_TABLE[] = {
    {' ', 0, 0x2C},
    // Rangée des chiffres, sans modificateur
    {'&', 0, 0x1E},  {u'é', 0, 0x1F}, {'"', 0, 0x20},  {'\'', 0, 0x21}, {'(', 0, 0x22},
    {'-', 0, 0x23},  {u'è', 0, 0x24}, {'_', 0, 0x25},  {u'ç', 0, 0x26}, {u'à', 0, 0x27},
    // Rangée des chiffres, AltGr (~ et ` sont des touches mortes, voir FR_DEAD)
    {'#', G, 0x20},  {'{', G, 0x21},  {'[', G, 0x22},  {'|', G, 0x23},  {'\\', G, 0x25},
    {'^', G, 0x26},  {'@', G, 0x27},
    {')', 0, 0x2D},  {u'°', S, 0x2D}, {']', G, 0x2D},
    {'=', 0, 0x2E},  {'+', S, 0x2E},  {'}', G, 0x2E},
    {'$', 0, 0x30},  {u'£', S, 0x30}, {u'¤', G, 0x30},
    {'*', 0, 0x31},  {u'µ', S, 0x31},
    {u'ù', 0, 0x34}, {'%', S, 0x34},  {u'²', 0, 0x35},
    // Rangée du bas : , ; : !
    {',', 0, 0x10},  {'?', S, 0x10},  {';', 0, 0x36},  {'.', S, 0x36},  {':', 0, 0x37},
    {'/', S, 0x37},  {'!', 0, 0x38},  {u'§', S, 0x38},
    {'<', 0, 0x64},  {'>', S, 0x64},
    {u'€', G, 0x08},
    // shortcut: œ = AltGr+o n'existe que sous Linux (xkb fr) ; l'AZERTY Windows n'a pas de œ.
    {u'œ', G, 0x12},
};

constexpr uint8_t FR_DEAD_KEY = 0x2F;  // touche ^ / ¨ à droite du P

const DeadEntry FR_DEAD[] = {
    {u'â', 0, FR_DEAD_KEY, 'a'}, {u'ê', 0, FR_DEAD_KEY, 'e'}, {u'î', 0, FR_DEAD_KEY, 'i'},
    {u'ô', 0, FR_DEAD_KEY, 'o'}, {u'û', 0, FR_DEAD_KEY, 'u'},
    {u'Â', 0, FR_DEAD_KEY, 'A'}, {u'Ê', 0, FR_DEAD_KEY, 'E'}, {u'Î', 0, FR_DEAD_KEY, 'I'},
    {u'Ô', 0, FR_DEAD_KEY, 'O'}, {u'Û', 0, FR_DEAD_KEY, 'U'},
    {u'ä', S, FR_DEAD_KEY, 'a'}, {u'ë', S, FR_DEAD_KEY, 'e'}, {u'ï', S, FR_DEAD_KEY, 'i'},
    {u'ö', S, FR_DEAD_KEY, 'o'}, {u'ü', S, FR_DEAD_KEY, 'u'}, {u'ÿ', S, FR_DEAD_KEY, 'y'},
    {u'Ä', S, FR_DEAD_KEY, 'A'}, {u'Ë', S, FR_DEAD_KEY, 'E'}, {u'Ï', S, FR_DEAD_KEY, 'I'},
    {u'Ö', S, FR_DEAD_KEY, 'O'}, {u'Ü', S, FR_DEAD_KEY, 'U'},
    {u'¨', S, FR_DEAD_KEY, ' '},
    {'~', G, 0x1F, ' '},  {u'ñ', G, 0x1F, 'n'}, {u'Ñ', G, 0x1F, 'N'},
    {'`', G, 0x24, ' '},
};

uint8_t letterKey(char lower, Layout layout) {
    if (layout == Layout::FR) {
        switch (lower) {
            case 'a': return 0x14;
            case 'q': return 0x04;
            case 'z': return 0x1A;
            case 'w': return 0x1D;
            case 'm': return 0x33;
            default: break;
        }
    }
    return 0x04 + (lower - 'a');
}

uint8_t digitKey(char d) { return d == '0' ? 0x27 : 0x1E + (d - '1'); }

template <size_t N>
const Entry* find(const Entry (&table)[N], uint32_t cp) {
    for (const Entry& e : table)
        if (e.cp == cp) return &e;
    return nullptr;
}

}  // namespace

bool parseLayout(const std::string& name, Layout& out) {
    if (name == "fr") { out = Layout::FR; return true; }
    if (name == "us") { out = Layout::US; return true; }
    return false;
}

bool appendCodepoint(uint32_t cp, Layout layout, std::vector<Stroke>& out) {
    if (cp == '\n') { out.push_back({0, KEY_ENTER}); return true; }
    if (cp == '\t') { out.push_back({0, KEY_TAB}); return true; }
    if (cp >= 'a' && cp <= 'z') {
        out.push_back({0, letterKey(char(cp), layout)});
        return true;
    }
    if (cp >= 'A' && cp <= 'Z') {
        out.push_back({S, letterKey(char(cp + 32), layout)});
        return true;
    }
    if (cp >= '0' && cp <= '9') {
        out.push_back({layout == Layout::FR ? S : uint8_t(0), digitKey(char(cp))});
        return true;
    }
    const Entry* e = layout == Layout::FR ? find(FR_TABLE, cp) : find(US_TABLE, cp);
    if (e) {
        out.push_back({e->mod, e->key});
        return true;
    }
    if (layout == Layout::FR) {
        for (const DeadEntry& d : FR_DEAD) {
            if (d.cp != cp) continue;
            out.push_back({d.mod, d.key});
            return appendCodepoint(uint8_t(d.base), layout, out);
        }
    }
    return false;
}

std::vector<Stroke> textToStrokes(const std::string& s, Layout layout,
                                  std::vector<uint32_t>* unsupported) {
    std::vector<Stroke> out;
    size_t i = 0;
    while (i < s.size()) {
        uint8_t c = uint8_t(s[i]);
        uint32_t cp;
        size_t len;
        if (c < 0x80)              { cp = c;        len = 1; }
        else if ((c >> 5) == 0x06) { cp = c & 0x1F; len = 2; }
        else if ((c >> 4) == 0x0E) { cp = c & 0x0F; len = 3; }
        else if ((c >> 3) == 0x1E) { cp = c & 0x07; len = 4; }
        else                       { cp = 0xFFFD;   len = 1; }
        if (i + len > s.size()) {
            cp = 0xFFFD;
            len = s.size() - i;
        } else {
            for (size_t k = 1; k < len; k++) {
                uint8_t cc = uint8_t(s[i + k]);
                if ((cc & 0xC0) != 0x80) { cp = 0xFFFD; len = k; break; }
                cp = (cp << 6) | (cc & 0x3F);
            }
        }
        i += len;
        if (cp == '\r') continue;
        if (!appendCodepoint(cp, layout, out) && unsupported) unsupported->push_back(cp);
    }
    return out;
}

std::string codepointToUtf8(uint32_t cp) {
    std::string r;
    if (cp < 0x80) {
        r += char(cp);
    } else if (cp < 0x800) {
        r += char(0xC0 | (cp >> 6));
        r += char(0x80 | (cp & 0x3F));
    } else if (cp < 0x10000) {
        r += char(0xE0 | (cp >> 12));
        r += char(0x80 | ((cp >> 6) & 0x3F));
        r += char(0x80 | (cp & 0x3F));
    } else {
        r += char(0xF0 | (cp >> 18));
        r += char(0x80 | ((cp >> 12) & 0x3F));
        r += char(0x80 | ((cp >> 6) & 0x3F));
        r += char(0x80 | (cp & 0x3F));
    }
    return r;
}
