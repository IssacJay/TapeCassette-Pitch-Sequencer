# Tape Cassette Pitch Sequencer
Pulse Width Modulation Motor controller for Cassette Machines, using a raspberry Pi Pico. 
https://youtu.be/hcBXBUudQDU

[![Beans on Toast](https://i3.ytimg.com/vi/hcBXBUudQDU/maxresdefault.jpg )](https://youtu.be/hcBXBUudQDU "Tape Machine Pitch Sequencer | Tascam Porta 02 and Raspberry Pi Pico")

OVERVIEW:

This directory is a series of Micropython files used to create an 8 Step Pitch and Volume Gate sequencer for any cassette machine, using a Raspberry Pi Pico. The full tutorial is available here: 
https://www.instructables.com/Pitch-Sequencer-for-Tascam-Porta-02-PWM-Microcontr/

MATERIALS:

Basic materials list needed for the build:
Raspberry Pi Pico - 
Rotary Encoder KY-040 - 
OLED SSD-1306 - 
2N7000 N-Channel MOSFET

GETTING STARTED:

Download the full directory, and load the files with the same file structure to your Pico. Then follow instructions in the Instructables Tutorial to begin building te circuit. You will need some additional Micropython packages, that must be saved to the /lib folder in the Pico. These are available below, as well as in the Instructables.

Rotary Encoder Package:
https://github.com/gurgleapps/rotary-encoder/blob/main/rotary.py

Frame Buffer Package:
https://github.com/dhylands/micropython-lib-1/blob/master/framebuf/framebuf.py

SSD-1306 Micropython package:
Available directly from the Thonny Package manager - follow this link for a video if you're unsure 
https://www.youtube.com/watch?v=YR9v04qzJ5E&t=379s
