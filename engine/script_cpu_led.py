#
# AtHomeLED - LED script engine
# Copyright (C) 2016  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#
# Some of the algorithms in this module have been derived from
# Adafruit published software. The original code is covered by
# the following:
#   Copyright (c) 2014, jgarff
#   All rights reserved.
# See https://github.com/jgarff/rpi_ws281x for the original source.
#

#
# Script cpu implementation for LED strips/strings (executes compiled scripts)
#

from . import script_cpu_base
from colorcyclers.sine_color_cycler import SineColorCycler
import time
import random
from collections import deque
import logging

logger = logging.getLogger("led")

class ScriptCPULED(script_cpu_base.ScriptCPUBase):
    def __init__(self, leddev, vm, terminate_event):
        """
        Constructor
        :param leddev: A LED device driver instance (e.g. ws2811 or dotstar)
        :param vm: A script VM instance
        :param terminate_event: A threading event to be tested for termination
        :return: None
        """
        script_cpu_base.ScriptCPUBase.__init__(self, leddev, vm, terminate_event)

        # Valid algorithm statements and their handlers
        valid_stmts = {
            "rainbow": self.rainbow,
            "rainbowcycle": self.rainbowCycle,
            "colorwipe": self.colorwipe_stmt,
            "theaterchase": self.theaterChase,
            "theaterchaserainbow": self.theaterChaseRainbow,
            "scrollpixels": self.scroll_pixels,
            "randompixels": self.random_pixels,
            "brightness": self.brightness,
            "sinewave": self.sinewave,
            "solidcolor": self.solidcolor_stmt,
            "colorfade": self.colorfade_stmt,
        }

        # Add the algorithms to the valid statement dict
        self._valid_stmts.update(valid_stmts)

    #
    # Start of algorithms derived from Adafruit code
    #

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return self._leddev.color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return self._leddev.color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return self._leddev.color(0, pos * 3, 255 - pos * 3)

    def rainbow(self, stmt):
        """Draw rainbow that fades across all pixels at once."""
        wait_ms = float(stmt[1])
        iterations = int(stmt[2])
        for j in range(256 * iterations):
            if self._terminate_event.isSet():
                break
            for i in range(self._leddev.numPixels()):
                self._leddev.setPixelColor(i, self.wheel((i + j) & 255))
            self._leddev.show()
            time.sleep(wait_ms / 1000.0)
        return self._stmt_index + 1

    def rainbowCycle(self, stmt):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        wait_ms = float(stmt[1])
        iterations = int(stmt[2])
        for j in range(256 * iterations):
            if self._terminate_event.isSet():
                break
            for i in range(self._leddev.numPixels()):
                self._leddev.setPixelColor(i, self.wheel(int((i * 256 / self._leddev.numPixels()) + j) & 255))
            self._leddev.show()
            time.sleep(wait_ms / 1000.0)
        return self._stmt_index + 1

    def colorwipe_stmt(self, stmt):
        """
        Run the colorwipe algorithm. Wipe color across display a pixel at a time.
        colorwipe r g b [wait]
        """
        # Wait time is optional
        wait_ms = 50.0
        if len(stmt) >= 5:
            wait_ms = stmt[4]

        color = self._leddev.color(stmt[1], stmt[2], stmt[3])
        for i in range(self._leddev.numPixels()):
            if self._terminate_event.isSet():
                break
            self._leddev.setPixelColor(i, color)
            self._leddev.show()
            time.sleep(wait_ms / 1000.0)
        return self._stmt_index + 1

    def theaterChase(self, stmt):
        """
        Movie theater light style chaser animation.
        theaterchase r g b [wait iterations]
        """
        color = self._leddev.color(stmt[1], stmt[2], stmt[3])
        wait_ms = 50.0
        iterations = 10
        if len(stmt) > 4:
            wait_ms = stmt[4]
            iterations = int(stmt[5])
        for j in range(iterations):
            if self._terminate_event.isSet():
                break
            for q in range(3):
                for i in range(0, self._leddev.numPixels(), 3):
                    self._leddev.setPixelColor(i + q, color)
                    self._leddev.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self._leddev.numPixels(), 3):
                    self._leddev.setPixelColor(i + q, 0)

        return self._stmt_index + 1

    def theaterChaseRainbow(self, stmt):
        """
        Rainbow movie theater light style chaser animation.
        :param stmt:
        :return:
        """
        wait_ms = float(stmt[1])
        for j in range(256):
            if self._terminate_event.isSet():
                break
            for q in range(3):
                for i in range(0, self._leddev.numPixels(), 3):
                    self._leddev.setPixelColor(i + q, self.wheel((i + j) % 255))
                    self._leddev.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self._leddev.numPixels(), 3):
                    self._leddev.setPixelColor(i + q, 0)
        return self._stmt_index + 1

    #
    # End of Adafruit derived code
    #

    def scroll_pixels(self, stmt):
        """
        Runs 5 LEDs at a time along strip
        scrollpixels r g b [wait=20.0] [iterations=1000]
        :param stmt:
        :return:
        """
        color = self._leddev.color(stmt[1], stmt[2], stmt[3])
        wait_ms = float(stmt[4]) / 1000.0
        iterations = int(float(stmt[5]))

        head = 0    # Index of first 'on' pixel
        tail = -5   # Index of last 'off' pixel

        for i in range(iterations):  # Loop for number of iterations
            if self._terminate_event.isSet():
                break

            self._leddev.setPixelColor(head, color)  # Turn on 'head' pixel
            if tail >= 0:
                self._leddev.setPixelColor(tail, 0)  # Turn off 'tail'
                self._leddev.show()  # Refresh strip
            time.sleep(wait_ms)  # Pause for delay time

            head += 1  # Advance head position
            if (head >= self._leddev.numPixels()):  # Off end of strip?
                head = 0  # Reset to start

            tail += 1  # Advance tail position
            if tail >= self._leddev.numPixels():
                tail = 0  # Off end? Reset

        # Not well documented, but this is how you turn
        # off everything
        self._leddev.clear()
        self._leddev.show()
        return self._stmt_index + 1

    @classmethod
    def get_random_int(cls, max_value=100):
        return int(random.random() * max_value)

    def get_random_color(self):
        r = int(ScriptCPULED.get_random_int(max_value=255))
        g = int(ScriptCPULED.get_random_int(max_value=255))
        b = int(ScriptCPULED.get_random_int(max_value=255))
        return self._leddev.color(r, g, b)

    def random_pixels(self, stmt):
        """
        Show random pixels
        randompixels [wait=20.0] [iterations=500]
        :param stmt:
        :return:
        """
        pixels = deque()
        active_size = int(self._leddev.numPixels() / 2)
        color = self._leddev.color(255, 0, 0)
        wait = float(stmt[1]) / 1000.0
        iterations = int(stmt[2])

        for i in range(iterations):
            if self._terminate_event.isSet():
                break
            if len(pixels) >= active_size:
                p = pixels.pop()
                self._leddev.setPixelColor(p, 0)
            p = ScriptCPULED.get_random_int(max_value=self._leddev.numPixels())
            pixels.appendleft(p)
            self._leddev.setPixelColor(p, self.get_random_color())
            self._leddev.show()
            time.sleep(wait)
        self._leddev.clear()
        return self._stmt_index + 1

    def brightness(self, stmt):
        """
        Set brightness level
        brightness n (n is 0-255)
        :param stmt:
        :return:
        """
        self._leddev.setBrightness(stmt[1])
        return self._stmt_index + 1

    def sinewave(self, stmt):
        """
        sinewave [wait=200.0] [iterations=300] [width=127] [center=128]
        :param stmt:
        :return:
        """
        wait_ms = float(stmt[1]) / 1000.0
        iterations = int(float(stmt[2]))
        width = float(stmt[3])
        center = float(stmt[4])
        pixels = self._leddev.numPixels()

        color_gen = SineColorCycler()
        # In binary RGB format. May require reordering.
        color_list = color_gen.create_color_list(center=center, width=width, colors=pixels)

        colorx = 0
        for i in range(iterations):
            if self._terminate_event.isSet():
                break
            for cx in range(pixels):
                modx = (colorx + cx) % len(color_list)
                self._leddev.setPixelColor(cx, color_list[modx])
            self._leddev.show()
            colorx = (colorx + 1) % len(color_list)
            time.sleep(wait_ms)
        self._leddev.clear()

        return self._stmt_index + 1

    def solidcolor_stmt(self, stmt):
        """
        Run the solid color algorithm.
        solidcolor r g b [wait]
        """
        # Wait time is optional
        wait_ms = 1000.0
        if len(stmt) >= 5:
            wait_ms = stmt[4]

        color = self._leddev.color(stmt[1], stmt[2], stmt[3])
        for i in range(self._leddev.numPixels()):
            self._leddev.setPixelColor(i, color)

        self._leddev.show()
        if not self._terminate_event.isSet():
            # Sleep time is in seconds (can be a float)
            # Wait time is in milliseconds.
            time.sleep(wait_ms / 1000.0)
        return self._stmt_index + 1

    def colorfade_stmt(self, stmt):
        """
        Run the color fade algorithm.
        colorfade r g b r g b wait iterations
        """
        # Arguments
        from_color = [stmt[1], stmt[2], stmt[3]]
        to_color = [stmt[4], stmt[5], stmt[6]]
        wait_ms = stmt[7]
        iterations = stmt[8]

        # Calc color delta for each iteration
        delta_rgb = [0.0, 0.0, 0.0]
        for i in range(3):
            delta_rgb[i] = float(to_color[i] - from_color[i]) / float(iterations - 1.0)

        current_color = from_color[:]
        for it in range(int(iterations + 1.0)):
            logger.debug(current_color)
            color = self._leddev.color(current_color[0], current_color[1], current_color[2])
            for i in range(self._leddev.numPixels()):
                self._leddev.setPixelColor(i, color)

            self._leddev.show()

            if not self._terminate_event.isSet():
                # Sleep time is in seconds (can be a float)
                # Wait time is in milliseconds.
                time.sleep(wait_ms / 1000.0)
            else:
                break

            # Generate next color
            for i in range(3):
                current_color[i] = round(float(from_color[i]) + (delta_rgb[i] * float(it)))

        return self._stmt_index + 1
