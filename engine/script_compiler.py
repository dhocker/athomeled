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
# Script compiler
#

import datetime
import logging
import re

logger = logging.getLogger("led")

class ScriptCompiler:
    """
    Builds an executable VM
    """
    _scrollpixels_default = 5

    def __init__(self, vm):
        self._last_error = None
        self._vm = vm
        self._stmt = None
        self._file_depth = 0
        self._line_number = [0]
        self._file_path = [""]
        # Index of last encountered do-for-n statement -1 to n
        self._do_for_n = -1
        # Index of last encountered do-for statement -1 to n
        self._do_for = -1
        self._do_at = False
        self._do_until = False
        self._do_forever = False

        # Valid statements and their handlers
        self._valid_stmts = {
            "define": self.define_stmt,
            "eval": self.eval_stmt,
            "import": self.import_stmt,
            "logmessage": self.logmessage_stmt,
            "do-for-n": self.do_for_n_stmt,
            "do-for-n-end": self.do_for_n_end_stmt,
            "do-for": self.do_for_stmt,
            "do-for-end": self.do_for_end_stmt,
            "do-at": self.do_at_stmt,
            "do-at-end": self.do_at_end_stmt,
            "do-until": self.do_until_stmt,
            "do-until-end": self.do_until_end_stmt,
            "do-forever": self.do_forever_stmt,
            "do-forever-end": self.do_forever_end_stmt,
            "pause": self.pause_stmt,
            "reset": self.reset_stmt,
            "color": self.color_stmt,
            "rainbow": self.rainbow_stmt,
            "rainbowcycle": self.rainbowcycle_stmt,
            "colorwipe": self.colorwipe_stmt,
            "theaterchase": self.theaterchase_stmt,
            "theaterchaserainbow": self.theaterchaserainbow_stmt,
            "scrollpixels": self.scrollpixels_stmt,
            "randompixels": self.randompixels_stmt,
            "brightness": self.brightness_stmt,
            "sinewave": self.sinewave_stmt,
            "solidcolor": self.solidcolor_stmt,
            "colorfade": self.colorfade_stmt,
            "twocolor": self.twocolor_stmt,
            "color77": self.color77_stmt,
        }

    @property
    def last_error(self):
        """
        Returns the last logged error message
        :return:
        """
        return self._last_error

    def compile(self, script_file):
        """
        Compile the script defined by the given file handle
        :param script_file:
        :return:
        """
        self._last_error = None
        self._vm.script_file = script_file

        # Open the script file for compiling
        try:
            sf = open(script_file, "r")
            self._file_path[self._file_depth] = script_file
        except Exception as ex:
            self.script_error("Error opening script file {0}".format(script_file))
            logger.error("Error opening script file %s", script_file)
            logger.error(str(ex))
            return False

        valid = True
        stmt = sf.readline()
        while stmt and valid:
            self._stmt = stmt
            self._line_number[self._file_depth] += 1
            # case insensitive tokenization
            tokens = stmt.lower().split()

            # Catch unhandled exceptions
            try:
                valid = self.compile_statement(stmt, tokens)
            except Exception as ex:
                self.script_error(str(ex))
                return False

            stmt = sf.readline()

        # TODO Validate that all script blocks are closed
        if self._do_for >= 0:
            logger.debug("%d do-for statement(s) open at script end", self._do_for + 1)

        sf.close()

        # End of main file
        if self._file_depth == 0:
            logger.debug("%d statements compiled", len(self._vm.stmts))
        return valid

    def compile_statement(self, stmt, tokens):
        """
        Compile a single tokenized statement.
        :param stmt:
        :param tokens:
        :return: True if statement is valid.
        """
        # Comments and empty lines
        if len(tokens) == 0 or tokens[0].startswith("#"):
            return True

        # A statement is valid by default
        valid = True

        # Compile the statement. Here we build a list of valid script statements.
        if tokens[0] in self._valid_stmts:
            # Run the statement compiler if there is one
            if self._valid_stmts[tokens[0]]:
                # Here's where the statement is actually compiled
                compiled_tokens = self._valid_stmts[tokens[0]](tokens)
                # If the statement is valid and executable, add it to the statement list
                if compiled_tokens and len(compiled_tokens):
                    self._vm.stmts.append(compiled_tokens)
                elif compiled_tokens is None:
                    valid = False
        else:
            self.script_error("Unrecognized statement")
            valid = False

        return valid

    def add_color(self, name, color_values):
        """
        Adds a color to the color dictionary.
        """
        # In Python 3, the iterator returned by map can only be used once
        self._vm.colors[name] = []
        self._vm.colors[name].extend(map(int, color_values))

    def add_define(self, name, value):
        """
        Adds an alias with a float value defines dictionary.
        """
        self._vm.defines[name] = float(value)

    def are_valid_colors(self, values):
        """
        Determines if a list of values are valid RGB color values (0-255).
        """
        try:
            int_values = map(int, values)
            for v in int_values:
                if (v >= 0) and (v <= 255):
                    continue
                else:
                    return False
        except Exception as ex:
            return False
        return True

    def is_valid_int(self, t):
        """
        Answers the question: Is t a valid integer?
        :param t:
        :return: True if t is a valid integer.
        """
        if t is None:
            return False
        try:
            v = int(t)
        except:
            return False
        return True

    def is_valid_float(self, t):
        """
        Answers the question: Is t a valid floating point number?
        :param t:
        :return: True if t is a valid floating point number.
        """
        if t is None:
            return False
        try:
            v = float(t)
        except:
            return False
        return True

    def resolve_define(self, token):
        """
        Resolve a token that is subject to substitution by a define.
        :param token:
        :return: The resolved value of the token.
        """
        if token in self._vm.defines:
            return self._vm.defines[token]
        elif self.is_valid_float(token):
            return float(token)
        else:
            return None

    def resolve_eval(self, token):
        """
        Resolve a token that is subject to substitution by an eval.
        :param token:
        :return: The resolved value of the token.
        """
        if token in self._vm.evals:
            return self._vm.evals[token]
        return None

    def resolve_color_arg(self, tokens, index):
        """
        Resolve an RGB color argument. The argument consists of either 1 or 3 tokens.
        A single token is a defined color. Triad tokens form an RGB color.
        color = [defined-color | R G B]
        :param tokens: Command tokens
        :param index: First token index for color
        :return: tuple = (number_tokens_consumed, [r, g, b])
        """
        # Look for defined color first
        if tokens[index] in self._vm.colors:
            return (1, self._vm.colors[tokens[index]])

        # Then, assume r, g, b color values. Each value can be a defined value or literal value.
        r = self.validate_color_value(tokens[index])
        if r is not None:
            g = self.validate_color_value(tokens[index + 1])
            if g is not None:
                b = self.validate_color_value(tokens[index + 2])
                if b is not None:
                    return (3, [r, g, b])
        # One of the rgb values was invalid
        return None

    def validate_color_value(self, v):
        """
        Validate a color value (r, g, b)
        @param v: A named, defined color or a color value that can be converted to int
        @return: A color value or None
        """
        cv = self.resolve_define(v)
        if cv is None:
            self.script_error("Invalid/undefined color argument: {0}".format(v))
            return None
        try:
            cv = int(cv)
        except Exception as ex:
            self.script_error(str(ex))
            return None
        return cv

    def resolve_wait_arg(self, tokens, index, default=None):
        """
        Resolve a wait time argument.
        :param tokens: Command tokens
        :param index: Token index of wait time argument
        :param default: Default wait time if there is no wait argument
        :return:
        """
        if len(tokens) > index:
            # Resolve wait time
            return 1, self.resolve_define(tokens[index])
        # Apply default
        return 0, self.resolve_define(default)

    def resolve_iterations_arg(self, tokens, index, default=1):
        """
        Resolve a iterations argument.
        :param tokens: Command tokens
        :param index: Token index of iterations argument
        :param default: Default iterations if there is no iterations argument
        :return:
        """
        if len(tokens) > index:
            # Resolve iterations
            return 1, self.resolve_define(tokens[index])
        # Apply default
        return 0, self.resolve_define(default)

    def resolve_algorithm_args(self, message_tokens, color=True, wait=None, iterations=None):
        """
        Resolve a statement that is subject to substitution by a color, wait and iterations
        command [color] [wait] [iterations]
        :param message_tokens:
        :param wait: If None, there is no wait argument. If not None, there can be a wait
        argument and the value is the default.
        :param iterations: If None, there is no iterations argument. If not None, there can be an
        iterations argument and the value is the default.
        :return: Effective argument list
        """
        trans_tokens = [message_tokens[0]]
        wait_index = 1 # Initially the first arg after the command
        if color:
            r = self.resolve_color_arg(message_tokens, wait_index)
            # r is a tuple (number-tokens-consumed, [r, g, b])
            if r is None:
                return None
            trans_tokens.extend(r[1])
            wait_index += r[0]

        iterations_index = wait_index
        # Resolve wait
        if wait:
            r = self.resolve_wait_arg(message_tokens, wait_index, default=wait)
            trans_tokens.append(r[1])
            iterations_index += r[0]

        # Resolve iterations
        if iterations:
            r = self.resolve_wait_arg(message_tokens, iterations_index, default=iterations)
            trans_tokens.append(r[1])
            iterations_index += r[0]

        # Handle remaining tokens, if any
        while (len(message_tokens) > (iterations_index)):
            trans_tokens.append(self.resolve_define(message_tokens[iterations_index]))
            iterations_index += 1

        return trans_tokens

    def script_error(self, message):
        """
        Single point error message logging
        :param message:
        :return:
        """
        self._last_error = []
        if self._stmt:
            error_at = "Script error in file {0} at line {1}".format(
                         self._file_path[self._file_depth],
                         self._line_number[self._file_depth])
            logger.error(error_at)
            logger.error(self._stmt)
            self._last_error.append(error_at)
        logger.error(message)
        self._last_error.append(message)

    def logmessage_stmt(self, tokens):
        """
        logmessage message...
        :param tokens: Ignored
        :return: Two token list consisting of command and message string
        """
        stmt_tokens = self._stmt.split(maxsplit=1)
        stmt_tokens[1] = stmt_tokens[1].rstrip()
        return stmt_tokens

    def eval_stmt(self, tokens):
        """
        eval name valid-python-definition-expression
        :param tokens:
        :return:
        """
        if len(tokens) < 3:
            self.script_error("Not enough tokens")
            return None

        # Use regex to parse statement
        regex = r"^\s*(\S+)\s+(\S+)\s+(\S.*$)"
        rp = re.compile(regex)
        # The match should produce 3 groups where
        # 1 = eval
        # 2 = name
        # 3 = eval-expression
        rm = rp.match(self._stmt)
        if not rm:
            self.script_error("Invalid eval statement: " + self._stmt)
            return None

        try:
            v = eval(rm.group(3), self._vm.evals, self._vm.colors)
            self._vm.evals[rm.group(2)] = v
        except Exception as ex:
            self.script_error(str(ex))
            return None

        return []

    def define_stmt(self, tokens):
        """
        define name v where v can be any value, int or float
        :param tokens:
        :return:
        """
        if len(tokens) < 3:
            self.script_error("Not enough tokens")
            return None
        if self.is_valid_float(tokens[2]):
            self.add_define(tokens[1], tokens[2])
        else:
            self.script_error("A defined value must be a valid float")
            return None
        return []

    def import_stmt(self, tokens):
        """
        Import a source file directly in-line
        :param tokens: filepath
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Missing file path")
            return None

        # Push the imported file onto the file stack
        self._file_depth += 1
        self._file_path.append(tokens[1])
        self._line_number.append(0)

        # This is a recursive call to compile the imported file
        # TODO Do we need a recursion limit here?
        self.compile(tokens[1])

        # Pop the file stack
        self._file_depth -= 1
        self._line_number.pop()
        self._file_path.pop()

        # The cpu will ignore this statement
        return tokens

    def do_for_n_stmt(self, tokens):
        """
        Execute a script block n times
        :param tokens:
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Missing statement argument")
            return None

        # Translate/validate iterations
        try:
            iterations = int(self.resolve_define(tokens[1]))
        except Exception as ex:
            self.script_error("Invalid iterations")
            return None

        tokens[1] = iterations
        self._do_for_n += 1
        return tokens

    def do_for_n_end_stmt(self, tokens):
        """
        Marks the end/foot of a block of code headed by a Do-For-N statement.
        :param tokens:
        :return:
        """
        if self._do_for_n < 0:
            self.script_error("No matching Do-For-N is open")
            return None
        self._do_for_n -= 1
        return tokens

    def do_for_stmt(self, tokens):
        """
        Execute a script block for a given period of time
        :param tokens: Duration (HH:MM)
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Missing statement argument")
            return None

        # Translate/validate duration
        try:
            duration_struct = datetime.datetime.strptime(tokens[1], "%H:%M:%S")
        except Exception as ex:
            self.script_error("Invalid duration")
            return None

        tokens[1] = duration_struct
        self._do_for += 1
        return tokens

    def do_for_end_stmt(self, tokens):
        """
        Marks the end/foot of a block of code headed by a Do-For statement.
        :param tokens:
        :return:
        """
        if self._do_for < 0:
            self.script_error("No matching Do-For is open")
            return None
        self._do_for -= 1
        return tokens

    def do_at_stmt(self, tokens):
        """
        Executes a block of script when a given time-of-day arrives.
        :param tokens: tokens[1] is the time in HH:MM format (24 hour clock).
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Missing statement arguments")
            return None
        if self._do_at:
            self.script_error("Only one Do-At statement is allowed")
            return None

        # Translate/validate start time
        try:
            start_time_struct = datetime.datetime.strptime(tokens[1], "%H:%M:%S")
        except Exception as ex:
            self.script_error("Invalid start time")
            return None

        tokens[1] = start_time_struct
        self._do_at = True
        return tokens

    def do_at_end_stmt(self, tokens):
        """
        Marks the end/foot of a block of code headed by a Do-At statement.
        :param tokens:
        :return:
        """
        if not self._do_at:
            self.script_error("No matching Do-At is open")
            return None
        return tokens

    def do_until_stmt(self, tokens):
        """
        Executes a block of script until a given time-of-day arrives.
        :param tokens: tokens[1] is the time in HH:MM format (24 hour clock).
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Missing statement arguments")
            return None
        if self._do_until:
            self.script_error("Only one Do-Until statement is allowed")
            return None

        # Translate/validate until time
        try:
            start_time = datetime.datetime.strptime(tokens[1], "%H:%M:%S")
        except Exception as ex:
            self.script_error("Invalid until time")
            return None

        tokens[1] = start_time
        self._do_until = True
        return tokens

    def do_until_end_stmt(self, tokens):
        """
        Marks the end/foot of a block of code headed by a Do-Until statement.
        :param tokens:
        :return:
        """
        if not self._do_until:
            self.script_error("No matching Do-Until is open")
            return None
        return tokens

    def do_forever_stmt(self, tokens):
        """
        Marks the beginning of a do-forever block.
        """
        if self._do_forever:
            self.script_error("Only one Do-Forever statement is allowed")
            return None
        self._do_forever = True
        return tokens

    def do_forever_end_stmt(self, tokens):
        """
        Marks the end/foot of a block of code headed by a Do-Forever statement.
        :param tokens:
        :return:
        """
        if not self._do_forever:
            self.script_error("No matching Do-Forever is open")
            return None
        return tokens

    def pause_stmt(self, tokens):
        """
        pause hh:mm:ss
        Pauses script execution for a specified amount of time.
        """
        if len(tokens) < 2:
            self.script_error("Missing statement arguments")
            return None

        # Translate/validate pause time
        try:
            pause_struct = datetime.datetime.strptime(tokens[1], "%H:%M:%S")
        except Exception as ex:
            self.script_error("Invalid pause time")
            return None

        tokens[1] = pause_struct
        return tokens

    def reset_stmt(self, tokens):
        """
        Sends zeroes to all LED channels.
        """
        return tokens

    def color_stmt(self, tokens):
        """
        color name [r g b | [0x]rrggbb] where r, g, b values are 0-255 and rr, gg, bb are hex 0-FF
        :param tokens:
        :return:
        """
        if len(tokens) == 3:
            # color name [0x]rrggbb
            rgb = tokens[2]
            if not (rgb.startswith("0x") or rgb.startswith("0X")):
                rgb = "0x" + rgb
            intrgb = int(rgb, base=16)
            cv = [0, 0, 0]
            for i in range(2, -1, -1):
                cv[i] = intrgb & 0xFF
                intrgb = intrgb >> 8
            self.add_color(tokens[1], cv)
        elif len(tokens) == 5:
            # color name r g b
            if self.are_valid_colors(tokens[2:]):
                self.add_color(tokens[1], tokens[2:])
            else:
                self.script_error("Color values must be 0-255")
                return None
        else:
            self.script_error("Wrong number of tokens.")
            return None

        return []

    def colorwipe_stmt(self, tokens):
        """
        colorwipe r g b [wait=50.0]
        :param tokens:
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Not enough tokens")
            return None
        trans_tokens = self.resolve_algorithm_args(tokens, wait=50.0)
        return trans_tokens

    def solidcolor_stmt(self, tokens):
        """
        solidcolor r g b [wait=1000.0]
        The wait value is how long the color is displayed.
        :param tokens:
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Not enough tokens")
            return None
        trans_tokens = self.resolve_algorithm_args(tokens, wait=1000.0)
        return trans_tokens

    def colorfade_stmt(self, tokens):
        """
        colorfade r g b r g b [wait=1000.0] [iterations=1000]
        The wait value is how long the color is displayed.
        :param tokens:
        :return:
        """
        if len(tokens) < 3:
            self.script_error("Not enough tokens")
            return None

        trans_tokens = [tokens[0]]
        token_index = 1 # Initially the first arg after the command

        # From color
        r = self.resolve_color_arg(tokens, token_index)
        # r is a tuple (number-tokens-consumed, [r, g, b])
        if r is None:
            return None
        trans_tokens.extend(r[1])
        token_index += r[0]

        # To color
        r = self.resolve_color_arg(tokens, token_index)
        # r is a tuple (number-tokens-consumed, [r, g, b])
        if r is None:
            return None
        trans_tokens.extend(r[1])
        token_index += r[0]

        # Resolve wait
        r = self.resolve_wait_arg(tokens, token_index, default=1000.0)
        trans_tokens.append(r[1])
        token_index += r[0]

        # Resolve iterations
        r = self.resolve_wait_arg(tokens, token_index, default=1000)
        trans_tokens.append(r[1])
        token_index += r[0]

        return trans_tokens

    def rainbow_stmt(self, tokens):
        """
        rainbow [wait=20.0 iterations=1]
        :param tokens:
        :return:
        """
        if len(tokens) < 1:
            self.script_error("Not enough tokens")
            return None
        trans_tokens = self.resolve_algorithm_args(tokens, color=False, wait=20.0, iterations=1)
        return trans_tokens

    def rainbowcycle_stmt(self, tokens):
        """
        rainbow [wait=20.0 iterations=5]
        :param tokens:
        :return:
        """
        if len(tokens) < 1:
            self.script_error("Not enough tokens")
            return None
        trans_tokens = self.resolve_algorithm_args(tokens, color=False, wait=20.0, iterations=5)
        return trans_tokens

    def theaterchase_stmt(self, tokens):
        """
        theaterchase r g b [wait=50.0 iterations=10]
        :param tokens:
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Not enough tokens")
            return None
        trans_tokens = self.resolve_algorithm_args(tokens, color=True, wait=50.0, iterations=10)
        return trans_tokens

    def theaterchaserainbow_stmt(self, tokens):
        """
        theaterchaserainbow [wait=50.0]
        :param tokens:
        :return:
        """
        if len(tokens) < 1:
            self.script_error("Not enough tokens")
            return None
        if len(tokens) > 1:
            tokens[1] = int(self.resolve_define(tokens[1]))
        else:
            tokens.append(50.0)
        return tokens

    def sinewave_stmt(self, tokens):
        """
        sinewave [wait=200.0] [iterations=300] [width=127] [center=128]
        :param tokens:
        :return:
        """
        trans_tokens = self.resolve_algorithm_args(tokens, color=False, wait=200.0, iterations=300)
        # Tokens: [0] = sinewave [1] = wait [2] = iterations [3] = width [4] = center

        # Cover defaults for width and center
        if len(trans_tokens) < 4:
            # width is defaulted
            trans_tokens.append(127)
        if len(trans_tokens) < 5:
            # center is defaulted
            trans_tokens.append(128)

        return trans_tokens

    def scrollpixels_stmt(self, tokens):
        """
        scrollpixels r g b [wait=20.0 iterations=1000 n=5]
        :param tokens:
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Not enough tokens")
            return None
        trans_tokens = self.resolve_algorithm_args(tokens, color=True, wait=20.0, iterations=1000)
        # If the number of pixels is omitted, default to the class value for backward compatibility
        if len(trans_tokens) < 7:
            trans_tokens.append(self._scrollpixels_default)
        return trans_tokens

    def randompixels_stmt(self, tokens):
        """
        randompixels [wait=20.0 iterations=500]
        :param tokens:
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Not enough tokens")
            return None
        trans_tokens = self.resolve_algorithm_args(tokens, color=False, wait=20.0, iterations=500)
        return trans_tokens

    def brightness_stmt(self, tokens):
        """
        brightness n (0 <= n <= 255)
        :param tokens:
        :return:
        """
        if len(tokens) < 2:
            self.script_error("Not enough tokens")
            return None
        brightness = self.resolve_define(tokens[1])
        if not self.is_valid_int(brightness):
            self.script_error("Invalid brightness value")
            return None
        tokens[1] = int(brightness)
        if tokens[1] < 0 or tokens[1] > 255:
            self.script_error("Invalid brightness value")
            return None
        return tokens

    def twocolor_stmt(self, tokens):
        """
        twocolor r g b r g b [wait=500.0] [iterations=100]
        The wait value is the time between iterations
        :param tokens:
        :return:
        """
        if len(tokens) < 3:
            self.script_error("Not enough tokens")
            return None

        trans_tokens = [tokens[0]]
        token_index = 1 # Initially the first arg after the command

        # color 1
        r = self.resolve_color_arg(tokens, token_index)
        # r is a tuple (number-tokens-consumed, [r, g, b])
        if r is None:
            return None
        trans_tokens.extend(r[1])
        token_index += r[0]

        # color 2
        r = self.resolve_color_arg(tokens, token_index)
        # r is a tuple (number-tokens-consumed, [r, g, b])
        if r is None:
            return None
        trans_tokens.extend(r[1])
        token_index += r[0]

        # Resolve wait
        r = self.resolve_wait_arg(tokens, token_index, default=500.0)
        trans_tokens.append(r[1])
        token_index += r[0]

        # Resolve iterations
        r = self.resolve_wait_arg(tokens, token_index, default=100)
        trans_tokens.append(r[1])
        token_index += r[0]

        return trans_tokens

    def color77_stmt(self, tokens):
        """
        color77 [color-list=color77-default [wait=200.0] [iterations=100]]
        :param tokens:
        :return:
        """
        trans_tokens = [tokens[0]]
        token_index = 1 # Initially the first arg after the command

        # Default statement check
        if len(tokens) == 1:
            trans_tokens.append(self._vm.evals["color77-default"])
        else:
            # The first arg MUST be a color-list
            cl = self.resolve_eval(tokens[1])
            if cl:
                trans_tokens.append(cl)
            else:
                self.script_error("Undefined color-list eval: " + tokens[1])
                return None
        token_index += 1

        # Resolve wait
        r = self.resolve_wait_arg(tokens, token_index, default=200.0)
        trans_tokens.append(r[1])
        token_index += r[0]

        # Resolve iterations
        r = self.resolve_wait_arg(tokens, token_index, default=100)
        trans_tokens.append(r[1])
        token_index += r[0]

        return trans_tokens
