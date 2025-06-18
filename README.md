# 📸 Attendance Management System

A modern, user-friendly **Attendance Management System** that leverages **Facial Recognition**, **GPS-based location tracking**, and **Cloud Integration** to automate and secure the attendance process for classrooms, training sessions, or corporate environments.

---

## 🚀 Features

- 🔍 **Facial Recognition-Based Attendance**
  - Detects and recognizes student faces in real-time.
  - Automatically marks attendance and stores data securely.
  
- 🗺️ **GPS Location Tracking**
  - Captures the exact location where attendance is marked.
  - Ensures geo-verification for authentic entries.
  
- ☁️ **Cloud Sync (AWS/Firebase)**
  - Stores attendance data in real-time on the cloud.
  - Accessible across multiple devices for professors/admins.

- 🧑‍🏫 **Class-Based Session Tracking**
  - Select or create a class before starting attendance.
  - Generates separate logs for each class session.

- 📊 **CSV Export & Reports**
  - Attendance logs saved locally and optionally to cloud.
  - Downloadable `.csv` reports for each session.

- 🧠 **Smart Face Registration**
  - If face not found, prompts to register new student.
  - Saves face data locally for future detection.

---

## 🛠️ Tech Stack

- **Frontend:** Python (Tkinter / PyQt5)
- **Backend:** OpenCV, face_recognition (dlib), NumPy, Pandas
- **Cloud:** AWS S3 / Firebase Realtime Database
- **Database:** CSV / Firebase
- **Location Services:** geopy, requests (for IP-based location or GPS)
- **Deployment:** Standalone Desktop App (.exe with PyInstaller)
