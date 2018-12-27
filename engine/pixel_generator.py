# coding: utf-8
#
# Pixel generator base class
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


class PixelGenerator:
    """
    Template base class for a pixel generator.
    """
    def __init__(self, num_pixels=0):
        self.num_pixels = num_pixels

    def start(self):
        pass

    def step(self):
        pass

    def pixel(self, n):
        """
        Returns pixel "n"
        :param n: Which pixel to return
        :return: A color 3-tuple (r,g,b)
        """
        return 0, 0, 0

    def stop(self):
        pass

    @staticmethod
    def color(rgb):
        """
        Create a composite integer RGB color value
        :param rgb: 3-tuple (r,g,b)
        :return: Integer color 0xrrggbb
        """
        return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
