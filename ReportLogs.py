import tkinter as tk
from tkinter import ttk
from pymongo import MongoClient

# MongoDB Connection (Make sure this is correctly set up)
try:
    connection_string = "mongodb+srv://altplusf42024:RuVAh3aZgUbC0YLE@altf4cluster.9p2yp.mongodb.net/?retryWrites=true&w=majority&appName=ALTF4Cluster"
    client = MongoClient(connection_string)
    db = client["ADB"]
    devices_collection = db["ReportLogs"]
except Exception as e:
    print("Error connecting to MongoDB:", e)

# Fetch the data from the MongoDB collection
def fetch_data_from_mongo():
    try:
        # Fetch all documents from the ReportLogs collection
        data = list(devices_collection.find())
        return data
    except Exception as e:
        print("Error fetching data from MongoDB:", e)
        return []

# Function to update the Treeview widget
def update_treeview():
    # Clear existing data in the Treeview
    for item in tree.get_children():
        tree.delete(item)

    # Fetch the updated data from MongoDB
    report_logs_data = fetch_data_from_mongo()

    if report_logs_data:
        # Set up the columns (header names) based on the keys of the first document
        tree["columns"] = list(report_logs_data[0].keys())

        # Set the heading for each column
        for col in tree["columns"]:
            tree.heading(col, text=col, anchor="center")  # Center the heading text

        # Set the column data to be centered as well
        for col in tree["columns"]:
            tree.column(col, anchor="center")  # Center the data in each column

        # Add alternating row colors and insert the data
        for index, record in enumerate(report_logs_data):
            # Convert each MongoDB document into a list of values
            row_data = [record.get(col, "") for col in tree["columns"]]

            # Alternate row color
            if index % 2 == 0:
                tree.insert("", tk.END, values=row_data, tags=("even",))
            else:
                tree.insert("", tk.END, values=row_data, tags=("odd",))

        # Configure the tag styles for alternating row colors
        tree.tag_configure("even", background="#f2f2f2")  # Light gray for even rows
        tree.tag_configure("odd", background="#ffffff")  # White for odd rows
    else:
        print("No data found in MongoDB.")

# Create the main tkinter window
root = tk.Tk()
root.title("ReportLogs Data Display")

# Create a Treeview widget to display the table
tree = ttk.Treeview(root, show="headings")  # Use 'headings' to hide the first blank column

# Create a scrollbar for the Treeview
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Pack the Treeview widget
tree.pack(padx=10, pady=10)

# Create a "Refresh" button
refresh_button = tk.Button(root, text="Refresh", command=update_treeview)
refresh_button.pack(padx=10, pady=10)

# Initial load of data into the Treeview
update_treeview()

# Start the main loop to run the GUI
root.mainloop()
