# coding: utf-8
#
# AtHomeLED - LED script engine
# Copyright © 2016, 2018  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

#
#
# LED script engine thread
#

import threading
import logging
import app_trace
from app_trace import log_trace
from . import led_engine_script

logger = logging.getLogger("led")


########################################################################
class LEDEngineThread(threading.Thread):
    ########################################################################
    # Constructor
    def __init__(self, thread_id, name, vm):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self._vm = vm
        self.terminate_signal = threading.Event()
        self._script = led_engine_script.LEDEngineScript(self.terminate_signal, vm)

    ########################################################################
    # Called by threading on the new thread
    def run(self):
        logger.info("Engine running script file %s", self._vm.script_file)

        # Initialize LED script. Establish initial state.
        if not self._script.initialize():
            logger.error("Script initialize failed. Thread terminated.")
            self.terminate_signal.set()
            return

        # run the script until termination is signaled
        try:
            self._script.execute()
        except Exception as ex:
            logger.error(str(ex))
            app_trace.log_trace(logger, ex=ex)
        self.terminate_signal.set()

    ########################################################################
    # Terminate the engine thread. Called on the main thread.
    def Terminate(self):
        self.terminate_signal.set()
        # wait for engine thread to exit - could be a while
        logger.info("Waiting for engine thread to stop...this could take a few seconds")
        # This waits until the engine thread has stopped
        self.join()
        logger.info("Engine thread stopped")

    @property
    def is_terminated(self):
        return self.terminate_signal.isSet()
