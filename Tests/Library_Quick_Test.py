from AD5933_Library import AD5933

Resistor = 220_000
sensor = AD5933()
sensor.set_increment_number(0)
sensor.set_settling_time_cycles(1000)
print('Calibrating')
Cal_Freqs, Gain_Factors, Sys_Phases = sensor.Calibration_Sweep(Resistor, 5_000, 105_000, 200, spacing_type='linear')
print('Sweeping')
freqs, real, imag = sensor.Complete_Sweep(10_000, 100_000, 200, spacing_type='linear')
print('Adjusting')
Magnitude = sensor.Adjust_Magnitude_Return_abs_Impedance(freqs, real, imag, Cal_Freqs, Gain_Factors)
Phase = sensor.Adjust_Phase_Return_Impedance(freqs, real, imag, Cal_Freqs, Sys_Phases)

import matplotlib.pyplot as plt

print('Plotting')
fig, axs = plt.subplots(2, 1)

axs[0].plot(freqs, Magnitude)
axs[0].set_xlabel('Frequency (Hz)')
axs[0].set_ylabel('Impedance (Ohms)')

axs[1].plot(freqs, Phase)
axs[1].set_xlabel('Frequency (Hz)')
axs[1].set_ylabel('Phase (Degrees)')

plt.tight_layout()

plt.show()