# Game
## Background
Welcome to Space Greg! You're playing as Greg, a brave frog who is collecting stardust to save the solar system and the rest of the frog species! But this mission is not without its challenges; there are multiple obstacles you'll have to face, all while managing your fuel.

## Gameplay
### Controls
- The game is intended to be played with a console we made with Arduino, however for debugging purposes arrowkeys also work. The joystick controls require flicking in a certain directions in order to gain speed in said direction.
- The shift button of the computer allows faster change in speed when flicking with the cost of more fuel spent
### Objects
- **Fuels** are needed to control the spaceship and can be collected through fly objects that appear on the map at random, running out of fuel results in end of the game. The remaining fuel amount is added to the final score. Fuels progressively get smaller.
- **Stardusts** are the main collectibles, and each one of them gain +1 stardust, at the end of the game the score is determined with # of stradust x time survived. Stardusts progressively get smaller.
- **Astroids** are singular moving obstacles that result in losing the game when hit, progressively they get bigger and more in amount
- **Comets** *very rarely* spawn and similar to astroids colliding ends the game. These rapid rocks also leave behind fast-disappearing particles that when collected gains +2 stardust.
- **Astroid groups** spawn much rarer than singular astroids but cover a larger area and travel together with varying sizes. Behaves very similar to astroids and a collision ends the game.
- **Wormholes** spawn at random locations in pairs and a collision with one of them teleports Greg to the other wormhole and both wormholes disappear. Can be used in risky situations as a quick escape.

## AI Use
- AI is used to search up infromation about certain libraries and specific syntax, as well as refinments and revisions of the code.

## Tech Stack
### Software
- Python - for the whole app
- Tkinter - for the visualization and the game itself
- Arduino (.ino) - for programming the console
### Sensors and hardware
- Joystick
- OLED screen
- 2 LEDs
- Arduino Uno

## How to setup
### Accessing the COM id of Arduino
- If you have arduino ide
    - Plug in your arduino, and whichever COM# it says it is
- Natively through windows:
    - Windows key + X and select **Device Manager**
    - Click an arrow next to **Ports (COM & LPT)** to expand the list.
    - Unplug your Arduino and see which port disappears
    - Plug it back in and the COM id that disappeared is the right one, change the const in game.py with your COM id (this might be different for each port your computer has)
