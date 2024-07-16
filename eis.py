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
        initial_guess = [150000, 10e-12]
    elif circuit == 'Parallel RC':
        circuit_model = 'p(R0, C1)'
        initial_guess = [100000, 5e-12]
    elif circuit == 'Randles':
        circuit_model = 'R0-p(C1,R2)'
        initial_guess = [10000, 5e-12, 100000]
    elif circuit == 'Randles With CPE':
        circuit_model = 'R0-p(CPE1,R2)'
        initial_guess = [10000, 5e-12, 0.9, 100000]
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
                writer.writerow([f, str(r), str(i)])
        send_notification(f"Data successfully exported to {file_path}")
    except Exception as e:
        send_notification(f"Failed to write to CSV: {e}")

def set_output_amplitude(voltage, sensor, Output_Gain_Mux):
    if voltage == 2 or voltage == .002:
        sensor.set_voltage_output(.2)
        Output_Gain_Mux.select_channel(2)
    elif voltage == 4 or voltage == .004:
        sensor.set_voltage_output(.4)
        Output_Gain_Mux.select_channel(2)
    elif voltage == 10 or voltage == .01:
        sensor.set_voltage_output(1)
        Output_Gain_Mux.select_channel(2)
    elif voltage == 20 or voltage == .02:
        sensor.set_voltage_output(.2)
        Output_Gain_Mux.select_channel(1)
    elif voltage == 38 or voltage == .038:
        sensor.set_voltage_output(.4)
        Output_Gain_Mux.select_channel(1)
    elif voltage == 100 or voltage == .1:
        sensor.set_voltage_output(1)
        Output_Gain_Mux.select_channel(1)
    elif voltage == 200 or voltage == .2:
        sensor.set_voltage_output(.2)
        Output_Gain_Mux.select_channel(0)
    elif voltage == 380 or voltage == .38:
        sensor.set_voltage_output(.4)
        Output_Gain_Mux.select_channel(0)
    elif voltage == 1 or voltage == 1:
        sensor.set_voltage_output(1)
        Output_Gain_Mux.select_channel(0)
    elif voltage == 2 or voltage == 2:
        sensor.set_voltage_output(2)
        Output_Gain_Mux.select_channel(0)
    else:
        print("Invalid voltage value")

def calculate_impedance_range(voltage, input_gain): #voltage(mV) as a float and input_gain as a float
    max_input_voltage = 3
    min_input_voltage = 0.2
    min_Impedance = ((voltage / 1000) * input_gain) / max_input_voltage
    max_Impedance = ((voltage / 1000) * input_gain) / min_input_voltage
    return min_Impedance, max_Impedance

def calibrate_all(voltage, start_freq, end_freq, hardware, send_notification):
    send_notification("Calibrating...")
    set_output_amplitude(voltage, hardware.sensor, hardware.Output_Gain_Mux)



    freqs, GainFactors, Sys_Phases = hardware.sensor.Calibration_Sweep()
    export_calibration_data(freqs, GainFactors, Sys_Phases, voltage)
    send_notification("Calibration complete")

def conduct_experiment(hardware, send_notification, voltage, start_freq, end_freq, num_steps, spacing_type='logarithmic'):
    send_notification("Running EIS experiment...")
    set_output_amplitude(voltage, hardware.sensor, hardware.Output_Gain_Mux)
    freqs, real, imag = hardware.sensor.EIS_Sweep(start_freq, end_freq, num_steps, spacing_type)
    return freqs, real, imag

def export_calibration_data(self, freqs, gain_factors, sys_phases, voltage, Impedance):
    data = np.array([freqs, gain_factors, sys_phases])
    folder_name = 'calibration_data'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_name = f'{voltage}_{Impedance}.csv'
    file_path = os.path.join(folder_name, file_name)
    np.savetxt(file_path, data, delimiter=',')

resistors = [100, 4_700, 200_000, 10_000_000]
calibrations = [100,10_000, 100_000, 1_000_000, 10_000_000]

# 10mV
print("\n10mV")
print(calculate_impedance_range(10,resistors[0]*5))
print(calculate_impedance_range(10,resistors[0]*5*5))
print(calculate_impedance_range(10,resistors[1]*5))
print(calculate_impedance_range(10,resistors[1]*5*5))
print(calculate_impedance_range(10,resistors[2]*5))
print(calculate_impedance_range(10,resistors[2]*5*5))
print(calculate_impedance_range(10,resistors[3]*5))
print(calculate_impedance_range(10,resistors[3]*5*5))


#100mV
print("\n100mV")
print(calculate_impedance_range(100,resistors[0]*5))
print(calculate_impedance_range(100,resistors[0]*5*5))
print(calculate_impedance_range(100,resistors[1]*5))
print(calculate_impedance_range(100,resistors[1]*5*5))
print(calculate_impedance_range(100,resistors[2]*5))
print(calculate_impedance_range(100,resistors[2]*5*5))
print(calculate_impedance_range(100,resistors[3]*5))
print(calculate_impedance_range(100,resistors[3]*5*5))

#1V
print("\n1V")
print(calculate_impedance_range(1000,resistors[0]*5))
print(calculate_impedance_range(1000,resistors[0]*5*5))
print(calculate_impedance_range(1000,resistors[1]*5))
print(calculate_impedance_range(1000,resistors[1]*5*5))
print(calculate_impedance_range(1000,resistors[2]*5))
print(calculate_impedance_range(1000,resistors[2]*5*5))
print(calculate_impedance_range(1000,resistors[3]*5))
print(calculate_impedance_range(1000,resistors[3]*5*5))