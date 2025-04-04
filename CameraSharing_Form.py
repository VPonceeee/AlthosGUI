import tkinter as tk
import cv2
import threading
import time
from fer import FER

# Emotion-to-color mapping
EMOTION_COLORS = {
    "angry": "red",
    "disgust": "green",
    "fear": "violet",
    "happy": "yellow",
    "sad": "blue",
    "surprise": "orange",
    "neutral": "gray",
}

class CameraSharing_Form(tk.Frame): 
    def __init__(self, parent):  
        super().__init__(parent) 
         
        self.TopSpacer_pnl = tk.Frame(self, height=10)  
        self.TopSpacer_pnl.pack(side="top", fill="both", expand=False)
        
        # Top Panel
        self.Top_pnl1 = tk.Frame(self)  
        self.Top_pnl1.pack(side="top", fill="both", expand=False)

        # Start sharing button
        self.Start_btn = tk.Button(self.Top_pnl1, text="Turn On Camera", bg="lightgray", height=2, width=15, relief="flat", command=self.start_fer)
        self.Start_btn.pack(side="left", fill="both", padx=2, pady=2)

        # Stop sharing button
        self.Stop_btn = tk.Button(self.Top_pnl1, text="Turn Off Camera", bg="lightgray", height=2, width=15, relief="flat", command=self.stop_fer, state="disabled")
        self.Stop_btn.pack(side="left", fill="both", padx=2, pady=2)

        # Status Label
        self.Status_lbl = tk.Label(self.Top_pnl1, text="Status", font=("Arial", 14)) 
        self.Status_lbl.pack(side="right", fill="both", padx=(1, 10), pady=5)

        # Main Panel
        self.main_panel = tk.Frame(self) 
        self.main_panel.pack(side="top", fill="both", expand=True, pady=5)

        # Status textbox 
        self.StatusMsg_txtb = tk.Text(self.main_panel, relief="sunken", bd=2, wrap="none")
        self.StatusMsg_txtb.pack(side="left", fill="both", expand=True)

        # Scroll Bar
        self.scrollbar = tk.Scrollbar(self.main_panel, orient="vertical", command=self.StatusMsg_txtb.yview)
        self.scrollbar.pack(side="right", fill="y")

        # Configure the Text widget to work with the Scrollbar
        self.StatusMsg_txtb.config(yscrollcommand=self.scrollbar.set, state="disabled")

        # FER-related attributes
        self.fer_thread = None
        self.running = False

    def start_fer(self):
        """Start the FER process in a separate thread."""
        self.running = True
        self.toggle_buttons()
        self.fer_thread = threading.Thread(target=self.run_fer, daemon=True)
        self.fer_thread.start()

    def stop_fer(self):
        """Stop the FER process."""
        self.running = False
        self.toggle_buttons()

    def run_fer(self):
        """Run the FER process using the webcam."""
        detector = FER(mtcnn=False)  # Initialize FER detector
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.update_status("Cannot open camera")
            return

        last_time = time.time()

        while self.running:
            ret, frame = cap.read()
            if not ret:
                self.update_status("Can't receive frame (stream end?). Exiting ...")
                break

            frame = cv2.flip(frame, 1)  # Flip the frame horizontally

            # Process every 3 seconds
            current_time = time.time()
            if current_time - last_time >= 3:
                emotions = detector.detect_emotions(frame)
                if emotions:
                    # Get the dominant emotion
                    top_emotion, score = detector.top_emotion(frame)

                    if top_emotion:
                        # Map emotion to color
                        color = EMOTION_COLORS.get(top_emotion, "unknown")
                        percentage_score = score * 100  # Convert score to percentage
                        self.update_status(f"Dominant Emotion: {top_emotion}, Color: {color}, Score: {percentage_score:.2f}%")

                last_time = current_time

            # Display the raw frame without annotations
            cv2.imshow("Facial Emotion Recognition", frame)

            # Check if the window is closed or 'q' is pressed
            key = cv2.waitKey(1)
            if key == ord("q") or cv2.getWindowProperty("Facial Emotion Recognition", cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()

    def update_status(self, message):
        """Update the status textbox with a message."""
        self.StatusMsg_txtb.config(state="normal")
        self.StatusMsg_txtb.insert("end", message + "\n")
        self.StatusMsg_txtb.see("end")
        self.StatusMsg_txtb.config(state="disabled")

    def toggle_buttons(self):
        """Toggle the state of the Start and Stop buttons."""
        if self.Start_btn["state"] == "normal":
            self.Start_btn.config(state="disabled")
            self.Stop_btn.config(state="normal")
        else:
            self.Start_btn.config(state="normal")
            self.Stop_btn.config(state="disabled")