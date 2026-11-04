// Tests natifs de la table de conversion : pio test -e native
#include <unity.h>
#include "keymap_fr_us.h"

void setUp() {}
void tearDown() {}

static std::vector<Stroke> fr(const char* s, std::vector<uint32_t>* bad = nullptr) {
    return textToStrokes(s, Layout::FR, bad);
}

static void assertStroke(const Stroke& st, uint8_t mod, uint8_t key) {
    TEST_ASSERT_EQUAL_HEX8(mod, st.mod);
    TEST_ASSERT_EQUAL_HEX8(key, st.key);
}

void test_fr_azerty_letters() {
    auto s = fr("azqwm");
    TEST_ASSERT_EQUAL(5, s.size());
    assertStroke(s[0], 0, 0x14);  // a = touche Q US
    assertStroke(s[1], 0, 0x1A);  // z = touche W US
    assertStroke(s[2], 0, 0x04);  // q = touche A US
    assertStroke(s[3], 0, 0x1D);  // w = touche Z US
    assertStroke(s[4], 0, 0x33);  // m = touche ; US
}

void test_fr_digits_need_shift() {
    auto s = fr("10");
    assertStroke(s[0], MOD_SHIFT, 0x1E);
    assertStroke(s[1], MOD_SHIFT, 0x27);
}

void test_fr_sentence_with_accents() {
    std::vector<uint32_t> bad;
    auto s = fr("Déjà vu, ça été où ?", &bad);
    TEST_ASSERT_EQUAL(0, bad.size());
    assertStroke(s[0], MOD_SHIFT, 0x07);  // D
    assertStroke(s[1], 0, 0x1F);          // é
    assertStroke(s[3], 0, 0x27);          // à
    assertStroke(s[7], 0, 0x10);          // ,
    assertStroke(s[9], 0, 0x26);          // ç
    // "où" : ù = 0x34
    assertStroke(s[17], 0, 0x34);
    assertStroke(s[19], MOD_SHIFT, 0x10);  // ?
}

void test_fr_email_and_symbols() {
    std::vector<uint32_t> bad;
    auto s = fr("a@b.fr #1 10€", &bad);
    TEST_ASSERT_EQUAL(0, bad.size());
    assertStroke(s[1], MOD_ALTGR, 0x27);   // @
    assertStroke(s[3], MOD_SHIFT, 0x36);   // .
    assertStroke(s[7], MOD_ALTGR, 0x20);   // #
    assertStroke(s[12], MOD_ALTGR, 0x08);  // €
    TEST_ASSERT_EQUAL(13, s.size());
}

void test_fr_dead_keys() {
    auto s = fr("être ü ~");
    // ê = ^ mort + e
    assertStroke(s[0], 0, 0x2F);
    assertStroke(s[1], 0, 0x08);
    // ü = ¨ mort (Shift+^) + u
    assertStroke(s[6], MOD_SHIFT, 0x2F);
    assertStroke(s[7], 0, 0x18);
    // ~ = AltGr+é (mort) + espace
    assertStroke(s[9], MOD_ALTGR, 0x1F);
    assertStroke(s[10], 0, KEY_SPACE);
    TEST_ASSERT_EQUAL(11, s.size());
}

void test_fr_brackets_and_pipes() {
    auto s = fr("{[|\\^]}");
    assertStroke(s[0], MOD_ALTGR, 0x21);
    assertStroke(s[1], MOD_ALTGR, 0x22);
    assertStroke(s[2], MOD_ALTGR, 0x23);
    assertStroke(s[3], MOD_ALTGR, 0x25);
    assertStroke(s[4], MOD_ALTGR, 0x26);
    assertStroke(s[5], MOD_ALTGR, 0x2D);
    assertStroke(s[6], MOD_ALTGR, 0x2E);
}

void test_us_layout() {
    std::vector<uint32_t> bad;
    auto s = textToStrokes("a@#1;", Layout::US, &bad);
    assertStroke(s[0], 0, 0x04);
    assertStroke(s[1], MOD_SHIFT, 0x1F);
    assertStroke(s[2], MOD_SHIFT, 0x20);
    assertStroke(s[3], 0, 0x1E);
    assertStroke(s[4], 0, 0x33);
    // € n'existe pas en US : ignoré et signalé
    s = textToStrokes("é€", Layout::US, &bad);
    TEST_ASSERT_EQUAL(0, s.size());
    TEST_ASSERT_EQUAL(2, bad.size());
    TEST_ASSERT_EQUAL_HEX32(0x20AC, bad[1]);
}

void test_unsupported_and_control_chars() {
    std::vector<uint32_t> bad;
    auto s = fr("a😀\r\nb", &bad);
    TEST_ASSERT_EQUAL(1, bad.size());
    TEST_ASSERT_EQUAL_HEX32(0x1F600, bad[0]);
    TEST_ASSERT_EQUAL(3, s.size());  // a, Entrée, b (\r ignoré)
    assertStroke(s[1], 0, KEY_ENTER);
    TEST_ASSERT_EQUAL_STRING("€", codepointToUtf8(0x20AC).c_str());
}

void test_invalid_utf8_does_not_crash() {
    std::vector<uint32_t> bad;
    auto s = fr("a\xC3", &bad);  // séquence tronquée
    TEST_ASSERT_EQUAL(1, s.size());
    TEST_ASSERT_EQUAL(1, bad.size());
}

void test_parse_layout() {
    Layout l;
    TEST_ASSERT_TRUE(parseLayout("fr", l));
    TEST_ASSERT_TRUE(l == Layout::FR);
    TEST_ASSERT_FALSE(parseLayout("de", l));
}

int main() {
    UNITY_BEGIN();
    RUN_TEST(test_fr_azerty_letters);
    RUN_TEST(test_fr_digits_need_shift);
    RUN_TEST(test_fr_sentence_with_accents);
    RUN_TEST(test_fr_email_and_symbols);
    RUN_TEST(test_fr_dead_keys);
    RUN_TEST(test_fr_brackets_and_pipes);
    RUN_TEST(test_us_layout);
    RUN_TEST(test_unsupported_and_control_chars);
    RUN_TEST(test_invalid_utf8_does_not_crash);
    RUN_TEST(test_parse_layout);
    return UNITY_END();
}
