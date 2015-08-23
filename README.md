# othelloTk
Edax gui to play Othello against the Edax engine.

John Cheetham August 2015

Written in python2/Tkinter and licensed under the GPL v3+
(see the file named LICENSE).

It was tested with edax 4.3.2 on CentOS7 64 bit.

Requirements
------------
Python 2.7, Tkinter, Edax.

Installation
------------
 1. Download the edax othello engine from http://abulmo.perso.neuf.fr
    This has a prebuilt binary for Linux 64 bit.

 2. Start othelloTk with 'python othelloTk'

 3. Do edit/preferences and set the engine path to the edax executable.
    This is called lEdax-x64 in the edax bin folder (if you are using
    Linux 64 bit).

 4. Set opponent to engine (you may need to exit preferences and then
    go in again).

 5. Do new game and play against edax.

The settings will be remembered so you only need do it once.
When changing the preferences you need to do New Game for them to
take effect.

This is a work in progress so it will have bugs and minimal features.

Usage
-----
You play black, computer plays white.
Click on a square to place a black piece.
If you find there are no legal moves then you can pass by right
clicking anywhere on the board. 

