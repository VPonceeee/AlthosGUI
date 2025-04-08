#LAST WORKING CODE
import customtkinter as ctk
import socket
import os
import threading
import time
from PIL import ImageGrab, Image, ImageDraw
import io
import pyautogui
import pystray
from pynput import keyboard

#======================Function Section==============================

def runintobckgrnd():
    global tray_icon
    app.withdraw()  # Hide the main window
    image = Image.new('RGB', (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, 54, 54), fill=(0, 0, 255))
    
    def on_restore(icon, item):
        icon.stop()
        app.deiconify()
    
    def on_exit(icon, item):
        icon.stop()
        appexit()
    
    tray_icon = pystray.Icon("App", image, menu=pystray.Menu(
        pystray.MenuItem("Open", on_restore),
        pystray.MenuItem("Exit", on_exit)
    ))
    tray_icon.run()

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

    global is_sharing, threads
    is_sharing = False
    threads = []

    def update_textbox(message):
        statusScreen_txtb.after(0, lambda: statusScreen_txtb.insert("end", message + "\n"))

    def start_sharing():
        global is_sharing, threads
        if not is_sharing:
            is_sharing = True
            threads = []
            
            for port in [5000, 5001]:
                thread = threading.Thread(target=run_server, args=(port,))
                thread.daemon = True
                thread.start()
                threads.append(thread)

            screentoggle_btn()
            screenstatus_lbl.configure(text="Status: Online", text_color="green")
            update_textbox("Screen sharing started on ports 5000 and 5001...")

    def stop_sharing():
        global is_sharing
        is_sharing = False
        update_textbox("Stopping screen sharing...")
        
        # Force close socket connections
        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect(("127.0.0.1", 5000))
            temp_socket.close()
        except:
            pass

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
            server_socket.settimeout(1)  # Prevents indefinite blocking

            update_textbox(f"Server listening on port {port}...")
            while is_sharing:
                try:
                    conn, addr = server_socket.accept()
                    if not is_sharing:
                        break
                    share_screen(conn)
                except socket.timeout:
                    continue
                except socket.error as e:
                    update_textbox(f"Socket error on port {port}: {e}")
                    break
            server_socket.close()
        except Exception as e:
            update_textbox(f"Error in server on port {port}: {e}")


    def share_screen(conn):
        try:
            while is_sharing:
                screenshot = ImageGrab.grab()
                buffer = io.BytesIO()
                screenshot.save(buffer, format="JPEG")
                data = buffer.getvalue()
                buffer.close()

                conn.sendall(len(data).to_bytes(4, 'big') + data)
                time.sleep(1)
        except:
            update_textbox("Client disconnected.")
        finally:
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

def show_kb_sharing():
    for widget in right_panel.winfo_children():
        widget.destroy()
    
    kbsharing_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    kbsharing_frame.pack(fill="both", expand=True, padx=10, pady=10)

    kbbtn_frame = ctk.CTkFrame(kbsharing_frame, fg_color="transparent")
    kbbtn_frame.pack(fill="x", padx=5, pady=5)

    kbstatus_lbl = ctk.CTkLabel(kbbtn_frame, text="Status: Offline", font=("Arial", 16, "bold"))
    kbstatus_lbl.pack(side="right", padx=10, pady=5)

    statuskbs_txtb = ctk.CTkTextbox(kbsharing_frame, width=500, height=400)
    statuskbs_txtb.pack(fill="both", expand=True, padx=10, pady=5)

    # Constants
    TIME_WINDOW = 5
    ERRATIC_THRESHOLD = 20
    NORMAL_THRESHOLD = 1

    # State Variables
    keystroke_times = []
    keystroke_intervals = []
    is_sharing_kb = False
    server_socket = [None]  # Use list to allow access inside nested functions
    listener = [None]

    def update_textbox(message):
        statuskbs_txtb.after(0, lambda: statuskbs_txtb.insert("end", message + "\n"))

    def on_key_press(key):
        current_time = time.time()
        keystroke_times.append(current_time)

        if len(keystroke_times) > 1:
            interval = keystroke_times[-1] - keystroke_times[-2]
            keystroke_intervals.append(interval)

        while keystroke_times and keystroke_times[0] < current_time - TIME_WINDOW:
            keystroke_times.pop(0)
            if keystroke_intervals:
                keystroke_intervals.pop(0)

    def get_activity_level():
        current_time = time.time()
        while keystroke_times and keystroke_times[0] < current_time - TIME_WINDOW:
            keystroke_times.pop(0)
            if keystroke_intervals:
                keystroke_intervals.pop(0)

        key_count = len(keystroke_times)
        if key_count == 0:
            return "Idle"
        elif key_count >= ERRATIC_THRESHOLD:
            return "Erratic"
        elif key_count >= NORMAL_THRESHOLD:
            return "Normal"
        return "Idle"

    def accept_admin_connection():
        while is_sharing_kb:
            try:
                conn, addr = server_socket[0].accept()
                update_textbox(f"Admin connected from {addr}")
                while is_sharing_kb:
                    activity_level = get_activity_level()
                    conn.sendall(activity_level.encode("utf-8"))
                    time.sleep(1)
                conn.close()
            except OSError as e:
                if is_sharing_kb:
                    update_textbox(f"Connection error: {e}")
            except Exception as e:
                update_textbox(f"Unexpected error: {e}")

    def start_sharing():
        nonlocal is_sharing_kb
        if not is_sharing_kb:
            is_sharing_kb = True
            kbstatus_lbl.configure(text="Status: Sharing", text_color="green")
            startkbs_btn.configure(state="disabled")
            stopkbs_btn.configure(state="normal")

            listener[0] = keyboard.Listener(on_press=on_key_press)
            listener[0].start()

            try:
                server_socket[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket[0].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket[0].bind(("0.0.0.0", 5004))
                server_socket[0].listen(1)

                threading.Thread(target=accept_admin_connection, daemon=True).start()
                update_textbox("Keyboard sharing started on port 5004...")
            except Exception as e:
                update_textbox(f"Failed to start server: {e}")
                stop_sharing()  # Roll back if error occurs

    def stop_sharing():
        nonlocal is_sharing_kb
        is_sharing_kb = False
        kbstatus_lbl.configure(text="Status: Offline", text_color="red")
        startkbs_btn.configure(state="normal")
        stopkbs_btn.configure(state="disabled")

        if listener[0]:
            listener[0].stop()
            listener[0] = None

        if server_socket[0]:
            try:
                server_socket[0].shutdown(socket.SHUT_RDWR)
            except:
                pass  # Socket might already be closed or not connected
            try:
                server_socket[0].close()
            except:
                pass
            server_socket[0] = None

        update_textbox("Keyboard sharing has been stopped.")

    # Buttons
    startkbs_btn = ctk.CTkButton(kbbtn_frame, text="Start", width=100, height=30, fg_color="darkgreen", command=start_sharing)
    startkbs_btn.pack(side="left", padx=5)
    startkbs_btn.bind("<Enter>", lambda e: startkbs_btn.configure(fg_color="green"))
    startkbs_btn.bind("<Leave>", lambda e: startkbs_btn.configure(fg_color="darkgreen"))

    stopkbs_btn = ctk.CTkButton(kbbtn_frame, text="Stop", width=100, height=30, fg_color="darkred", command=stop_sharing, state="disabled")
    stopkbs_btn.pack(side="left", padx=5)
    stopkbs_btn.bind("<Enter>", lambda e: stopkbs_btn.configure(fg_color="red"))
    stopkbs_btn.bind("<Leave>", lambda e: stopkbs_btn.configure(fg_color="darkred"))

    # Start sharing automatically
    start_sharing()




def appexit():

    #ScreenSharing
    global is_sharing, threads
    is_sharing = False
    threads = []

    def stop_sharing():
        global is_sharing
        is_sharing = False

        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect(("127.0.0.1", 5000))
            temp_socket.close()
        except:
            pass

        for thread in threads:
            thread.join(timeout=2)

    stop_sharing()
    app.destroy()

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
app.after(105, show_kb_sharing)
app.after(110, show_deviceinfo)

# Buttons in left panel
deviceinfo_btn = ctk.CTkButton(left_panel, text="Device Information", width=240, height=40, command=show_deviceinfo)
deviceinfo_btn.pack(fill="x", padx=10, pady=(20, 5))

screensharing_btn = ctk.CTkButton(left_panel, text="Screen Sharing Service", width=240, height=40, command=show_screen_sharing)
screensharing_btn.pack(fill="x", padx=10, pady=5)

camerasharing_btn = ctk.CTkButton(left_panel, text="Camera Service", width=240, height=40, command=show_camera_sharing)
camerasharing_btn.pack(fill="x", padx=10, pady=5)

kbsharing_btn = ctk.CTkButton(left_panel, text="keyboard Service", width=240, height=40, command=show_kb_sharing)
kbsharing_btn.pack(fill="x", padx=10, pady=5)

stopservice_btn = ctk.CTkButton(left_panel, text="Stop Service", width=240, height=40)
stopservice_btn.pack(fill="x", padx=10, pady=5)

app.protocol("WM_DELETE_WINDOW", runintobckgrnd)

# Run the application
app.mainloop()
