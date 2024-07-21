import customtkinter as ctk
import os
from gui.eis_window import EISWindow
from gui.cv_window import CVWindow
from gui.time_window import TimeWindow

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Experiment GUI")
        self.geometry("800x480")
        self._set_appearance_mode("dark")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.attributes("-fullscreen", True)

        self.current_window = None
        self.previous_selection = "EIS"
        self.setup_main_frame()
        self.setup_toolbar()
        self.setup_frames()
        self.on_selection_change("EIS")

    def setup_main_frame(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill = ctk.BOTH, expand = True)
        self.readme_text_area = None

    def setup_toolbar(self):
        self.toolbar_frame = ctk.CTkFrame(self.main_frame)
        self.toolbar_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        label = ctk.CTkLabel(self.toolbar_frame, text="Select Experiment:")
        label.pack(side=ctk.LEFT, padx=10)

        self.dropdown = ctk.CTkComboBox(self.toolbar_frame, values=["EIS", "CV", "Time"], command=self.on_selection_change)
        self.dropdown.pack(side=ctk.LEFT, padx=10)

        readme_button = ctk.CTkButton(self.toolbar_frame, text="Open README", command=self.open_readme)
        readme_button.pack(side=ctk.LEFT, padx=10)

        close_button = ctk.CTkButton(self.toolbar_frame, text="Close", command=self.on_close)
        close_button.pack(side=ctk.RIGHT, padx=10)

    def setup_frames(self):
        self.plot_frame = ctk.CTkFrame(self.main_frame)
        self.plot_frame.grid(row=1, column=0, sticky="nsew")

        self.controls_frame = ctk.CTkFrame(self.main_frame)
        self.controls_frame.grid(row=1, column=1, sticky="nsew")

        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

    def on_selection_change(self, selection):
        self.previous_selection = selection
        if self.current_window:
            self.current_window.destroy()
        if selection == "EIS":
            self.current_window = EISWindow(self.plot_frame, self.controls_frame, self.button_frame, self.toolbar_frame)
        elif selection == "CV":
            self.current_window = CVWindow(self.plot_frame, self.controls_frame, self.button_frame, self.toolbar_frame)
        elif selection == "Time":
            self.current_window = TimeWindow(self.plot_frame, self.controls_frame, self.button_frame, self.toolbar_frame)

    def open_readme(self):
        if self.current_window:
            self.current_window.destroy()

        self.current_window = ctk.CTkFrame(self.main_frame)
        self.current_window.grid(row=1, column=0, columnspan=2, rowspan=2, sticky="nsew")

        self.current_window.grid_columnconfigure(0, weight=1)
        self.current_window.grid_rowconfigure(0, weight=1)

        self.readme_text_area = ctk.CTkTextbox(self.current_window, wrap=ctk.WORD, activate_scrollbars=True)
        self.readme_text_area.grid(row=0, column=0, sticky="nsew")

        self.button_frame_readme = ctk.CTkFrame(self.main_frame)
        self.button_frame_readme.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        close_readme_button = ctk.CTkButton(self.button_frame_readme, text="Close README", command=self.close_readme)
        close_readme_button.pack(side=ctk.BOTTOM, pady=10)

        try:
            with open("readme.md", "r") as file:
                content = file.read()
                self.readme_text_area.insert(ctk.END, content)
        except FileNotFoundError:
            self.readme_text_area.insert(ctk.END, "README.md file not found")

    def close_readme(self):
        if self.current_window:
            self.current_window.destroy()
        if hasattr(self, 'button_frame_readme'):
            self.button_frame_readme.destroy()
        self.on_selection_change(self.previous_selection)

    def on_close(self):
        os._exit(0)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
