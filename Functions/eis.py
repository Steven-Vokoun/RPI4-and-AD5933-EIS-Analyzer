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

def set_output_amplitude(voltage, sensor, Output_Gain_Mux, send_notification):
    if voltage == "2mV" or voltage == '2' or voltage == 2:
        sensor.set_output_voltage(.2)
        Output_Gain_Mux.select_gain('.01x')
    elif voltage == "4mV" or voltage == '4' or voltage == 4:
        sensor.set_output_voltage(.4)
        Output_Gain_Mux.select_gain('.01x')
    elif voltage == "10mV" or voltage == '10' or voltage == 10:
        sensor.set_output_voltage(1)
        Output_Gain_Mux.select_gain('.01x')
    elif voltage == "20mV" or voltage == '20' or voltage == 20:
        sensor.set_output_voltage(.2)
        Output_Gain_Mux.select_gain('.1x')
    elif voltage == "38mV" or voltage == '38' or voltage == 38:
        sensor.set_output_voltage(.4)
        Output_Gain_Mux.select_gain('.1x')
    elif voltage == "100mV" or voltage == '100' or voltage == 100:
        sensor.set_output_voltage(1)
        Output_Gain_Mux.select_gain('.1x')
    elif voltage == "200mV" or voltage == '200' or voltage == 200:
        sensor.set_output_voltage(.2)
        Output_Gain_Mux.select_gain('1x')
    elif voltage == "380mV" or voltage == '380' or voltage == 380:
        sensor.set_output_voltage(.4)
        Output_Gain_Mux.select_gain('1x')
    elif voltage == "1V" or voltage == '1000' or voltage == 1000:
        sensor.set_output_voltage(1)
        Output_Gain_Mux.select_gain('1x')
    elif voltage == "2V" or voltage == '2000' or voltage == 2000:
        sensor.set_output_voltage(2)
        Output_Gain_Mux.select_gain('1x')
    else:
        send_notification("Invalid voltage value")


def Adjust_Magnitude_Return_abs_Impedance(Freqs_Measured, real, imag, Freqs_Calibration, GainFactors):
    if any(f < min(Freqs_Calibration) or f > max(Freqs_Calibration) for f in Freqs_Measured):
        raise ValueError("One or more measured frequencies fall outside the calibration frequency range.")
    Magnitudes_Measured = np.sqrt(real**2 + imag**2)
    interpolated_gain_factors = np.interp(Freqs_Measured, Freqs_Calibration, GainFactors)
    adjusted_magnitudes = [mag * gf for mag, gf in zip(Magnitudes_Measured, interpolated_gain_factors)]
    adjusted_impedances = [1/mag for mag in adjusted_magnitudes]
    return adjusted_impedances

def Adjust_Phase_Return_Phase(Freqs_Measured, real, imag, Freqs_Calibration, Sys_Phases):
    if any(f < min(Freqs_Calibration) or f > max(Freqs_Calibration) for f in Freqs_Measured):
        raise ValueError("One or more measured frequencies fall outside the calibration frequency range.")
    Phases_Measured = np.rad2deg(np.arctan2(imag,real))
    interpolated_sys_phases = np.interp(Freqs_Measured, Freqs_Calibration, Sys_Phases)
    adjusted_phases = [phase - sys_phase for phase, sys_phase in zip(Phases_Measured, interpolated_sys_phases)]
    return adjusted_phases

def Adjust_Magnitude_Return_abs_Impedance_single(Freq_Measured, real, imag, Freqs_Calibration, GainFactors):
    if Freq_Measured < min(Freqs_Calibration) or Freq_Measured > max(Freqs_Calibration):
        raise ValueError("The measured frequency falls outside the calibration frequency range.")
    Magnitude_Measured = np.sqrt(real**2 + imag**2)
    interpolated_gain_factor = np.interp(Freq_Measured, Freqs_Calibration, GainFactors)
    adjusted_magnitude = Magnitude_Measured * interpolated_gain_factor
    adjusted_impedance = 1 / adjusted_magnitude
    return adjusted_impedance

def Adjust_Phase_Return_Phase_single(Freq_Measured, real, imag, Freqs_Calibration, Sys_Phases):
    if Freq_Measured < min(Freqs_Calibration) or Freq_Measured > max(Freqs_Calibration):
        raise ValueError("The measured frequency falls outside the calibration frequency range.")
    Phase_Measured = np.rad2deg(np.arctan2(imag, real))
    interpolated_sys_phase = np.interp(Freq_Measured, Freqs_Calibration, Sys_Phases)
    adjusted_phase = Phase_Measured - interpolated_sys_phase
    return adjusted_phase


def calibrate_all(voltage, start_freq, end_freq, hardware, send_notification, num_steps, spacing_type):

    hardware.Electrode_Mux.select_electrode('3 Electrode')

    send_notification("Calibrating...")
    send_notification(str(voltage))
    set_output_amplitude(voltage, hardware.sensor, hardware.Output_Gain_Mux, send_notification)

    impedances = [10e6, 1e6, 100e3, 10e3, 100]
    for impedance in impedances:
        hardware.Calibration_Mux.select_calibration(impedance)
        
        estimated_current = (voltage/1000)/impedance
        estimated_gain = None
        gains = [100, 10e3, 100e3, 1e6]
        for gain in gains:
            if estimated_current * gain < 1.5:  #~~VCC/2
                estimated_gain = gain
            else:
                break
        if estimated_gain is None:
            send_notification("Unable to find suitable gain setting")
        hardware.Input_Gain_Mux.select_gain(estimated_gain)

        
        freqs, GainFactors, Sys_Phases = hardware.sensor.Calibration_Sweep(impedance, start_freq, end_freq, num_steps, spacing_type)


        export_calibration_data(freqs, GainFactors, Sys_Phases, voltage, int(impedance))

        send_notification("impedance", newline=False)
    send_notification("Calibration complete")

def conduct_experiment(hardware, send_notification, voltage, estimated_impedance, start_freq, end_freq, num_steps = 100, spacing_type='logarithmic', output_location = 'Counter0', binary_search = True):
    
    send_notification("Running EIS experiment...")
    hardware.Electrode_Mux.select_electrode('3 Electrode')

    #Set Calibration
    hardware.Calibration_Mux.select_calibration(output_location)

    #Set Output
    set_output_amplitude(voltage, hardware.sensor, hardware.Output_Gain_Mux, send_notification)

    #Set Gain
    impedance_values = {0: '100', 1: '10000', 2: '100000', 3: '1000000', 4: '10000000'}
    estimated_impedance = int(impedance_values[estimated_impedance])

    if binary_search == True:
        freqs, real, imag, Phase = conduct_binary_search_experiment(hardware, send_notification, voltage, estimated_impedance, start_freq, end_freq, num_steps, spacing_type)

    else:
        estimated_gain = find_gain_from_voltage_and_Impedance(voltage, estimated_impedance, send_notification)
        hardware.Input_Gain_Mux.select_gain(estimated_gain)
        #Run Experiment
        freqs, real, imag = hardware.sensor.Complete_Sweep(start_freq, end_freq, num_steps, spacing_type)

        #Adjust Data
        cal_data = import_calibration_data(voltage, estimated_impedance)
        Magnitude = Adjust_Magnitude_Return_abs_Impedance(freqs, real, imag, cal_data.Cal_Freqs, cal_data.Gain_Factors)
        Phase = Adjust_Phase_Return_Phase(freqs, real, imag, cal_data.Cal_Freqs, cal_data.Sys_Phases)
        freqs = np.array(freqs)
        Magnitude = np.array(Magnitude)
        Phase = np.array(Phase)
        real = Magnitude * np.cos(np.deg2rad(Phase))
        imag = Magnitude * np.sin(np.deg2rad(Phase))

    return freqs, real, imag, Phase

def binary_search_gain(hardware, send_notification, voltage, estimated_impedance, freq, calibration_data):
    for trial in range(3):
        # Setup starting parameters
        estimated_gain = find_gain_from_voltage_and_Impedance(voltage, estimated_impedance, send_notification)
        hardware.Input_Gain_Mux.select_gain(estimated_gain)
        real_temp, imag_temp = hardware.sensor.run_freq_sweep(freq)
    
        # Adjust the impedance with the calibration factor
        estimated_impedance = find_impedance_from_voltage_and_gain(voltage, estimated_gain, send_notification)
        impedance = Adjust_Magnitude_Return_abs_Impedance_single(
            freq, real_temp, imag_temp, 
            calibration_data[str(estimated_impedance)].Cal_Freqs, 
            calibration_data[str(estimated_impedance)].Gain_Factors
        )
        optimal_gain = find_gain_from_voltage_and_Impedance(voltage, impedance, send_notification)
        if optimal_gain == estimated_gain:
            break
        else:
            estimated_gain = optimal_gain
    Phase = Adjust_Phase_Return_Phase_single(
        freq, real_temp, imag_temp, 
        calibration_data[str(estimated_impedance)].Cal_Freqs, 
        calibration_data[str(estimated_impedance)].Gain_Factors
    )
    real = impedance * np.cos(np.deg2rad(Phase))
    imag = impedance * np.sin(np.deg2rad(Phase))

    return impedance, real, imag, Phase

def conduct_binary_search_experiment(hardware, send_notification, voltage, impedance, start_freq, end_freq, num_steps, spacing_type):
    # Setup Frequencies of interest
    if spacing_type == 'logarithmic':
        freqs = np.logspace(np.log10(start_freq), np.log10(end_freq), num=num_steps)
    elif spacing_type == 'linear':
        freqs = np.linspace(start_freq, end_freq, num=num_steps)
    else:
        raise ValueError('Invalid Frequency Spacing Type')

    # Import Calibration Data
    calibration_data = import_all_calibration_data(voltage)
    
    # Initialize results arrays
    real_results = np.zeros(num_steps)
    imag_results = np.zeros(num_steps)
    phase_results = np.zeros(num_steps)

    # Repeat the first datapoint for settling
    for _ in range(3):
        real_temp, imag_temp = hardware.sensor.run_freq_sweep(freqs[0])

    # Loop through each frequency
    for i, freq in enumerate(freqs):
        impedance, real_adjusted, imag_adjusted, Phase = binary_search_gain(
            hardware, send_notification, voltage, impedance, freq, calibration_data)
        real_results[i] = real_adjusted
        imag_results[i] = imag_adjusted
        phase_results[i] = Phase

    return freqs, real_results, imag_results, phase_results

def export_calibration_data(freqs, gain_factors, sys_phases, voltage, Impedance):
    data = np.array([freqs, gain_factors, sys_phases])
    folder_name = 'calibration_data'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_name = f'{voltage}_{Impedance}.csv'
    file_path = os.path.join(folder_name, file_name)
    np.savetxt(file_path, data, delimiter=',')

class CalibrationData:
    def __init__(self, cal_freqs, gain_factors, sys_phases):
        self.Cal_Freqs = cal_freqs
        self.Gain_Factors = gain_factors
        self.Sys_Phases = sys_phases

def import_calibration_data(voltage, impedance):
    folder_name = 'calibration_data'
    file_name = f'{voltage}_{impedance}.csv'
    file_path = os.path.join(folder_name, file_name)
    data = np.loadtxt(file_path, delimiter=',')
    return CalibrationData(data[0], data[1], data[2])

def import_all_calibration_data(voltage):
    calibration_data = {}
    for impedance in ['100', '10000', '100000', '1000000', '10000000']:
        calibration_data[impedance] = import_calibration_data(voltage, impedance)
    return calibration_data

def find_gain_from_voltage_and_Impedance(voltage, estimated_impedance, send_notification):
    estimated_current = (voltage/1000)/estimated_impedance
    estimated_gain = None
    gains = [100, 10e3, 100e3, 1e6]
    for gain in gains:
        if estimated_current * gain < 1.5:
            estimated_gain = gain
        else:
            break
    if estimated_gain is None:
        send_notification("Unable to find suitable gain setting")
    else:
        send_notification(f"Estimated input gain setting: {estimated_gain}")
    return int(estimated_gain)

def find_impedance_from_voltage_and_gain(voltage, gain, send_notification):
    estimate = (voltage / 1000) * gain / 1.5
    impedances = [100, 10e3, 100e3, 1e6, 10e6]
    estimated_impedance = None
    
    for impedance in impedances:
        if estimate > impedance:
            estimated_impedance = impedance
        else:
            break
    
    if estimated_impedance is None:
        send_notification("Unable to find suitable impedance setting")
    else:
        send_notification(f"Estimated impedance setting: {estimated_impedance}")
    
    return int(estimated_impedance)



'''
def import_calibration_data(voltage, impedance):
    folder_name = 'calibration_data'
    file_name = f'{voltage}_{impedance}.csv'
    file_path = os.path.join(folder_name, file_name)
    data = np.loadtxt(file_path, delimiter=',')
    return data[0], data[1], data[2]

def import_all_calibration_data(voltage):
    calibration_data = {}
    for impedance in ['100', '10000', '100000', '1000000', '10000000']:
        calibration_data[impedance] = import_calibration_data(voltage, impedance)
    return calibration_data
'''


