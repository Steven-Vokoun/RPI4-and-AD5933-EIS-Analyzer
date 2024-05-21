import time
import numpy as np
import impedance as imp
from impedance.models.circuits import CustomCircuit


def calculate_impedance(frequencies, Rs, Rp, C):
    omega = 2 * np.pi * frequencies
    Z_R = Rs
    Z_C = Rp / (1 + Rp * 1j * omega * C)
    Z = Z_R + Z_C
    return Z.real, Z.imag

def run_demo_EIS_experiment(update_data_callback, max_freq, min_freq, spacing_type, num_steps):
    if spacing_type == 'logarithmic':
        frequencies = np.logspace(np.log10(min_freq), np.log10(max_freq), num = num_steps)
    else:
        frequencies = np.linspace(min_freq, max_freq, num_steps)
    
    Rs = 1000
    Rp = 100000
    C = 5E-8
    
    real_impedances, imag_impedances = calculate_impedance(frequencies, Rs, Rp, C)

    update_data_callback(frequencies, real_impedances, imag_impedances)

def fit_eis_data(frequencies, real_impedances, imag_impedances, circuit):
    Z = real_impedances + 1j * imag_impedances

    # Define circuit models
    if circuit == 'Series RC':
        circuit_model = 'R0-C1'
        initial_guess = [1000, 5E-8]
    elif circuit == 'Parallel RC':
        circuit_model = 'R0-p(C1,R1)'
        initial_guess = [1000, 5E-8, 100000]
    elif circuit == 'Randles':
        circuit_model = 'R0-p(C1,R1)'
        initial_guess = [1000, 5E-8, 100000]
    elif circuit == 'Randles With CPE':
        circuit_model = 'R0-p(CPE1,R1)'
        initial_guess = [1000, 5E-8, 0.9, 100000]
    else:
        raise ValueError(f"Unknown circuit type: {circuit}")

    circuit = CustomCircuit(initial_guess=initial_guess, circuit=circuit_model)
    circuit.fit(frequencies, Z)

    fitted_params = circuit.parameters_
    Z_fit = circuit.predict(frequencies)
    real_fit = Z_fit.real
    imag_fit = Z_fit.imag

    return real_fit, imag_fit, fitted_params