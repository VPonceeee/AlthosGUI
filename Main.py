import customtkinter as ctk
from Dashboard import Dashboard
from ViewGroup import ViewGroup
import sys

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
navbar.columnconfigure((0, 1, 2), weight=1)

left_label = ctk.CTkLabel(navbar, text="ALTHOS", font=("Arial", 20, "bold"))
left_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)

right_label = ctk.CTkLabel(navbar, text=f"{username}", font=("Arial", 20, "bold"))
right_label.grid(row=0, column=2, sticky="e", padx=20, pady=10)

# Content Panel (Main Frame for Forms)
content_panel = ctk.CTkFrame(app)
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

# Run the application
app.mainloop()
