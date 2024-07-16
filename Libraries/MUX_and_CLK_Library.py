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

class MUX:
    def __init__(self, control_pins, size):
        """
        control_pins (list): List of GPIO pins
        size (int): (1, 4, or 8)
        USES BROADCOM NUMBERING
        """
        if size not in [1, 4, 8]:
            raise ValueError("Size must be 1, 4, or 8")

        self.control_pins = control_pins
        self.size = size
        self.num_control_pins = len(control_pins)

        if 2 ** self.num_control_pins < self.size:
            raise ValueError("Not enough control pins for the specified size")

        GPIO.setmode(GPIO.BCM)
        for pin in self.control_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    def select_channel(self, channel):
        if channel < 0 or channel >= self.size:
            raise ValueError(f"Channel must be between 0 and {self.size - 1}")

        # Format the channel to binary with leading zeros
        binary_value = format(channel, f'0{self.num_control_pins}b')

        for i in range(len(self.control_pins)):
            GPIO.output(self.control_pins[i], GPIO.HIGH if binary_value[i] == '1' else GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()

