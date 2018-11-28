#
# AtHomeLED - LED engine client
# Copyright (C) 2016  Dave Hocker (email: AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (the LICENSE file).  If not, see <http://www.gnu.org/licenses/>.
#

import app_logger
import configuration
import engine.led_engine
import os
import glob
import json
import socket
from collections import OrderedDict

logger = app_logger.getAppLogger()

class LEDCommandHandler:
    """
    Handles commands sent by a network client.
    The commands provide the means to control LED engine.

    The protocol is simple.
    The client sends a command line terminated by a newline (\n).
    The server executes the command a returns a JSON formatted response.
    The response is one line, terminated with a newline.
    The JSON payload is a dictionary. The following properties appear in all responses.
        command: the command for which the response was generated
        result: OK or ERROR
    The remainder of the response is command dependent. Here some additional properties
    that may appear
        state: RUNNING, STOPPED or CLOSED
        message: Message text usually explaining an error
        scriptfile: The name of the currently running script file

    Example
    Client sends:
        scriptfiles\n
    Server responds:
        {"command": "scriptfiles", "result": "OK", "scriptfiles": ["definitions.led", "test-end.led", "test.led"]}\n

    Client sends:
        bad-command\n
    Server responds:
        {"command": "bad-command", "result": "ERROR", "messages": ["Unrecognized command"]}\n

    The easiest way to experiment with the client is to use telnet. Simply open
    a connection and type commands.
        telnet server host

    Recognized commands
        status
        scriptfiles
        start <script-name>
        stop
        quit
        close
    """

    # Protocol constants
    OK_RESPONSE = "OK"
    ERROR_RESPONSE = "ERROR"
    END_RESPONSE_DELIMITER = "\n"
    STATUS_RUNNING = "RUNNING"
    STATUS_STOPPED = "STOPPED"
    STATUS_CLOSED = "CLOSED"

    # Singleton instance of LED engine
    # TODO Access to this variable should be under lock control is multiple, concurrent sockets are supported
    led_engine = engine.led_engine.LEDEngine()
    led_script = None

    class Response:
        def __init__(self, command, result=None, state=None):
            self._response = OrderedDict()
            self._response["command"] = command
            self._response["hostname"] = socket.gethostname()
            if result:
                self._response["result"] = result
            if state:
                self._response["state"] = state

        def set_result(self, result):
            self._response["result"] = result

        def set_state(self, state):
            self._response["state"] = state

        def set_value(self, key, value):
            self._response[key] = value

        def is_closed(self):
            if "state" in self._response:
                return self._response["state"] == LEDCommandHandler.STATUS_CLOSED
            return False

        def __str__(self):
            return json.dumps(self._response) + LEDCommandHandler.END_RESPONSE_DELIMITER

    def __init__(self):
        """
        Constructor for an instance of LEDClient
        """
        # Valid commands and their handlers
        self._valid_commands = {
            "scriptfiles": self.get_script_files,
            "start": self.start_script,
            "stop": self.stop_script,
            "status": self.get_status,
            "quit": self.quit_session,
            "close": self.close_connection,
            "configuration": self.get_configuration,
        }

    def execute_command(self, port, raw_command):
        """
        Execute a client command/request.
        :param port: The port number receiving the request. It can be used
        to qualify or descriminate the request. The idea is to be able to
        map a port number to a device.
        :param raw_command: The command line sent by the client.
        :return:
        """
        logger.debug("Control command: %s", raw_command)
        tokens = raw_command.lower().split()
        if (len(tokens) >= 1) and (tokens[0] in self._valid_commands):
            if self._valid_commands[tokens[0]]:
                response = self._valid_commands[tokens[0]](tokens, raw_command)
            else:
                r = LEDCommandHandler.Response(tokens[0], result=LEDCommandHandler.ERROR_RESPONSE)
                r.set_value("messages", "Command not implemented")
                response = r
        else:
            r = LEDCommandHandler.Response(tokens[0], result=LEDCommandHandler.ERROR_RESPONSE)
            r.set_value("messages", "Unrecognized command")
            response = r

        # Return the command generated response with the end of response
        # delimiter tacked on.
        logger.debug("Control command response: %s", str(response))
        return response

    def get_configuration(self, tokens, command):
        """
        Return current server configuration.
        :param tokens:
        :param command:
        :return:
        """
        r = LEDCommandHandler.Response(tokens[0], result=LEDCommandHandler.OK_RESPONSE)

        r.set_value("port", configuration.Configuration.Port())
        r.set_value("driver", configuration.Configuration.Driver())
        r.set_value("scriptfiledirectory", configuration.Configuration.ScriptFileDirectory())
        r.set_value("logfile", configuration.Configuration.Logfile())
        r.set_value("logconsole", configuration.Configuration.Logconsole())
        r.set_value("loglevel", configuration.Configuration.LogLevel())

        return r

    def get_status(self, tokens, command):
        """
        Return current status of LED script engine.
        :param tokens:
        :param command:
        :return:
        """
        r = LEDCommandHandler.Response(tokens[0], result=LEDCommandHandler.OK_RESPONSE)

        if LEDCommandHandler.led_engine.Running():
            r.set_state(LEDCommandHandler.STATUS_RUNNING)
            r.set_value("scriptfile", LEDCommandHandler.led_script)
        else:
            r.set_state(LEDCommandHandler.STATUS_STOPPED)

        return r

    def get_script_files(self, tokens, command):
        """
        Return a list of all of the *.dmx files in the script file directory.
        :param tokens:
        :param command:
        :return: List of file names without path.
        """
        r = LEDCommandHandler.Response(tokens[0], result=LEDCommandHandler.OK_RESPONSE)

        search_for = configuration.Configuration.ScriptFileDirectory() + "/*.led"
        files = glob.glob(search_for)
        names = []
        for f in files:
            names.append(os.path.split(f)[1])

        r.set_value("scriptfiles", names)
        return r

    def close_connection(self, tokens, command):
        """
        Close the current connection/session. Note that the LED Engine
        state is not changed. If it is running, it stays running.
        :param tokens:
        :param command:
        :return:
        """
        r = LEDCommandHandler.Response(tokens[0], result=LEDCommandHandler.OK_RESPONSE, state=LEDCommandHandler.STATUS_CLOSED)
        return r

    def quit_session(self, tokens, command):
        """
        Close the current connection/session. Note that the LED Engine
        is stopped if it is running.
        :param tokens:
        :param command:
        :return:
        """
        # If necessary, stop the LED Engine
        LEDCommandHandler.stop_engine()

        r = LEDCommandHandler.Response(tokens[0], result=LEDCommandHandler.OK_RESPONSE, state=LEDCommandHandler.STATUS_CLOSED)
        return r

    def start_script(self, tokens, command):
        """
        Start the LED engine running a script file
        :param tokens: tokens[1] is the script file name
        :param command:
        :return:
        """

        r = LEDCommandHandler.Response(tokens[0], result=LEDCommandHandler.OK_RESPONSE)

        # At least one command argument is required - the script name
        if len(tokens) < 2:
            r.set_result(LEDCommandHandler.ERROR_RESPONSE)
            r.set_value("messages", ["Missing script file name argument"])
            return r

        # Full path to script file
        # TODO Concurrency issue
        r.set_value("scriptfile", tokens[1])
        full_path = "{0}/{1}".format(configuration.Configuration.ScriptFileDirectory(), tokens[1])
        if not os.path.exists(full_path):
            r.set_result(LEDCommandHandler.ERROR_RESPONSE)
            r.set_value("messages", ["Script file does not exist"])
            return r

        # Stop a running script
        LEDCommandHandler.stop_engine()

        # Compile the script
        if LEDCommandHandler.led_engine.compile(full_path):
            LEDCommandHandler.led_script = tokens[1]
        else:
            r.set_result(LEDCommandHandler.ERROR_RESPONSE)
            r.set_state(LEDCommandHandler.STATUS_STOPPED)
            r.set_value("messages", LEDCommandHandler.led_engine.last_error)
            return r
        # Execute the compiled script
        # The engine will run until terminated by stop
        # Note than the LED engine runs the script on its own thread
        if not LEDCommandHandler.led_engine.execute():
            r.set_result(LEDCommandHandler.ERROR_RESPONSE)
            r.set_state(LEDCommandHandler.STATUS_STOPPED)
            r.set_value("messages", ["Script failed to start"])
            return r

        r.set_state(LEDCommandHandler.STATUS_RUNNING)

        return r

    def stop_script(self, tokens, command):
        """
        Stop any running script. If no script is running,
        the command does nothing (this is not considered an error).
        :param tokens:
        :param command:
        :return:
        """
        r = LEDCommandHandler.Response(tokens[0], result=LEDCommandHandler.OK_RESPONSE)

        LEDCommandHandler.stop_engine()

        r.set_state(LEDCommandHandler.STATUS_STOPPED)
        return r

    @classmethod
    def stop_engine(cls):
        """
        If the script engine is running, stop it.
        :return: True if the engine was running and stopped.
        Otherwise, False.
        """
        if cls.led_engine.Running():
            cls.led_engine.Stop()
            cls.led_script = None
            return True
        return False
