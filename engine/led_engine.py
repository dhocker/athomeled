#
# AtHomeDMX - DMX script engine
# Copyright (C) 2016  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

#
# Engine class encapsulating script engine thread
#

from . import led_engine_thread
from . import script_vm
from . import script_compiler
import app_trace
import logging
import sys

logger = logging.getLogger("led")


# This class should be used as a singleton
class LEDEngine:
    def __init__(self):
        self.engine_thread = None
        self._vm = None
        self._compiler = None
        self._last_error = None

    @property
    def last_error(self):
        """
        Returns the last logged error message
        :return:
        """
        return self._last_error

    def compile(self, script_file):
        # Create a VM instance
        self._vm = script_vm.ScriptVM(script_file)

        # Compile the script (pass 1) of the current (main) thread
        self._compiler = script_compiler.ScriptCompiler(self._vm)
        rc = self._compiler.compile(script_file)
        if not rc:
            self._last_error = self._compiler.last_error
            return rc

        logger.info("Successfully compiled script %s", script_file)
        return rc

    def execute(self):
        """
        Execute the compiled script on a separate thread
        :return: True if the script started. Otherwise, False.
        """
        #
        try:
            self.engine_thread = led_engine_thread.LEDEngineThread(1, "LEDEngineThread", self._vm)
            self.engine_thread.start()
        except Exception as e:
            logger.error("Unhandled exception starting LED engine")
            logger.error(e)
            logger.error(sys.exc_info()[0])
            app_trace.log_trace(logger, ex=e)
            return False
        return True

    def Stop(self):
        """
        Stops the script engine thread
        :return:
        """
        if self.engine_thread is not None:
            self.engine_thread.Terminate()

    def Running(self):
        """
        Returns the running status of the thread
        :return: Returns True if the thread is running
        """
        return self.engine_thread and (not self.engine_thread.is_terminated)
