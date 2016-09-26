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

import ws2811
import configuration
import dummy_driver
import logging

logger = logging.getLogger("led")

def get_driver():
    """
    Returns a driver instance for the interface type specified
    in the configuration file.
    :return:
    """
    driver = configuration.Configuration.Driver().lower()
    d = None
    if driver == "ws2811" or driver == "neopixels":
        d = ws2811.WS2811()
    elif driver == "dotstar" or driver == "apa102":
        d = dummy_driver.DummyDriver()

    if d:
        logger.info("%s driver created", driver)
    else:
        logger.error("%s is not a recognized LED interface type", driver)

    return d