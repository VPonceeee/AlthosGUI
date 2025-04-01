#LAST WORKING CODE
import customtkinter as ctk
import socket
import os
import threading
import time
from PIL import ImageGrab, Image, ImageDraw
import io
import pyautogui

#======================Function Section==============================

def show_deviceinfo():
    for widget in right_panel.winfo_children():
        widget.destroy()
    
    deviceinfo_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    deviceinfo_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def get_pc_info():
        pc_name = os.getenv('COMPUTERNAME')  
        ip_address = socket.gethostbyname(socket.gethostname())
        return pc_name, ip_address

    pc_name, ip_address = get_pc_info()
    
    devicename_lbl = ctk.CTkLabel(deviceinfo_frame, text=f"Device Name: {pc_name}", fg_color="transparent", font=("Arial", 25), anchor="w", justify="left")
    devicename_lbl.pack(fill="x", padx=10, pady=(10, 5))

    deviceip_lbl = ctk.CTkLabel(deviceinfo_frame, text=f"Device IP Address: {ip_address}", fg_color="transparent", font=("Arial", 25), anchor="w", justify="left")
    deviceip_lbl.pack(fill="x", padx=10, pady=(0, 5))

def show_screen_sharing():
    for widget in right_panel.winfo_children():
        widget.destroy()
    
    screen_sharing_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    screen_sharing_frame.pack(fill="both", expand=True, padx=10, pady=10)

    screenbtn_frame = ctk.CTkFrame(screen_sharing_frame, fg_color="transparent")
    screenbtn_frame.pack(fill="x", padx=5, pady=5)

    screenstatus_lbl = ctk.CTkLabel(screenbtn_frame, text="Status: Active", font=("Arial", 16, "bold"))
    screenstatus_lbl.pack(side="right", padx=10, pady=5)

    statusScreen_txtb = ctk.CTkTextbox(screen_sharing_frame, width=500, height=400)
    statusScreen_txtb.pack(fill="both", expand=True, padx=10, pady=5)

    is_sharing = False
    threads = []

    def update_textbox(message):
        statusScreen_txtb.after(0, lambda: statusScreen_txtb.insert("end", message + "\n"))

    def start_sharing():
        nonlocal is_sharing, threads
        if not is_sharing:
            is_sharing = True
            threads = []
            
            for port in [5000, 5001]:
                thread = threading.Thread(target=run_server, args=(port,))
                thread.start()
                threads.append(thread)

            screentoggle_btn()
            screenstatus_lbl.configure(text="Status: Online", text_color="green")
            update_textbox("Screen sharing started on ports 5000 and 5001...")

    def stop_sharing():
        nonlocal is_sharing
        is_sharing = False
        update_textbox("Stopping screen sharing...")
        
        for thread in threads:
            thread.join(timeout=2)

        update_textbox("Screen sharing has been stopped.")
        screentoggle_btn()
        screenstatus_lbl.configure(text="Status: Offline", text_color="red")
        

    def run_server(port):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(("0.0.0.0", port))
            server_socket.listen(5)
            update_textbox(f"Server listening on port {port}...")

            server_socket.settimeout(1)  # Avoid indefinite blocking
            while is_sharing:
                try:
                    conn, addr = server_socket.accept()
                    if not is_sharing:
                        break  # Exit if sharing was stopped
                    print(f"Connected to {addr} on port {port}")
                    share_screen(conn)
                except socket.timeout:
                    continue  # Check again if is_sharing is still True
                except socket.error as e:
                    print(f"Socket error on port {port}: {e}")
            server_socket.close()
        except Exception as e:
            print(f"Error in server on port {port}: {e}")


    def share_screen(conn):
        try:
            while is_sharing and conn:
                screenshot = ImageGrab.grab()
                cursor_x, cursor_y = pyautogui.position()

                cursor_image = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
                draw = ImageDraw.Draw(cursor_image)
                draw.ellipse([(0, 0), (20, 20)], fill=(255, 0, 0, 255))

                screenshot.paste(cursor_image, (cursor_x - 10, cursor_y - 10), cursor_image)

                buffer = io.BytesIO()
                screenshot.save(buffer, format="JPEG")
                data = buffer.getvalue()
                buffer.close()

                conn.sendall(len(data).to_bytes(4, 'big') + data)
                time.sleep(1)
        except (socket.error, BrokenPipeError) as e:
            print(f"Error during screen sharing: {e}")
        finally:
            if conn:
                conn.close()

    def screentoggle_btn(): #buttons function on and off
        if startss_btn.cget("state") == "disabled":
            startss_btn.configure(state="normal")
            stopss_btn.configure(state="disabled")
        else:
            startss_btn.configure(state="disabled")
            stopss_btn.configure(state="normal")

    startss_btn = ctk.CTkButton(screenbtn_frame, text="Start", width=100, height=30, fg_color="darkgreen", command=start_sharing)
    startss_btn.pack(side="left", padx=5)
    startss_btn.bind("<Enter>", lambda e: startss_btn.configure(fg_color="limegreen"))
    startss_btn.bind("<Leave>", lambda e: startss_btn.configure(fg_color="darkgreen"))

    stopss_btn = ctk.CTkButton(screenbtn_frame, text="Stop", width=100, height=30, fg_color="darkred", command=stop_sharing)
    stopss_btn.pack(side="left", padx=5)
    stopss_btn.bind("<Enter>", lambda e: stopss_btn.configure(fg_color="#B22222"))
    stopss_btn.bind("<Leave>", lambda e: stopss_btn.configure(fg_color="darkred"))
    
    #excute first
    start_sharing()


def show_camera_sharing():
    for widget in right_panel.winfo_children():
        widget.destroy()
    
    camera_sharing_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    camera_sharing_frame.pack(fill="both", expand=True, padx=10, pady=10)

    camerabtn_frame = ctk.CTkFrame(camera_sharing_frame, fg_color="transparent")
    camerabtn_frame.pack(fill="x", padx=5, pady=5)

    startcs_btn = ctk.CTkButton(camerabtn_frame, text="Start", width=100, height=30, fg_color="darkgreen")
    startcs_btn.pack(side="left", padx=5)
    startcs_btn.bind("<Enter>", lambda e: startcs_btn.configure(fg_color="green"))
    startcs_btn.bind("<Leave>", lambda e: startcs_btn.configure(fg_color="darkgreen"))

    stopcs_btn = ctk.CTkButton(camerabtn_frame, text="Stop", width=100, height=30, fg_color="darkred")
    stopcs_btn.pack(side="left", padx=5)
    stopcs_btn.bind("<Enter>", lambda e: stopcs_btn.configure(fg_color="red"))
    stopcs_btn.bind("<Leave>", lambda e: stopcs_btn.configure(fg_color="darkred"))

    camerastatus_lbl = ctk.CTkLabel(camerabtn_frame, text="Status: Active", font=("Arial", 16, "bold"))
    camerastatus_lbl.pack(side="right", padx=10, pady=5)

    statuscs_txtb = ctk.CTkTextbox(camera_sharing_frame, width=500, height=400)
    statuscs_txtb.pack(fill="both", expand=True, padx=10, pady=5)

#======================Form Design Section==============================

app = ctk.CTk()
app.title("User App")
app.resizable(False, False)

width = 800
height = 600

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x = (screen_width - width) // 2
y = (screen_height - height) // 2
app.geometry(f"{width}x{height}+{x}+{y}")

main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True)


left_panel = ctk.CTkFrame(main_frame, fg_color="transparent", width=240)
left_panel.pack(side="left", fill="y")

right_panel = ctk.CTkFrame(main_frame)
right_panel.pack(side="right", fill="both", expand=True)

#Form Load

app.after(100, show_screen_sharing)
app.after(110, show_deviceinfo)

# Buttons in left panel
deviceinfo_btn = ctk.CTkButton(left_panel, text="Device Information", width=240, height=40, command=show_deviceinfo)
deviceinfo_btn.pack(fill="x", padx=10, pady=(20, 5))

screensharing_btn = ctk.CTkButton(left_panel, text="Screen Sharing Service", width=240, height=40, command=show_screen_sharing)
screensharing_btn.pack(fill="x", padx=10, pady=5)

camerasharing_btn = ctk.CTkButton(left_panel, text="Camera Service", width=240, height=40, command=show_camera_sharing)
camerasharing_btn.pack(fill="x", padx=10, pady=5)

stopservice_btn = ctk.CTkButton(left_panel, text="Stop Service", width=240, height=40)
stopservice_btn.pack(fill="x", padx=10, pady=5)

# Run the application
app.mainloop()
