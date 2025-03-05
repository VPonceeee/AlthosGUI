import customtkinter as ctk
from pymongo import MongoClient
from bson import ObjectId
from PIL import Image, ImageTk
import socket
import threading
import io
import tkinter as tk

class ViewMember(ctk.CTkToplevel):
    def __init__(self, parent, device, device_ip):
        super().__init__(parent)

        self.title("View Device")
        self.geometry("1300x900")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.attributes("-toolwindow", True)
        self.grab_set()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = (screen_width // 2) - (1300 // 2)
        y_position = (screen_height // 2) - (900 // 2)
        self.geometry(f"1300x900+{x_position}+{y_position}")

        device_name = device.get("DeviceName", "Unnamed Device")
        self.ip = device.get("DeviceIP", "Unknown Device IP")

        # Display Device Name and IP
        message_lbl = ctk.CTkLabel(self, text=f"Device: {device_name}\nIP: {self.ip}", font=("Arial", 18))
        message_lbl.pack(pady=15)

        # **Main Container Frame**
        container_frame = ctk.CTkFrame(self)
        container_frame.pack(side="left", anchor="nw", padx=20, pady=20)

        # **Screen Frame (Fixed Size)**
        self.screenframe = ctk.CTkFrame(container_frame, width=700, height=400, corner_radius=10)
        self.screenframe.pack_propagate(False)  # Prevent resizing
        self.screenframe.pack(side="top", pady=10)

        # **Label for Displaying Screen (Fixed Size)**
        self.screen_label = tk.Label(self.screenframe, text="No Screen Available", font=("Arial", 14, "bold"), bg="lightgray", width=700, height=400)
        self.screen_label.pack(fill="both", expand=True)

        # Start receiving screen data in a separate thread
        threading.Thread(target=self.receive_screen, daemon=True).start()

    def receive_screen(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(5)
                try:
                    client_socket.connect((self.ip, 5000))
                    print(f"Connected to {self.ip}")
                    self.update_screen_status("Online")

                    while True:
                        try:
                            length = client_socket.recv(4)
                            if len(length) < 4:
                                print("Connection closed by server.")
                                break
                            data_length = int.from_bytes(length, 'big')

                            data = b""
                            while len(data) < data_length:
                                packet = client_socket.recv(data_length - len(data))
                                if not packet:
                                    print("Connection lost.")
                                    break
                                data += packet

                            if data:
                                image = Image.open(io.BytesIO(data))
                                image = image.resize((700, 400), Image.LANCZOS)  # Always resize to 700x400

                                photo = ImageTk.PhotoImage(image)

                                # Update screen_label with the new image
                                self.screen_label.config(image=photo)
                                self.screen_label.image = photo
                        except Exception as e:
                            print(f"Error receiving screen: {e}")
                            break
                except socket.timeout:
                    print(f"Connection to {self.ip} timed out.")
                    self.update_screen_status("Offline")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.update_screen_status("Offline")

    def update_screen_status(self, status):
        """ Update the screen status label based on connection status """
        if status == "Online":
            self.screen_label.config(text="Receiving Screen", font=("Arial", 14, "bold"), bg="lightgreen", fg="black")
        elif status == "Offline":
            self.screen_label.config(text="No Screen Available", font=("Arial", 14, "bold"), bg="lightgray", fg="black")
