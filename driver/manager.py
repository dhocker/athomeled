#
# AtHomeLED - LED interface driver
# Copyright (C) 2016  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

#
# LED interface driver
#

import configuration
from . import dummy_driver
import logging

logger = logging.getLogger("led")

# Singleton driver instance
_driver = None

def initialize_driver():
    """
    Initializes a singleton driver instance based on the configuration file
    """
    global _driver

    driver = configuration.Configuration.Driver().lower()
    d = None
    if driver == "ws2811" or driver == "neopixels":
        from . import ws2811
        d = ws2811.WS2811()
    elif driver == "dotstar" or driver == "apa102":
        from . import dotstar_driver
        d = dotstar_driver.DotStar()
    elif driver == "ledemulator" or driver == "emulator":
        from .led_emulator import LEDEmulator
        d = LEDEmulator()
    elif driver == "circuitpython_dotstarapa102"  or driver == "cpdotstarapa102":
        from .cp_dotstarapa102 import CPDotStarAPA102Driver
        d = CPDotStarAPA102Driver()
    # The name could be longer...:-)
    elif driver == "adafruit-circuitpython-neopixel" or driver == "adafruit_circuitpython_neopixel":
        from .cp_ws28xx import AdafruitCircuitPythonWS28xxDriver
        d = AdafruitCircuitPythonWS28xxDriver()
    else:
        d = dummy_driver.DummyDriver()

    if d:
        logger.info("%s driver created", d.name)
    else:
        logger.error("%s is not a recognized LED interface type", driver)

    _driver = d

    # Set up driver according to the configuration file
    if d.open(configuration.Configuration.NumberPixels(), order=configuration.Configuration.ColorOrder()):
        logger.info("LED interface driver opened")
    else:
        logger.error("LED interface driver failed to open")
        return False
    return True

def get_driver():
    # Return the current driver instance
    global _driver
    return _driver

def release_driver():
    global _driver
    # One time clean up
    if _driver:
        _driver.close()
        _driver = None
