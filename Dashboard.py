import customtkinter as ctk
import subprocess
from pymongo import MongoClient
from bson import ObjectId  # Required for handling ObjectId

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
        self.acc_id = AccID  
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
        self.panel_padding = 10  # Adjusted padding

        # Fetch and display groups
        self.fetch_groups()

        # Bind resize event to update layout dynamically
        self.bind("<Configure>", self.on_resize)

    def fetch_groups(self):
        """Fetch groups where CreatedBy matches self.acc_id and display them."""
        try:
            if ObjectId.is_valid(self.acc_id):
                acc_id_obj = ObjectId(self.acc_id)
            else:
                print("Invalid ObjectId format.")
                return

            query = {"CreatedBy": acc_id_obj}
            groups = list(groups_collection.find(query))

            if groups:
                print(f"Groups found for CreatedBy {self.acc_id}:")
                self.display_groups(groups)
            else:
                print(f"No groups found for CreatedBy {self.acc_id}")
        except Exception as e:
            print("Error fetching groups:", e)

    def display_groups(self, groups):
        """Dynamically create responsive panels with a button and label for each group."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()  # Clear previous widgets

        max_columns = self.calculate_columns()  # Dynamically determine columns
        total_items = len(groups)
        
        # Calculate starting column index for centering
        for i, group in enumerate(groups):
            group_name = group.get("GroupName", "Unnamed Group")

            # Create a sub-panel for the group
            sub_panel = ctk.CTkFrame(self.scroll_frame)
            sub_panel.grid(row=i // max_columns, column=i % max_columns, padx=self.panel_padding, pady=10, sticky="n")

            # Group button
            group_btn = ctk.CTkButton(sub_panel, text=group_name, width=250, height=150, command=lambda g=group_name: self.open_group(g))
            group_btn.pack(pady=(10, 5), expand=True)

            # Group label
            group_lbl = ctk.CTkLabel(sub_panel, text=group_name, font=("Arial", 14))
            group_lbl.pack(pady=(0, 10))

        # Center align by setting column weights
        for col in range(max_columns):
            self.scroll_frame.grid_columnconfigure(col, weight=1)

        self.scroll_frame.update_idletasks()

    def on_resize(self, event=None):
        """Recalculate column count and refresh UI when resizing."""
        self.display_groups(list(groups_collection.find({"CreatedBy": ObjectId(self.acc_id)})))

    def calculate_columns(self):
        """Calculate the number of columns based on the available width."""
        available_width = self.winfo_width()
        if available_width <= 1:  # Prevent division error when minimized
            return 3  # Default fallback

        max_columns = max(1, (available_width - 40) // (self.panel_width + self.panel_padding * 2))
        return max_columns

    def open_group(self, group_name):
        """Placeholder function when clicking a group button."""
        print(f"Opening group: {group_name}")

    def show_addgroup(self):
        subprocess.Popen(["python", "AddGroup.py"])  # Opens AddGroup.py as a new process
