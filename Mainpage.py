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
from pynput import keyboard, mouse
import tkinter as tk
import cv2
from fer import FER

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
        if statusScreen_txtb.winfo_exists():  # Check if the widget still exists
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

    EMOTION_COLORS = {
    "angry": "red",
    "disgust": "green",
    "fear": "violet",
    "happy": "yellow",
    "sad": "blue",
    "surprise": "orange",
    "neutral": "gray",
    }

    for widget in right_panel.winfo_children():
        widget.destroy()
    
    camera_sharing_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    camera_sharing_frame.pack(fill="both", expand=True, padx=10, pady=10)

    camerabtn_frame = ctk.CTkFrame(camera_sharing_frame, fg_color="transparent")
    camerabtn_frame.pack(fill="x", padx=5, pady=5)

    camerastatus_lbl = ctk.CTkLabel(camerabtn_frame, text="Status: Active", font=("Arial", 16, "bold"))
    camerastatus_lbl.pack(side="right", padx=10, pady=5)

    statuscs_txtb = ctk.CTkTextbox(camera_sharing_frame, width=500, height=400)
    statuscs_txtb.pack(fill="both", expand=True, padx=10, pady=5)

    global is_camera_sharing, camera_threads
    is_camera_sharing = False
    camera_threads = []
    detector = FER(mtcnn=False)  # Initialize FER detector
    cap = cv2.VideoCapture(0)  # Open the default camera
    

    def update_textbox(message):
        if statuscs_txtb.winfo_exists():  # Check if the widget still exists
            statuscs_txtb.after(0, lambda: statuscs_txtb.insert("end", message + "\n"))

    def start_camera_sharing():
        global is_camera_sharing, camera_threads
        if not is_camera_sharing:
            is_camera_sharing = True
            camera_threads = []

            for port in [5004]:
                thread = threading.Thread(target=run_camera_server, args=(port,))
                thread.daemon = True
                thread.start()
                camera_threads.append(thread)

                emotion_tread = threading.Thread(target=run_emotion_server)
                emotion_tread.daemon = True
                emotion_tread.start()
                camera_threads.append(emotion_tread)
            
            cameratoggle_btn()
            camerastatus_lbl.configure(text="Status: Online", text_color="green")
            update_textbox("Camera sharing started on ports 5004...")
    
    def stop_camera_sharing():
        global is_camera_sharing
        is_camera_sharing = False
        update_textbox("Stopping camera sharing...")

        if cap.isOpened():
            cap.release()

        # Force close socket connections
        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect(("127.0.0.1", 5004))
            temp_socket.close()
        except:
            pass

        for thread in camera_threads:
            thread.join(timeout=2)
        
        update_textbox("Camera sharing has been stopped.")
        cameratoggle_btn()
        camerastatus_lbl.configure(text="Status: Offline", text_color="red")

    def run_camera_server(port):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(("0.0.0.0", port))
            server_socket.listen(5)
            server_socket.settimeout(1)  # Prevents indefinite blocking

            update_textbox(f"Camera server listening on port {port}...")
            while is_camera_sharing:
                try:
                    conn, addr = server_socket.accept()
                    if not is_camera_sharing:
                        break
                    share_camera(conn)
                except socket.timeout:
                    continue
                except socket.error as e:
                    update_textbox(f"Socket error on port {port}: {e}")
                    break
            server_socket.close()
        except Exception as e:
            update_textbox(f"Error in camera server on port {port}: {e}")
        
    def share_camera(conn):
        last_time = time.time()
        try:
            while is_camera_sharing and conn:
                ret, frame = cap.read()
                if not ret:
                    update_textbox("Can't receive frame (stream end?).")
                frame = cv2.flip(frame, 1)  # Flip the frame horizontally

                # Process emotions every 3 seconds
                current_time = time.time()
                if current_time - last_time >= 3:
                    emotions = detector.detect_emotions(frame)
                    if emotions:
                        # Get the dominant emotion
                        top_emotion, score = detector.top_emotion(frame)

                        if top_emotion:
                            # Map emotion to color
                            color = EMOTION_COLORS.get(top_emotion, "gray")
                            percentage_score = score * 100  # Convert score to percentage
                            update_textbox(f"Dominant Emotion: {top_emotion}, Color: {color}, Score: {percentage_score:.2f}%")

                    last_time = current_time

                # Resize the frame to reduce data size
                resized_frame = cv2.resize(frame, (640, 480))  # Resize to 640x480 resolution

                # Encode the frame as JPEG
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # Set JPEG quality to 50
                _, buffer = cv2.imencode(".jpg", resized_frame, encode_param)
                frame_data = buffer.tobytes()

                # Send the size of the frame followed by the frame data
                conn.sendall(len(frame_data).to_bytes(4, "big") + frame_data)
                
                # Add a delay to control the frame rate (e.g., 10 FPS)
                time.sleep(0.1)
        except (socket.error, BrokenPipeError) as e:
            update_textbox(f"Error during camera sharing: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    update_textbox(f"Error closing connection: {e}")
    
    def run_emotion_server():
        try:
            emotion_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            emotion_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            emotion_server_socket.bind(("0.0.0.0", 5005))
            emotion_server_socket.listen(1)
            update_textbox("Emotion server is listening on port 5005...")

            while is_camera_sharing:
                try:
                    econn, addr = emotion_server_socket.accept()
                    update_textbox(f"Emotion server connected to {addr}")

                    while is_camera_sharing:
                        try:
                            ret, frame = cap.read()
                            if not ret:
                                update_textbox("Can't receive frame (stream end?).")
                                break

                            frame = cv2.flip(frame, 1)  # Flip the frame horizontally
                            emotions = detector.detect_emotions(frame)
                            if emotions:
                                top_emotion, score = detector.top_emotion(frame)
                                if top_emotion:
                                    # Map emotion to color
                                    color = EMOTION_COLORS.get(top_emotion, "gray")
                                    emotion_data = f"{top_emotion}:{color}".encode()
                                    econn.sendall(len(emotion_data).to_bytes(4, "big") + emotion_data)
                                    percentage_score = score * 100
                                    update_textbox(f"Dominant Emotion: {top_emotion}, Color: {color}, Score: {percentage_score:.2f}%")
                            time.sleep(3)  # Control the frame rate
                        except (socket.error, BrokenPipeError) as e:
                            update_textbox(f"Error sending emotion data: {e}")
                            break
                except Exception as e:
                    update_textbox(f"Error in emotion server: {e}")
                finally:
                    if econn:
                        econn.close()
        finally:
            emotion_server_socket.close()
    
    # def share_emotion(econn, emotion_data):
    #     try:
    #         while not is_camera_sharing and econn:
    #             econn.sendall(len(emotion_data).to_bytes(4, "big") + emotion_data)
    #             time.sleep(1)  # Control the frame rate
    #     except socket.timeout:
    #         update_textbox("Emotion server timed out.")
    #     except (socket.error, BrokenPipeError) as e:
    #         update_textbox(f"Error during emotion sharing: {e}")
    #     finally:
    #         if econn:
    #             econn.close()
                

    def cameratoggle_btn():
        if startcs_btn.cget("state") == "disabled":
            startcs_btn.configure(state="normal")
            stopcs_btn.configure(state="disabled")
        else:
            startcs_btn.configure(state="disabled")
            stopcs_btn.configure(state="normal")
    
    startcs_btn = ctk.CTkButton(camerabtn_frame, text="Start", width=100, height=30, fg_color="darkgreen", command=start_camera_sharing)
    startcs_btn.pack(side="left", padx=5)
    startcs_btn.bind("<Enter>", lambda e: startcs_btn.configure(fg_color="green"))
    startcs_btn.bind("<Leave>", lambda e: startcs_btn.configure(fg_color="darkgreen"))

    stopcs_btn = ctk.CTkButton(camerabtn_frame, text="Stop", width=100, height=30, fg_color="darkred", command=stop_camera_sharing)
    stopcs_btn.pack(side="left", padx=5)
    stopcs_btn.bind("<Enter>", lambda e: stopcs_btn.configure(fg_color="red"))
    stopcs_btn.bind("<Leave>", lambda e: stopcs_btn.configure(fg_color="darkred"))
    


def show_kb_sharing():
    for widget in right_panel.winfo_children():
        widget.destroy()

    kbsharing_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    kbsharing_frame.pack(fill="both", expand=True, padx=10, pady=10)

    kbbtn_frame = ctk.CTkFrame(kbsharing_frame, fg_color="transparent")
    kbbtn_frame.pack(fill="x", padx=5, pady=5)

    kbstatus_lbl = ctk.CTkLabel(kbbtn_frame, text="Status: Offline", font=("Arial", 16, "bold"))
    kbstatus_lbl.pack(side="right", padx=10, pady=5)

    statuskb_txtb = ctk.CTkTextbox(kbsharing_frame, width=500, height=400)
    statuskb_txtb.pack(fill="both", expand=True, padx=10, pady=5)

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

    def log_status(msg):
        statuskb_txtb.after(0, lambda: statuskb_txtb.insert("end", msg + "\n"))

    ### KEYBOARD MONITORING ###
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
                conn, addr = kb_server_socket[0].accept()
                log_status(f"[KB] Admin connected from {addr}")
                while is_kb_sharing[0]:
                    classify_keyboard()
                    conn.sendall(kb_status[0].encode("utf-8"))
                    time.sleep(1)
                conn.close()
            except:
                break

    def start_keyboard_sharing():
        if not is_kb_sharing[0]:
            is_kb_sharing[0] = True
            kbstatus_lbl.configure(text="Status: Sharing", text_color="green")
            start_btn.configure(state="disabled")
            stop_btn.configure(state="normal")

            kb_listener[0] = keyboard.Listener(on_press=on_press)
            kb_listener[0].start()

            try:
                kb_server_socket[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                kb_server_socket[0].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                kb_server_socket[0].bind(("0.0.0.0", 5002))
                kb_server_socket[0].listen(1)
                threading.Thread(target=accept_kb_connection, daemon=True).start()
                log_status("[KB] Keyboard sharing started on port 5002...")
            except Exception as e:
                log_status(f"[KB] Error: {e}")
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
        log_status("[KB] Keyboard sharing stopped.")

    ### MOUSE MONITORING ###
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
                conn, addr = mouse_server_socket[0].accept()
                log_status(f"[Mouse] Admin connected from {addr}")
                while is_mouse_sharing[0]:
                    classify_mouse()
                    conn.sendall(mouse_status[0].encode("utf-8"))
                    time.sleep(1)
                conn.close()
            except:
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
                mouse_server_socket[0].listen(1)
                threading.Thread(target=accept_mouse_connection, daemon=True).start()
                log_status("[Mouse] Mouse sharing started on port 5003...")
            except Exception as e:
                log_status(f"[Mouse] Error: {e}")
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
        log_status("[Mouse] Mouse sharing stopped.")

    def stop_sharing():
        kbstatus_lbl.configure(text="Status: Offline", text_color="red")
        start_btn.configure(state="normal")
        stop_btn.configure(state="disabled")
        stop_keyboard_sharing()
        stop_mouse_sharing()

    # Buttons
    start_btn = ctk.CTkButton(kbbtn_frame, text="Start", width=100, height=30, fg_color="darkgreen", command=lambda: [start_keyboard_sharing(), start_mouse_sharing()])
    start_btn.pack(side="left", padx=5)
    start_btn.bind("<Enter>", lambda e: start_btn.configure(fg_color="green"))
    start_btn.bind("<Leave>", lambda e: start_btn.configure(fg_color="darkgreen"))

    stop_btn = ctk.CTkButton(kbbtn_frame, text="Stop", width=100, height=30, fg_color="darkred", command=stop_sharing, state="disabled")
    stop_btn.pack(side="left", padx=5)
    stop_btn.bind("<Enter>", lambda e: stop_btn.configure(fg_color="red"))
    stop_btn.bind("<Leave>", lambda e: stop_btn.configure(fg_color="darkred"))

    #loads
    start_keyboard_sharing()
    start_mouse_sharing()

def appexit():
    #ScreenSharing
    global is_sharing, threads, is_camera_sharing, camera_threads
    is_sharing = False
    threads = []    
    is_camera_sharing = False
    camera_threads = []

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
    
    def stop_camera_sharing():
        global is_camera_sharing
        is_camera_sharing = False
        cap = cv2.VideoCapture(0)

        if cap:
            cap.release()
        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect(("127.0.0.1", 5004))
            temp_socket.close()
        except:
            pass

        for thread in threads:
            thread.join(timeout=2)
    stop_camera_sharing()
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
