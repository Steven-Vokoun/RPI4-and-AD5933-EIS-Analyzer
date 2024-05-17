import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from eis import run_eis_experiment
import numpy as np
import matplotlib

class EISWindow:
    def __init__(self, plot_frame, controls_frame, button_frame):
        self.plot_frame = plot_frame
        self.controls_frame = controls_frame
        self.button_frame = button_frame
        self.spacing_type = tk.StringVar(value="logarithmic")
        self.circuit_type = tk.StringVar(value="series RC")
        self.setup_ui()
        self.setup_plot()
        self.freq_data = None
        self.real_data = None
        self.imag_data = None

    def setup_ui(self):
        self.setup_calibrate_button()
        self.setup_freq_frame()
        self.setup_spacing_type_frame()
        self.setup_step_size()
        self.setup_start_button()
        self.setup_circuit_type_dropdown()
        self.setup_run_fitting_button()
        self.setup_plot_type_buttons()

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
        self.min_freq_entry.insert(0, "100")
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

        self.freq_phase_button = ttk.Radiobutton(self.button_frame, text="Real Vs Imaginary", variable=self.plot_type, value="real_vs_imag", command=self.update_plot)
        self.freq_phase_button.pack(side=tk.LEFT, padx=10)

    def setup_circuit_type_dropdown(self):
        self.circuit_type_dropdown = ttk.Combobox(self.controls_frame, textvariable=self.circuit_type)
        self.circuit_type_dropdown['values'] = ("series RC", "parallel RC", "Randles", "Randles with CPE")
        self.circuit_type_dropdown.pack(pady=5, padx=10, anchor="n", fill=tk.X)

    def setup_run_fitting_button(self):
        self.run_fitting_button = ttk.Button(self.controls_frame, text="Run Fitting", command=self.run_fitting)
        self.run_fitting_button.pack(pady=5, padx=10, anchor="n", fill=tk.X)

    def calibrate_experiment(self):
        """Placeholder for calibrate EIS button functionality."""
        pass

    def start_experiment(self):
        # Retrieve and validate the input values
        max_freq = int(self.max_freq_entry.get())
        min_freq = int(self.min_freq_entry.get())
        spacing_type = self.spacing_type.get()
        num_steps = int(self.step_size_entry.get())

        # Implement the logic to handle these parameters in the experiment
        run_eis_experiment(self.update_data, max_freq, min_freq, spacing_type, num_steps)

    def run_fitting(self):
        """Placeholder for run fitting button functionality."""
        pass

    def update_data(self, freq_data, real_data, imag_data):
        # Update data variables
        self.freq_data = freq_data
        self.real_data = real_data
        self.imag_data = imag_data

        # Update plot
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
        self.ax.plot(self.freq_data, np.sqrt(self.real_data**2 + self.imag_data**2))
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Magnitude")
        self.ax.set_title("Frequency vs Magnitude")
        self.canvas.draw()

    def plot_freq_vs_phase(self):
        self.ax.clear()
        self.ax.plot(self.freq_data, np.arctan(self.imag_data/self.real_data))
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Phase")
        self.ax.set_title("Frequency vs Phase")
        self.canvas.draw()

    def plot_real_vs_imag(self):
        self.ax.clear()
        self.ax.plot(self.real_data, -self.imag_data)
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
        self.plot_frame.destroy()
        self.controls_frame.destroy()
        self.button_frame.destroy()
        self.freq_frame.destroy()
        self.spacing_type_frame.destroy()
        self.circuit_type_dropdown.destroy()
        self.run_fitting_button.destroy()
