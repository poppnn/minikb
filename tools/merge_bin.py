"""Fusionne bootloader + partitions + boot_app0 + firmware + LittleFS en une image unique (offset 0x0).

Usage : python tools/merge_bin.py esp32c3 esp32s3
Pré-requis : pio run -e <env> et pio run -e <env> -t buildfs. Sortie : webflasher/firmware/minikb-<env>.bin
"""
import pathlib
import struct
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PIO_HOME = pathlib.Path.home() / ".platformio"
BOOT_APP0 = PIO_HOME / "packages" / "framework-arduinoespressif32" / "tools" / "partitions" / "boot_app0.bin"
ESPTOOL = PIO_HOME / "packages" / "tool-esptoolpy" / "esptool.py"
CHIPS = {"esp32c3": "esp32c3", "esp32s3": "esp32s3"}


def partitions(path):
    """Lit la table binaire ESP-IDF : entrées de 32 octets commençant par 0xAA50."""
    data = path.read_bytes()
    out = {}
    for i in range(0, len(data), 32):
        magic, ptype, subtype, offset, size, label = struct.unpack("<HBBII16s", data[i:i + 28])
        if magic != 0x50AA:
            break
        out[label.rstrip(b"\0").decode()] = (ptype, subtype, offset)
    return out


def merge(env):
    build = ROOT / ".pio" / "build" / env
    table = partitions(build / "partitions.bin")
    fs = [off for ptype, sub, off in table.values() if ptype == 1 and sub == 0x82]  # data / spiffs (LittleFS)
    otadata = [off for ptype, sub, off in table.values() if ptype == 1 and sub == 0x00]
    app = min(off for ptype, sub, off in table.values() if ptype == 0)
    if not (fs and otadata):
        raise SystemExit(f"{env}: partitions LittleFS/otadata introuvables")
    out = ROOT / "webflasher" / "firmware" / f"minikb-{env}.bin"
    out.parent.mkdir(parents=True, exist_ok=True)
    # En CI, tool-esptoolpy n'est pas téléchargé par un simple build : on prend alors esptool de pip.
    esptool = [str(ESPTOOL)] if ESPTOOL.exists() else ["-m", "esptool"]
    cmd = [sys.executable, *esptool, "--chip", CHIPS[env], "merge_bin", "-o", str(out),
           "0x0", str(build / "bootloader.bin"),
           "0x8000", str(build / "partitions.bin"),
           hex(otadata[0]), str(BOOT_APP0),
           hex(app), str(build / "firmware.bin"),
           hex(fs[0]), str(build / "littlefs.bin")]
    subprocess.run(cmd, check=True)
    print(f"{env}: app {hex(app)}, otadata {hex(otadata[0])}, littlefs {hex(fs[0])} -> {out.relative_to(ROOT)} "
          f"({out.stat().st_size // 1024} Ko)")


if __name__ == "__main__":
    for env in sys.argv[1:] or CHIPS:
        merge(env)
