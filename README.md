# CTA_ETA

This is a personal project to pull arrival time info for CTA train and bus stops nearest to my home.
The program also pulls information on the 4 divvy stations nearest my home. Arrival times are
calculated assuming central time zone.

The program is setup to run on a 1280x1024 monitor and is directly launched when my raspberry pi
is turned on. In my home, my raspberry pi is connected to a light switch which will activate/deactivate
the program when flipped.

The display for this program is controlled through Tkinter. It essentially displays a background image
with text objects overlaid on top. The text objects are updated every 15 seconds with new arrival time
information.

The program is designed to enter full screen mode when started. It can be exited by clicking the 'X'
in the NW corner of the screen which will kill full screen mode and exit the program.

Thanks for checking it out!
-Scott Cronin