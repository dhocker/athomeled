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
# Script virtual machine
#

class ScriptVM():
    def __init__(self, script_file):
        # TODO Some/most/all of these should be made properties

        # Underlying script file
        self.script_file = script_file

        # Script statements are a list of token lists
        self.stmts = []

        # Color definitions
        self.colors = {}

        # Defines
        self.defines = {}

        # Evaluated values
        self.evals = {}
        # The default color list for the color77 alg
        self.evals["color77-default"] = [
            (255,0,0),
            (0,255,0),
            (0,0,255),
            (255,255,0),
            (255,0,255),
            (0,255,255),
            (255,0,255)
        ]

        # Main statement index
        self.main_index = -1
