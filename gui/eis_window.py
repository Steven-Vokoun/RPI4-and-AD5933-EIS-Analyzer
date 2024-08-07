import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import os

from Functions.eis import fit_eis_data, export_to_usb, run_demo_EIS_experiment, calibrate_all, set_output_amplitude, conduct_experiment
from Libraries.MUX_and_CLK_Library import Calibration_Mux, Output_Gain_Mux, Input_Gain_Mux, Electrode_Switch, LTC6904
from Libraries.AD5933_Library import AD5933


class EISWindow:
    def __init__(self, plot_frame, controls_frame, button_frame, toolbar_frame):
        self.plot_frame = plot_frame
        self.controls_frame = controls_frame
        self.button_frame = button_frame
        self.toolbar_frame = toolbar_frame

        self.spacing_type = ctk.StringVar(value="logarithmic")
        self.circuit_type = ctk.StringVar(value="Series RC")
        self.voltage = ctk.IntVar(value=1000)
        self.output_location = ctk.StringVar(value="100k")
        self.binary_search = ctk.BooleanVar(value=True)

        self.freq_data = None
        self.real_data = None
        self.imag_data = None
        self.phase_data = None
        self.freq_fit_data = None
        self.real_fit_data = None
        self.imag_fit_data = None

        self.setup_ui()
        self.setup_hardware()
        self.show_temp()

    def setup_ui(self):
        self.setup_calibrate_and_voltage()
        self.setup_freq_and_spacing()
        self.setup_step_size_and_start()
        self.setup_circuit_and_fitting()
        self.setup_plot_and_params()
        self.setup_export_and_notification()
        self.setup_hardware()

    def setup_hardware(self):
        if os.name == 'nt':
            pass
        else:
            self.hardware = self.HardwareComponents()

    class HardwareComponents:
        def __init__(self):
            self.sensor = AD5933()
            self.Calibration_Mux = Calibration_Mux()
            self.Output_Gain_Mux = Output_Gain_Mux()
            self.Input_Gain_Mux = Input_Gain_Mux()
            self.Electrode_Mux = Electrode_Switch()
            self.CLK = LTC6904()
    
    '''
    def Temporary_Test(self):
        self.hardware.Calibration_Mux.select_calibration('100k')
        self.hardware.Electrode_Mux.select_electrode('3 Electrode')
        self.hardware.Output_Gain_Mux.select_gain('1x_uncorrected')
        self.hardware.Input_Gain_Mux.select_gain('10kx')
        self.hardware.sensor.set_output_voltage(1)

        #Calibration
        max_freq = int(self.max_freq_slider.get())
        min_freq = int(self.min_freq_slider.get())
        num_steps = int(self.step_size_slider.get())
        spacing_type = self.spacing_type.get()
        self.send_notification("Calibrating EIS")
        self.hardware.sensor.Calibration_Sweep(100_000, min_freq, max_freq, num_steps, spacing_type=spacing_type)
        self.send_notification("Calibration Complete")

        #Run EIS
        max_freq = int(self.max_freq_slider.get())
        min_freq = int(self.min_freq_slider.get())
        spacing_type = self.spacing_type.get()
        num_steps = int(self.step_size_slider.get())
        self.freq_data, self.real_data, self.imag_data, self.phase = self.hardware.sensor.Sweep_And_Adjust(min_freq, max_freq, num_steps, spacing_type=spacing_type)
        self.send_notification("Experiment Complete")
        self.update_plot()
    '''

    def show_temp(self):
        self.temperature = 25
        if os.name == 'nt':
            pass
        else:
            self.temperature = self.hardware.sensor.measure_temperature()
            self.hardware.sensor.send_cmd('STANDBY')
        
        self.Temperature_Widget = ctk.CTkLabel(self.toolbar_frame, text="Temperature: " + str(self.temperature) + " C")
        self.Temperature_Widget.pack(side=ctk.RIGHT, padx=10)
        self.Temperature_Widget.configure(corner_radius=8)

    def setup_plot(self):
        matplotlib.rcParams['font.size'] = 10
        self.figure, self.ax = plt.subplots(figsize=(4, 3))
        self.figure.subplots_adjust(left=0.2)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    def setup_calibrate_and_voltage(self):
        self.calibrate_voltage_frame = ctk.CTkFrame(self.controls_frame)
        self.calibrate_voltage_frame.pack(pady=3, padx=5, anchor="n", fill=ctk.X)

        self.calibrate_button = ctk.CTkButton(self.calibrate_voltage_frame, text="Calibrate EIS", command=self.calibrate_experiment)
        self.calibrate_button.pack(side=ctk.LEFT, pady=3, padx=1)

        self.voltage_label = ctk.CTkLabel(self.calibrate_voltage_frame, text="Voltage (mV): ")
        self.voltage_label.pack(side=ctk.LEFT, padx=5)
        voltage_values = [str(value) for value in [2, 4, 10, 20, 38, 100, 200, 380, 1000, 2000]]
        self.voltage_dropdown = ctk.CTkComboBox(self.calibrate_voltage_frame, variable=self.voltage, values=voltage_values, command=self.update_voltage)
        self.voltage_dropdown.pack(side=ctk.LEFT, padx=1)

        #self.Temporary_Test_Button = ctk.CTkButton(self.calibrate_voltage_frame, text="Temporary Test", command=self.Temporary_Test)
        #self.Temporary_Test_Button.pack(side=ctk.LEFT, pady=3, padx=10)

    def setup_freq_and_spacing(self):
        self.freq_frame = ctk.CTkFrame(self.controls_frame)
        self.freq_frame.pack(pady=3, padx=5, anchor="n", fill=ctk.X)

        # Min Frequency
        self.min_freq_frame = ctk.CTkFrame(self.freq_frame, width=300)
        self.min_freq_frame.pack(fill=ctk.X)
        self.min_freq_label = ctk.CTkLabel(self.min_freq_frame, text="Min Frequency:")
        self.min_freq_label.pack(side=ctk.LEFT, padx=5)
        self.min_freq_slider = ctk.CTkSlider(self.min_freq_frame, from_=10, to=20000, command=self.update_min_freq_label)
        self.min_freq_slider.set(1000)
        self.min_freq_slider.pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        self.min_freq_value_label = ctk.CTkLabel(self.min_freq_frame, text=f"{self.min_freq_slider.get()}", width=50)
        self.min_freq_value_label.pack(side=ctk.LEFT, padx=2)

        # Max Frequency
        self.max_freq_frame = ctk.CTkFrame(self.freq_frame, width=300)
        self.max_freq_frame.pack(fill=ctk.X)
        self.max_freq_label = ctk.CTkLabel(self.max_freq_frame, text="Max Frequency:")
        self.max_freq_label.pack(side=ctk.LEFT, padx=5)
        self.max_freq_slider = ctk.CTkSlider(self.max_freq_frame, from_=50000, to=200000, command=self.update_max_freq_label)
        self.max_freq_slider.set(100000)
        self.max_freq_slider.pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        self.max_freq_value_label = ctk.CTkLabel(self.max_freq_frame, text=f"{self.max_freq_slider.get()}", width=50)
        self.max_freq_value_label.pack(side=ctk.LEFT, padx=2)

        # Step Size
        self.step_size_frame = ctk.CTkFrame(self.freq_frame, width=300)
        self.step_size_frame.pack(fill=ctk.X)
        self.step_size_label = ctk.CTkLabel(self.step_size_frame, text="Number Of Steps:")
        self.step_size_label.pack(side=ctk.LEFT, padx=5)
        self.step_size_slider = ctk.CTkSlider(self.step_size_frame, from_=1, to=2000, command=self.update_step_size_label)
        self.step_size_slider.set(100)
        self.step_size_slider.pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        self.step_size_value_label = ctk.CTkLabel(self.step_size_frame, text=f"{self.step_size_slider.get()}", width=50)
        self.step_size_value_label.pack(side=ctk.LEFT, padx=2)

        # Estimated Impedance
        self.impedance_frame = ctk.CTkFrame(self.freq_frame, width=300)
        self.impedance_frame.pack(fill=ctk.X)
        self.impedance_label = ctk.CTkLabel(self.impedance_frame, text="Estimated Impedance:")
        self.impedance_label.pack(side=ctk.LEFT, padx=5)
        self.impedance_slider = ctk.CTkSlider(self.impedance_frame, from_=0, to=4, command=self.update_impedance_label)
        self.impedance_slider.set(0)
        self.impedance_slider.pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        self.impedance_value_label = ctk.CTkLabel(self.impedance_frame, text='100', width=50)
        self.impedance_value_label.pack(side=ctk.LEFT, padx=2)
        
        # Spacing Type
        self.spacing_type_frame = ctk.CTkFrame(self.controls_frame)
        self.spacing_type_frame.pack(pady=5, padx=10, anchor="n", fill=ctk.X)

        self.logarithmic_radio = ctk.CTkRadioButton(self.spacing_type_frame, text="Logarithmic Spacing", variable=self.spacing_type, value="logarithmic")
        self.logarithmic_radio.pack(side=ctk.LEFT, padx=10)

        self.linear_radio = ctk.CTkRadioButton(self.spacing_type_frame, text="Linear Spacing", variable=self.spacing_type, value="linear")
        self.linear_radio.pack(side=ctk.LEFT, padx=10)

    def update_min_freq_label(self, value):
        step_value = round(float(value) / 100) * 100
        self.min_freq_value_label.configure(text=f"{step_value}")
        self.min_freq_slider.set(step_value)

    def update_max_freq_label(self, value):
        step_value = round(float(value) / 1000) * 1000
        self.max_freq_value_label.configure(text=f"{step_value}")
        self.max_freq_slider.set(step_value)

    def update_step_size_label(self, value):
        step_value = round(float(value) / 10) * 10
        self.step_size_value_label.configure(text=f"{step_value}")
        self.step_size_slider.set(step_value)

    def update_impedance_label(self, value):
        impedance_values = {0: '100', 1: '10k', 2: '100k', 3: '1Meg', 4: '10Meg'}
        step_value = int(value)
        self.impedance_value_label.configure(text=impedance_values[step_value])
        self.impedance_slider.set(step_value)

    def setup_step_size_and_start(self):
        self.start_fitting_frame = ctk.CTkFrame(self.controls_frame)
        self.start_fitting_frame.pack(pady=3, padx=10, anchor="n", fill=ctk.X)

        self.start_button = ctk.CTkButton(self.start_fitting_frame, text="Start EIS", command=self.start_experiment)
        self.start_button.pack(side=ctk.LEFT, pady=3, padx=3, fill=ctk.X)

        locations = ['Counter0', 'Counter1', 'Randles', '100', '10k', '100k', '1Meg', '10Meg']
        self.output_location_dropdown = ctk.CTkComboBox(self.start_fitting_frame, variable=self.output_location, values=locations)
        self.output_location_dropdown.pack(side=ctk.LEFT, pady=3, padx=3, fill=ctk.X)

        self.binary_search_checkbox = ctk.CTkCheckBox(self.start_fitting_frame, variable = self.binary_search, text="Auto Gain")
        self.binary_search_checkbox.pack(side=ctk.LEFT, pady=3, padx=3)

    def setup_circuit_and_fitting(self):
        self.circuit_type_frame = ctk.CTkFrame(self.controls_frame)
        self.circuit_type_frame.pack(pady=3, padx=5, anchor="n", fill=ctk.X)

        self.left_frame = ctk.CTkFrame(self.circuit_type_frame)
        self.left_frame.pack(side=ctk.LEFT, pady=3, padx=5)

        self.run_fitting_button = ctk.CTkButton(self.left_frame, text="Run Fitting", command=self.run_fitting)
        self.run_fitting_button.pack(pady=3, padx=5, fill=ctk.X)

        self.circuit_type_dropdown = ctk.CTkComboBox(self.left_frame, variable=self.circuit_type, values=["Series RC", "Parallel RC", "Randles", "Randles With CPE"])
        self.circuit_type_dropdown.pack(pady=3, padx=5)

        self.params_display = ctk.CTkTextbox(self.circuit_type_frame, height=80, width=250)
        self.params_display.pack(side=ctk.LEFT, pady=2, padx=5)


    def setup_plot_and_params(self):
        self.plot_type = ctk.StringVar(value="mag_vs_freq")

        self.freq_mag_button = ctk.CTkRadioButton(self.button_frame, text="Magnitude vs Frequency", variable=self.plot_type, value="mag_vs_freq", command=self.update_plot)
        self.freq_mag_button.pack(side=ctk.LEFT, padx=5)

        self.freq_phase_button = ctk.CTkRadioButton(self.button_frame, text="Phase vs Frequency", variable=self.plot_type, value="phase_vs_freq", command=self.update_plot)
        self.freq_phase_button.pack(side=ctk.LEFT, padx=5)

        self.real_imag_button = ctk.CTkRadioButton(self.button_frame, text="Imaginary vs Real", variable=self.plot_type, value="imag_vs_real", command=self.update_plot)
        self.real_imag_button.pack(side=ctk.LEFT, padx=5)

        self.real_freq_button = ctk.CTkRadioButton(self.button_frame, text="Real vs Frequency", variable=self.plot_type, value="real_vs_freq", command=self.update_plot)
        self.real_freq_button.pack(side=ctk.LEFT, padx=5)

        self.imag_freq_button = ctk.CTkRadioButton(self.button_frame, text="Imaginary vs Frequency", variable=self.plot_type, value="imag_vs_freq", command=self.update_plot)
        self.imag_freq_button.pack(side=ctk.LEFT, padx=5)

        self.setup_plot()

    def setup_export_and_notification(self):
        self.export_frame = ctk.CTkFrame(self.controls_frame)
        self.export_frame.pack(pady=3, padx=5, anchor="n", fill=ctk.X)

        self.export_button = ctk.CTkButton(self.export_frame, text="Export Data", command=self.export_data)
        self.export_button.pack(side=ctk.LEFT, pady=3, padx=5)

        self.notification_box = ctk.CTkTextbox(self.export_frame, height=80, width=275)
        self.notification_box.pack(side=ctk.LEFT, padx=2)
        self.notification_box.insert(ctk.END, "Welcome! Please calibrate your device.")

    def send_notification(self, message, newline=True):
        if newline is True:
            message = "\n" + message
        self.notification_box.insert(ctk.END, message)
        self.notification_box.see(ctk.END)

    # External Calls
    def export_data(self):
        # make sure there is actually data to export
        if self.freq_data is None:
            self.send_notification("No data to export. Please run an experiment first.")
        else:
            export_to_usb(self.send_notification, self.freq_data, self.real_data, self.imag_data)
    
    def update_voltage(self, why):
        set_output_amplitude(self.voltage.get(), self.hardware.sensor, self.hardware.Output_Gain_Mux, self.send_notification)

    # Experiments
    def calibrate_experiment(self):
        max_freq = int(self.max_freq_slider.get())
        min_freq = int(self.min_freq_slider.get())
        spacing_type = self.spacing_type.get()
        num_steps = int(self.step_size_slider.get())
        voltage = self.voltage.get()
        calibrate_all(voltage, min_freq, max_freq, self.hardware, self.send_notification, num_steps, spacing_type)

    def start_experiment(self):
        if os.name == 'nt':
            run_demo_EIS_experiment(self.update_data, int(self.min_freq_slider.get()), int(self.max_freq_slider.get()), self.spacing_type.get(), int(self.step_size_slider.get()))
            self.send_notification("Demo Experiment Complete")
        else:
            max_freq = int(self.max_freq_slider.get())
            min_freq = int(self.min_freq_slider.get())
            spacing_type = self.spacing_type.get()
            num_steps = int(self.step_size_slider.get())
            voltage = self.voltage.get()
            estimated_impedance = self.impedance_slider.get()
            output_location = self.output_location.get()
            binary_search = self.binary_search.get()
            self.freq_data, self.real_data, self.imag_data, self.phase = conduct_experiment(self.hardware, self.send_notification, voltage, estimated_impedance, min_freq, max_freq, num_steps, spacing_type, output_location, binary_search)
            self.update_plot()

    def run_fitting(self):
        circuit = self.circuit_type.get()
        real_fit, imag_fit, fitted_params, Labels = fit_eis_data(self.freq_data, self.real_data, self.imag_data, circuit)
        self.update_fit_data(real_fit, imag_fit, fitted_params, Labels)
        self.send_notification("Fitting Complete")

    # Update Data and Plots
    def update_data(self, freq_data, real_data, imag_data):
        self.freq_data = freq_data
        self.real_data = real_data
        self.imag_data = imag_data
        self.phase = np.rad2deg(np.arctan2(imag_data, real_data))
        self.update_plot()

    def update_fit_data(self, real_fit, imag_fit, fitted_params, Labels):
        self.freq_fit_data = self.freq_data
        self.real_fit_data = real_fit
        self.imag_fit_data = imag_fit
        self.params_display.delete(1.0, ctk.END)
        self.params_display.insert(ctk.END, f"Fitted Parameters:\n{Labels}\n{fitted_params}")
        self.update_plot()

    def update_plot(self):
        plot_type = self.plot_type.get()
        if plot_type == "mag_vs_freq":
            self.plot_freq_vs_mag()
        elif plot_type == "phase_vs_freq":
            self.plot_freq_vs_phase()
        elif plot_type == "imag_vs_real":
            self.plot_real_vs_imag()
        elif plot_type == "real_vs_freq":
            self.plot_freq_vs_real()
        elif plot_type == "imag_vs_freq":
            self.plot_freq_vs_imag()

    def plot_freq_vs_mag(self):
        self.ax.clear()
        self.ax.scatter(self.freq_data, np.sqrt(self.real_data**2 + self.imag_data**2), s=5)
        if self.freq_fit_data is not None:
            self.ax.plot(self.freq_fit_data, np.sqrt(self.real_fit_data**2 + self.imag_fit_data**2), color='red')
        self.ax.set_xscale("log")
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Magnitude")
        self.ax.set_title("Magnitude vs Frequency")
        self.canvas.draw()

    def plot_freq_vs_phase(self):
        self.ax.clear()
        self.ax.scatter(self.freq_data, self.phase, s=5)
        if self.freq_fit_data is not None:
            self.ax.plot(self.freq_fit_data, np.rad2deg(np.arctan2(self.imag_fit_data, self.real_fit_data)), color='red')
        self.ax.set_xscale("log")
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Phase")
        self.ax.set_title("Phase vs Frequency")
        self.canvas.draw()

    def plot_real_vs_imag(self):
        self.ax.clear()
        self.ax.scatter(self.real_data, -self.imag_data, s=5)
        if self.real_fit_data is not None:
            self.ax.plot(self.real_fit_data, -self.imag_fit_data, color='red')
        self.ax.set_xlabel("Real")
        self.ax.set_ylabel("Imaginary")
        self.ax.set_title("Imaginary vs Real")
        self.canvas.draw()

    def plot_freq_vs_real(self):
        self.ax.clear()
        self.ax.scatter(self.freq_data, abs(self.real_data), s=5)
        if self.freq_fit_data is not None:
            self.ax.plot(self.freq_fit_data, abs(self.real_fit_data), color='red')
        self.ax.set_xscale("log")
        self.ax.set_yscale("log")
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Real")
        self.ax.set_title("Real vs Frequency")
        self.canvas.draw()

    def plot_freq_vs_imag(self):
        self.ax.clear()
        self.ax.scatter(self.freq_data, abs(self.imag_data), s=5)
        if self.freq_fit_data is not None:
            self.ax.plot(self.freq_fit_data, abs(self.imag_fit_data), color='red')
        self.ax.set_xscale("log")
        self.ax.set_yscale("log")
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Imaginary")
        self.ax.set_title("Imaginary vs Frequency")
        self.canvas.draw()

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            if widget.winfo_children():
                self.clear_frame(widget)
            widget.destroy()

    def destroy(self):
        self.ax.clear()
        self.canvas.get_tk_widget().pack_forget()
        self.canvas.get_tk_widget().destroy()
        self.clear_frame(self.controls_frame)
        self.clear_frame(self.button_frame)
        self.clear_frame(self.plot_frame)
        self.Temperature_Widget.destroy()
