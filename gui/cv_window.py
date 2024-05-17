import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from cv import run_cv_experiment

class CVWindow:
    def __init__(self, plot_frame, controls_frame, button_frame):
        self.plot_frame = plot_frame
        self.controls_frame = controls_frame
        self.setup_ui()
        self.figure, self.ax = plt.subplots(figsize=(2, 4))  # Adjust figure size
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_ui(self):
        self.start_button = ttk.Button(self.controls_frame, text="Start CV", command=self.start_experiment)
        self.start_button.pack(pady=10)

    def start_experiment(self):
        self.run_experiment(run_cv_experiment)

    def update_plot(self, x, y):
        self.ax.clear()
        self.ax.plot(x, y)
        self.canvas.draw()

    def run_experiment(self, experiment_func):
        experiment_func(self.update_plot)

    def destroy(self):
        self.ax.clear()
        self.canvas.get_tk_widget().pack_forget()
        self.canvas.get_tk_widget().destroy()
        self.start_button.destroy()