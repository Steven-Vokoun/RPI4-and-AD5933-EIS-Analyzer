import os
import numpy as np

try:
    from smbus2 import SMBus
    import RPi.GPIO as GPIO
except ImportError:
    if os.name == 'nt':  # Check if the operating system is Windows
        print("smbus2 library is not supported on Windows, using dummy class instead...")
    else:
        ValueError("smbus2 library is not installed")



class LTC6904:
    #DEFINITIONS
    LTC6904_ADDRESS = 0x17  # I2C address of the LTC6904

    LTC6904_CLK_ON_CLK_INV_ON   = 0x00    # Clock on, inverted clock on
    LTC6904_CLK_OFF_CLK_INV_ON  = 0x01    # Clock off, inverted clock on
    LTC6904_CLK_ON_CLK_INV_OFF  = 0x02    # Clock on, inverted clock off
    LTC6904_POWER_DOWN          = 0x03    # Powers down clocks

    #FUNCTIONS
    def __init__(self):
        self.bus = SMBus(1)

    def write_registers(self, MS, LS):
        self.bus.write_byte_data(self.LTC6904_ADDRESS, MS, LS)

    def Turn_On_Clock(self, frequency):
        OCT = int(3.322 * np.log10(frequency / 1039))
        DAC = 2048 - int((2078 * (2 ** (10+OCT))) / frequency)
        MS = OCT << 4 | DAC >> 4
        LS = DAC << 4 | self.LTC6904_CLK_ON_CLK_INV_OFF
        LTC6904.write_registers(MS, LS)

    def Turn_Off_Clock(self):
        MS = 0x00
        LS = self.LTC6904_POWER_DOWN
        LTC6904.write_registers(MS, LS)

class Calibration_Mux:
    def __init__(self):
        pins = [9,10,22]  # 9 is A2, 10 A1, 22 A0
        GPIO.setmode(GPIO.BCM)
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    def select_calibration(setting):
        if setting == '10Meg' or setting == 0:
            GPIO.output(9, GPIO.LOW)
            GPIO.output(10, GPIO.LOW)
            GPIO.output(22, GPIO.LOW)
        elif setting == '1Meg' or setting == 1:
            GPIO.output(9, GPIO.LOW)
            GPIO.output(10, GPIO.LOW)
            GPIO.output(22, GPIO.HIGH)
        elif setting == '100k' or setting == 2:
            GPIO.output(9, GPIO.LOW)
            GPIO.output(10, GPIO.HIGH)
            GPIO.output(22, GPIO.LOW)
        elif setting == '10k' or setting == 3:
            GPIO.output(9, GPIO.LOW)
            GPIO.output(10, GPIO.HIGH)
            GPIO.output(22, GPIO.HIGH)
        elif setting == '100' or setting == 4:
            GPIO.output(9, GPIO.HIGH)
            GPIO.output(10, GPIO.LOW)
            GPIO.output(22, GPIO.LOW)
        elif setting == 'Randles' or setting == 5:
            GPIO.output(9, GPIO.HIGH)
            GPIO.output(10, GPIO.LOW)
            GPIO.output(22, GPIO.HIGH)
        elif setting == 'Counter0' or setting == 6:
            GPIO.output(9, GPIO.HIGH)
            GPIO.output(10, GPIO.HIGH)
            GPIO.output(22, GPIO.LOW)
        elif setting == 'Counter1' or setting == 7:
            GPIO.output(9, GPIO.HIGH)
            GPIO.output(10, GPIO.HIGH)
            GPIO.output(22, GPIO.HIGH)

class Output_Gain_Mux:
    def __init__():
        pins = [27,17]  # 27 is A1, 17 is A0
        GPIO.setmode(GPIO.BCM)
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    def select_gain(setting):
        if setting == '1x' or setting == 0:
            GPIO.output(27, GPIO.LOW)
            GPIO.output(17, GPIO.LOW)
        elif setting == '.1x' or setting == 1:
            GPIO.output(27, GPIO.LOW)
            GPIO.output(17, GPIO.HIGH)
        elif setting == '.01x' or setting == 2:
            GPIO.output(27, GPIO.HIGH)
            GPIO.output(17, GPIO.LOW)
        elif setting == '1x_uncorrected' or setting == 3:
            GPIO.output(27, GPIO.HIGH)
            GPIO.output(17, GPIO.HIGH)

class Input_Gain_Mux:
    def __init__():
        pins = [24,23]  # 24 is A1, 23 is A0
        GPIO.setmode(GPIO.BCM)
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    def select_gain(setting):
        if setting == '100x' or setting == 0:
            GPIO.output(24, GPIO.LOW)
            GPIO.output(23, GPIO.LOW)
        elif setting == '10kx' or setting == 1:
            GPIO.output(24, GPIO.LOW)
            GPIO.output(23, GPIO.HIGH)
        elif setting == '100kx' or setting == 2:
            GPIO.output(24, GPIO.HIGH)
            GPIO.output(23, GPIO.LOW)
        elif setting == '1Mx' or setting == 3:
            GPIO.output(24, GPIO.HIGH)
            GPIO.output(23, GPIO.HIGH)

class Electrode_Switch:
    def __init__():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(25, GPIO.OUT)
        GPIO.output(25, GPIO.LOW)
    def select_electrode(setting):
        if setting == '2 Electrode' or setting == 0:
            GPIO.output(25, GPIO.LOW)
        elif setting == '3 Electrode' or setting == 1:
            GPIO.output(25, GPIO.HIGH)