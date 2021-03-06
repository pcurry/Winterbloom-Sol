import io
import time
import os
import subprocess
import shutil
import sys
import zipfile

import requests

from libwinter import utils
from libsol import calibrate

DEVICE_NAME = "winterbloom_sol"
JLINK_DEVICE = "ATSAMD51J20"
JLINK_SCRIPT = "scripts/flash.jlink"

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIRMWARE_DIR = os.path.join(ROOT_DIR, "firmware")
LIB_DIR = os.path.join(FIRMWARE_DIR, "lib")
EXAMPLES_DIR = os.path.join(ROOT_DIR, "examples")

FILES_TO_DOWNLOAD = {
    "https+zip://github.com/adafruit/Adafruit_CircuitPython_NeoPixel/releases/download/6.0.0/adafruit-circuitpython-neopixel-5.x-mpy-6.0.0.zip:adafruit-circuitpython-neopixel-5.x-mpy-6.0.0/lib/neopixel.mpy": "neopixel.mpy"
}

FILES_TO_DEPLOY = {
    utils.get_cache_path("neopixel.mpy"): "lib",
    os.path.join(FIRMWARE_DIR, "winterbloom_sol"): "lib",
    os.path.join(FIRMWARE_DIR, "LICENSE"): ".",
    os.path.join(FIRMWARE_DIR, "README.HTM"): ".",
    os.path.join(
        LIB_DIR, "adafruit_circuitpython_busdevice/adafruit_bus_device"
    ): "lib",
    os.path.join(LIB_DIR, "winterbloom_ad_dacs/winterbloom_ad_dacs"): "lib",
    os.path.join(LIB_DIR, "winterbloom_voltageio/winterbloom_voltageio.py"): "lib",
    os.path.join(LIB_DIR, "winterbloom_smolmidi/winterbloom_smolmidi.py"): "lib",
    EXAMPLES_DIR: ".",
    os.path.join(EXAMPLES_DIR, "1_default.py"): "code.py",
}


def program_firmware():
    print("========== PROGRAMMING FIRMWARE ==========")

    bootloader_url = utils.find_latest_bootloader(DEVICE_NAME)
    circuitpython_url = utils.find_latest_circuitpython(DEVICE_NAME)

    utils.download_file_to_cache(bootloader_url, "bootloader.bin")
    firmware_path = utils.download_file_to_cache(circuitpython_url, "firmware.uf2")
    utils.convert_uf2_to_bin(firmware_path)

    utils.run_jlink(JLINK_DEVICE, JLINK_SCRIPT)


def deploy_circuitpython_code(destination=None):
    print("========== DEPLOYING CODE ==========")

    if not destination:
        print("Waiting for CIRCUITPY drive...")
        destination = utils.wait_for_drive("CIRCUITPY")

    print("Cleaning temporary files from src directories...")
    utils.clean_pycache(FIRMWARE_DIR)
    utils.clean_pycache(EXAMPLES_DIR)
    print("Downloading files to cache...")
    utils.download_files_to_cache(FILES_TO_DOWNLOAD)
    print("Copying files...")
    utils.deploy_files(FILES_TO_DEPLOY, destination)


def run_calibration():
    print("========== CALIBRATION & TEST ==========")
    calibrate.main()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "publish":
        deploy_circuitpython_code("distribution")
        return

    try:
        circuitpython_drive = utils.find_drive_by_name("CIRCUITPY")
    except:
        circuitpython_drive = None

    if not circuitpython_drive:
        program_firmware()

    if circuitpython_drive and os.path.exists(
        os.path.join(circuitpython_drive, "code.py")
    ):
        if input("redeploy code? y/n: ").strip() == "y":
            deploy_circuitpython_code()
    else:
        deploy_circuitpython_code()

    if not circuitpython_drive or not os.path.exists(
        os.path.join(circuitpython_drive, "calibration.py")
    ):
        run_calibration()


if __name__ == "__main__":
    main()
