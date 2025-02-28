import customtkinter as ctk

def close_window():
    app.destroy()  # Closes AddGroup.py


ctk.set_appearance_mode("dark") 

app = ctk.CTk()
app.title("Add Group")
app.geometry("500x200")
app.resizable(False, False)  # Fix the size
app.attributes("-topmost", True)  # Keep window on top
app.attributes("-toolwindow", True)


# Center the window on the screen
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x_position = (screen_width // 2) - (500 // 2)
y_position = (screen_height // 2) - (200 // 2)
app.geometry(f"500x200+{x_position}+{y_position}")

# Message label under the SignUp button
message_lbl = ctk.CTkLabel(app, text="Add Group", font=("Arial", 18))
message_lbl.pack(pady=15)

# Username entry
gname_txtb = ctk.CTkEntry(app, placeholder_text="Name", width=400, height=35)
gname_txtb.pack(pady=5)

# Button frame for side-by-side layout
btn_frame = ctk.CTkFrame(app, fg_color="transparent")
btn_frame.pack(pady=10)

# Buttons
add_btn = ctk.CTkButton(btn_frame, text="Add", width=190)
add_btn.pack(side="left", padx=10)

cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", width=190, fg_color="darkred", hover_color="red", command=close_window)
cancel_btn.pack(side="left", padx=10)




app.mainloop()
