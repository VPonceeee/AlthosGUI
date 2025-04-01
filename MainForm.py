import tkinter as tk
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from DeviceInfo_Form import DeviceInfo_Form
from ScreenSharing_Form import ScreenSharing_Form
from CameraSharing_Form import CameraSharing_Form


class MainForm(tk.Tk):
    def __init__(self): 
        super().__init__()

        # Form Section
        self.title("User App")  
        Formwidth, Formheight = 800, 600 
        self.geometry(f"{Formwidth}x{Formheight}") 
        self.resizable(False, False)  
        screen_width = self.winfo_screenwidth() 
        screen_height = self.winfo_screenheight() 
        x = (screen_width - Formwidth) // 2 
        y = (screen_height - Formheight) // 2  
        self.geometry(f"{Formwidth}x{Formheight}+{x}+{y}") 

        # Panel Section
        self.left_pnl = tk.Frame(self, bg="lightgray", width=240, height=Formheight)  
        self.left_pnl.pack(side="left", fill="y", expand=False)

        self.main_panel = tk.Frame(self) 
        self.main_panel.pack(side="left", fill="both", expand=True, padx=5)

        # Button section
        self.spacer1_pnl = tk.Frame(self.left_pnl, bg="lightgray", width=30, height=2)  
        self.spacer1_pnl.pack(side="top", fill="x", padx=10, pady=5)

        # Device Info Button
        self.deviceInfo_btn = tk.Button(self.left_pnl, text="Device Info", bg="white", height=2, width=30, relief="flat", command=self.Show_DeviceInfo)
        self.deviceInfo_btn.pack(side="top", fill="x", padx=10, pady=2)

        # Camera Service Button
        self.cam_btn = tk.Button(self.left_pnl, text="Camera Service", bg="white", height=2, width=30, relief="flat", command=self.Show_CameraSharing)
        self.cam_btn.pack(side="top", fill="x", padx=10, pady=2)

        # Screen Service Button
        self.screen_btn = tk.Button(self.left_pnl, text="Screen Service", bg="white", height=2, width=30, relief="flat", command=self.Show_ScreenSharing)
        self.screen_btn.pack(side="top", fill="x", padx=10, pady=2)

        # Stop All Service Button
        self.stop_btn = tk.Button(self.left_pnl, text="Stop All Service", bg="white", height=2, width=30, relief="flat", command=self.stop_all_services)
        self.stop_btn.pack(side="top", fill="x", padx=10, pady=2)

        # Close Button
        self.close_btn = tk.Button(self.left_pnl, text="Close", bg="white", height=2, width=30, relief="flat", command=self.on_closing)
        self.close_btn.pack(side="top", fill="x", padx=10, pady=2)

        # Form Load
        self.screen_sharing_form = None
        self.Show_ScreenSharing()
        self.Show_DeviceInfo()

        # Bind window close and minimize events
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Unmap>", self.on_minimize)

        # Create a system tray icon
        self.tray_icon = None
        self.create_tray_icon()

    def create_tray_icon(self):
        # Create an icon for the system tray
        image = Image.new("RGB", (64, 64), "blue")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 64, 64), fill="blue")
        draw.text((10, 20), "App", fill="white")

        menu = Menu(
            MenuItem("Restore", self.restore_window),
            MenuItem("Exit", self.on_closing)
        )
        self.tray_icon = Icon("User App", image, "User App", menu)

    def on_minimize(self, event):
        if self.state() == "iconic":  # Minimized state
            self.withdraw()  # Hide the window
            if self.tray_icon:
                self.tray_icon.run_detached()  # Show the tray icon

    def restore_window(self):
        self.deiconify()  # Restore the window
        if self.tray_icon:
            self.tray_icon.stop()  # Remove the tray icon

    def Show_DeviceInfo(self): 
        for widget in self.main_panel.winfo_children():  
            widget.destroy()  

        DeviceInfo = DeviceInfo_Form(self.main_panel) 
        DeviceInfo.pack(fill=tk.BOTH, expand=True)    

    def Show_ScreenSharing(self): 
        for widget in self.main_panel.winfo_children():  
            widget.destroy()  

        self.screen_sharing_form = ScreenSharing_Form(self.main_panel) 
        self.screen_sharing_form.pack(fill=tk.BOTH, expand=True)
        self.screen_sharing_form.start_sharing()

    def Show_CameraSharing(self): 
        for widget in self.main_panel.winfo_children():  
            widget.destroy()  

        CameraSharing = CameraSharing_Form(self.main_panel) 
        CameraSharing.pack(fill=tk.BOTH, expand=True)

    def stop_all_services(self):
        if self.screen_sharing_form:
            self.screen_sharing_form.stop_sharing()

    def on_closing(self):
        # Stop screen sharing before closing the app
        if self.screen_sharing_form:
            self.screen_sharing_form.stop_sharing()
        if self.tray_icon:
            self.tray_icon.stop()  # Stop the tray icon
        self.quit()


# Start the Tkinter event loop
if __name__ == "__main__":  
    app = MainForm()  
    app.mainloop()
