import customtkinter as ctk
from pymongo import MongoClient
from bson import ObjectId  # Import ObjectId for proper querying
import tkinter as tk
from tkinter import ttk

# MongoDB Connection (Make sure this is correctly set up)
try:
    connection_string = "mongodb+srv://altplusf42024:RuVAh3aZgUbC0YLE@altf4cluster.9p2yp.mongodb.net/?retryWrites=true&w=majority&appName=ALTF4Cluster"
    client = MongoClient(connection_string)
    db = client["ADB"]
    devices_collection = db["Members"]
except Exception as e:
    print("Error connecting to Members MongoDB:", e)

#-------------------- ViewMember Class -----------------------
class rl(ctk.CTkToplevel):
    def __init__(self, parent, group_name, group_id):
        super().__init__(parent)

        self.group_name = group_name  
        self.group_id = group_id  

        self.title(f"Report logs of {self.group_name} ({self.group_id})")
        self.geometry("800x600")
        self.resizable(True, True)  # Allow resizing
        self.attributes("-topmost", True)
        self.attributes("-toolwindow", True)
        self.grab_set()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = (screen_width // 2) - (800 // 2)
        y_position = (screen_height // 2) - (600 // 2)
        self.geometry(f"800x600+{x_position}+{y_position}")

        self.fullscreen = False  # Track fullscreen state

        # Main container frame
        container_frame = ctk.CTkFrame(self, fg_color="transparent")
        container_frame.pack(side="left", anchor="nw", padx=20, pady=20, fill="both", expand=True)

        # Initial load of data into the Treeview
        self.update_treeview(container_frame)

    def fetch_and_print_members(self):
        # Convert self.group_id to ObjectId for proper query
        group_id_objectid = ObjectId(self.group_id)
        
        # Query MongoDB for all documents with the same group_id
        members = devices_collection.find({"GroupID": group_id_objectid})

        return members

    def update_treeview(self, container_frame):
        # Fetch the updated data from MongoDB
        members = self.fetch_and_print_members()

        if members:
            # Clear existing frames in the container frame
            for widget in container_frame.winfo_children():
                widget.destroy()

            # Create a frame for each member
            for record in members:
                # Create the frame for each device
                device_frame = ctk.CTkFrame(container_frame)
                device_frame.pack(fill="x", padx=5, pady=5, anchor="nw")

                # Combine device name and device IP into a single string
                device_info = f"{record.get('DeviceName', '')}: ({record.get('DeviceIP', '')})"

                # Label showing the device info
                device_info_label = ctk.CTkLabel(device_frame, text=device_info, anchor="w")
                device_info_label.pack(side="left", padx=10)

                # "View" button
                view_button = ctk.CTkButton(device_frame, text="View", command=lambda device=record: self.view_device(device))
                view_button.pack(side="right", padx=10)

        else:
            print("No data found in MongoDB.")

    def view_device(self, device):
        # Example function that will be called when "View" is pressed
        print(f"Viewing device: {device['DeviceName']} with IP: {device['DeviceIP']}")

