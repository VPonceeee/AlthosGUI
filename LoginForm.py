import customtkinter as ctk
from pymongo import MongoClient
import subprocess

# ============================== DATABASE CONNECTION ==============================
try:
    connection_string = "mongodb+srv://altplusf42024:RuVAh3aZgUbC0YLE@altf4cluster.9p2yp.mongodb.net/?retryWrites=true&w=majority&appName=ALTF4Cluster"
    client = MongoClient(connection_string)
    db = client["ADB"]
    accounts_collection = db["Accounts"] 
    print("Connected to MongoDB Atlas!")
except Exception as e:
    print("Error connecting to MongoDB:", e)


ctk.set_appearance_mode("dark") 

app = ctk.CTk()
app.title("Althos")
app.geometry("500x600")
app.resizable(False, False)  # Fix the size

# Center the window on the screen
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x_position = (screen_width // 2) - (500 // 2)
y_position = (screen_height // 2) - (600 // 2)
app.geometry(f"500x600+{x_position}+{y_position}")

# ============================== FORM FUNCTIONS ==============================

def showpass():
    if password_txtb.cget("show") == "*":
        password_txtb.configure(show="")
    else:
        password_txtb.configure(show="*")

def login():
    email = username_txtb.get()
    password = password_txtb.get()
    user = accounts_collection.find_one({"email": email, "password": password})
    if user:
        message_lbl.configure(text="Login Successful", text_color="green")
        app.withdraw()  # Hide the login form

        #Get the data on the database
        AccID = str(user.get("_id", "Unknown"))
        username = user.get("username", "Unknown")

        process = subprocess.Popen(["python", "Main.py", AccID, username])  # Open Main.py
        process.wait()
        app.quit()
    else:
        message_lbl.configure(text="Invalid email or password!", text_color="red")

# ============================== FORM DESIGN ==============================

# Create a label with text "Althos" aligned at the top center
title_lbl = ctk.CTkLabel(app, text="ALTHOS", font=("Arial", 50, "bold"), text_color="blue")
title_lbl.pack(pady=80)

# Username entry
username_txtb = ctk.CTkEntry(app, placeholder_text="Username", width=350, height=35)
username_txtb.pack(pady=5)

# Password entry
password_txtb = ctk.CTkEntry(app, placeholder_text="Password", show="*",width=350, height=35)
password_txtb.pack(pady=5)

# Checkbox below password
showpass_cb = ctk.CTkCheckBox(app, text="Show Password", command=showpass)
showpass_cb.pack(pady=5)
showpass_cb.pack(pady=5, anchor="w", padx=75)

# Buttons
login_btn = ctk.CTkButton(app, text="Login",width=350, height=35, command=login)
login_btn.pack(pady=5)

signup_btn = ctk.CTkButton(app, text="SignUp",width=350, height=35)
signup_btn.pack(pady=5)

# Message label under the SignUp button
message_lbl = ctk.CTkLabel(app, text="", font=("Arial", 14))
message_lbl.pack(pady=5)

app.mainloop()
