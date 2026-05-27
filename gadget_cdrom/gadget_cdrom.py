#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import logging
import time
import subprocess
from pathlib import Path
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
APP_DIR = os.path.dirname(os.path.realpath(__file__))
PXE_ROOT = "/pxe"

MODE_CD = "cd"
MODE_HDD = "hdd"
MODE_USB = "usb"
MODE_PXE = "pxe"
MODE_SHUTDOWN = "shutdown"

ALL_MODES = [MODE_CD, MODE_HDD, MODE_USB, MODE_PXE, MODE_SHUTDOWN]
BROWSE_MODES = [MODE_CD, MODE_USB, MODE_PXE]

FILE_EXTS = {
    MODE_CD: "iso",
    MODE_USB: "img",
    MODE_PXE: "ipxe",
}

LIST_SCRIPTS = {
    MODE_CD: "list_iso.sh",
    MODE_USB: "list_iso.sh",
    MODE_PXE: "list_pxe.sh",
}

INSERT_SCRIPTS = {
    MODE_CD: "insert_iso.sh",
    MODE_USB: "insert_iso.sh",
    MODE_PXE: "insert_pxe.sh",
}

REMOVE_SCRIPTS = {
    MODE_CD: "remove_iso.sh",
    MODE_USB: "remove_iso.sh",
    MODE_PXE: "remove_pxe.sh",
}

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

class SH1106:
    def __init__(self):
        spi = spidev.SpiDev(0, 0)
        spi.max_speed_hz = 2000000
        spi.mode = 0
        self._spi = spi

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RESET_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        GPIO.setup(self.BL_PIN, GPIO.OUT)

        GPIO.output(self.CS_PIN, 0)
        GPIO.output(self.BL_PIN, 1)
        GPIO.output(self.DC_PIN, 0)

        self.reset()
        self._run_commands(self.INIT_COMMANDS)
        time.sleep(0.1)
        self._run_command(0xAF)

    def _run_command(self, command):
        GPIO.output(self.DC_PIN, GPIO.LOW)
        self._spi.writebytes((command,))

    def _run_commands(self, commands):
        for command in commands:
            self._run_command(command)

    def reset(self):
        GPIO.output(self.RESET_PIN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.RESET_PIN, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.RESET_PIN, GPIO.HIGH)
        time.sleep(0.1)

    def display_image(self, pil_image, invert = True):
        buf_size = self.HEIGHT_RES * self.WIDTH_RES // 8
        buf = [0xFF] * buf_size
        image_raw_pixels = pil_image.convert('1').load()
        for y in range(self.HEIGHT_RES):
            for x in range(self.WIDTH_RES):
                if image_raw_pixels[x, y] == 0:
                    buf[x + (y // 8) * self.WIDTH_RES] &= ~(1 << (y % 8))

        for page in range(0, self.HEIGHT_RES // 8):
            self._run_command(0xB0 + page)
            self._run_command(0x02)
            self._run_command(0x10)
            time.sleep(0.01)
            GPIO.output(self.DC_PIN, GPIO.HIGH)

            for i in range(0, self.WIDTH_RES):
                page_data = buf[i + self.WIDTH_RES * page]
                if not invert:
                    page_data = ~page_data
                self._spi.writebytes((~page_data,))

    HEIGHT_RES = 64
    WIDTH_RES = 128
    RESET_PIN       = 25
    DC_PIN          = 24
    CS_PIN          = 8
    BL_PIN          = 18
    INIT_COMMANDS   = (0xAE,
    0x02,
    0x10,
    0x40,
    0x81,
    0xA0,
    0xC0,
    0xA6,
    0xA8,
    0x3F,
    0xD3,
    0x00,
    0xD5,
    0x80,
    0xD9,
    0xF1,
    0xDA,
    0x12,
    0xDB,
    0x40,
    0x20,
    0x02,
    0xA4,
    0xA6,
    )


class ST7735S:
    WIDTH_RES = 128
    HEIGHT_RES = 128
    RESET_PIN = 27
    DC_PIN = 25
    CS_PIN = 8
    BL_PIN = 24

    def __init__(self):
        spi = spidev.SpiDev(0, 0)
        spi.max_speed_hz = 32000000
        spi.mode = 0
        self._spi = spi

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RESET_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        GPIO.setup(self.BL_PIN, GPIO.OUT)

        GPIO.output(self.CS_PIN, 0)
        GPIO.output(self.BL_PIN, 1)
        GPIO.output(self.DC_PIN, 0)

        self.reset()
        self._run_commands(self.INIT_COMMANDS)

    def _run_command(self, command, data=()):
        GPIO.output(self.DC_PIN, GPIO.LOW)
        self._spi.writebytes((command,))
        if data:
            GPIO.output(self.DC_PIN, GPIO.HIGH)
            self._spi.writebytes(tuple(data))

    def _run_commands(self, commands):
        for command, data, delay in commands:
            self._run_command(command, data)
            if delay:
                time.sleep(delay)

    def reset(self):
        GPIO.output(self.RESET_PIN, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(self.RESET_PIN, GPIO.LOW)
        time.sleep(0.05)
        GPIO.output(self.RESET_PIN, GPIO.HIGH)
        time.sleep(0.12)

    def _set_window(self, x0, y0, x1, y1):
        self._run_command(0x2A, (0x00, x0, 0x00, x1))
        self._run_command(0x2B, (0x00, y0, 0x00, y1))
        self._run_command(0x2C)

    def display_image(self, pil_image, invert=True):
        image = pil_image.convert("RGB").resize((self.WIDTH_RES, self.HEIGHT_RES), Image.Resampling.NEAREST)
        self._set_window(0, 0, self.WIDTH_RES - 1, self.HEIGHT_RES - 1)
        GPIO.output(self.DC_PIN, GPIO.HIGH)

        buf = bytearray()
        for red, green, blue in image.getdata():
            color = ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)
            buf.append((color >> 8) & 0xFF)
            buf.append(color & 0xFF)

        self._spi.writebytes2(buf)

    INIT_COMMANDS = (
        (0x01, (), 0.15),
        (0x11, (), 0.15),
        (0xB1, (0x01, 0x2C, 0x2D), 0.0),
        (0xB2, (0x01, 0x2C, 0x2D), 0.0),
        (0xB3, (0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D), 0.0),
        (0xB4, (0x07,), 0.0),
        (0xC0, (0xA2, 0x02, 0x84), 0.0),
        (0xC1, (0xC5,), 0.0),
        (0xC2, (0x0A, 0x00), 0.0),
        (0xC3, (0x8A, 0x2A), 0.0),
        (0xC4, (0x8A, 0xEE), 0.0),
        (0xC5, (0x0E,), 0.0),
        (0x36, (0xC8,), 0.0),
        (0x3A, (0x05,), 0.0),
        (0xE0, (0x02, 0x1C, 0x07, 0x12, 0x37, 0x32, 0x29, 0x2D, 0x29, 0x25, 0x2B, 0x39, 0x00, 0x01, 0x03, 0x10), 0.0),
        (0xE1, (0x03, 0x1D, 0x07, 0x06, 0x2E, 0x2C, 0x29, 0x2D, 0x2E, 0x2E, 0x37, 0x3F, 0x00, 0x00, 0x02, 0x10), 0.0),
        (0x13, (), 0.1),
        (0x29, (), 0.1),
    )


class State:
    def __init__(self):
        self._iso_select = 0
        self._mode = None
        self._iso_name = None
        self._pxe_name = None
        self._iso_ls_cache = None
        self.set_mode(MODE_CD)

    def inserted_iso(self):
        if self._mode == MODE_PXE and self._pxe_name is not None:
            return os.path.basename(self._pxe_name)
        if self._iso_name is not None:
            return os.path.basename(self._iso_name)
        return None

    def insert_iso(self):
        self.remove_iso()
        script = os.path.join(APP_DIR, INSERT_SCRIPTS[self._mode])
        iso_list = self.iso_ls()
        if not iso_list:
            LOGGER.error("No ISO available.")
            return
        
        iso_name = iso_list[self.get_iso_select()]
        LOGGER.info("Inserting %s: %s", self._mode, iso_name)
        if self._mode == MODE_PXE:
            self._pxe_name = iso_name
        else:
            self._iso_name = iso_name
        subprocess.check_call((script, iso_name, self._mode))

    def get_iso_select(self):
        return self._iso_select

    def set_iso_select(self, select):
        self._iso_select = select

    def set_iso_select_next(self):
        if self._iso_select == len(self.iso_ls()) - 1:
            return False
        self._iso_select += 1
        return True

    def set_iso_select_prev(self):
        if self._iso_select == 0:
            return False
        self._iso_select -= 1
        return True

    def iso_ls(self, paths=True):
        if self._mode not in BROWSE_MODES:
            raise Exception("invalid mode", self._mode)

        if self._iso_ls_cache and self._iso_ls_cache_type == self._mode:
            if paths:
                return self._iso_ls_cache
            return [os.path.basename(x) for x in self._iso_ls_cache]

        script = os.path.join(APP_DIR, LIST_SCRIPTS[self._mode])
        output = subprocess.check_output((script, FILE_EXTS[self._mode]))
        iso_list = output.decode().split("\0")
        iso_list = sorted(filter(len, iso_list))
        if len(iso_list) < self._iso_select:
            self._iso_select = 0
        self._iso_ls_cache_type = self._mode
        self._iso_ls_cache = iso_list
        if paths:
            return iso_list
        LOGGER.debug("isolist: %r", [os.path.basename(x) for x in self._iso_ls_cache])
        return [os.path.basename(x) for x in self._iso_ls_cache]

    def get_mode(self):
        return self._mode

    def set_mode(self, mode):
        if mode not in ALL_MODES:
            raise Exception("invalid mode", mode)

        self._iso_name = None
        self._pxe_name = None
        script = os.path.join(APP_DIR, "mode.sh")
        try:
            subprocess.check_call([script, mode])
            self._mode = mode
        except subprocess.CalledProcessError:
            LOGGER.exception("mode.sh failed for mode %s", mode)
            # don't raise here to keep the UI running; caller can retry or show error
        self._iso_ls_cache = None

    def toogle_mode(self):
        mode = self.get_mode()
        if mode == MODE_CD:
            self.set_mode(MODE_USB)
        elif mode == MODE_USB:
            self.set_mode(MODE_HDD)
        else:
            self.set_mode(MODE_CD)
        return self.get_mode()

    def remove_iso(self):
        if self._mode not in BROWSE_MODES:
            return

        self._iso_name = None
        self._pxe_name = None
        script = os.path.join(APP_DIR, REMOVE_SCRIPTS[self._mode])
        subprocess.check_call((script,))

    def shutdown_prepare(self):
        self.remove_iso()
        self.set_mode(MODE_SHUTDOWN)

    def shutdown(self):
        script = os.path.join(APP_DIR, "shutdown.sh")
        subprocess.check_call((script,))


class Display:
    def __init__(self):
        disp = ST7735S()

        self._disp = disp
        self._font = ImageFont.truetype(FONT, 13)
        self._font_small = ImageFont.truetype(FONT, 11)
        self._font_hdd = ImageFont.truetype(FONT, 36)


    def refresh(self, state):
        if state.get_mode() not in ALL_MODES:
            raise Exception("invalid mode", state.get_mode())

        mode_text = state.get_mode().upper()
        image = Image.new('RGB', (self._disp.WIDTH_RES, self._disp.HEIGHT_RES), (10, 14, 18))
        draw = ImageDraw.Draw(image)

        if state.get_mode() in (MODE_HDD, MODE_SHUTDOWN):
            draw.rounded_rectangle((8, 16, 120, 92), radius=10, outline=(80, 130, 255), width=2, fill=(18, 24, 32))
            draw.text((18, 34), mode_text, font=self._font_hdd, fill=(240, 244, 255))
            self._disp.display_image(image)
            return

        iso_name = state.inserted_iso()
        if iso_name is None:
            iso_name = ""

        iso_choice = ["", "", ""]
        iso_select = state.get_iso_select()
        iso_ls = state.iso_ls(paths=False)

        if len(iso_ls) == 0:
            iso_choice[1] = "    No image"
        else:
            iso_choice[1] = ">" + iso_ls[iso_select]
            try:
                if iso_select > 0:
                    iso_choice[0] = " " + iso_ls[iso_select - 1]
            except IndexError:
                pass
            try:
                iso_choice[2] = " " + iso_ls[iso_select + 1]
            except IndexError:
                pass

        accent = (77, 170, 255) if state.get_mode() != MODE_PXE else (109, 214, 153)
        draw.rounded_rectangle((6, 6, 122, 24), radius=8, fill=(18, 24, 32), outline=accent, width=2)
        draw.text((10, 8), mode_text + " • " + iso_name, font=self._font_small, fill=(240, 244, 255))
        draw.text((8, 34), iso_choice[0], font=self._font, fill=(170, 180, 190))
        draw.text((8, 54), iso_choice[1], font=self._font, fill=accent)
        draw.text((8, 74), iso_choice[2], font=self._font, fill=(170, 180, 190))
        if state.get_mode() == MODE_PXE:
            draw.text((8, 104), "PXE via eth0", font=self._font_small, fill=(109, 214, 153))
        self._disp.display_image(image)

    def clear(self):
        image = Image.new('1', (self._disp.WIDTH_RES, self._disp.HEIGHT_RES), "WHITE")
        self._disp.display_image(image)


class WVSButtons:
    def __init__(self):
        self._button_last_time = 0
        self._button_last = 0
        for pin in self.PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def wait_on_button(self):
        while True:
            time.sleep(0.01)
            for pin in self.PINS:
                if not GPIO.input(pin):
                    button_time_d = time.time() - self._button_last_time
                    if self._button_last == pin and button_time_d > 0 and button_time_d < 0.1:
                        continue
                    self._button_last_time = time.time()
                    self._button_last = pin
                    try:
                        return self.BUTTON_NAMES[pin]
                    except KeyError:
                        pass

    KEY1 = 21
    KEY2 = 20
    KEY3 = 16
    J_UP = 6
    J_DOWN = 19
    J_LEFT = 5
    J_RIGHT = 26
    J_PRESS = 13
    PINS = (KEY1,
    KEY2,
    KEY3,
    J_UP,
    J_DOWN,
    J_LEFT,
    J_RIGHT,
    J_PRESS,
    )
    BUTTON_NAMES = {
        KEY1 : "mount",
        KEY2 : "umount",
        KEY3 : "mode",
        J_PRESS: "confirm",
        J_UP : "up",
        J_DOWN : "down",
        J_LEFT : "left",
    }


class Main:
    def __init__(self):
        self._state = State()
        self._display = Display()
        self._display.clear()
        self._display.refresh(self._state)
        self._buttons = WVSButtons()

        self._BUTTON_FUNC = {
            "up" : self._button_up,
            "down" : self._button_down,
            "mount" : self._button_mount,
            "umount" : self._button_umount,
            "mode" : self._button_mode,
            "left" : self._button_shutdown,
        }

    def main(self):
        try:
            while True:
                button = self._buttons.wait_on_button()
                try:
                    f = self._BUTTON_FUNC[button]
                except KeyError:
                    pass
                LOGGER.debug("Pressed %s", button)
                f()
                self._display.refresh(self._state)
        finally:
            self._display.clear()

    def _button_up(self):
        self._state.set_iso_select_prev()

    def _button_down(self):
        self._state.set_iso_select_next()

    def _button_mode(self):
        # Open a mode selection menu so the user can choose the desired mode
        self._open_mode_menu()

    def _open_mode_menu(self):
        # Interactive mode selection using the existing display and buttons.
        modes = ALL_MODES
        try:
            idx = modes.index(self._state.get_mode())
        except ValueError:
            idx = 0

        while True:
            # Render menu
            disp = self._display._disp
            image = Image.new('RGB', (disp.WIDTH_RES, disp.HEIGHT_RES), (10, 14, 18))
            draw = ImageDraw.Draw(image)
            draw.text((8, 4), 'Select Mode:', font=self._display._font_small, fill=(240, 244, 255))
            for i, m in enumerate(modes):
                y = 22 + i * 18
                prefix = '>' if i == idx else ' '
                color = (109, 214, 153) if i == idx else (170, 180, 190)
                draw.text((8, y), f"{prefix} {m.upper()}", font=self._display._font, fill=color)

            disp.display_image(image)

            # Wait for a button press to navigate/confirm
            button = self._buttons.wait_on_button()
            if button == 'up':
                idx = (idx - 1) % len(modes)
            elif button == 'down':
                idx = (idx + 1) % len(modes)
            elif button == 'confirm':
                # Confirm selection (J_PRESS)
                chosen = modes[idx]
                try:
                    self._state.set_mode(chosen)
                except Exception:
                    LOGGER.exception('Failed to set mode %s', chosen)

                # Show confirmation / feedback on-screen
                disp = self._display._disp
                msg_img = Image.new('RGB', (disp.WIDTH_RES, disp.HEIGHT_RES), (10, 14, 18))
                draw = ImageDraw.Draw(msg_img)
                # If set_mode succeeded, state.get_mode() will equal chosen
                if self._state.get_mode() == chosen:
                    txt = f"MODE: {chosen.upper()}"
                    color = (109, 214, 153)
                else:
                    txt = f"MODE: {chosen.upper()} (failed)"
                    color = (220, 80, 80)
                draw.text((8, 54), txt, font=self._display._font_hdd, fill=color)
                disp.display_image(msg_img)
                time.sleep(1.6)
                break
            elif button in ('left', 'umount'):
                # Cancel selection
                # brief cancel message
                disp = self._display._disp
                msg_img = Image.new('RGB', (disp.WIDTH_RES, disp.HEIGHT_RES), (10, 14, 18))
                draw = ImageDraw.Draw(msg_img)
                draw.text((8, 54), "CANCELLED", font=self._display._font_hdd, fill=(170,170,170))
                disp.display_image(msg_img)
                time.sleep(0.8)
                break

        # Refresh display after exiting menu
        self._display.refresh(self._state)

    def _button_mount(self):
        self._state.insert_iso()

    def _button_umount(self):
        self._state.remove_iso()

    def _button_shutdown(self):
        self._state.shutdown_prepare()
        self._display.refresh(self._state)
        self._state.shutdown()
        

if __name__ == "__main__":
    Main().main()
