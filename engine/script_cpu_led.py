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

import script_cpu_base
import time
import datetime
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
            "brightness": self.brightness,
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
            for i in range(self._leddev.numPixels()):
                self._leddev.setPixelColor(i, self.wheel(((i * 256 / self._leddev.numPixels()) + j) & 255))
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
        wait_ms = int(stmt[1])
        for j in range(256):
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

    def brightness(self, stmt):
        """
        Set brightness level
        brightness n (n is 0-255)
        :param stmt:
        :return:
        """
        self._leddev.setBrightness(stmt[1])
        return self._stmt_index + 1
