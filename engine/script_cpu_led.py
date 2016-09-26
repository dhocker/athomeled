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
            "colorwipe": self.colorwipe_stmt,
        }

        # Add the algorithms to the valid statement dict
        self._valid_stmts.update(valid_stmts)

    def colorwipe_stmt(self, stmt):
        """
        Run the colorwipe algorithm. Wipe color across display a pixel at a time.
        """
        # Make this a command operand
        wait_ms = 50.0
        color = self._leddev.color(stmt[1], stmt[2], stmt[3])
        for i in range(self._leddev.numPixels()):
            if self._terminate_event.isSet():
                break
            self._leddev.setPixelColor(i, color)
            self._leddev.show()
            time.sleep(wait_ms / 1000.0)
        return self._stmt_index + 1
