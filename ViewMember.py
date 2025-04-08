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

        device_name = device.get("DeviceName", "Unnamed Device")
        self.ip = device.get("DeviceIP", "Unknown Device IP")
        
        self.title("View Device")
        self.geometry("1450x650")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.attributes("-toolwindow", True)
        self.grab_set()
        self.title(f"{self.ip}")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = (screen_width // 2) - (1450 // 2)
        y_position = (screen_height // 2) - (650 // 2)
        self.geometry(f"1450x650+{x_position}+{y_position}")

        self.fullscreen = False  # Track fullscreen state
        
        # **Main Container Frame**
        container_frame = ctk.CTkFrame(self, fg_color="transparent")
        container_frame.pack(side="left", anchor="nw", padx=20, pady=20)

        #keyboard & mouse label (KML) frame
        kml_frame = ctk.CTkFrame(container_frame,fg_color="transparent")
        kml_frame.pack(side="top", pady=10)

        #keyboard & mouse (KM) frame
        km_frame = ctk.CTkFrame(container_frame,fg_color="transparent")
        km_frame.pack(side="top", pady=2)

        # keyboard label
        kb_lbl = ctk.CTkLabel(kml_frame, text="Keyboard Status:", font=("Arial", 14, "bold"), width=700, height=30, fg_color="transparent", corner_radius=10)
        kb_lbl.pack(side="left", expand=True,pady=2)

        # keyboard label
        mouse_lbl = ctk.CTkLabel(kml_frame, text="Mouse Status:", font=("Arial", 14, "bold"), width=700, height=30, fg_color="transparent", corner_radius=10)
        mouse_lbl.pack(side="left", expand=True,pady=2)

        # keyboard Status
        self.kbstatus_lbl = ctk.CTkLabel(km_frame, text=" ", font=("Arial", 14, "bold"), width=680, height=30, fg_color="green", corner_radius=10)
        self.kbstatus_lbl.pack(side="left", padx=10)

        # Mouse Status
        self.mousestatus_lbl = ctk.CTkLabel(km_frame, text="MOUSE STATUS", font=("Arial", 14, "bold"), width=680, height=30, fg_color="green", corner_radius=10)
        self.mousestatus_lbl.pack(side="left", padx=10)

        #Screen & Camera (SC) frame
        sc_frame = ctk.CTkFrame(container_frame,fg_color="transparent")
        sc_frame.pack(side="top", pady=6)

        # **Screen Frame (Fixed Size)**
        self.screenframe = ctk.CTkFrame(sc_frame, width=700, height=400, corner_radius=10)
        self.screenframe.pack_propagate(False)  # Prevent resizing
        self.screenframe.pack(side="left", pady=10)

        # **Label for Displaying Screen (Fixed Size)**
        self.screen_label = ctk.CTkLabel(self.screenframe, text=" ", font=("Arial", 14, "bold"), width=700, height=400, fg_color="gray")
        self.screen_label.pack(fill="both", expand=True)

        self.cameraframe = ctk.CTkFrame(sc_frame, width=700, height=400, corner_radius=10)
        self.cameraframe.pack_propagate(False)
        self.cameraframe.pack(side="left", padx=10)

        self.camera_label = ctk.CTkLabel(self.cameraframe, text=" ", font=("Arial", 14, "bold"), width=700, height=400, fg_color="gray")
        self.camera_label.pack(fill="both", expand=True)

        # Start receiving screen data in a separate thread
        threading.Thread(target=self.receive_screen, daemon=True).start()
        threading.Thread(target=self.receive_keyboard_status, daemon=True).start()

    def receive_screen(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(5)
                try:
                    client_socket.connect((self.ip, 5000))
                    print(f"Connected to {self.ip}")

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
                                image = image.resize((700, 400), Image.LANCZOS)
                                photo = ImageTk.PhotoImage(image)
                                self.screen_label.configure(image=photo)
                                self.screen_label.image = photo
                        except Exception as e:
                            print(f"Error receiving screen: {e}")
                            break

                except socket.timeout:
                    print(f"Connection to {self.ip} timed out. Device may be offline.")
                    self.set_offline_state()

                except ConnectionRefusedError:
                    print(f"Connection to {self.ip} was refused. Device is offline.")
                    self.set_offline_state()

        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.set_offline_state()

    def set_offline_state(self):
        # Show device is offline visually
        self.screen_label.configure(text="Screen Offline", image=None, fg_color="black")
        self.camera_label.configure(text="Camera Offline", image=None, fg_color="black")

#--------------Keyboard Activity Monitoring------------------------------------
    def receive_keyboard_status(self):
        """Receives real-time keyboard status updates from the client and updates the UI."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(5)
                client_socket.connect((self.ip, 5004))
                print(f"[Keyboard] Connected to {self.ip}")

                while True:
                    try:
                        data = client_socket.recv(1024).decode("utf-8").strip().lower()
                        if not data:
                            print("[Keyboard] Connection closed by client.")
                            break

                        # Decide label color based on status
                        if data == "erratic":
                            color = "red"
                        elif data == "normal":
                            color = "green"
                        elif data == "idle":
                            color = "gray"
                        else:
                            color = "orange"  # Unknown status

                        self.kbstatus_lbl.configure(text=f"{data.upper()}", fg_color=color)

                    except Exception as e:
                        print(f"[Keyboard] Error receiving data: {e}")
                        self.kbstatus_lbl.configure(text="ERROR", fg_color="red")
                        break

        except (ConnectionRefusedError, socket.timeout) as e:
            print(f"[Keyboard] Cannot connect to {self.ip}: {e}")
            self.kbstatus_lbl.configure(text="OFFLINE", fg_color="black")
