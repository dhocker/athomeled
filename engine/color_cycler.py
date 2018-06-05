# coding: utf-8
#
# ColorCycler - sine wave based RGB color generator
# Copyright © 2018 Dave Hocker (email: AtHomeX10@gmail.com)
# Copyright © 2010 Matt Troutman (email: )
#
# Derived from Java code originally written by Matt Troutman
# Converted to Python 2.7/3.6. Will work with either.
# Reference: https://krazydad.com/tutorials/makecolors.php
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

import math

class ColorCycler:
    """
    RGB color sequence generator using a sine wave based algorithm.
    See https://krazydad.com/tutorials/makecolors.php
    for an in depth discussion.

    We are basically sliding red/green/blue values through a range using a sine wave and
    can alter the center line and amplitude to adjust the range of colors calculated.

    The sequence of colors is generated into a Python list (which
    acts like a cached set of generated colors).

    Example 1 (for binary RGB colors):
        cc = ColorCycler()
        color_list = cc.create_color_list()
        for i in range(len(color_list)):
            color = color_list[i]

    Example 2 (for Tkinter colors):
        cc = ColorCycler()
        tkcolor_list = Colorcycler.to_tkcolor_list(cc.create_color_list())
        for i in range(len(tkcolor_list)):
            tkcolor = tkcolor_list[i]
    """
    def __init__(self, red_freq=None, green_freq=None, blue_freq=None,
                 red_phase=0.0, green_phase=2.0, blue_phase=4.0,
                 center=128, width=127, cycles=32):
        """
        Creates a color generator for a given set of parameters. The defaults produce
        a set of colors with a full color spectrum. For pastel colors, try
        center=200 and width=55.
        :param red_freq: 0 < f < 1.0 determines the frequency of change for red
        :param green_freq: 0 < f < 1.0 determines the frequency of change for green
        :param blue_freq: 0 < f < 1.0 determines the frequency of change for blue
        :param red_phase: For red, the phase angle in radians. Since a sine wave
        repeats after 2π radians (6.28), a phase angle of more than 2π does
        not make much sense.
        :param green_phase: For green, the phase angle in radians
        :param blue_phase: For blue, the phase angle in radians
        :param center: 0-128 Essentially the bias value (0 <= center <= 128)
        :param width: 1-127. Becasue an RGB component value is in the range
        0-255, the value of center + width should be in the range 0-255.
        :param cycles: The number of colors to be generated for a sequence.
        Essentially, this is the size of the list that will be generated.
        """
        # The default for freq is to set it to a value that will produce
        # one sine wave.
        self.__initialize(red_freq, green_freq, blue_freq,
                 red_phase, green_phase, blue_phase,
                 center, width, cycles)

    def __initialize(self, red_freq, green_freq, blue_freq,
                     red_phase, green_phase, blue_phase,
                     center, width, colors):
        """
        Instance set up
        :param red_freq:
        :param green_freq:
        :param blue_freq:
        :param red_phase:
        :param green_phase:
        :param blue_phase:
        :param center:
        :param width:
        :param colors:
        :return:
        """
        if red_freq:
            self.red_freq = red_freq
        else:
            self.red_freq = (math.pi * 2.0) / colors
        if green_freq:
            self.green_freq = green_freq
        else:
            self.green_freq = (math.pi * 2.0) / colors
        if blue_freq:
            self.blue_freq = blue_freq
        else:
            self.blue_freq = (math.pi * 2.0) / colors

        self.red_phase = float(red_phase)
        self.green_phase = float(green_phase)
        self.blue_phase = float(blue_phase)

        self.center = center
        self.width = width

        self.colors = colors

        self.__calculated_colors = None

    def create_color_list(self, red_freq=None, green_freq=None, blue_freq=None,
                          red_phase=0.0, green_phase=2.0, blue_phase=4.0,
                          center=128, width=127, colors=32):
        """
        Creates a color list for a given set of parameters. The defaults produce
        a set of colors with a full color spectrum. For pastel colors, try
        center=200 and width=55. The list of colors can to used in a
        variety of ways.
        :param freq1: 0 < f < 1.0 determines the frequency of change for red
        :param freq2: 0 < f < 1.0 determines the frequency of change for green
        :param freq3: 0 < f < 1.0 determines the frequency of change for blue
        :param phase1: For red, the phase angle in radians. Since a sine wave
        repeats after 2π radians (6.28), a phase angle of more than 2π does
        not make much sense.
        :param phase2: For green, the phase angle in radians
        :param phase3: For blue, the phase angle in radians
        :param center: 0-128 Essentially the bias value (0 <= center <= 128)
        :param width: 1-127. Becasue an RGB component value is in the range
        0-255, the value of center + width should be in the range 0-255.
        :param colors: The number of colors to be generated for a sequence.
        Essentially, this is the size of the list that will be generated.
        """
        # The default for freq is to set it to a value that will produce
        # one sine wave.
        self.__initialize(red_freq, green_freq, blue_freq,
                          red_phase, green_phase, blue_phase,
                          center, width, colors)

        # Create and return the list of colors
        self.__precalc_colors()
        return self.__calculated_colors

    def __precalc_colors(self):
        """
        Generates a list of colors based on the instance initialization properties.
        :return:
        """
        self.__calculated_colors = []
        for i in range(self.colors):
            self.__calculated_colors.append(self.__calculate_next_color(i))

    @staticmethod
    def to_tkcolor_list(color_list):
        """
        Convert a binary color list to a TK color format (#rrggbb) list.
        :param color_list:
        :return:
        """
        tkcolor_list = []
        for i in range(len(color_list)):
            # Produces a 3-tuple RGB value
            rgb = ColorCycler.decode_rgb(color_list[i])
            tkcolor_list.append("#%02x%02x%02x" % rgb)
        return tkcolor_list

    def __calculate_next_color(self, cycle):
        red = ColorCycler.__calc_color_component(cycle, self.red_freq, self.red_phase, self.width, self.center)
        green = ColorCycler.__calc_color_component(cycle, self.green_freq, self.green_phase, self.width, self.center)
        blue = ColorCycler.__calc_color_component(cycle, self.blue_freq, self.blue_phase, self.width, self.center)
        # print(cycle, red, green, blue)

        return 0xff000000 | (red << 16) | (green << 8) | (blue << 0);

    @staticmethod
    def __calc_color_component(cycle, freq, phase, width, center):
        """
        The algorithm for calculating a color component.
        :param cycle: The color cycle being calculated.
        :param freq: A positive value such that (cycle * freq) is in the
        range of 0 to 2π.
        :param phase: Offset value for this color. Ideally, in the range
        of 0 to 2π.
        :param width: Because an RGB component value is in the range
        0-255, the value of center + width should be in the range 0-255.
        :param center: Essentially the bias value (0 <= center <= 128).
        The sine function oscillates around this value.
        :return:
        """
        return int((math.sin((freq * cycle) + phase) * width) + center) % 256

    def print_colors(self):
        """
        For debugging and analysis.
        :return: None
        """
        for i in range(self.colors):
            color = self.__calculated_colors[i]
            rgb = ColorCycler.decode_rgb(color)
            print(i, rgb)

    @staticmethod
    def decode_rgb(color):
        """
        Decodes a single binary RGB value into a tuple.
        :param color:
        :return: a tuple of (r, g, b)
        """
        red = (color >> 16) & 0xff
        green = (color >> 8) & 0xff
        blue = color & 0xff
        return red, green, blue

"""
Test code
"""
if __name__ == "__main__":
    print ("Defaults colors=32, red_freq=0.3, green_freq=0.3, blue_freq=0.3 =============================")
    color_generator = ColorCycler()
    color_generator.create_color_list()
    color_generator.print_colors()
