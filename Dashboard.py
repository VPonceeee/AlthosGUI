import customtkinter as ctk
from pymongo import MongoClient
from bson import ObjectId
import AddGroup
import ViewGroup

# ============================== DATABASE CONNECTION ==============================
try:
    connection_string = "mongodb+srv://altplusf42024:RuVAh3aZgUbC0YLE@altf4cluster.9p2yp.mongodb.net/?retryWrites=true&w=majority&appName=ALTF4Cluster"
    client = MongoClient(connection_string)
    db = client["ADB"]
    groups_collection = db["Groups"]  # Connect to Groups collection
    print("Connected to Groups MongoDB Atlas!")
except Exception as e:
    print("Error connecting to MongoDB:", e)

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, switch_page, AccID, username):
        super().__init__(parent)
        self.switch_page = switch_page
        self.AccID = AccID  
        self.username = username  

        # Make Dashboard fill the entire content panel
        self.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Scrollable Frame
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Default Panel Size
        self.panel_width = 270
        self.panel_padding = 10

        # Store groups data
        self.groups = []

        # Fetch and display groups
        self.fetch_groups()

        # Bind resize event to update layout dynamically
        self.bind("<Configure>", self.on_resize)

    def fetch_groups(self):
        """Fetch groups where CreatedBy matches self.AccID and store them."""
        try:
            if ObjectId.is_valid(self.AccID):
                acc_id_obj = ObjectId(self.AccID)
            else:
                print("Invalid ObjectId format.")
                return

            query = {"CreatedBy": acc_id_obj}
            self.groups = list(groups_collection.find(query))  # Store fetched data

            if self.groups:
                print(f"Groups found for CreatedBy {self.AccID}:")
                self.display_groups()
            else:
                print(f"No groups found for CreatedBy {self.AccID}")
        except Exception as e:
            print("Error fetching groups:", e)

    def display_groups(self):
        """Dynamically create responsive panels with a button and label for each group."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()  # Clear previous widgets

        max_columns = self.calculate_columns()
        if max_columns < 1:
            return

        # Create the '+' button
        plus_panel = ctk.CTkFrame(self.scroll_frame)
        plus_panel.grid(row=0, column=0, padx=self.panel_padding, pady=10, sticky="n")

        button_width = max(200, (self.winfo_width() - 40) // max_columns - (self.panel_padding * 2))

        plus_btn = ctk.CTkButton(
            plus_panel, text="+", width=button_width, height=150, 
            font=("Arial", 24), command=self.show_addgroup
        )
        plus_btn.pack(pady=(10, 5), expand=True)

        plus_lbl = ctk.CTkLabel(plus_panel, text="Add Group", font=("Arial", 14))
        plus_lbl.pack(pady=(0, 10))

        # Add the group buttons
        for i, group in enumerate(self.groups):
            group_name = group.get("GroupName", "Unnamed Group")

            sub_panel = ctk.CTkFrame(self.scroll_frame)
            sub_panel.grid(row=(i + 1) // max_columns, column=(i + 1) % max_columns, padx=self.panel_padding, pady=10, sticky="n")

            group_btn = ctk.CTkButton(
                sub_panel, text=group_name, width=button_width, height=150,
                command=lambda g=group: self.open_group(g)  # Pass full group data
            )
            group_btn.pack(pady=(10, 5), expand=True)

            group_lbl = ctk.CTkLabel(sub_panel, text=group_name, font=("Arial", 14))
            group_lbl.pack(pady=(0, 10))

        # Center align columns
        for col in range(max_columns):
            self.scroll_frame.grid_columnconfigure(col, weight=1)

        self.scroll_frame.update_idletasks()

    def on_resize(self, event=None):
        """Refresh UI layout dynamically on window resize without refetching."""
        self.display_groups()

    def calculate_columns(self):
        """Calculate number of columns dynamically."""
        available_width = self.winfo_width()
        if available_width <= 1:
            return 3
        return max(1, (available_width - 40) // (self.panel_width + self.panel_padding * 2))

    def show_addgroup(self):
        """Open AddGroup and refresh dashboard after closing."""
        self.add_group_window = AddGroup.AddGroup(self, self.AccID, self.username)
        self.add_group_window.focus()

    def open_group(self, group):
        """Switch to ViewGroup with the selected group's ID and name."""
        group_id = str(group.get("_id", "Unknown"))  # Get Group ID
        group_name = group.get("GroupName", "Unnamed Group")
        
        # Pass both GroupID and GroupName
        self.switch_page("ViewGroup", {"GroupID": group_id, "GroupName": group_name})

