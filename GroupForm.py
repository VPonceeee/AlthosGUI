import customtkinter as ctk

class GroupForm(ctk.CTkFrame):
    def __init__(self, parent, switch_page):
        super().__init__(parent)  # Parent is content_panel
        self.switch_page = switch_page


        label = ctk.CTkLabel(self, text="Group Page", font=("Arial", 20))
        label.pack(pady=20)

        back_button = ctk.CTkButton(
            master=self,
            text="Back to Dashboard",
            command=lambda: self.switch_page("Dashboard")
        )
        back_button.pack(pady=10)
