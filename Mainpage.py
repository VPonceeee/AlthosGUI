import customtkinter as ctk
import socket
import os
import threading
import time
from PIL import ImageGrab, Image, ImageDraw
import io
import pyautogui
import pystray
from pynput import keyboard, mouse
import tkinter as tk

# Keep references to frames for reuse
deviceinfo_frame = None
screen_sharing_frame = None
camera_sharing_frame = None
KeyboardMouse_frame = None

#=================================================RUN IN BACKGROUND SECTION=================================================
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


#=================================================DEVICE INFORMATION SECTION=================================================
def DeviceInfoUI():
    hide_all_frames()

    global deviceinfo_frame
    if not deviceinfo_frame:
        deviceinfo_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        
        pc_name = os.getenv('COMPUTERNAME')
        ip_address = socket.gethostbyname(socket.gethostname())

        devicename_lbl = ctk.CTkLabel(deviceinfo_frame, text=f"Device Name: {pc_name}", fg_color="transparent", font=("Arial", 25), anchor="w", justify="left")
        devicename_lbl.pack(fill="x", padx=10, pady=(10, 5))

        deviceip_lbl = ctk.CTkLabel(deviceinfo_frame, text=f"Device IP Address: {ip_address}", fg_color="transparent", font=("Arial", 25), anchor="w", justify="left")
        deviceip_lbl.pack(fill="x", padx=10, pady=(0, 5))
    
    deviceinfo_frame.pack(fill="both", expand=True, padx=10, pady=10)

#=================================================SCREEN SHARING SECTION=================================================
# ============== GLOBAL VARIABLES ==============
is_sharing = False
threads = []
statusScreen_txtb = None
screenstatus_lbl = None
startss_btn = None
stopss_btn = None
screen_sharing_frame = None
right_panel = None

# ============== SCREEN SHARING FUNCTION ==============
def ScreenSharingFunc():
    def update_textbox(message):
        statusScreen_txtb.after(0, lambda: (
            statusScreen_txtb.configure(state="normal"),
            statusScreen_txtb.insert("end", message + "\n"),
            statusScreen_txtb.see("end"),
            statusScreen_txtb.configure(state="disabled")
        ))

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
            server_socket.settimeout(1)

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

    def screentoggle_btn():
        if startss_btn.cget("state") == "disabled":
            startss_btn.configure(state="normal")
            stopss_btn.configure(state="disabled")
        else:
            startss_btn.configure(state="disabled")
            stopss_btn.configure(state="normal")

    # Expose methods
    ScreenSharingFunc.update_textbox = update_textbox
    ScreenSharingFunc.start_sharing = start_sharing
    ScreenSharingFunc.stop_sharing = stop_sharing
    ScreenSharingFunc.screentoggle_btn = screentoggle_btn

# ============== SCREEN SHARING UI DESIGN ==============
def hide_all_frames():
    for widget in right_panel.winfo_children():
        widget.pack_forget()

def ScreenSharingUI():
    hide_all_frames()

    global screen_sharing_frame, statusScreen_txtb, screenstatus_lbl, startss_btn, stopss_btn

    if not screen_sharing_frame:
        screen_sharing_frame = ctk.CTkFrame(right_panel, fg_color="transparent")

        screenbtn_frame = ctk.CTkFrame(screen_sharing_frame, fg_color="transparent")
        screenbtn_frame.pack(fill="x", padx=5, pady=5)

        screenstatus_lbl = ctk.CTkLabel(screenbtn_frame, text="Status: Offline", font=("Arial", 16, "bold"))
        screenstatus_lbl.pack(side="right", padx=10, pady=5)

        statusScreen_txtb = ctk.CTkTextbox(screen_sharing_frame, width=500, height=400)
        statusScreen_txtb.pack(fill="both", expand=True, padx=10, pady=5)
        statusScreen_txtb.configure(state="disabled")

        ScreenSharingFunc()

        startss_btn = ctk.CTkButton(screenbtn_frame, text="Start", width=100, height=30, fg_color="darkgreen", command=ScreenSharingFunc.start_sharing)
        startss_btn.pack(side="left", padx=5)
        startss_btn.bind("<Enter>", lambda e: startss_btn.configure(fg_color="limegreen"))
        startss_btn.bind("<Leave>", lambda e: startss_btn.configure(fg_color="darkgreen"))

        stopss_btn = ctk.CTkButton(screenbtn_frame, text="Stop", width=100, height=30, fg_color="darkred", command=ScreenSharingFunc.stop_sharing)
        stopss_btn.pack(side="left", padx=5)
        stopss_btn.bind("<Enter>", lambda e: stopss_btn.configure(fg_color="#B22222"))
        stopss_btn.bind("<Leave>", lambda e: stopss_btn.configure(fg_color="darkred"))
        stopss_btn.configure(state="disabled")

    screen_sharing_frame.pack(fill="both", expand=True, padx=10, pady=10)

def FLscreensharing():
    ScreenSharingUI()
    ScreenSharingFunc.start_sharing


#=================================================KEYBOARD AND MOUSE SHARING SECTION=================================================
# ============== GLOBAL VARIABLES ==============
KeyboardMouseStatus_txtb = None
KeyboardMouseStatus_lbl = None
KeyboardMouseStart_btn = None
KeyboardMouseStop_btn = None
KeyboardMouse_frame = None

def KeyboardMouseFunc():
    ### SHARED CONFIG ###
    IDLE_TIMEOUT = 5
    ERRATIC_THRESHOLD = 10

    ### KEYBOARD SHARING ###
    last_key_time = [None]
    kb_activity_start = [None]
    kb_status = ["Initializing..."]
    is_kb_sharing = [False]
    kb_server_socket = [None]
    kb_listener = [None]

    ### MOUSE SHARING ###
    last_move_time = [None]
    last_click_time = [None]
    mouse_activity_start = [None]
    mouse_status = ["Initializing..."]
    is_mouse_moving = [False]
    is_mouse_clicking = [False]
    is_mouse_sharing = [False]
    mouse_server_socket = [None]
    mouse_listener = [None]

    lock = threading.Lock()

    def update_textbox(message):
        if KeyboardMouseStatus_txtb:
            KeyboardMouseStatus_txtb.after(0, lambda: (
                KeyboardMouseStatus_txtb.configure(state="normal"),
                KeyboardMouseStatus_txtb.insert("end", message + "\n"),
                KeyboardMouseStatus_txtb.see("end"),
                KeyboardMouseStatus_txtb.configure(state="disabled")
            ))

    #================ KEYBOARD SHARING ==================
    def on_press(key):
        with lock:
            last_key_time[0] = time.time()

    def classify_keyboard():
        now = time.time()
        with lock:
            if last_key_time[0] is None or now - last_key_time[0] > IDLE_TIMEOUT:
                kb_status[0] = "Idle"
                kb_activity_start[0] = None
            else:
                if kb_activity_start[0] is None:
                    kb_activity_start[0] = last_key_time[0]
                duration = now - kb_activity_start[0]
                kb_status[0] = "Erratic" if duration > ERRATIC_THRESHOLD else "Normal"

    def accept_kb_connection():
        while is_kb_sharing[0]:
            try:
                print("[KB] Waiting for Admin to connect...")
                conn, addr = kb_server_socket[0].accept()
                update_textbox(f"[KB] Admin connected from {addr}")
                with conn:
                    while is_kb_sharing[0]:
                        classify_keyboard()
                        try:
                            conn.sendall(kb_status[0].encode("utf-8"))
                        except Exception as e:
                            print(f"[KB] Connection lost: {e}")
                            break
                        time.sleep(1)
            except Exception as e:
                print(f"[KB] Error in accept loop: {e}")
                break

    def start_keyboard_sharing():
        if not is_kb_sharing[0]:
            is_kb_sharing[0] = True
            KeyboardMouseStatus_lbl.configure(text="Status: Sharing", text_color="green")
            KeyboardMouseStart_btn.configure(state="disabled")
            KeyboardMouseStop_btn.configure(state="normal")

            kb_listener[0] = keyboard.Listener(on_press=on_press)
            kb_listener[0].start()

            try:
                kb_server_socket[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                kb_server_socket[0].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                kb_server_socket[0].bind(("0.0.0.0", 5002))
                kb_server_socket[0].listen(5)
                threading.Thread(target=accept_kb_connection, daemon=True).start()
                update_textbox("[KB] Keyboard sharing started on port 5002...")
            except Exception as e:
                update_textbox(f"[KEYBOARD] Error: {e}")
                stop_sharing()

    def stop_keyboard_sharing():
        is_kb_sharing[0] = False
        if kb_listener[0]:
            kb_listener[0].stop()
            kb_listener[0] = None
        if kb_server_socket[0]:
            try: kb_server_socket[0].close()
            except: pass
            kb_server_socket[0] = None
        update_textbox("Keyboard sharing has been stopped.")

    #================ MOUSE SHARING ==================
    def on_move(x, y):
        with lock:
            last_move_time[0] = time.time()
            is_mouse_moving[0] = True

    def on_click(x, y, button, pressed):
        if pressed:
            with lock:
                last_click_time[0] = time.time()
                is_mouse_clicking[0] = True

    def classify_mouse():
        now = time.time()
        with lock:
            last_event = max(filter(None, [last_move_time[0], last_click_time[0]]), default=None)
            if last_event is None or now - last_event > IDLE_TIMEOUT:
                mouse_status[0] = "Idle"
                mouse_activity_start[0] = None
                is_mouse_moving[0] = False
                is_mouse_clicking[0] = False
            else:
                if mouse_activity_start[0] is None:
                    mouse_activity_start[0] = last_event
                duration = now - mouse_activity_start[0]
                mouse_status[0] = "Erratic" if duration > ERRATIC_THRESHOLD else "Normal"

    def accept_mouse_connection():
        while is_mouse_sharing[0]:
            try:
                print("[Mouse] Waiting for Admin to connect...")
                conn, addr = mouse_server_socket[0].accept()
                update_textbox(f"[Mouse] Admin connected from {addr}")
                with conn:
                    while is_mouse_sharing[0]:
                        classify_mouse()
                        try:
                            conn.sendall(mouse_status[0].encode("utf-8"))
                        except Exception as e:
                            print(f"[Mouse] Connection lost: {e}")
                            break
                        time.sleep(1)
            except Exception as e:
                print(f"[Mouse] Error in accept loop: {e}")
                break

    def start_mouse_sharing():
        if not is_mouse_sharing[0]:
            is_mouse_sharing[0] = True

            mouse_listener[0] = mouse.Listener(on_move=on_move, on_click=on_click)
            mouse_listener[0].start()

            try:
                mouse_server_socket[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                mouse_server_socket[0].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                mouse_server_socket[0].bind(("0.0.0.0", 5003))
                mouse_server_socket[0].listen(5)
                threading.Thread(target=accept_mouse_connection, daemon=True).start()
                update_textbox("Mouse sharing started on port 5003...")
            except Exception as e:
                update_textbox(f"[Mouse] Error: {e}")
                stop_sharing()

    def stop_mouse_sharing():
        is_mouse_sharing[0] = False
        if mouse_listener[0]:
            mouse_listener[0].stop()
            mouse_listener[0] = None
        if mouse_server_socket[0]:
            try: mouse_server_socket[0].close()
            except: pass
            mouse_server_socket[0] = None
        update_textbox("[Mouse] Mouse sharing stopped.")

    def start_sharing():
        start_keyboard_sharing()
        start_mouse_sharing()

    def stop_sharing():
        KeyboardMouseStatus_lbl.configure(text="Status: Offline", text_color="red")
        KeyboardMouseStart_btn.configure(state="normal")
        KeyboardMouseStop_btn.configure(state="disabled")
        stop_keyboard_sharing()
        stop_mouse_sharing()

    KeyboardMouseFunc.update_textbox = update_textbox
    KeyboardMouseFunc.start_sharing = start_sharing
    KeyboardMouseFunc.stop_sharing = stop_sharing

# ============== UI FOR KEYBOARD & MOUSE SHARING ==============

def KeyboardMouseUI():
    hide_all_frames()

    global KeyboardMouse_frame, KeyboardMouseStatus_txtb, KeyboardMouseStatus_lbl, KeyboardMouseStart_btn, KeyboardMouseStop_btn

    if not KeyboardMouse_frame:
        KeyboardMouse_frame = ctk.CTkFrame(right_panel, fg_color="transparent")

        KeyboardMousebtn_frame = ctk.CTkFrame(KeyboardMouse_frame, fg_color="transparent")
        KeyboardMousebtn_frame.pack(fill="x", padx=5, pady=5)

        KeyboardMouseStatus_lbl = ctk.CTkLabel(KeyboardMousebtn_frame, text="Status: Offline", font=("Arial", 16, "bold"))
        KeyboardMouseStatus_lbl.pack(side="right", padx=10, pady=5)

        KeyboardMouseStatus_txtb = ctk.CTkTextbox(KeyboardMouse_frame, width=500, height=400)
        KeyboardMouseStatus_txtb.pack(fill="both", expand=True, padx=10, pady=5)
        KeyboardMouseStatus_txtb.configure(state="disabled")

        KeyboardMouseFunc()

        KeyboardMouseStart_btn = ctk.CTkButton(KeyboardMousebtn_frame, text="Start", width=100, height=30, fg_color="darkgreen", command=KeyboardMouseFunc.start_sharing)
        KeyboardMouseStart_btn.pack(side="left", padx=5)
        KeyboardMouseStart_btn.bind("<Enter>", lambda e: KeyboardMouseStart_btn.configure(fg_color="green"))
        KeyboardMouseStart_btn.bind("<Leave>", lambda e: KeyboardMouseStart_btn.configure(fg_color="darkgreen"))

        KeyboardMouseStop_btn = ctk.CTkButton(KeyboardMousebtn_frame, text="Stop", width=100, height=30, fg_color="darkred", command=KeyboardMouseFunc.stop_sharing)
        KeyboardMouseStop_btn.pack(side="left", padx=5)
        KeyboardMouseStop_btn.bind("<Enter>", lambda e: KeyboardMouseStop_btn.configure(fg_color="red"))
        KeyboardMouseStop_btn.bind("<Leave>", lambda e: KeyboardMouseStop_btn.configure(fg_color="darkred"))
        KeyboardMouseStop_btn.configure(state="disabled")

    KeyboardMouse_frame.pack(fill="both", expand=True, padx=10, pady=10)

def FLkeyboardmouse():
    KeyboardMouseUI()
    KeyboardMouseFunc.start_sharing

#=================================================CAMERA SHARING SECTION=================================================
def CameraSharingUI():
    hide_all_frames()

    global camera_sharing_frame
    if not camera_sharing_frame:
        camera_sharing_frame = ctk.CTkFrame(right_panel, fg_color="transparent")

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
        statuscs_txtb.configure(state="disabled")
    
    camera_sharing_frame.pack(fill="both", expand=True, padx=10, pady=10)


#=================================================HELPER FUNCTION TO HIDE ALL=================================================
def hide_all_frames():
    if deviceinfo_frame: deviceinfo_frame.pack_forget()
    if screen_sharing_frame: screen_sharing_frame.pack_forget()
    if camera_sharing_frame: camera_sharing_frame.pack_forget()
    if KeyboardMouse_frame: KeyboardMouse_frame.pack_forget()

#=================================================MAIN APP WINDOW=================================================
app = ctk.CTk()
app.title("User App")
app.resizable(False, False)

width = 800
height = 600
x = (app.winfo_screenwidth() - width) // 2
y = (app.winfo_screenheight() - height) // 2
app.geometry(f"{width}x{height}+{x}+{y}")

main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True)

left_panel = ctk.CTkFrame(main_frame, fg_color="transparent", width=240)
left_panel.pack(side="left", fill="y")

right_panel = ctk.CTkFrame(main_frame)
right_panel.pack(side="right", fill="both", expand=True)


# Left panel buttons
deviceinfo_btn = ctk.CTkButton(left_panel, text="Device Information", width=240, height=40, command=DeviceInfoUI)
deviceinfo_btn.pack(fill="x", padx=10, pady=(20, 5))

screensharing_btn = ctk.CTkButton(left_panel, text="Screen Sharing Service", width=240, height=40, command=ScreenSharingUI)
screensharing_btn.pack(fill="x", padx=10, pady=5)

camerasharing_btn = ctk.CTkButton(left_panel, text="Camera Service", width=240, height=40, command=CameraSharingUI)
camerasharing_btn.pack(fill="x", padx=10, pady=5)

kbsharing_btn = ctk.CTkButton(left_panel, text="Keyboard & Mouse Service", width=240, height=40, command=KeyboardMouseUI)
kbsharing_btn.pack(fill="x", padx=10, pady=5)

stopservice_btn = ctk.CTkButton(left_panel, text="Stop Service", width=240, height=40)
stopservice_btn.pack(fill="x", padx=10, pady=5)

ScreenSharingUI()
KeyboardMouseUI()


app.after(100, ScreenSharingFunc.start_sharing)
app.after(105, KeyboardMouseFunc.start_sharing)
app.after(110, DeviceInfoUI)

app.protocol("WM_DELETE_WINDOW", runintobckgrnd)

# Run app
app.mainloop()
