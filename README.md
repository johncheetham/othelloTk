# othelloTk
Edax gui to play Othello against the Edax engine.

John Cheetham August 2015

Written in python3/Tkinter and licensed under the GPL v3+
(see the file named LICENSE).

It was tested with edax 4.3.2 and Python 3.4.3 on CentOS7 64 bit.

Requirements
------------
Python 3, Tkinter, Edax.

Installation
------------
 1. Download the edax othello engine from http://abulmo.perso.neuf.fr
    This has a prebuilt binary for Linux 64 bit.

 2. Start othelloTk with 'python othelloTk'

 3. Do Engine/Set Engine Path and set the engine path to the edax
    executable.
    This is called lEdax-x64 in the edax bin folder (if you are using
    Linux 64 bit).

 4. Start the game by left clicking to place a black stone.

Usage
-----
You play black, computer plays white.
Click on a square to place a black stone.
If you find there are no legal moves then you can pass by right
clicking anywhere on the board.

You can set some edax engine options using an edax.ini file.
Copy this file into the ~/.othelloTk/ folder (or into the edax bin folder)
for it to work. For example if you want edax to output a log file then
add a line like this:

    ui-log-file /path/to/logfile.txt

To display debug messages use the -debug flag:

    python othelloTk -debug

If the engine is taking too long to move you can use ctrl-m to make it
move instantly. Use the time control menu option to set the time to
move.

