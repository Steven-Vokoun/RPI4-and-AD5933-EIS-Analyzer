import tkinter as tk
from tkinter import ttk
from gui.eis_window import EISWindow
from gui.cv_window import CVWindow
from gui.time_window import TimeWindow
import tkinter as tk
from tkinter import ttk, filedialog
import os

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Experiment GUI")
        self.geometry("800x480")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.toolbar_frame = tk.Frame(self.main_frame)
        self.toolbar_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.plot_frame = tk.Frame(self.main_frame)
        self.plot_frame.grid(row=1, column=0, sticky="nsew")

        self.controls_frame = tk.Frame(self.main_frame)
        self.controls_frame.grid(row=1, column=1, sticky="nsew")

        # Adjust column weights to balance the layout
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Set a minimum width for the controls frame
        self.controls_frame.grid_propagate(False)
        self.controls_frame.config(width=200)

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.current_window = None
        self.setup_ui()
        self.default_to_eis_window()

    def setup_ui(self):
        self.label = ttk.Label(self.toolbar_frame, text="Select Experiment:")
        self.label.pack(side=tk.LEFT, padx=10)

        self.dropdown = ttk.Combobox(self.toolbar_frame, values=["EIS", "CV", "Time"])
        self.dropdown.pack(side=tk.LEFT, padx=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_selection_change)

        self.readme_button = ttk.Button(self.toolbar_frame, text="Open README", command=self.open_readme)
        self.readme_button.pack(side=tk.LEFT, padx=10)

    def default_to_eis_window(self):
        self.dropdown.set("EIS")
        self.on_selection_change(None)

    def on_selection_change(self, event):
        selection = self.dropdown.get()
        if self.current_window:
            self.current_window.destroy()

        if selection == "EIS":
            self.current_window = EISWindow(self.plot_frame, self.controls_frame, self.button_frame)
        elif selection == "CV":
            self.current_window = CVWindow(self.plot_frame, self.controls_frame, self.button_frame)
        elif selection == "Time":
            self.current_window = TimeWindow(self.plot_frame, self.controls_frame, self.button_frame)

    def open_readme(self):
        new_window = tk.Toplevel(self)
        new_window.title("README.txt")
        new_window.geometry("800x480")

        text_area = tk.Text(new_window, wrap=tk.WORD)
        text_area.pack(expand=True, fill=tk.BOTH)

        try:
            with open("readme.md", "r") as file:
                content = file.read()
                text_area.insert(tk.END, content)
        except FileNotFoundError:
            text_area.insert(tk.END, "README.txt file not found")

    def on_close(self):
        os._exit(0)
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()