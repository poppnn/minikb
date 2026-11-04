# MiniKB : clavier de macros BLE (ESP32-C3 SuperMini)

Un mini clavier de 1 à 10 touches mécaniques MX. Chaque touche tape un texte (ou un trigger espanso) en Bluetooth, comme un vrai clavier. La configuration se fait depuis le téléphone, sur une page web servie par le clavier.

```
platformio.ini      cibles esp32c3 (SuperMini), esp32s3 (BLE + USB HID), native (tests)
src/                config, keymap_fr_us, ble_hid, usb_hid (S3), buttons, webserver, power, main
data/index.html     web UI (sans CDN), envoyée dans LittleFS
test/test_keymap/   tests unitaires de la table de conversion (PC)
test/webui/         tests Playwright du web UI (API mockée)
docs/wiring.svg     schéma de câblage
webflasher/         page ESP Web Tools (GitHub Pages)
tools/merge_bin.py  image unique bootloader + firmware + LittleFS
.github/workflows/  CI : tests, builds, déploiement du web flasher
enclosure/          modèle Fusion, STL, captures et README d'impression
```

## Câblage

Pas de matrice ni de diodes : chaque switch a une patte sur un GPIO et l'autre sur un GND commun, relié en guirlande. Voir [docs/wiring.svg](docs/wiring.svg).

- Pins utilisables : 0, 1, 3, 4, 5, 6, 7, 10, 20, 21. Les touches par défaut utilisent 0, 1, 3, 4, 5, 6, 7 et 10.
- Interdits : 2, 8, 9 (strapping, LED, BOOT), 18 et 19 (USB). Le firmware et le web UI les refusent tous les deux.
- Seules les touches sur 0, 1, 3, 4 et 5 réveillent le clavier du deep sleep.

## Flasher

### Depuis le navigateur (le plus simple)

Ouvre le **web flasher** dans Chrome ou Edge sur ordinateur : **https://poppnn.github.io/minikb/**. Branche la carte, clique sur « Connecter et flasher » et coche « Effacer l'appareil » pour une première installation. Le firmware et le web UI sont écrits en une seule image.

**Après le flash, appuie sur RST.** Sur la SuperMini, le reset par USB laisse la puce en mode téléchargement : la LED reste éteinte tant que tu n'as pas appuyé.

Le site est reconstruit par GitHub Actions à chaque push sur `main` : tests natifs, firmware C3 et S3, tests Playwright, puis images fusionnées par `tools/merge_bin.py`.

### Avec PlatformIO

Utilise l'extension PlatformIO de VS Code ou la CLI `pio`. Sous Windows, si `pio` répond par une erreur Python, c'est le paquet PyPI homonyme : lance `~/.platformio/penv/Scripts/pio.exe`.

```bash
pio run -e esp32c3 -t upload
```

```bash
pio run -e esp32c3 -t uploadfs
```

La première commande flashe le firmware, la deuxième envoie `data/index.html` dans LittleFS. Sans `uploadfs`, le mode config répond « index.html absent ».

Après l'upload, appuie aussi sur RST. Pour voir l'état du clavier, ouvre le moniteur série et envoie n'importe quel caractère : il répond par une ligne `[status] ...` (mode, BLE, nombre de touches, layout, mot de passe Wi-Fi). Les logs du démarrage sont souvent perdus, parce que l'USB se réénumère au reset.

```bash
pio device monitor
```

Si la carte ne se laisse pas flasher : maintiens BOOT, appuie sur RESET, relâche BOOT, puis relance l'upload.

## Premier appairage BLE

1. Branche le clavier. La LED clignote : il attend une connexion.
2. Windows : Paramètres → Bluetooth et appareils → Ajouter un appareil → Bluetooth → **MiniKB**. Sur Android ou Linux, c'est la même chose depuis les réglages Bluetooth.
3. La LED reste fixe : il est connecté. Le bonding est activé, donc il se reconnecte tout seul ensuite.

**Le layout de l'hôte doit correspondre au réglage `layout`.** Un clavier HID envoie des positions de touches, pas des caractères. Avec `fr`, l'ordinateur doit être en AZERTY français.

## Mode config

1. En fonctionnement normal, maintiens **BOOT 3 secondes**. Le clavier redémarre, coupe le BLE et la LED flashe rapidement.
2. Connecte le téléphone au Wi-Fi **MiniKB-Config**.
3. Par défaut, ce réseau est **ouvert**, sans mot de passe. Tu peux en définir un dans la page (8 à 63 caractères) ; le laisser vide rend le réseau à nouveau ouvert.
4. Ouvre **http://192.168.4.1**.
5. Après 10 min sans requête, le clavier redémarre en mode normal. « Enregistrer » redémarre aussi.

Dans la page, tu peux :

- ajouter, supprimer ou réordonner les touches (1 à 10). Chaque touche a un pin (seuls les pins libres et autorisés sont proposés), un label, un texte et une case « Entrée à la fin » ;
- régler le layout fr/us, le nom BLE, le délai entre touches, l'anti-rebond et la veille ;
- **Tester** une touche. Comme le BLE et le Wi-Fi ne tournent jamais en même temps sur le C3, le test ne tape rien : il vérifie que chaque caractère est convertible dans le layout choisi et liste ceux qui ne le sont pas ;
- exporter le fichier espanso, exporter ou importer la config en JSON, et revenir aux valeurs par défaut.

La config est stockée dans `/config.json` :

```json
{"layout":"fr","ble_name":"MiniKB","ap_pass":"","key_delay_ms":8,"debounce_ms":30,"sleep_min":0,
 "keys":[{"pin":0,"label":"Mail","send":";mail","enter":false}]}
```

Si le fichier est illisible ou invalide, il est renommé en `/config.bad` et la config par défaut est utilisée.

API : `GET/POST /api/config`, `POST /api/test` (`{"text":"...","enter":false}`), `POST /api/reboot`, `GET /api/pins`.

## Utilisation avec espanso

Le plus fiable : chaque touche envoie un trigger court en ASCII (par ex. `;mail`), et espanso le remplace par le texte long, accents et emojis compris.

1. Dans le web UI : **Exporter espanso** → `minikb.yml`.
2. Copie-le dans le dossier `match` d'espanso : `%APPDATA%\espanso\match\` sous Windows, `~/.config/espanso/match/` sous Linux.
3. Remplace chaque `replace:` par le texte voulu. L'export met le label en attendant, puisque le clavier ne connaît que le trigger.
4. Si espanso rate des caractères, augmente `key_delay_ms` (par ex. 15).

## Changer le nombre de touches

- **Firmware** : rien à recompiler. Ajoute ou retire des touches dans le web UI. Les pins non déclarés restent des entrées flottantes, sans effet.
- **Boîtier** : modifie `cols` et `rows` dans Fusion, puis relance le script pour les keycaps. Voir [enclosure/README.md](enclosure/README.md).

## Veille

`sleep_min` > 0 active un deep sleep après ce nombre de minutes sans appui. Le réveil se fait par une touche sur GPIO 0, 1, 3, 4 ou 5. Cet appui ne fait que réveiller : il n'est pas tapé. Si aucune touche n'est sur ces pins, la veille est annulée (message sur le port série).

## ESP32-S3

`pio run -e esp32s3` compile la même base. Les rapports clavier partent en BLE **et** en USB HID natif (TinyUSB). Retire `-DMINIKB_USB_HID` dans `platformio.ini` pour n'avoir que le BLE. Les pins autorisés y sont différents (voir `src/config.h`). En deep sleep, seule la première touche sur un pin RTC réveille le S3 (limite d'ESP-IDF 4.4).

## Tests

```bash
pio run -e esp32c3 -e esp32s3
```

```bash
pio test -e native
```

```bash
cd test/webui && npm install && npx playwright install chromium-headless-shell && npx playwright test
```

- `pio test -e native` demande un gcc sur le PATH. Celui installé via winget (WinLibs) est dans `%LOCALAPPDATA%\Microsoft\WinGet\Packages\BrechtSanders.WinLibs...\mingw64\bin`.
- Les tests natifs couvrent l'AZERTY (a/q, z/w, m), les chiffres avec Shift, les accents, `@ € # { } [ ] | \ ^`, les touches mortes (ê, ü, ~), le layout US, les caractères non supportés et l'UTF-8 invalide.
- Les tests UI couvrent le chargement, l'ajout et la suppression, l'exclusion des pins interdits et des doublons, la limite de 10, le réordonnancement, l'enregistrement, le mot de passe (vide accepté = réseau ouvert), le test de touche et l'export YAML.

## Dépannage

| Symptôme | Cause probable et solution |
|---|---|
| Lettres mélangées (`q` au lieu de `a`) | Le layout de l'ordinateur ne correspond pas à `layout`. |
| Caractères manquants avec espanso | Augmenter `key_delay_ms`. |
| `œ` ne sort pas sous Windows | L'AZERTY Windows n'a pas de `œ`. Passe par espanso. |
| Pas de reconnexion après reflash | Supprime MiniKB des appareils Bluetooth et réappaire-le. |
| La LED clignote mais l'hôte ne voit rien | Supprime l'appareil côté hôte. Le nom BLE a peut-être changé. |
| Page config « index.html absent » | Lancer `pio run -t uploadfs`. |
| Mot de passe Wi-Fi oublié | Envoie un caractère sur le port série : la ligne `[status]` l'affiche. Sinon, réflashe en effaçant l'appareil (retour au réseau ouvert). |
| LED éteinte après un flash | Appuie sur RST : le reset par USB laisse la SuperMini en mode téléchargement. |
| Une touche ne répond pas | Vérifie la soudure et le GND commun. Un pin interdit est refusé à l'enregistrement. |
| Caractère ignoré | Message `[keymap] caractère non supporté` sur le port série. Utilise le bouton Tester du web UI. |
