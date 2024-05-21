from smbus2 import SMBus
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp


#Device Address
DEV_ADDR =              0x0D  # 7 bit address
ADDR_PTR=               (0xB0)

# Registers
CONTROL_REG1 = 			0x80 #D15 to D8
CONTROL_REG0 = 			0x81 #D7 to D0

FREQ_MIN_REG2 = 		0x82 #D23 to D16
FREQ_MIN_REG1 = 		0x83 #D15 to D8
FREQ_MIN_REG0 = 		0x84 #D7 to D0

FREQ_INC_REG2 = 		0x85 #D23 to D16
FREQ_INC_REG1 = 		0x86 #D15 to D8
FREQ_INC_REG0 = 		0x87 #D7 to D0

INC_NUM_REG1 = 			0x88 #D15 to D8
INC_NUM_REG0 = 			0x89 #D7 to D0

STTL_TIME_CY_NUM_REG1 = 0x8A #D15 to D8
STTL_TIME_CY_NUM_REG0 = 0x8B #D7 to D0

STATUS_REG = 			0x8F #D7 to D0

TEMP_DATA_REG1 = 		0x92 #D15 to D8
TEMP_DATA_REG0 = 		0x93 #D7 to D0

REAL_DATA_REG1 = 		0x94 #D15 to D8
REAL_DATA_REG0 = 		0x95 #D7 to D0

IMG_DATA_REG1 = 		0x96 #D15 to D8
IMG_DATA_REG0 = 		0x97 #D7 to D0

MAX_FREQ = 				100_000
MIN_FREQ = 				1_000


# High Control Register (D8-D15)
#D15-D12
INIT_WITH_START_FREQ = 	(0x01 << 4)
START_FREQ_SWEEP = 		(0x02 << 4)
INCREMENT_FREQ = 		(0x03 << 4)
REPEAT_FREQ = 			(0x04 << 4)
MEASURE_TEMP = 			(0x09 << 4)
POWER_DOWN = 			(0x0A << 4)
STANDBY = 				(0x0B << 4)

#D10-D9
V_OUT_1 = 				(0 << 1) #2Vpp
V_OUT_2 =               (3 << 1) #1vpp
V_OUT_3 =               (2 << 1) #400mVpp
V_OUT_4 =               (1 << 1) #200mVpp

#D8
PGA_GAIN_5 = 			(0 << 0)
PGA_GAIN_1 = 			(1 << 0)

# Low Control Register (D0-D7)
RESET = 				(0x01 << 4)
CLOCK_SEL_EXTERNAL=     (0x01 << 3)
CLOCK_SEL_INTERNAL =    (0x00 << 3)

# Status Register
TEMP_VALID =             (0x01) 
REAL_IMAG_VALID =        (0x02)
FREQ_SWEEP_DONE =        (0x04)

#Settling Time
SETTLING_TIME_1x =       (0 << 9)
SETTLING_TIME_2x =       (1 << 9)
SETTLING_TIME_4x =       (3 << 9)



class AD5933:
    def __init__(self, clk =  16.776e6, clk_source='internal', PGA_Gain = 1):
        self.bus = SMBus(1)
        self.clk = clk
        self.set_clock_source(clk_source)
        self.set_pga_gain(PGA_Gain)
        self.set_increment_number(0)
        self.set_settling_time_cycles(100)

    def write_register(self, reg, value):
        self.bus.write_byte_data(DEV_ADDR, reg, value)
    def read_register(self, reg):
        return self.bus.read_byte_data(DEV_ADDR, reg)
    def write_registers(self, reg, data):
        length = len(data)
        for i in range(length):
            self.bus.write_byte_data(DEV_ADDR, reg + i, data[i])

    def send_cmd(self, cmd):
        control_reg = self.read_register(CONTROL_REG1)
        control_reg &= 0x0F
        if cmd == INIT_WITH_START_FREQ or cmd == 'INIT_WITH_START_FREQ':
            control_reg |= INIT_WITH_START_FREQ
            self.write_register(CONTROL_REG1, control_reg)
        elif cmd == START_FREQ_SWEEP or cmd == 'START_FREQ_SWEEP':
            control_reg |= START_FREQ_SWEEP
            self.write_register(CONTROL_REG1, control_reg)
        elif cmd == INCREMENT_FREQ or cmd == 'INCREMENT_FREQ':
            control_reg |= INCREMENT_FREQ
            self.write_register(CONTROL_REG1, control_reg)
        elif cmd == REPEAT_FREQ or cmd == 'REPEAT_FREQ':
            control_reg |= REPEAT_FREQ
            self.write_register(CONTROL_REG1, control_reg)
        elif cmd == MEASURE_TEMP or cmd == 'MEASURE_TEMP':
            control_reg |= MEASURE_TEMP
            self.write_register(CONTROL_REG1, control_reg)
        elif cmd == POWER_DOWN or cmd == 'POWER_DOWN':
            control_reg |= POWER_DOWN
            self.write_register(CONTROL_REG1, control_reg)
        elif cmd == STANDBY or cmd == 'STANDBY':
            control_reg |= STANDBY
            self.write_register(CONTROL_REG1, control_reg)
        else:
            raise ValueError('Invalid Command to send_cmd')

    def reset(self):
        control_reg = self.read_register(CONTROL_REG0)
        self.write_register(CONTROL_REG0, control_reg | RESET)

    def set_clock_source(self, source):
        if source == 'internal':
            source = CLOCK_SEL_INTERNAL
        elif source == 'external':
            source = CLOCK_SEL_EXTERNAL
        else:
            raise ValueError('Invalid Clock Source')

        control_reg = self.read_register(CONTROL_REG0)
        control_reg &= ~CLOCK_SEL_EXTERNAL #Clear the clock bit
        control_reg |= source #Set the clock bit if needed
        self.write_register(CONTROL_REG0, control_reg)

    def set_pga_gain(self, gain):
        if gain == 1:
            gain = PGA_GAIN_1
        elif gain == 5:
            gain = PGA_GAIN_5
        else:
            raise ValueError('Invalid PGA Gain')

        control_reg = self.read_register(CONTROL_REG1)
        control_reg &= ~PGA_GAIN_5
        control_reg |= gain
        self.write_register(CONTROL_REG1, control_reg)

    def measure_temperature(self):
        self.send_cmd(MEASURE_TEMP)

        while not self.read_register(STATUS_REG) & TEMP_VALID:
            pass

        temp_data = self.read_register(TEMP_DATA_REG1) << 8
        temp_data |= self.read_register(TEMP_DATA_REG0)
        if temp_data < 8192:
            temp_data = temp_data / 32
        else:
            temp_data = temp_data - 16384
            temp_data = temp_data / 32
        print(temp_data)
        return temp_data
    
    def set_start_frequency(self, freq):
        freq_reg = int((freq * (2**27)) / (self.clk / 4))
        freq_reg = freq_reg.to_bytes(3, 'big')
        self.write_registers(FREQ_MIN_REG2, freq_reg)

    def set_increment_frequency(self, freq):
        freq_reg = int((freq * (2**27)) / (self.clk / 4))
        freq_reg = freq_reg.to_bytes(3, 'big')
        self.write_registers(FREQ_INC_REG2, freq_reg)
    
    def set_increment_number(self, num):
        num = num.to_bytes(2, 'big')
        self.write_registers(INC_NUM_REG1, num)
    
    def set_settling_time_cycles(self, cycles):
        if cycles < 512:
            cycles = cycles | SETTLING_TIME_1x
            cycles = cycles.to_bytes(2, 'big')
            self.write_registers(STTL_TIME_CY_NUM_REG1, cycles)
        elif cycles >=512 and cycles < 1023:
            cycles = int(cycles/2)
            cycles = cycles | SETTLING_TIME_2x
            cycles = cycles.to_bytes(2, 'big')
            self.write_registers(STTL_TIME_CY_NUM_REG1, cycles)
        elif cycles >= 1023 and cycles < 2044:
            cycles = int(cycles/4)
            cycles = cycles | SETTLING_TIME_4x
            cycles = cycles.to_bytes(2, 'big')
            self.write_registers(STTL_TIME_CY_NUM_REG1, cycles)
        else:
            if cycles >= 2044:
                raise ValueError('Settling Time Cycles Too High')
            if cycles < 1:
                raise ValueError('Settling Time Cycles Too Low')

    def poll_status_register(self, type):
        if type == 'temperature':
            while not self.read_register(STATUS_REG) & TEMP_VALID:
                pass
        elif type == 'real_imag':
            while not self.read_register(STATUS_REG) & REAL_IMAG_VALID:
                pass
        elif type == 'freq_sweep':
            while not self.read_register(STATUS_REG) & FREQ_SWEEP_DONE:
                pass
        else:
            raise ValueError('Invalid Status Poll Type')
    
    def twos_complement_to_int(self, value, bits):
        """Convert a 2's complement number to an integer."""
        if value & (1 << (bits - 1)):
            value -= 1 << bits
        return value
    
    def get_impedance_data(self):
        real_data = ((self.read_register(REAL_DATA_REG1) << 8) | self.read_register(REAL_DATA_REG0))
        real_data = self.twos_complement_to_int(real_data, 16)
        imag_data = ((self.read_register(IMG_DATA_REG1) << 8) | self.read_register(IMG_DATA_REG0))
        imag_data = self.twos_complement_to_int(imag_data, 16)
        return real_data, imag_data

    def run_freq_sweep(self, freq):
        self.set_start_frequency(freq)
        self.send_cmd(STANDBY)
        self.send_cmd(INIT_WITH_START_FREQ)
        self.send_cmd(START_FREQ_SWEEP)
        self.poll_status_register('real_imag')
        return self.get_impedance_data() #Return the real and imaginary data

    def Complete_Sweep(self, start_freq, end_freq, num_steps, spacing_type='logarithmic'):
        real_data = []
        imag_data = []        
        
        if spacing_type == 'logarithmic':
            freqs = np.logspace(np.log10(start_freq), np.log10(end_freq), num=num_steps)
        elif spacing_type == 'linear':
            freqs = np.linspace(start_freq, end_freq, num=num_steps)
        else:
            raise ValueError('Invalid Frequency Spacing Type')

        for freq in freqs:
            real, imag = self.run_freq_sweep(freq)
            real_data.append(real)
            imag_data.append(imag)
        
        real_data = np.array(real_data)
        imag_data = np.array(imag_data)

        self.send_cmd(STANDBY)

        return freqs, real_data, imag_data
    

    def Calculate_Impedance_Mag_At_Frequency(self, Impedance, freq):
        s = sp.symbols('s')
        if isinstance(Impedance, int) or isinstance(Impedance, float):
            return Impedance
        elif isinstance(Impedance, complex):
            return abs(Impedance)
        elif isinstance(Impedance, sp.Expr):
            return abs(Impedance.subs(s, 1j * 2 * np.pi * freq))
        else:
            raise ValueError("Invalid type for Impedance_Mag")
        
    def Calculate_Impedance_Phase_At_Frequency(self, Impedance, freq):
        s = sp.symbols('s')
        if isinstance(Impedance, int) or isinstance(Impedance, float):
            return 0
        elif isinstance(Impedance, complex):
            return np.angle(Impedance, deg = True)
        elif isinstance(Impedance, sp.Expr):
            return np.angle(Impedance.subs(s, 1j * 2 * np.pi * freq), deg = True)
        else:
            raise ValueError("Invalid type for Impedance_Phase")
        
    def find_phase_arctan(self, real, imag):
        if real > 0 and imag > 0:
            return (np.arctan(imag/real))*(180/np.pi)
        elif real < 0 and imag > 0:
            return 180 + (np.arctan(imag/real))*(180/np.pi)
        elif real < 0 and imag < 0:
            return 180 + (np.arctan(imag/real))*(180/np.pi)
        elif real > 0 and imag < 0:
            return 360 + (np.arctan(imag/real))*(180/np.pi)
        else:
            ValueError('Invalid Input')

    def Calibrate_Single_Point(self, Impedance, freq):
        Impedance_Magnitude = self.Calculate_Impedance_Mag_At_Frequency(Impedance, freq)
        Impedance_Phase = self.Calculate_Impedance_Phase_At_Frequency(Impedance, freq)
        real, imag = self.run_freq_sweep(freq)
        mag = np.sqrt((real**2) + (imag **2))
        GainFactor = 1/(Impedance_Magnitude * mag)
        Sys_Phase = self.find_phase_arctan(real, imag) - Impedance_Phase
        return GainFactor, Sys_Phase

    def Calibration_Sweep(self, Impedance, start_freq, end_freq, num_steps, spacing_type='logarithmic'):
        print('Calibrating sweep')
        GainFactors = []
        Sys_Phases = []

        if spacing_type == 'logarithmic':
            freqs = np.logspace(np.log10(start_freq), np.log10(end_freq), num=num_steps)
        elif spacing_type == 'linear':
            freqs = np.linspace(start_freq, end_freq, num=num_steps)
        else:
            raise ValueError('Invalid Frequency Spacing Type')

        for freq in freqs:
            gf, sys_phase = self.Calibrate_Single_Point(Impedance, freq)
            GainFactors.append(gf)
            Sys_Phases.append(sys_phase)
        
        self.export_calibration_data(freqs, GainFactors, Sys_Phases)
        return freqs, GainFactors, Sys_Phases

    def Adjust_Magnitude_Return_abs_Impedance(self, Freqs_Measured, real, imag, Freqs_Calibration, GainFactors):
        if any(f < min(Freqs_Calibration) or f > max(Freqs_Calibration) for f in Freqs_Measured):
            raise ValueError("One or more measured frequencies fall outside the calibration frequency range.")
        Magnitudes_Measured = np.sqrt(real**2 + imag**2)
        interpolated_gain_factors = np.interp(Freqs_Measured, Freqs_Calibration, GainFactors)
        adjusted_magnitudes = [mag * gf for mag, gf in zip(Magnitudes_Measured, interpolated_gain_factors)]
        adjusted_impedances = [1/mag for mag in adjusted_magnitudes]
        return adjusted_impedances

    def Adjust_Phase_Return_Impedance(self, Freqs_Measured, real, imag, Freqs_Calibration, Sys_Phases):
        if any(f < min(Freqs_Calibration) or f > max(Freqs_Calibration) for f in Freqs_Measured):
            raise ValueError("One or more measured frequencies fall outside the calibration frequency range.")
        Phases_Measured = np.rad2deg(np.arctan2(imag,real))
        interpolated_sys_phases = np.interp(Freqs_Measured, Freqs_Calibration, Sys_Phases)
        adjusted_phases = [phase - sys_phase + 180 for phase, sys_phase in zip(Phases_Measured, interpolated_sys_phases)]
        return adjusted_phases
        
    def export_calibration_data(self, freqs, gain_factors, sys_phases):
        data = np.array([freqs, gain_factors, sys_phases])
        np.savetxt('calibration_data.csv', data, delimiter=',')  

    def import_calibration_data(self):
        data = np.loadtxt('calibration_data.csv', delimiter=',')
        return data[0], data[1], data[2]  #freqs, gain_factors, sys_phases
    
    def Sweep_And_Adjust(self, start_freq, end_freq, num_steps, spacing_type='logarithmic'):
        freqs, real, imag = self.Complete_Sweep(start_freq, end_freq, num_steps, spacing_type)
        Cal_Freqs, Gain_Factors, Sys_Phases = self.import_calibration_data()
        Magnitude = self.Adjust_Magnitude_Return_abs_Impedance(freqs, real, imag, Cal_Freqs, Gain_Factors)
        Phase = self.Adjust_Phase_Return_Impedance(freqs, real, imag, Cal_Freqs, Sys_Phases)
        freqs = np.array(freqs)
        Magnitude = np.array(Magnitude)
        Phase = np.array(Phase)
        real = Magnitude * np.cos(np.deg2rad(Phase))
        imag = Magnitude * np.sin(np.deg2rad(Phase))
        return freqs, real, imag, Phase