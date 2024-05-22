import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from eis import fit_eis_data
from eis import export_to_usb
from eis import run_demo_EIS_experiment
import numpy as np
import matplotlib
import os

class EISWindow:
    def __init__(self, plot_frame, controls_frame, button_frame, sensor):
        self.plot_frame = plot_frame
        self.controls_frame = controls_frame
        self.button_frame = button_frame
        self.spacing_type = tk.StringVar(value="logarithmic")
        self.circuit_type = tk.StringVar(value="Series RC")
        self.freq_data = None
        self.real_data = None
        self.imag_data = None
        self.phase_data = None
        self.freq_fit_data = None
        self.real_fit_data = None
        self.imag_fit_data = None
        self.sensor = sensor        
        self.setup_ui()

    def setup_ui(self):
        self.setup_calibrate_button()
        self.setup_freq_frame()
        self.setup_spacing_type_frame()
        self.setup_step_size()
        self.setup_start_button()
        self.setup_circuit_type_dropdown()
        self.setup_run_fitting_button()
        self.setup_plot_type_buttons()
        self.setup_plot()
        self.setup_params_display()
        self.setup_export_button()
        self.setup_notification_box()
        

    def setup_plot(self):
        matplotlib.rcParams['font.size'] = 5
        self.figure, self.ax = plt.subplots(figsize=(2, 4))
        self.figure.subplots_adjust(left=0.2)
        self.figure.subplots_adjust(bottom=0.2)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_calibrate_button(self):
        self.calibrate_button = ttk.Button(self.controls_frame, text="Calibrate EIS", command=self.calibrate_experiment)
        self.calibrate_button.pack(pady=5, padx=10, anchor="n", fill=tk.X)

    def setup_freq_frame(self):
        self.freq_frame = ttk.Frame(self.controls_frame)
        self.freq_frame.pack(pady=5, padx=10, anchor="n", fill=tk.X)

        self.min_freq_label = tk.Label(self.freq_frame, text="Min Frequency:")
        self.min_freq_label.grid(row=0, column=0)
        self.min_freq_entry = tk.Entry(self.freq_frame, width=10)
        self.min_freq_entry.insert(0, "10000")
        self.min_freq_entry.grid(row=0, column=1)

        self.max_freq_label = tk.Label(self.freq_frame, text="Max Frequency:")
        self.max_freq_label.grid(row=0, column=2)
        self.max_freq_entry = tk.Entry(self.freq_frame, width=10)
        self.max_freq_entry.insert(0, "100000")
        self.max_freq_entry.grid(row=0, column=3)

    def setup_spacing_type_frame(self):
        self.spacing_type_frame = ttk.Frame(self.controls_frame)
        self.spacing_type_frame.pack(pady=5, padx=10, anchor="n", fill=tk.X)

        self.logarithmic_radio = ttk.Radiobutton(self.spacing_type_frame, text="Logarithmic Spacing", variable=self.spacing_type, value="logarithmic")
        self.logarithmic_radio.pack(side=tk.LEFT)

        self.linear_radio = ttk.Radiobutton(self.spacing_type_frame, text="Linear Spacing", variable=self.spacing_type, value="linear")
        self.linear_radio.pack(side=tk.LEFT)

    def setup_step_size(self):
        self.step_size_frame = tk.Frame(self.controls_frame)
        self.step_size_frame.pack(pady=5, padx=10, anchor="n", fill=tk.X)

        self.step_size_label = tk.Label(self.step_size_frame, text="Number Of Steps:")
        self.step_size_label.pack(side=tk.LEFT)

        self.step_size_entry = tk.Entry(self.step_size_frame, width=10)
        self.step_size_entry.insert(0, "100")
        self.step_size_entry.pack(side=tk.LEFT)

    def setup_start_button(self):
        self.start_button = ttk.Button(self.controls_frame, text="Start EIS", command=self.start_experiment)
        self.start_button.pack(pady=5, padx=10, anchor="n", fill=tk.X)

    def setup_plot_type_buttons(self):
        self.plot_type = tk.StringVar(value="freq_vs_mag")

        self.freq_mag_button = ttk.Radiobutton(self.button_frame, text="Frequency vs Magnitude", variable=self.plot_type, value="freq_vs_mag", command=self.update_plot)
        self.freq_mag_button.pack(side=tk.LEFT, padx=10)

        self.freq_phase_button = ttk.Radiobutton(self.button_frame, text="Frequency vs Phase", variable=self.plot_type, value="freq_vs_phase", command=self.update_plot)
        self.freq_phase_button.pack(side=tk.LEFT, padx=10)

        self.real_imag_button = ttk.Radiobutton(self.button_frame, text="Real Vs Imaginary", variable=self.plot_type, value="real_vs_imag", command=self.update_plot)
        self.real_imag_button.pack(side=tk.LEFT, padx=10)

    def setup_circuit_type_dropdown(self):
        self.circuit_type_dropdown = ttk.Combobox(self.controls_frame, textvariable=self.circuit_type)
        self.circuit_type_dropdown['values'] = ("Series RC", "Parallel RC", "Randles", "Randles With CPE")
        self.circuit_type_dropdown.pack(pady=5, padx=10, anchor="n", fill=tk.X)

    def setup_run_fitting_button(self):
        self.run_fitting_button = ttk.Button(self.controls_frame, text="Run Fitting", command=self.run_fitting)
        self.run_fitting_button.pack(pady=5, padx=10, anchor="n", fill=tk.X)

    def setup_params_display(self):
        self.params_display = tk.Text(self.controls_frame, height=3, width=10)
        self.params_display.pack(pady=5, padx=10, fill = tk.X)
        self.params_display.insert(tk.END, 'Fitting Parameters Window:')

    def setup_export_button(self):
        self.export_button = ttk.Button(self.controls_frame, text="Export Data", command=self.export_data)
        self.export_button.pack(pady=5, padx=10, anchor="n", fill=tk.X)
    
    def export_data(self):
        export_to_usb(self.send_notification, self.freq_data, self.real_data, self.imag_data)
    
    def setup_notification_box(self):
        self.notification_box = tk.Text(self.controls_frame, height=4, width=10)
        self.notification_box.pack(pady=5, padx=10, fill = tk.X)
        self.notification_box.insert(tk.END, "Notifications:")

    def send_notification(self, message):
        print(message)
        message = "\n" + message
        self.notification_box.insert(tk.END, message)
        self.notification_box.see(tk.END)

    def calibrate_experiment(self):
        max_freq = int(self.max_freq_entry.get())
        min_freq = int(self.min_freq_entry.get())
        num_steps = int(self.step_size_entry.get())
        spacing_type = self.spacing_type.get()
        self.send_notification("Calibrating EIS")
        self.sensor.Calibration_Sweep(220_000, min_freq, max_freq, num_steps, spacing_type=spacing_type)
        self.send_notification("Calibration Complete")

    def start_experiment(self):
        if os.name == 'nt':
            run_demo_EIS_experiment(self.update_data, 10000, 100000, 'linear', 200)
            self.send_notification("Demo Experiment Complete")
        else:
            max_freq = int(self.max_freq_entry.get())
            min_freq = int(self.min_freq_entry.get())
            spacing_type = self.spacing_type.get()
            num_steps = int(self.step_size_entry.get())
            self.freq_data, self.real_data, self.imag_data, self.phase = self.sensor.Sweep_And_Adjust(min_freq, max_freq, num_steps, spacing_type=spacing_type)
            self.send_notification("Experiment Complete")
            self.update_plot()

    def run_fitting(self):
        circuit = self.circuit_type.get()
        real_fit, imag_fit, fitted_params, Labels = fit_eis_data(self.freq_data, self.real_data, self.imag_data, circuit)
        self.update_fit_data(real_fit, imag_fit, fitted_params, Labels)
        self.send_notification("Fitting Complete")

    def update_data(self, freq_data, real_data, imag_data):
        self.freq_data = freq_data
        self.real_data = real_data
        self.imag_data = imag_data
        self.update_plot()
    
    def update_fit_data(self, real_fit, imag_fit, fitted_params, Labels):
        self.freq_fit_data = self.freq_data
        self.real_fit_data = real_fit
        self.imag_fit_data = imag_fit
        self.params_display.delete(1.0, tk.END)
        self.params_display.insert(tk.END, f"Fitted Parameters:\n{Labels}\n{fitted_params}")
        self.update_plot()

    def update_plot(self):
        plot_type = self.plot_type.get()

        if plot_type == "freq_vs_mag":
            self.plot_freq_vs_mag()
        elif plot_type == "freq_vs_phase":
            self.plot_freq_vs_phase()
        elif plot_type == "real_vs_imag":
            self.plot_real_vs_imag()

    def plot_freq_vs_mag(self):
        self.ax.clear()
        self.ax.scatter(self.freq_data, np.sqrt(self.real_data**2 + self.imag_data**2), s=5)
        if self.freq_fit_data is not None:
            self.ax.plot(self.freq_fit_data, np.sqrt(self.real_fit_data**2 + self.imag_fit_data**2), color='red')
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Magnitude")
        self.ax.set_title("Frequency vs Magnitude")
        self.canvas.draw()

    def plot_freq_vs_phase(self):
        self.ax.clear()
        self.ax.scatter(self.freq_data, self.phase, s=5)
        if self.freq_fit_data is not None:
            self.ax.plot(self.freq_fit_data, np.rad2deg(np.arctan2(self.imag_fit_data,self.real_fit_data)), color='red')
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Phase")
        self.ax.set_title("Frequency vs Phase")
        self.canvas.draw()

    def plot_real_vs_imag(self):
        self.ax.clear()
        self.ax.scatter(self.real_data, self.imag_data, s=5)
        if self.real_fit_data is not None:
            self.ax.plot(self.real_fit_data, self.imag_fit_data, color='red')
        self.ax.set_xlabel("Real")
        self.ax.set_ylabel("Imaginary")
        self.ax.set_title("Real vs Imaginary")
        self.canvas.draw()

    def destroy(self):
        self.ax.clear()
        self.canvas.get_tk_widget().pack_forget()
        self.canvas.get_tk_widget().destroy()
        self.calibrate_button.destroy()
        self.max_freq_label.destroy()
        self.max_freq_entry.destroy()
        self.min_freq_label.destroy()
        self.min_freq_entry.destroy()
        self.logarithmic_radio.destroy()
        self.linear_radio.destroy()
        self.step_size_label.destroy()
        self.step_size_entry.destroy()
        self.start_button.destroy()
        self.freq_mag_button.destroy()
        self.freq_phase_button.destroy()
        self.real_imag_button.destroy()
        self.spacing_type_frame.destroy()
        self.circuit_type_dropdown.destroy()
        self.run_fitting_button.destroy()
        self.params_display.destroy()