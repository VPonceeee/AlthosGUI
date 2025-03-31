import customtkinter as ctk
import socket
import os

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

    screenbtn_frame = ctk.CTkFrame(screen_sharing_frame,fg_color="transparent")
    screenbtn_frame.pack(fill="x", padx=5, pady=5)

    startss_btn = ctk.CTkButton(screenbtn_frame, text="Start", width=100, height=30,fg_color="darkgreen")
    startss_btn.pack(side="left", padx=5)

    stopss_btn = ctk.CTkButton(screenbtn_frame, text="Stop", width=100, height=30,fg_color="darkred")
    stopss_btn.pack(side="left", padx=5)
    
    screenstatus_lbl = ctk.CTkLabel(screenbtn_frame, text="Status: Active", font=("Arial", 16, "bold"))
    screenstatus_lbl.pack(side="right", padx=10, pady=5)

    statusScreen_txtb = ctk.CTkTextbox(screen_sharing_frame, width=500, height=400)
    statusScreen_txtb.pack(fill="both", expand=True, padx=10, pady=5)

def show_camera_sharing():
    for widget in right_panel.winfo_children():
        widget.destroy()
    
    camera_sharing_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    camera_sharing_frame.pack(fill="both", expand=True, padx=10, pady=10)

    camerabtn_frame = ctk.CTkFrame(camera_sharing_frame,fg_color="transparent")
    camerabtn_frame.pack(fill="x", padx=5, pady=5)

    startcs_btn = ctk.CTkButton(camerabtn_frame, text="Start", width=100, height=30,fg_color="darkgreen")
    startcs_btn.pack(side="left", padx=5)

    stopcs_btn = ctk.CTkButton(camerabtn_frame, text="Stop", width=100, height=30,fg_color="darkred")
    stopcs_btn.pack(side="left", padx=5)

    screenstatus_lbl = ctk.CTkLabel(camerabtn_frame, text="Status: Active", font=("Arial", 16, "bold"))
    screenstatus_lbl.pack(side="right", padx=10, pady=5)

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
show_deviceinfo()

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
