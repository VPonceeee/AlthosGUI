import customtkinter as ctk
from Dashboard import Dashboard
from GroupForm import GroupForm

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

app.title("Althos")  # Form title

# Navbar Frame
navbar = ctk.CTkFrame(app, height=50)
navbar.pack(fill="x", side="top")

# Equal aligned text using grid
navbar.columnconfigure((0, 1, 2), weight=1)

left_label = ctk.CTkLabel(navbar, text="Left", font=("Arial", 20, "bold"))
left_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)

center_label = ctk.CTkLabel(navbar, text="Center", font=("Arial", 20, "bold"))
center_label.grid(row=0, column=1, sticky="n", pady=10)

right_label = ctk.CTkLabel(navbar, text="Right", font=("Arial", 20, "bold"))
right_label.grid(row=0, column=2, sticky="e", padx=20, pady=10)

# Content Panel (Main Frame for Forms)
content_panel = ctk.CTkFrame(app)
content_panel.pack(fill="both", expand=True, padx=20, pady=20)

# Enable resizing inside content_panel
content_panel.rowconfigure(0, weight=1)
content_panel.columnconfigure(0, weight=1)

# Dictionary to store pages
pages = {}

def add_page(page_class, page_name):
    """Create and store a page inside content_panel."""
    page = page_class(content_panel, switch_page)
    pages[page_name] = page
    page.grid(row=0, column=0, sticky="nsew")  # Make it fill the space

def switch_page(page_name):
    """Show the selected page."""
    page = pages.get(page_name)
    if page:
        page.tkraise()

# Add pages inside content_panel
add_page(Dashboard, "Dashboard")
add_page(GroupForm, "GroupForm")

# Show Dashboard on startup
switch_page("Dashboard")

# Run the application
app.mainloop()
