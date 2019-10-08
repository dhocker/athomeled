# coding: utf-8
#
# Color77 pixel generator algorithm
# Copyright © 2019 Dave Hocker (email: AtHomeX10@gmail.com)
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

from .pixel_generator import PixelGenerator


class Color77PixelGenerator(PixelGenerator):
    """
    Color77 (note the originality of the name -:))
    A set of 7 colors is marched across the string.
    One at a time, every 7 pixels
    iiiiiii...iiiiiii
    aiiiiii...aiiiiii
    aaiiiii...aaiiiii
    ...
    aaaaaaa...aaaaaaa
    baaaaaa...baaaaaa
    """
    def __init__(self, num_pixels=50, color_list=None):
        """
        Constructor
        :param num_pixels:  Number of pixels in string.
        :param color_list: List of 7 colors (3-tuple color (r,g,b))
        """
        super(Color77PixelGenerator, self).__init__(num_pixels=num_pixels)
        # Defaults
        self.num_colors = 7
        if color_list:
            if len(color_list) != 7:
                raise ValueError("Color list must contain 7 items")
            self.color_list = color_list
        else:
            self.color_list = [(0, 0, 0)] * self.num_colors
            # TODO Provide a way to set the colors from a script
            self.color_list[0] = (255, 0, 0)
            self.color_list[1] = (0, 255, 0)
            self.color_list[2] = (0, 0, 255)
            self.color_list[3] = (255, 255, 0)
            self.color_list[4] = (255, 255, 255)
            self.color_list[5] = (0, 255, 255)
            self.color_list[6] = (255, 0, 255)
        self.pixels = [self.color_list[0]] * self.num_pixels
        self.color_index = 0
        self.pixel_index = 0

    def start(self):
        self.color_index = 0
        self.pixel_index = 0

    def step(self):
        for x in range(0, self.num_pixels, self.num_colors):
            if x + self.pixel_index >= self.num_pixels:
                break;
            self.pixels[x + self.pixel_index] = self.color_list[self.color_index]
        self.pixel_index = (self.pixel_index + 1) % self.num_colors
        if self.pixel_index == 0:
            self.color_index = (self.color_index + 1) % self.num_colors

    def pixel(self, n):
        return self.pixels[n]
        # For TK
        # return "#%02x%02x%02x" % self.pixels[n]

    def stop(self):
        pass
