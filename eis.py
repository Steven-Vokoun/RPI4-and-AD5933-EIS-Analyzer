import numpy as np
import impedance as imp
from impedance.models.circuits import CustomCircuit
import csv
import os
import time
import psutil
import re

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

def extract_information(input_string):
    # Extract the relevant information using regular expressions
    pattern = r'(?:R|C|CPE|Wo)\d+|(?<=,)(?:R|C|CPE|Wo)\d+(?=\))'
    extracted_info = re.findall(pattern, input_string)
    for i, item in enumerate(extracted_info):
        if 'CPE' in item:
            num = item[3:]
            extracted_info[i] = 'Q' + num
            extracted_info.insert(i+1, 'n' + num)
    return extracted_info

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

    print(f"Fitted parameters: {fitted_params}")
    return real_fit, imag_fit, fitted_params, extract_information(circuit_model)

def detect_usb_drive():
    """Detect the USB drive mount point."""
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if 'media' in partition.mountpoint and 'rw' in partition.opts:  # 'rw' indicates read/write access
            return partition.mountpoint
    return None


def export_to_usb(send_notification, frequencies, real, imaginary):
    """Export frequencies, real, and imaginary data to a CSV file on a USB drive."""
    usb_mount_point = None
    # Wait until a USB drive is detected
    send_notification("Waiting for USB drive...")
    while usb_mount_point is None:
        usb_mount_point = detect_usb_drive()
        if usb_mount_point is None:
            time.sleep(1)  # Check every second

    # Prepare the file path
    file_path = os.path.join(usb_mount_point, 'exported_data.csv')
    
    # Write data to CSV file
    try:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Frequency', 'Real', 'Imaginary'])
            for f, r, i in zip(frequencies, real, imaginary):
                writer.writerow([f, r, i])
        send_notification(f"Data successfully exported to {file_path}")
    except Exception as e:
        send_notification(f"Failed to write to CSV: {e}")