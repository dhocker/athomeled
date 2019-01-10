# AtHomeLED - LED Light Strip Server
Copyright © 2016, 2018 by Dave Hocker

## Overview
The AtHomeLED server is designed to run simple LED strip light shows on
a Raspberry Pi. 
The original motive for the AtHomeLED server was for
something to run a holiday lighting program on a strip of C9 LED lights.

The server can be controlled locally or remotely via a TCP based communication interface
([the remote control interface](#remote-control)).
The interface is suited to command-line control via telnet or a front-end client application
that uses the interface as an API.

A show is constructed as a script using a relatively simple
scripting language ([Script Engine](#script-engine)). Scripts are stored in script
files in the [ScriptFileDirectory](#configuration) on the AtHomeLED host.

Using the remote control interface you can:

* view a list of available script files
* start a script file
* stop the currently running script file
* view the status of the AtHomeLED server

There are several different kinds of LED strips depending on which 
controller string is used. AtHomeLED supports the following.

* WS2811 based LED strings
* APA102 (SPI protocol) based LED strips (e.g. Adafruit DotStars)

How to wire these to a Raspberry Pi is out of the scope of this
document, but examples of how to wire these strings can be found in
the [references](#references).

AtHomeLED comes with a driver for the both of these LED strings.
If you want to
use another LED string type you will need to write your own driver. 
The AtHomeLED/driver/dummy_driver.py
file provides a template for implementing a driver. The DUMMY driver can 
be used as a mock device. This is a good solution for testing.

## License

The AtHomeLED server is licensed under the GNU General Public License v3 as published 
by the Free Software Foundation, Inc..
See the LICENSE file for the full text of the license.

## Source Code

The full source is maintained on [GitHub](https://www.github.com/dhocker/AtHomeLED).

AtHomeLED was developed using PyCharm CE. PyCharm CE is highly recommended. However, if you
want to make changes, a good text editor of your choice is all that is really required.

## Execution Environment

AtHomeLED was originally written in Python 2.7 but has been converted to Python 3. 
Currently, it will run on either Python 2.7+ or Python 3.5+. However, only Python 3 
will be supported in the future.

A suitable execution environment would use 
virtualenv and virtualenvwrapper to create a working virtual environment. 

AtHomeLED has been tested on Raspbian Stretch.

## Dependencies
The requirements.txt file can be used with pip to create the required virtual environment with 
some but not all dependencies. This includes:

* [rpi-ws281x](https://pypi.org/project/rpi_ws281x/)
* [athomesocketserver](https://www.github.com/dhocker/athomesocketserver)
* [ColorCycler](https://github.com/dhocker/colorcycler.git)
* [AtHomeUtils](https://github.com/dhocker/athomeutils.git)

The following dependencies must be individually and manually installed from source.

* [Adafruit_DotStar_Pi](https://github.com/adafruit/Adafruit_DotStar_Pi)

## Configuration <a id="configuration"></a>

AtHomeLED is setup using the JSON formatted **at_home_led.conf** file. The easiest way to create a configuration
file is to copy at_home_led.example.conf to at_home_led.conf and edit as required.

|Key           | Use         |
|------------- |-------------|
| Driver | WS2811, NeoPixels, APA102 or DotStar. Case insensitive. |
| NumberPixels | Number of LEDs in the string or strip. |
| ColorOrder | The order of colors as sent to the LED strip. Only applies to APA102/DotStars. Default and recommended value is rgb. |
| Invert | Inverts data signal. For WS2811 only. Use when no level shifter is employed. |
| DataPin | For WS2811 driver, specifies the output data pin. This is almost always GPIO 18 as it must support PWM. |
| ScriptFileDirectory | Full path to location where script files are stored. Script files should be named with a .led extension. |
| LogFile | Full path and name of log file. |
| LogConsole | True or False. If True logging output will be routed to the log file and the console. |
| LogLevel | Debug, Info, Warn, or Error. Case insensitive. |
| Port | The TCP port to be used for remote control. The default is 5000. |
| Timeout | How long a remote control connection is held open when there is no activity. |
| AutoRun | Script file to be started when AtHomeDMX starts. The default is none. |
| WaitForClockSync | In seconds, the amount of up time required to assure time-of-day clock sync. The default is 30. |

## Device Driver Configuration
### WS2811/NeoPixels
* **ColorOrder** - Color order on the WS2811 chips is fixed and this value
is ignored.
* **Invert** - If an inverting level shifter is used, set this to True.
For a non-inverting level shifter (e.g 74AHCT125) set this to False.
The default is False.
* **DataPin** - The GPIO pin where data is emitted. On the Raspberry Pi 
only GPIO 18 has PWM capability so this value is almost always 18.

Example at_home_led.conf:

    {
      "Configuration":
      {
        "Driver": "ws2811",
        "NumberPixels": "50",
        "DataPin": "18",
        "Invert": "false",
        "ScriptFileDirectory": "/home/pi/rpi/athomeled",
        "Port": "5000",
        "LogFile": "/home/pi/rpi/athomeled/at_home_led.log",
        "LogConsole": "True",
        "LogLevel": "DEBUG"
      }
    }

### APA102/DotStar
* **ColorOrder** - Some DotStar strips require a non-RGB color order. The
default value is RGB.
* **DataPin** - Not used. The APA102/DotStar driver uses the stock SPI
pin configuration where GPIO 10 is Clock and GPIO 11 is Data.

Example at_home_led.conf:

    {
      "Configuration":
      {
        "Driver": "dotstar",
        "NumberPixels": "30",
        "ColorOrder": "rgb",
        "ScriptFileDirectory": "/home/pi/rpi/athomeled",
        "Port": "5000",
        "LogFile": "/home/pi/rpi/athomeled/at_home_led.log",
        "LogConsole": "True",
        "LogLevel": "DEBUG"
      }
    }

## Script Engine <a id="script-engine"></a>
The script engine executes the contents of a script file. It is a two phase interpreter. The first phase is a
compile phase where statements are validated and definitions are captured. The second phase is an 
execution phase. Because of the two phase design, definitional statements are
compiled so that the last definition wins. That is, if a name is defined multiple times, the last
definition wins.

## Script File
A script file contains any number of statements. 

* Each line is a statement.
* Leading and trailing blanks are ignored.
* Blank lines are ignored.
* Lines that begin with a # are ignored.
* Everything is case insensitive.

## Statements

### Syntax
A statement consists of a number of white space delimited tokens. Except for the # character, there
are no special rules for characters. The single quote, double quote and all other special characters are treated
just like alpha-numeric characters.

The first token of a statement is the statement identifier (a.k.a. an opcode or command).

    statement [argument-1 [argument-2...argument-n]]

All arguments are positional. In the documentation an argument in square brackets
is optional. For example, [wait=20.0] identifies a positional parameter
for a wait time with a default value of 20.0. The "wait=" part of
the parameter description is not a part of the actual argument. It
is there merely to identify the purpose of the argument.

    statement argument-1 25.0

This statement has two arguments where the second argument is a
wait time of 25.0. In the documentation, it would be described as:

    statement argument-1 [wait=20.0]

indicating that the default wait time is 20.0.

### Names
Several statements involve the definition of a name (a constant). The only rule for a name is that it
cannot contain blanks. A name can contain any alpha-numeric or special character.
Single or double quotes have no special significance. 

### Comment
Any line whose first non-blank character is a # is a comment. Comments are ignored.

    # This is a comment

Comments are not recognized as such when placed at the end of an otherwise valid statement.

### Define
A define statement defines a general use numeric value. 
A valid define value is an integer or floating point number. For example, 10.0 or 10.

    define name value

### Color
Use the color statement to define an RGB color.

    color name red green blue

### Eval
Use the eval statement to define a named value where the value is a Python expression.
Any expression that is valid on the right side of a Python assignment statement is valid.
The eval statement is useful for things like defining a list of colors.

    eval name python-expression

For example

    eval color-list [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(255,255,255)]

defines the color-list named value as a list of 7 color 3-tuples.

### Import
The import statement includes another file into the script file. This works like a C/C++ include or a Python import
statement. The content of the imported file is inserted into the script in line. There is no duplicate import
checking. If you import the same file multiple times, its contents will be inserted multiple times.

    import filename

### Do-At
The Do-At statement is designed for running a lighting program on a daily basis. This is the kind of thing that
you would do for a holiday lighting program. The Do-At statement allows you to specify a time of day when the
program is to run. The lighting program is the script block between the Do-At statement
and its corresponding Do-At-End statement. There can only be one Do-At statement in a script.
This is a simple limitation to avoid overly complicating the script language.

    do-at hh:mm:ss
        # script block statements
    do-at-end
    
The argument is the time of day (24 hour clock) when the program is to run. When the Do-At statement executes, 
it puts the script into a wait state where it waits for the time of day to arrive.

Example

    do-at 18:00:00
        # script block statements
    do-at-end

This example waits until 18:00:00 (6:00pm) at which time it runs the script block.

Note: If you need to break a waiting Do-At statement, use the stop command on the remote control interface.

### Do-At-End
The Do-At-End statement serves as the foot of the Do-At loop or the end of the Do-At block.
When script execution reaches the Do-At-End statement, all LED channels are reset and 
execution returns to the corresponding Do-At statement.

    do-at-end

### Do-For-N
The Do-For-N statement executes a script block a given number of times. The script block is the
set of statements between the Do-For-N statement and its corresponding Do-For-N-End statement.
This is the equivalent of the common programming statement "for i in range(N)" or 
"for i = 0 to N".
    
    do-for-n 24
        # script block statements
    do-for-n-end
    
The argument is the number of times the loop is to execute (24 in the above example).

Do-For-N statements **may be nested**.

### Do-For-N-End
The Do-For-N-End statement is the foot of the Do-For-N loop.

    do-for-n-end

### Do-For
The Do-For statement executes a script block for a given period of time. The script block is the
set of statements between the Do-For statement and its corresponding Do-For-End statement.
    
    do-for hh:mm:ss
        # script block statements
    do-for-end
    
The argument is a duration in hours, minutes and seconds.

Do-For statements **may be nested**.

### Do-For-End
The Do-For-End statement is the foot of the Do-For loop. When execution reaches the Do-For-End statement,
the elapsed time since the entry into the Do-For loop is evaluated. If the elapsed time is less than
the Do-For duration, execution returns to the next statement after the Do-For. If the elapsed time
is greater than or equal to the Do-For duration, execution continues with the statement after
the Do-For-End. Note that with this behavior, the time spent in the loop may actually be longer than
the Do-For duration. This is completely dependent on how long it takes to execute the script block.

    do-for-end

### Do-forever
The do-forever statement is the script equivalent of the C/C++ "while true" statement. The block of script
following the do-forever statement is executed until script engine execution is terminated.
There can only be one Do-Forever statement in a script.

    do-forever
        # Block of statements
    do-forever-end

Note: Script engine execution can be terminiated in two ways:
* the remote control interface stop command
* killing the AtHomeLED server process (e.g. ctrl-C or kill command or service stop command)

### Do-forever-end
The do-forever-end statement is the foot of the do-forever loop. When the statement executes, it sets the next
statement to the statement following the corresponding do-forever statement.

    do-forever-end

### Pause
Pause suspends the execution of the script for the specified amount of time.

    pause hh:mm:ss
    
### Reset
Reset sets all pixels to off (black).

    reset

### Derived Algorithms
Some of the algorithms in this program have been derived from
Adafruit published software. The original, unmodified code is covered by
the following:

    Copyright (c) 2014, jgarff
    All rights reserved.

See [https://github.com/jgarff/rpi_ws281x](https://github.com/jgarff/rpi_ws281x) for the original source.

#### Colorwipe
Fills the LED strip from first to last pixel. 
The wait (time in milliseconds) value determines
how fast the wipe occurs.

    colorwipe {r g b | color} [wait=50.0]
    
#### Theaterchase
Movie theater light style chaser animation.
Fills the LED strip from first to last pixel. 
The wait (time in milliseconds) value determines
how fast the chase proceeds. The iterations value determines 
how many times the algorithm is executed.

    theaterchase {r g b | color} [wait=50.0] [iterations=10]
    
#### Rainbow
Draw a rainbow that fades across all pixels at once. 
The wait (time in milliseconds) value determines
how fast the animation proceeds. The iterations value determines 
how many times the algorithm is executed.

    rainbow {r g b | color} [wait=20.0] [iterations=1]
    
#### Rainbowcycle
Draws a rainbow that uniformly distributes itself across all pixels.
The wait (time in milliseconds) value determines
how fast the animation proceeds. The iterations value determines 
how many times the algorithm is executed.

    rainboxcycle {r g b | color} [wait=20.0] [iterations=5]
    
#### Theaterchaserainbow
This is a rainbow movie theater light style chaser animation.
The wait (time in milliseconds) value determines
how fast the chase proceeds.

    theaterchaserainbow [wait=50.0]
    
### Original Algorithms
These algorithms were written by the author.

#### SolidColor
Fills all pixels with a specified single color.

    solidcolor { r g b | color} [wait=1000.0]

The wait time (in millisedonds) is how long the color is displayed.

#### TwoColor
Alternates pixels between two colors. Assume two colors c1 and c2 and a string of LEDs
with 4 pixels. On the first pass, the pixels will be c1 c2 c1 c2. On the sceond pass,
the pixels will be c2 c1 c2 c1. Even pixels will alternate from c1 to c2 while odd
pixels will alternate from c2 to c1.

    twocolor { r g b | color} { r g b | color} [wait=500.0] [iterations=100]

The wait time (in milliseconds) is how long to pause between iterations.
The iterations are how many times to repeat.

#### ColorFade
Morphs all pixels from one color to another color over a given period of time.

    colorfade { r g b | color} { r g b | color} [wait=1000.0] [iterations=1000]

The first color is the "from" color and the second color is the "to" color. 
The wait time is how long to pause between iterations.
The iterations are how many steps to use to complete the fade.

#### SineWave
Generates sequential colors using a sine wave based algorithm. See the
article
[Making annoying rainbows in javascript](https://krazydad.com/tutorials/makecolors.php)
for an in depth discussion behind the algorithm.

    sinewave [wait=200.0] [iterations=300] [width=127] [center=128]

The wait (time in milliseconds) value determines
how fast the sine wave moves. The iterations value determines
how many times the algorithm is executed. A sine wave cycle depends
on the number pixels/LEDs in the string. For example, if the string has
30 pixels, a full sine wave cycle will occur every 30 iterations.
For the math inclined, the full cycle covers 2π radians and the
algorithm moves (2π / number-of-pixels) radians every iteration.

The center value determines the value that is equivalent to the zero
crossing of the sine wave. Since RGB values are 0-255, a value of 128
sets the middle of the range as the crossing point. In other words,
the values of R, G and B will oscillate around this value.

The width value establish how far away from the center the center
the sine wave can oscillate. Essentially, it establishses the
range of RGB values.

Since the maximum RGB component value is 255, the value of
width + center must be less than or equal to 255.

#### Color77
Implements a 7 x 7 algorithm using 7 colors across groups of 7 pixels.
For the set of colors abcdefg, the sequence looks like this.

    iiiiiii...iiiiiii
    aiiiiii...aiiiiii
    aaiiiii...aaiiiii
    ...
    aaaaaaa...aaaaaaa
    baaaaaa...baaaaaa
    bbaaaaa...bbaaaaa
    ...
    bbbbbbb...bbbbbbb
    ...
    ggggggg...ggggggg

The command is:

    color77 [wait=200.0] [iterations=100]

The wait time controls how fast the algorithm runs and the iterations
determines how long the command runs.

Currently, the set of 7 colors is fixed. However, in the future there will be
some way to set the colors.

#### Scrollpixels
Starting from the first pixel, scrolls a group of 5 pixels across the strip. 
The wait (time in milliseconds) value determines
how fast the animation proceeds. The iterations value determines 
how many times the algorithm is executed.

    scrollpixels {r g b | color} [wait=20.0] [iterations=1000]

#### Randompixels
Sets a randomly chosen pixel to a randomly generated color.
Up to half of the pixels on the strip can be lighted at any time.
The wait (time in milliseconds) value determines
how fast the animation proceeds. The iterations value determines 
how many times the algorithm is executed.

    randompixels [wait=20.0] [iterations=500]
    
### Brightness
Sets the brightness of all pixels in the strip. The brightness level
essentially implements a scaling of the color values.

    brightness n
    
Where n is in the range 0 <= n <= 255. The effective brightness is
approximately n / 255. Thus, a brightness of 128 is about 50% bright and a
brightness of 64 is about 25% bright.

### Script File EOF
When end-of-file is reached, the script terminates. As part of script termination, all LED channels
are reset.

### Script Example
The following script runs one hour every day at 6:30pm local time.

    #
    # LED test script
    #

    # Colors
    color orange 255 83 14
    color red 255 0 0
    
    # Time definitions
    define default-fade-time 3.0
    define default-step-time 5.0
    define periodtime 0.2
    
    # Set the global step time
    step-period periodtime
    
    do-at 18:30:00   
        # This one hour loop contains three steps with a step-time of 5.0 seconds.
        # That means one pass through the main loop will take 3 * 5.0 = 15.0 seconds.
        # Note that indention is not required, but it does improve readability.
        do-for 01:00:00
            # Run LED algorithms
        do-for-end
    do-at-end

## Remote Control Interface (API) <a id="remote-control"></a>
The remote control interface uses a simple TCP socket connection to implement a client-server
arrangement. The client sends simple commands and the server responds with JSON formatted responses.
A basic telnet app can be used as the client or a UI application can be written.

A connection to the AtHomeLED server can usually be opened like this.

    telnet hostname 5000

## Control Commands
Each command produces a JSON formatted response. There are several response
properties that are common to most command responses.

|Property      | Description |
|------------- |-------------|
| command | The command that produced this response. |
| result | OK or ERROR. |
| messages | If the result == ERROR this property (a list) will describe the error. |

Commands that produce an error will include an error message list in the response.


### LED Engine Status
The status command returns the current status of the LED Engine.

**Command:** status

**Response:** {"command": "status", "result": "OK", "state": "STOPPED"}

**Response:** {"command": "status", "result": "OK", "state": "RUNNING", "scriptfile": "test.led"}

### LED Server Configuration
The configuration command returns the current configuration settings for the LED server.

**Command:** configuration

**Response:** {"command": "configuration", "result": "OK", "port": 5000, "interface": "dummy", 
"scriptfiledirectory": "/home/user1/AtHomeLED/scriptfiles", "logfile": "at_home_led.log", "logconsole": true, "loglevel": "DEBUG"}
 
### List Script Files
The scriptfiles command returns a list of all of the available script files.

**Command:** scriptfiles

**Response:** {"command": "scriptfiles", "result": "OK", "scriptfiles": ["definitions.led", "test-end.led", "test.led"]}

### Start Script Execution
The start command is used to start execution of a specified script. Any running script is stopped before the
new script is started.

**Command:** start script-file-name

**Response:** {"command": "start", "result": "OK", "scriptfile": "test.led", "state": "RUNNING"}

**Error Response:** {"command": "start", "result": "ERROR", "messages": ["Script file does not exist"], "scriptfile": "x.led"}

Note that the messages property is a list. Script compilation errors will typically produce a multi-line message.

### Stop Script Execution
The stop command terminates execution of the current script. If no script is running,
the command is ignored.

**Command:** stop

**Response:** {"command": "stop", "result": "OK", "state": "STOPPED"}

### Close Socket Connection
The close command closes the TCP socket while leaving the LED Engine in its current
state. If the LED Engine is running it will continue running. Use the close command
when you want to start a script and leave it running.

**Command:** close

**Response:** {"command": "close", "result": "OK", "state": "CLOSED"}

### Quit
The quit command stops the LED Engine and closes the TCP socket. Essentially, it is a stop command
followed by a close command.

**Command:** quit

**Response:** {"command": "quit", "result": "OK", "state": "CLOSED"}

### Telnet Session Example
The following console output shows an example of how the remote control interface works.

    telnet localhost 5000
    Trying ::1...
    telnet: connect to address ::1: Connection refused
    Trying 127.0.0.1...
    Connected to localhost.
    Escape character is '^]'.
    scriptfiles
    {"command": "scriptfiles", "result": "OK", "scriptfiles": ["definitions.led", "test-end.led", "test.led"]}
    status
    {"command": "status", "result": "OK", "state": "STOPPED"}
    start test.led
    {"command": "start", "result": "OK", "scriptfile": "test.led", "state": "RUNNING"}
    stop
    {"command": "stop", "result": "OK", "state": "STOPPED"}
    close
    {"command": "close", "result": "OK", "state": "CLOSED"}
    Connection closed by foreign host.

## Running AtHomeLED Server as a Daemon
On Raspbian Jessie you can easily run the AtHomeLED
server as a daemon. The athomeledD.sh shell script will help you do just that.

Assuming Raspbian:

    sudo cp athomeledD.sh /etc/init.d
    sudo update-rc.d athomeledD.sh defaults
    sudo service athomeledD.sh start

## References <a id="references"></a>
* [Adafruit DotStars](https://learn.adafruit.com/adafruit-dotstar-leds/dotstar-matrices?view=all)
* [Adafruit NeoPixels](https://learn.adafruit.com/neopixels-on-raspberry-pi)
* [NeoPixel/WS2811 Wiring including level shifter](https://learn.adafruit.com/neopixels-on-raspberry-pi/wiring)
* [74AHCT125 level shifter](https://www.adafruit.com/product/1787)
* [Making annoying rainbows in javascript](https://krazydad.com/tutorials/makecolors.php).
