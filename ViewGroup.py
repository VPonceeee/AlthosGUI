import customtkinter as ctk
from pymongo import MongoClient
from bson import ObjectId
import AddMember

# ============================== DATABASE CONNECTION ==============================
try:
    connection_string = "mongodb+srv://altplusf42024:RuVAh3aZgUbC0YLE@altf4cluster.9p2yp.mongodb.net/?retryWrites=true&w=majority&appName=ALTF4Cluster"
    client = MongoClient(connection_string)
    db = client["ADB"]
    devices_collection = db["Members"]  # Ensure correct collection name
    print("Connected to Members MongoDB Atlas!")
except Exception as e:
    print("Error connecting to MongoDB:", e)

class ViewGroup(ctk.CTkFrame):
    def __init__(self, parent, switch_page, group_id="Unknown", group_name="Group Pages"):
        super().__init__(parent)
        self.switch_page = switch_page
        self.group_id = group_id 
        self.group_name = group_name  

        self.devices = []  
        self.panel_padding = 10  
        self.panel_width = 200  

        # Top Frame
        self.top_frame = ctk.CTkFrame(self, height=50)
        self.top_frame.pack(fill="x", side="top", padx=10, pady=2)

        # Back Button
        self.back_button = ctk.CTkButton(
            self.top_frame, text="← Back", width=80,
            command=lambda: self.switch_page("Dashboard")
        )
        self.back_button.pack(side="left", padx=10, pady=10)

        # Page Label (Displays group name)
        self.label = ctk.CTkLabel(self.top_frame, text=self.group_name, font=("Arial", 20, "bold"))
        self.label.pack(side="left", padx=10, pady=10)

        # Content Frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=2)

        self.bind("<Configure>", self.on_resize)
        self.display_devices()

    def display_devices(self):
        """Dynamically create responsive panels with a button and label for each device."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()  # Clear previous widgets

        max_columns = self.calculate_columns()
        if max_columns < 1:
            return

        # Create the '+' button
        plus_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        plus_panel.grid(row=0, column=0, padx=self.panel_padding, pady=10, sticky="n")

        button_width = max(200, (self.winfo_width() - 40) // max_columns - (self.panel_padding * 2))

        plus_btn = ctk.CTkButton(
            plus_panel, text="+", width=button_width, height=150, 
            font=("Arial", 24), command=self.show_addmem
        )
        plus_btn.pack(pady=(10, 5), expand=True)

        plus_lbl = ctk.CTkLabel(plus_panel, text="Add Device", font=("Arial", 14))
        plus_lbl.pack(pady=(0, 10))

        # Add the device buttons
        for i, device in enumerate(self.devices):
            device_name = device.get("DeviceName", "Unnamed Device")  # Correct field

            sub_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            sub_panel.grid(row=(i + 1) // max_columns, column=(i + 1) % max_columns, padx=self.panel_padding, pady=10, sticky="n")

            device_btn = ctk.CTkButton(
                sub_panel, text=device_name, width=button_width, height=150,
                command=lambda d=device: self.open_device(d)  # Pass full device data
            )
            device_btn.pack(pady=(10, 5), expand=True)

            device_lbl = ctk.CTkLabel(sub_panel, text=device_name, font=("Arial", 14))
            device_lbl.pack(pady=(0, 10))

        # Center align columns
        for col in range(max_columns):
            self.content_frame.grid_columnconfigure(col, weight=1)

        self.content_frame.update_idletasks()

    def on_resize(self, event=None):
        """Refresh UI layout dynamically on window resize without refetching."""
        self.display_devices()

    def calculate_columns(self):
        """Calculate number of columns dynamically."""
        available_width = self.winfo_width()
        if available_width <= 1:
            return 3
        return max(1, (available_width - 40) // (self.panel_width + self.panel_padding * 2))

    def set_group_data(self, group_id, group_name):
        """Update group ID and name dynamically if needed."""
        self.group_id = group_id
        self.group_name = group_name
        self.label.configure(text=self.group_name)
        
        # Fetch devices from MongoDB
        try:
            query_filter = {"GroupID": ObjectId(self.group_id)} if ObjectId.is_valid(self.group_id) else {"GroupID": self.group_id}
            self.devices = list(devices_collection.find(query_filter))

            print("Fetched Devices:", self.devices)  # Debugging print

            if not self.devices:
                print("No devices found for GroupID:", self.group_id)

        except Exception as e:
            print("Error fetching devices:", e)

        self.display_devices()  # Refresh UI with devices list

    def open_device(self, device):
        """Handle device button click event."""
        print(f"Opening device: {device}")

    def show_addmem(self):
        """Open AddGroup and refresh dashboard after closing."""
        self.ShowAddMem = AddMember.AddMember(self,self.group_id, self.group_name)
        self.ShowAddMem.focus()