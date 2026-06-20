
## How to setup
### Accessing the COM id of Arduino
- If you have arduino ide
    - Plug in your arduino, and whichever COM# it says it is
- Natively through windows:
    - Windows key + X and select **Device Manager**
    - Click an arrow next to **Ports (COM & LPT)** to expand the list.
    - Unplug your Arduino and see which port disappears
    - Plug it back in and the COM id that disappeared is the right one, change the const in game.py with your COM id (this might be different for each port your computer has)
