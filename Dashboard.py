import customtkinter as ctk

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, switch_page):
        super().__init__(parent)  # Parent is content_panel
        self.switch_page = switch_page

        # Add Button
        Add_btn = ctk.CTkButton(
            master=self,
            text="+",
            width=250,
            height=150,
            border_width=2,
            font=("Arial", 100, "bold"),
            command=lambda: self.switch_page("GroupForm")  # Navigate to GroupForm
        )
        Add_btn.pack(
            pady=20,
            padx=20,
            anchor="center",
            expand=True
        )
