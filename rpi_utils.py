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
import time
import logging
import ntplib

logger = logging.getLogger("led")

def is_raspberry_pi(raise_on_errors=False):
    """
    Determines if the current system is Raspberry Pi based.
    If the /proc/cpuinfo file exists it is opened and searched for a
    Hardware record. If a Hardware record is found it is tested to see if it
    is an RPi CPU in which case a Raspberry Pi is recognized.
    Ref: https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
    @param raise_on_errors: True to raise exceptions for errors. False to return True/False result.
    @return: True or False.
    """
    rpi_hardware_list = [
        'BCM2708',
        'BCM2709',
        'BCM2835',
        'BCM2836'
    ]
    try:
        with io.open('/proc/cpuinfo', 'r') as cpuinfo:
            found = False
            # Look for the Hardware record
            for line in cpuinfo:
                if line.startswith('Hardware'):
                    found = True
                    label, value = line.strip().split(':', 1)
                    value = value.strip().upper()
                    if value in rpi_hardware_list:
                        return True
                    elif raise_on_errors:
                        raise ValueError('/proc/cpuinfo Hardware record is not a Raspberry Pi')
                    else:
                        return False

            if not found:
                if raise_on_errors:
                    raise ValueError('/proc/cpuinfo did not contain a Hardware record')
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
    logger.debug("Wait for clock sync called")

    # Manually track elapsed time to avoid using system clock
    elapsed = 0.0

    # Run the clock sync procedure a fixed number of times before giving up
    for retry in range(5):
        try:
            # Get the local time from the designated NTP server
            client = ntplib.NTPClient()
            logger.debug("Calling NTPServer %s", ntpserver)
            response = client.request(ntpserver)
            t = time.time()
            logger.debug("Starting system clock = %f", t)
            logger.debug("NTPServer time = %f", response.tx_time)
            max_wait = float(max_wait)
            # Loop until system time catches up to NTP time or max wait time is exhausted
            while t < response.tx_time:
                if elapsed > max_wait:
                    return False
                time.sleep(1.0)
                elapsed += 1.0
                t = time.time()
                logger.debug("Current system clock = %f, delta = %f", t, response.tx_time - t)
            return True
        except Exception as ex:
            # During boot up, several different network errors can occur.
            # Basically, we keep trying until the network is up.
            logger.error("Exception occurred trying to sync system clock")
            logger.error(str(ex))
            logger.debug("Waiting to retry")
            time.sleep(5.0)
            elapsed += 5.0

    return False
