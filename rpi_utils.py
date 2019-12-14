#
# Raspberry Pi specific utility functions
# Copyright © 2019  Dave Hocker (email: AtHomeX10@gmail.com)
# Based on a Stack Exchange solution offered by Artur Barseghyan
# See https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
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

import io
import datetime
import time
import ntplib


def is_raspberry_pi(raise_on_errors=False):
    """
    Determines if the current system is Raspberry Pi based.
    If the /proc/cpuinfo file exists it is opened and searched for a
    Model record. If a Model record is found it is tested to see if it
    starts with "Raspberry Pi" in which case a Raspberry Pi is recognized.
    @param raise_on_errors: True to raise exceptions for errors. False to return True/False result.
    @return: True or False.
    """
    try:
        with io.open('/proc/cpuinfo', 'r') as cpuinfo:
            found = False
            # Look for the Model record
            for line in cpuinfo:
                if line.startswith('Model'):
                    found = True
                    label, value = line.strip().split(':', 1)
                    value = value.strip()
                    if value.startswith("Raspberry Pi"):
                        return True
                    elif raise_on_errors:
                        raise ValueError('/proc/cpuinfo Model record does not start with Raspberry Pi')
                    else:
                        return False

            if not found:
                if raise_on_errors:
                    raise ValueError('/proc/cpuinfo did not contain a Model record')
                else:
                    return False
    except IOError:
        if raise_on_errors:
            raise ValueError('Unable to open /proc/cpuinfo.')
        else:
            return False

    return False


def wait_for_clock_sync(ntpserver="time.nist.gov", max_wait=120):
    """
    If this is a Raspberry Pi, wait until the system clock has been
    synced to to current local time.
    @param ntpserver: Where to get current time.
    @param max_wait: Length of time in seconds to wait for clock to sync.
    @return:
    """
    client = ntplib.NTPClient()
    response = client.request(ntpserver, version=3)
    start_time = datetime.datetime.now()
    while time.time() < response.tx_time:
        time.sleep(1.0)
        elapsed = datetime.datetime.now() - start_time
        if elapsed.total_seconds() > max_wait:
            return False
    return True
