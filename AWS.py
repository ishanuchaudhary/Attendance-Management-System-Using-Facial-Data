import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.simpledialog import askstring
import threading
import cv2
import face_recognition
import numpy as np
import os
import pandas as pd
from datetime import datetime
from PIL import Image, ImageTk
import time
import requests

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("1100x950")
        self.root.configure(bg="#e6f2ff")

        self.class_name = tk.StringVar()
        self.attendance_count = tk.IntVar(value=0)
        self.time_var = tk.StringVar()
        self.location_var = tk.StringVar(value="🌍 Location: Fetching...")

        self.setup_ui()

        self.cap = None
        self.running = False
        self.known_encodings = []
        self.class_names = []
        self.marked_names = set()

        self.image_path = "images"
        os.makedirs(self.image_path, exist_ok=True)

        self.update_clock()
        self.update_location()

    def setup_ui(self):
        title = tk.Label(self.root, text="📸 Face Recognition Attendance System", font=("Segoe UI", 24, "bold"), bg="#e6f2ff", fg="#003366")
        title.pack(pady=20)

        frame = tk.Frame(self.root, bg="#e6f2ff")
        frame.pack(pady=10)

        tk.Label(frame, text="Class Name:", font=("Segoe UI", 12), bg="#e6f2ff").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame, textvariable=self.class_name, font=("Segoe UI", 12), width=20).grid(row=0, column=1, padx=5, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=6, background="#007acc", foreground="white")

        ttk.Button(frame, text="▶ Start Attendance", command=self.start_attendance).grid(row=0, column=2, padx=10)
        ttk.Button(frame, text="➕ Add Student", command=self.add_new_student).grid(row=0, column=3, padx=10)
        ttk.Button(frame, text="📁 Export CSV", command=self.export_csv).grid(row=0, column=4, padx=10)
        ttk.Button(frame, text="❌ Exit", command=self.exit_app).grid(row=0, column=5, padx=10)

        self.dashboard_frame = tk.Frame(self.root, bg="#e6f2ff")
        self.dashboard_frame.pack(pady=5)

        tk.Label(self.dashboard_frame, textvariable=self.time_var, font=("Segoe UI", 14), bg="#e6f2ff", fg="#003366").pack()
        tk.Label(self.dashboard_frame, textvariable=self.location_var, font=("Segoe UI", 12), bg="#e6f2ff", fg="#003366").pack(pady=2)
        tk.Label(self.dashboard_frame, text="✅ Total Marked Attendance:", font=("Segoe UI", 14, "bold"), bg="#e6f2ff").pack()
        tk.Label(self.dashboard_frame, textvariable=self.attendance_count, font=("Segoe UI", 24, "bold"), fg="green", bg="#e6f2ff").pack()

        self.video_label = tk.Label(self.root, bg="#000", bd=3, relief=tk.SUNKEN)
        self.video_label.pack(pady=10, ipadx=10, ipady=10)

        self.log_area = tk.Text(self.root, height=15, state='disabled', bg="#f4f4f4", font=("Consolas", 10), relief=tk.GROOVE)
        self.log_area.pack(pady=10, fill=tk.X, padx=20)

        self.checkmark_label = tk.Label(self.root, text="✅", font=("Segoe UI", 40), fg="green", bg="#e6f2ff")
        self.checkmark_label.place_forget()

        self.animate_border()

    def animate_border(self):
        colors = ["#007acc", "#3399ff", "#66ccff"]
        def pulse(index=0):
            color = colors[index % len(colors)]
            self.video_label.config(highlightbackground=color, highlightthickness=4)
            self.root.after(500, pulse, index + 1)
        pulse()

    def update_clock(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(f"🕒 Current Time: {now}")
        self.root.after(1000, self.update_clock)

    def update_location(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            city = data.get("city", "Unknown")
            region = data.get("region", "Unknown")
            country = data.get("country", "Unknown")
            self.current_location = f"{city}, {region}, {country}"
            self.location_var.set(f"🌍 Location: {self.current_location}")
        except:
            self.current_location = "Unknown"
            self.location_var.set("🌍 Location: Unknown")

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def load_images(self):
        images = []
        names = []
        for file in os.listdir(self.image_path):
            img = cv2.imread(os.path.join(self.image_path, file))
            if img is not None:
                images.append(img)
                names.append(os.path.splitext(file)[0])
        return images, names

    def encode_faces(self, images):
        encodings = []
        for idx, img in enumerate(images):
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            enc = face_recognition.face_encodings(rgb)
            if enc:
                encodings.append(enc[0])
        return encodings

    def show_checkmark_animation(self):
        self.checkmark_label.place(relx=0.9, rely=0.1)
        self.root.after(1500, lambda: self.checkmark_label.place_forget())

    def mark_attendance(self, name):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = f"attendance_{self.class_name.get()}.csv"
        if not os.path.exists(filename):
            df = pd.DataFrame(columns=["Name", "Timestamp", "Location", "Status"])
        else:
            df = pd.read_csv(filename)

        if name not in df["Name"].values:
            new_entry = pd.DataFrame([[name, now, self.current_location, "Present"]], columns=["Name", "Timestamp", "Location", "Status"])
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(filename, index=False)
            self.attendance_count.set(len(df))
            self.log(f"✅ {name} marked present at {now} from {self.current_location}")
            self.show_checkmark_animation()

    def start_attendance(self):
        if not self.class_name.get():
            messagebox.showerror("Error", "Please enter class name.")
            return

        # Clear logs on new session
        self.log_area.config(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.config(state='disabled')

        self.marked_names.clear()
        self.images, self.class_names = self.load_images()
        self.known_encodings = self.encode_faces(self.images)

        if not self.known_encodings:
            messagebox.showerror("Error", "No face encodings found. Please add at least one student.")
            return

        self.attendance_count.set(0)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.running = True

        threading.Thread(target=self.update_frame, daemon=True).start()

    def update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            faces = face_recognition.face_locations(rgb_small)
            encodings = face_recognition.face_encodings(rgb_small, faces)

            for encode_face, face_loc in zip(encodings, faces):
                matches = face_recognition.compare_faces(self.known_encodings, encode_face)
                face_dist = face_recognition.face_distance(self.known_encodings, encode_face)

                if True in matches:
                    best_match_index = np.argmin(face_dist)
                    if matches[best_match_index]:
                        name = self.class_names[best_match_index].upper()
                        if name not in self.marked_names:
                            self.mark_attendance(name)
                            self.marked_names.add(name)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.root.after(0, self.update_video_label, imgtk)

        self.cap.release()

    def update_video_label(self, imgtk):
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

    def export_csv(self):
        filename = f"attendance_{self.class_name.get()}.csv"
        if os.path.exists(filename):
            export_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=filename
            )
            if export_path:
                df = pd.read_csv(filename)
                df.to_csv(export_path, index=False)
                self.log(f"📁 CSV exported to: {export_path}")
        else:
            messagebox.showinfo("Info", "No attendance file found.")

    def exit_app(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.destroy()

    def add_new_student(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        time.sleep(1)
        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to access the camera.")
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)

        if len(faces) == 0:
            messagebox.showinfo("Info", "No face detected. Please try again.")
            return

        if len(faces) > 1:
            messagebox.showinfo("Info", "Multiple faces detected. Please ensure only one face is visible.")
            return

        name = askstring("Student Name", "Enter the name of the new student:")
        if not name:
            return

        top, right, bottom, left = faces[0]
        face_img = frame[top:bottom, left:right]
        filename = os.path.join(self.image_path, f"{name}.jpg")
        cv2.imwrite(filename, face_img)

        self.log(f"➕ {name} added successfully!")

        self.images, self.class_names = self.load_images()
        self.known_encodings = self.encode_faces(self.images)

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
