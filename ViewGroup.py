import customtkinter as ctk
from pymongo import MongoClient
from bson import ObjectId
import AddMember
import ViewMember

from PIL import Image, ImageTk
import socket
import threading
import io
import tkinter as tk

# ============================== DATABASE CONNECTION ==============================
try:
    connection_string = "mongodb+srv://altplusf42024:RuVAh3aZgUbC0YLE@altf4cluster.9p2yp.mongodb.net/?retryWrites=true&w=majority&appName=ALTF4Cluster"
    client = MongoClient(connection_string)
    db = client["ADB"]
    devices_collection = db["Members"]
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

        # Page Label
        self.label = ctk.CTkLabel(self.top_frame, text=self.group_name, font=("Arial", 20, "bold"))
        self.label.pack(side="left", padx=10, pady=10)

        # Content Frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=2)

        self.bind("<Configure>", self.on_resize)
        self.display_devices()

    def display_devices(self):
        """Dynamically create responsive panels for each device."""
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

        # Add device screens
        for i, device in enumerate(self.devices):
            device_ip = device.get("DeviceIP", "Unnamed Device IP")

            sub_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            sub_panel.grid(row=(i + 1) // max_columns, column=(i + 1) % max_columns, padx=self.panel_padding, pady=10, sticky="n")

            # Create unique screen frame for each device
            screenframe = ctk.CTkFrame(sub_panel, width=button_width, height=150, corner_radius=10)
            screenframe.pack_propagate(False)
            screenframe.pack(side="top", pady=10)

            # Create unique label for each screen
            screen_label = ctk.CTkLabel(screenframe, text=" ", font=("Arial", 14, "bold"), width=button_width, height=150, fg_color="lightgray")
            screen_label.pack(fill="both", expand=True)

            screen_label.bind("<Button-1>", lambda event, dev=device: self.open_member(dev))
            
            # Start screen receiving for this specific device
            threading.Thread(target=self.receive_screen, args=(device, screen_label), daemon=True).start()

            device_lbl = ctk.CTkLabel(sub_panel, text=device_ip, font=("Arial", 14))
            device_lbl.pack(pady=(0, 10))

        # Center align columns
        for col in range(max_columns):
            self.content_frame.grid_columnconfigure(col, weight=1)

        self.content_frame.update_idletasks()

    def on_resize(self, event=None):
        """Refresh UI layout dynamically on window resize."""
        self.display_devices()

    def calculate_columns(self):
        """Calculate number of columns dynamically based on window size."""
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

            print("Fetched Devices:", self.devices)

            if not self.devices:
                print("No devices found for GroupID:", self.group_id)

        except Exception as e:
            print("Error fetching devices:", e)

        self.display_devices()

    def receive_screen(self, device, screen_label):
        """Receives and displays the screen data from the device."""
        device_ip = device.get("DeviceIP", "Unnamed Device IP")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(5)
                try:
                    client_socket.connect((device_ip, 5001))

                    while True:
                        try:
                            length = client_socket.recv(4)
                            if len(length) < 4:
                                print(f"Connection closed by server ({device_ip}).")
                                break
                            data_length = int.from_bytes(length, 'big')

                            data = b""
                            while len(data) < data_length:
                                packet = client_socket.recv(data_length - len(data))
                                if not packet:
                                    print(f"Connection lost ({device_ip}).")
                                    break
                                data += packet

                            if data:
                                image = Image.open(io.BytesIO(data))

                                # Get dynamic frame size
                                frame_width = screen_label.winfo_width()
                                frame_height = screen_label.winfo_height()

                                image = image.resize((frame_width, frame_height), Image.LANCZOS)

                                photo = ImageTk.PhotoImage(image)

                                # Update the correct screen_label
                                screen_label.configure(image=photo)
                                screen_label.image = photo  # Keep a reference to prevent garbage collection

                        except Exception as e:
                            print(f"Error receiving screen from {device_ip}: {e}")
                            break
                except socket.timeout:
                    print(f"Connection to {device_ip} timed out.")

        except Exception as e:
            print(f"Error connecting to {device_ip}: {e}")

    def show_addmem(self):
        """Open AddGroup and refresh dashboard after closing."""
        self.ShowAddMem = AddMember.AddMember(self, self.group_id, self.group_name)
        self.ShowAddMem.focus()

    def open_member(self, device):
        """Switch to ViewMember page with the selected device's details."""
        print("Device Data:", device)  # Debugging: Check if 'IP' exists

        device_ip = device.get("DeviceIP", "Unknown IP")  # Extract IP address safely
        print(f"Opening device with IP: {device_ip}")  # Debugging log


        self.openmem = ViewMember.ViewMember(self, device, device_ip)  # Pass IP to ViewMember
        self.openmem.focus()



    