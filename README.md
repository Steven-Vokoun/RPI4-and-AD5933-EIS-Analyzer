# RPI4 and AD5933 EIS Analyzer
Overview:
- Mostly functioning but needs improvements.
- Libraries for AD5933 and MUX's working at this time.
- GUI utilizes custom tkinter.
- Fitting utilized "Impedance" python library (planning to update for robustness)
- Automatic gain switching methods implemented, but has bugs


Improvements I need to make in the future:
- Implementation of the internal 5x switchable gains
- Shift screen off to the left hand side of the enclosure, so then the power supply can be placed right next to the analog board.  Also put filtering on the i2c lines.
- Configuration of 3 electrode switching with a double pole relay instead to completely get it out of the circuit
- Have an external calibration board to account for lead inductance and capacitance
- Add a warning for when the output is hitting supply rails

Future Goals:
- Switch off of a RPI, to a lower level board for lower power consumption
- Shrink the device
- Make my own battery management board
