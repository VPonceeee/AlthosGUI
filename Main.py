import customtkinter as ctk
from Dashboard import Dashboard
from ViewGroup import ViewGroup
import sys
import subprocess

# Retrieve user info from command-line arguments
AccID = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
username = sys.argv[2] if len(sys.argv) > 1 else "Guest"

# Initialize the application
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("1080x720")
app.minsize(1080, 720)

# Set maximum size based on screen resolution
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
app.maxsize(screen_width, screen_height)

# Center the window on the screen
x_position = (screen_width // 2) - (1080 // 2)
y_position = (screen_height // 2) - (720 // 2)
app.geometry(f"1080x720+{x_position}+{y_position}")

app.title("Althos")  # Window title

# Navbar Frame
navbar = ctk.CTkFrame(app, height=50)
navbar.pack(fill="x", side="top")

# Equal aligned text using grid
navbar.columnconfigure(0, weight=0)  # Hamburger - fixed
navbar.columnconfigure(1, weight=0)  # App Name - fixed

dropdown_menu = ctk.CTkFrame(app, width=300, height=app.winfo_height() - 50)
dropdown_menu.pack_propagate(False) 
dropdown_menu.place_forget()

#dropdown_menu items
menu_label = ctk.CTkLabel(dropdown_menu, text="Menu", font=("Arial", 18, "bold"))
menu_label.pack(pady=10)

RL_btn = ctk.CTkButton(dropdown_menu, text="Report Logs", width=280,command=lambda: open_report_logs())
RL_btn.pack(pady=1)

Settings_btn = ctk.CTkButton(dropdown_menu, text="Settings", width=280)
Settings_btn.pack(pady=1)

def logout():
    app.destroy()
    subprocess.Popen(["python", "LoginForm.py"])

logout_btn = ctk.CTkButton(dropdown_menu, text="Logout", command=logout, width=280, fg_color="darkred", hover_color="red")
logout_btn.pack(side="bottom", pady=10)

def toggle_menu():
    if dropdown_menu.winfo_ismapped():
        dropdown_menu.place_forget()
    else:
        form_height = app.winfo_height()
        dropdown_menu.configure(height=form_height - 50)  # Dynamically update height
        dropdown_menu.place(x=0, y=50)  # y=50 to stay under navbar
        dropdown_menu.lift()

hamburger_btn = ctk.CTkButton(navbar, text="≡", width=40, command=toggle_menu, fg_color="transparent", font=("Arial", 20))
hamburger_btn.grid(row=0, column=0, padx=(10, 2), pady=10)

left_label = ctk.CTkLabel(navbar, text="ALTHOS", font=("Arial", 20, "bold"))
left_label.grid(row=0, column=1, padx=3, pady=10)

# Content Panel (Main Frame for Forms)
content_panel = ctk.CTkFrame(app, fg_color="transparent")
content_panel.pack(fill="both", expand=True, padx=20, pady=20)

content_panel.rowconfigure(0, weight=1)
content_panel.columnconfigure(0, weight=1)

# Dictionary to store pages
pages = {}

def add_page(page_class, page_name):
    """Create and store a page inside content_panel."""
    if page_name == "Dashboard":
        page = page_class(content_panel, switch_page, AccID, username)  # Pass AccID and username
    else:
        page = page_class(content_panel, switch_page)
    
    pages[page_name] = page
    page.grid(row=0, column=0, sticky="nsew")  # Make it fill the space

#Default
def switch_page(page_name, data=None):
    """Show the selected page and pass optional data."""
    if page_name in pages:
        for page in pages.values():
            page.grid_forget()  # Hide other pages
        
        pages[page_name].grid(row=0, column=0, sticky="nsew")  # Show new page
        
    if data and hasattr(pages[page_name], "set_group_data"):
        pages[page_name].set_group_data(data["GroupID"], data["GroupName"])  # Pass both ID and Name


# Add pages inside content_panel
add_page(Dashboard, "Dashboard")
add_page(ViewGroup, "ViewGroup")

# Show Dashboard on startup
switch_page("Dashboard")

def open_report_logs():
    subprocess.Popen(["python", "reportlogs.py", AccID])

# Run the application
app.mainloop()
