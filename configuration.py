#
# AtHomeLED - LED string script executor
# Copyright (C) 2016  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

#
# Server configuration
#
# The at_home_dmx.conf file holds the configuration data in JSON format.
# Currently, it looks like this:
#
# {
#   "Configuration":
#   {
#     "Driver": "ws2811"
#     "ScriptFile": "/path/to/scriptfile.dmx",
#     "LogFile": "/path/to/filename.log",
#     "LogConsole": "True",
#     "LogLevel": "DEBUG"
#   }
# }
#
# The JSON parser is quite finicky about strings being quoted as shown above.
#
# This class behaves like a singleton class. There is only one instance of the configuration.
# There is no need to create an instance of this class, as everything about it is static.
#

import os
import json
import logging

logger = logging.getLogger("led")


########################################################################
class Configuration():
    ActiveConfig = None
    DEFAULT_PORT = 5000

    ######################################################################
    def __init__(self):
        Configuration.LoadConfiguration()
        pass

    ######################################################################
    # Load the configuration file
    @classmethod
    def LoadConfiguration(cls):
        # Try to open the conf file. If there isn't one, we give up.
        try:
            cfg_path = Configuration.GetConfigurationFilePath()
            print("Opening configuration file {0}".format(cfg_path))
            cfg = open(cfg_path, 'r')
        except Exception as ex:
            print("Unable to open {0}".format(cfg_path))
            print(str(ex))
            return

        # Read the entire contents of the conf file
        cfg_json = cfg.read()
        cfg.close()
        # print cfg_json

        # Try to parse the conf file into a Python structure
        try:
            config = json.loads(cfg_json)
            # The interesting part of the configuration is in the "Configuration" section.
            cls.ActiveConfig = config["Configuration"]
        except Exception as ex:
            print("Unable to parse configuration file as JSON")
            print(str(ex))
            return

        # print str(Configuration.ActiveConfig)
        return

    @classmethod
    def dump_configuration(cls):
        logger.info("Active configuration file")
        logger.info(json.dumps(cls.ActiveConfig, indent=4))

    ######################################################################
    @classmethod
    def IsLinux(cls):
        """
        Returns True if the OS is of Linux type (Debian, Ubuntu, etc.)
        """
        return os.name == "posix"

    ######################################################################
    @classmethod
    def IsWindows(cls):
        """
        Returns True if the OS is a Windows type (Windows 7, etc.)
        """
        return os.name == "nt"

    ######################################################################
    @classmethod
    def get_config_var(cls, var_name, default_value=None):
        try:
            return cls.ActiveConfig[var_name]
        except Exception as ex:
            logger.error("Unable to find configuration variable {0}".format(var_name))
            logger.error(str(ex))
            pass
        return default_value

    ######################################################################
    @classmethod
    def Port(cls):
        p = cls.get_config_var("Port")
        if p:
            try:
                port = int(p)
                if port > 65535:
                    raise ValueError
            except:
                port = cls.DEFAULT_PORT
                logger.info("Invalid TCP port value. Using default TCP port {}".format(cls.DEFAULT_PORT))
        else:
            # Default
            port = cls.DEFAULT_PORT
            logger.info("Using default TCP port {}".format(cls.DEFAULT_PORT))
        return port

    ######################################################################
    @classmethod
    def Driver(cls):
        return cls.get_config_var("Driver")

    ######################################################################
    @classmethod
    def NumberPixels(cls):
        return int(cls.get_config_var("NumberPixels"))

    ######################################################################
    @classmethod
    def ColorOrder(cls):
        order = cls.get_config_var("ColorOrder")
        if not order:
            return 'rgb'
        return order

    ######################################################################
    @classmethod
    def Scriptfile(cls):
        return cls.get_config_var("ScriptFile")

    ######################################################################
    @classmethod
    def ScriptFileDirectory(cls):
        return cls.get_config_var("ScriptFileDirectory")

    ######################################################################
    @classmethod
    def Logconsole(cls):
        return cls.get_config_var("LogConsole").lower() == "true"

    ######################################################################
    @classmethod
    def Logfile(cls):
        return cls.get_config_var("LogFile")

    ######################################################################
    @classmethod
    def LogLevel(cls):
        return cls.get_config_var("LogLevel")

    ######################################################################
    @classmethod
    def Invert(cls):
        return cls.get_config_var("Invert").lower() == "true"

    ######################################################################
    @classmethod
    def DataPin(cls):
        datapin = cls.get_config_var("DataPin")
        if not datapin:
            # The default data pin is GPIO 18
            return 18
        return datapin

    ######################################################################
    @classmethod
    def AutoRun(cls):
        return cls.get_config_var("AutoRun", default_value="")

    ######################################################################
    @classmethod
    def Timeout(cls):
        return float(cls.get_config_var("Timeout", default_value=10.0))

    ######################################################################
    @classmethod
    def WaitForClockSync(cls):
        return int(cls.get_config_var("WaitForClockSync", default_value=60))

    ######################################################################
    @classmethod
    def NTPServer(cls):
        return str(cls.get_config_var("NTPServer", default_value="time.nist.gov"))

    ######################################################################
    @classmethod
    def GetConfigurationFilePath(cls):
        """
        Returns the full path to the configuration file.
        The intention is to keep all LED controller configurations in the
        conf folder. Each configuration file is named with the hostname where
        it is intended to be used. However, we allow a configuration file in the
        home directory (the local configuration file) to override the hostname
        configuration file. This allows the local configuration file to be used for
        testing. If a controller's conf file is not found in
        the root conf folder, we'll look in the conf folder for a hostname
        specific configuration file. If there is no hostname configuration file
        we'll look for the default configuration file.

        In summary, the order of precedence for the configuration file is:
        at_home_led.conf
        conf/at_home_led_hostname.conf
        conf/at_home_led_default.conf

        :return: full path to the configuration file.
        """

        # First, look for the local configuration file (in the home directory)
        file_name = "at_home_led.conf"
        if os.path.exists(file_name):
            return file_name

        # Next, look for a host specific conf file
        hostname = os.uname()[1]
        hostname = hostname.split('.')[0]  # only the first token of the hostname
        file_name = f"conf/at_home_led_{hostname}.conf"
        if os.path.exists(file_name):
            return file_name

        # Finally, look for the default conf file
        file_name = "conf/at_home_led_default.conf"
        if os.path.exists(file_name):
            return file_name

        # Does not exist, but is the last resort
        return "at_home_led.conf"
