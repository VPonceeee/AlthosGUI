import customtkinter as ctk
import subprocess

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, switch_page):
        super().__init__(parent)  # Parent is content_panel
        self.switch_page = switch_page

        # Make Dashboard fill the entire content panel
        self.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)  # Allow content inside to expand
        self.columnconfigure(0, weight=1)

        # Add Panel
        panel = ctk.CTkFrame(self)#fg_color="red"
        panel.grid(row=0, column=0, sticky="nsew")  # Make it expand and fill space
        panel.rowconfigure(0, weight=1)
        panel.columnconfigure(0, weight=1)

        # Sub-panel
        sub_panel = ctk.CTkFrame(panel, width=270, height=170,fg_color="transparent")
        sub_panel.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        # Center content inside sub-panel
        sub_panel.grid_propagate(False)  # Prevent resizing based on child widgets
        sub_panel.rowconfigure(0, weight=1)
        sub_panel.rowconfigure(1, weight=1)
        sub_panel.columnconfigure(0, weight=1)

        #
        add_btn = ctk.CTkButton(sub_panel, text="+", width=250, height=150, command=self.show_addgroup)
        add_btn.grid(row=0, column=0, pady=(10, 5)) 

        # "add" Label
        add_lbl = ctk.CTkLabel(sub_panel, text="ADD", font=("Arial", 14))
        add_lbl.grid(row=1, column=0, pady=(0, 10))

    def show_addgroup(self):
        subprocess.Popen(["python", "AddGroup.py"])  # Opens AddGroup.py as a new process
 
