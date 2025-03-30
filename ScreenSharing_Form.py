import tkinter as tk
import socket
import threading
import time
from PIL import ImageGrab, Image, ImageDraw
import io
import pyautogui

class ScreenSharing_Form(tk.Frame): 
    def __init__(self, parent):  
        super().__init__(parent)
        self.is_sharing = False
        self.threads = []

        self.TopSpacer_pnl = tk.Frame(self, height=10)  
        self.TopSpacer_pnl.pack(side="top", fill="both", expand=False)
        
        self.Top_pnl1 = tk.Frame(self)  
        self.Top_pnl1.pack(side="top", fill="both", expand=False)

        self.Start_btn = tk.Button(self.Top_pnl1, text="Start Sharing", bg="lightgray", height=2, width=15, relief="flat", command=self.start_sharing)
        self.Start_btn.pack(side="left", fill="both", padx=2, pady=2)

        self.Stop_btn = tk.Button(self.Top_pnl1, text="Stop Sharing", bg="lightgray", height=2, width=15, relief="flat", command=self.stop_sharing)
        self.Stop_btn.pack(side="left", fill="both", padx=2, pady=2)

        self.Status_lbl = tk.Label(self.Top_pnl1, text="Status", font=("Arial", 14)) 
        self.Status_lbl.pack(side="right", fill="both", padx=(1, 10), pady=5)

        self.main_panel = tk.Frame(self) 
        self.main_panel.pack(side="top", fill="both", expand=True, pady=5)

        self.StatusMsg_txtb = tk.Text(self.main_panel, relief="sunken", bd=2, wrap="word", font=("Arial", 12))
        self.StatusMsg_txtb.pack(side="left", fill="both", expand=False)

        self.scrollbar = tk.Scrollbar(self.main_panel, orient="vertical", command=self.StatusMsg_txtb.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.StatusMsg_txtb.config(yscrollcommand=self.scrollbar.set)

    def toggle_buttons(self):
        self.Start_btn.config(state="disabled" if self.is_sharing else "normal")
        self.Stop_btn.config(state="normal" if self.is_sharing else "disabled")

    def start_sharing(self):
        if not self.is_sharing:
            self.is_sharing = True
            self.threads = []
            
            for port in [5000, 5001]:
                thread = threading.Thread(target=self.run_server, args=(port,))
                thread.start()
                self.threads.append(thread)

            self.toggle_buttons()
            self.Status_lbl.config(text="Online", fg="green")
            self.StatusMsg_txtb.insert("end", "Screen sharing started on ports 5000 and 5001...\n")

    def stop_sharing(self):
        self.is_sharing = False
        self.StatusMsg_txtb.insert("end", "Stopping screen sharing...\n")
        
        for thread in self.threads:
            thread.join(timeout=2)

        self.StatusMsg_txtb.insert("end", "Screen sharing has been stopped.\n")
        self.toggle_buttons()

    def run_server(self, port):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(("0.0.0.0", port))
            server_socket.listen(5)
            self.StatusMsg_txtb.insert("end", f"Server listening on port {port}...\n")

            while self.is_sharing:
                try:
                    conn, addr = server_socket.accept()
                    print(f"Connected to {addr} on port {port}")
                    self.share_screen(conn)
                except socket.error as e:
                    print(f"Socket error on port {port}: {e}")
                finally:
                    if conn:
                        conn.close()
        except Exception as e:
            print(f"Error in server on port {port}: {e}")
        finally:
            server_socket.close()

    def share_screen(self, conn):
        try:
            while self.is_sharing and conn:
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