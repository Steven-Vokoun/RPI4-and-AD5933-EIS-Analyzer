import time
import numpy as np

def calculate_impedance(frequencies, Rs, Rp, C):
    omega = 2 * np.pi * frequencies
    Z_R = Rs
    Z_C = Rp / (1 + Rp * 1j * omega * C)
    Z = Z_R + Z_C
    return Z.real, Z.imag

def run_eis_experiment(update_data_callback, max_freq, min_freq, spacing_type, num_steps):
    if spacing_type == 'logarithmic':
        frequencies = np.logspace(np.log10(min_freq), np.log10(max_freq), num = num_steps)
    else:
        frequencies = np.linspace(min_freq, max_freq, num_steps)
    
    Rs = 1000
    Rp = 100000
    C = 5E-8
    
    real_impedances, imag_impedances = calculate_impedance(frequencies, Rs, Rp, C)

    update_data_callback(frequencies, real_impedances, imag_impedances)