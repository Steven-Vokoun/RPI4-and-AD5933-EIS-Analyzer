import time
import numpy as np

def run_time_experiment(update_plot_callback):
    # Dummy example of an experiment that updates the plot
    for i in range(100):
        x = np.linspace(0, 10, 100)
        y = np.tan(x + i * 0.1)
        update_plot_callback(x, y)
        time.sleep(0.1)
