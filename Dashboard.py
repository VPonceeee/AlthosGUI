import customtkinter as ctk
from pymongo import MongoClient
from bson import ObjectId

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, switch_page):
        super().__init__(parent)  # Parent is content_panel
        self.switch_page = switch_page
        #self.AccID = acc_id  # Store logged-in user ID

        # Scrollable frame for dynamic group buttons
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=900, height=600)
        self.scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.load_groups()  # Load groups dynamically

    def load_groups(self):
        """Dynamically load groups from MongoDB and display buttons."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()  # Clear previous widgets

        # Add the "+" button first
        self.plus_button = ctk.CTkButton(
            master=self.scrollable_frame,
            text="+",
            width=200,
            height=100,
            border_width=2,
            font=("Arial", 50, "bold"),
            command=lambda: self.switch_page("GroupForm")  # Navigate to GroupForm
        )
        self.plus_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        try:
            # Database connection
            connection_string = "mongodb+srv://altplusf42024:RuVAh3aZgUbC0YLE@altf4cluster.9p2yp.mongodb.net/?retryWrites=true&w=majority&appName=ALTF4Cluster"
            client = MongoClient(connection_string)
            db = client["ADB"]
            groups_collection = db["Groups"]
            
            # Fetch groups created by the logged-in user
            groups = groups_collection.find({"CreatedBy": ObjectId(self.AccID)})

            # Layout variables
            button_width = 220  # Approximate button width (px)
            available_width = self.scrollable_frame.winfo_width() - 40
            max_columns = max(1, available_width // button_width)  # At least 1 per row

            row, column = 0, 1  # Start at row 0, column 1 (since column 0 is the "+" button)

            for group in groups:
                group_name = group["GroupName"]
                group_id = str(group["_id"])

                group_button = ctk.CTkButton(
                    master=self.scrollable_frame,
                    text=group_name,
                    width=200,
                    height=100,
                    border_width=2,
                    font=("Arial", 20, "bold"),
                    command=lambda g_name=group_name, g_id=group_id: self.ShowViewGroup(g_name, g_id)
                )
                group_button.grid(row=row, column=column, padx=5, pady=5, sticky="w")

                column += 1
                if column >= max_columns:  # Move to next row if limit is reached
                    column = 0
                    row += 1

        except Exception as e:
            print(f"Error fetching groups: {e}")

    def ShowViewGroup(self, group_name, group_id):
        """Placeholder for viewing a group. Implement as needed."""
        print(f"Viewing group: {group_name} (ID: {group_id})")
