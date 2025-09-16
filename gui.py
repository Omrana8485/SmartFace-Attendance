############### IMPORTS ###############
import customtkinter as ctk
from datetime import datetime
import threading
import csv
import os
import cv2
from PIL import Image, ImageTk
import numpy as np
import sys
from tkinter import filedialog
import shutil
from tkinter import messagebox
from tkinter import filedialog

# PROJECT PATHS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STUDENTS_DIR = os.path.join(DATA_DIR, "students")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

for p in (DATA_DIR, STUDENTS_DIR, IMAGES_DIR):
    os.makedirs(p, exist_ok = True)

# Import DB 
from logic import db_handler
from logic.camera import Camera
from logic.face_trainer import Trainer
from logic.user_auth import Authenticator
#######################################

# CLASS: AttendanceApp
# Purpose: Main GUI class for Attendance System using CustomTkinter
class AttendanceApp(ctk.CTk):

    # FN: __init__
    # Purpose: Initialize the main window and set up UI elements
    def __init__(self):
        # Backend instances
        self.camera_obj = Camera()
        self.trainer_obj = Trainer()
        self.authenticator = Authenticator()

        super().__init__()

        #instance variables
        self.total_students = 0
        self.today_present = 0
        self.today_absent = 0

        # Window setup
        self.title("FaceTrack - Smart Attendance System") #Window Title
        self.geometry("1280x720")   #Window Size
        self.configure(bg = "#FFFFFF")  # Main Background Color

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width = 300, fg_color = "#201F1E")
        self.sidebar.pack(side = "left", fill = "y")
        self.sidebar.pack_propagate(False)

        # App name on sidebar
        self.app_label = ctk.CTkLabel(self.sidebar, text = "FaceTrack",
                                      text_color = "white", font = ("Segoe UI", 36, "bold"))
        self.app_label.pack(side = "top", pady = 20)

        # Sidebar buttons
        button_font = ("Segoe UI", 18, "bold")
        self.dashboard_btn = ctk.CTkButton(self.sidebar, text = "Dashboard", fg_color = "#0078D4", hover_color = "#106EBE", 
                                           text_color = "white", width = 220, height = 45, font = button_font, corner_radius = 8, command = self.show_dashboard)
        self.dashboard_btn.pack(pady = 10)

        self.attendance_btn = ctk.CTkButton(self.sidebar, text = "Take Attendance", fg_color = "#0078D4", hover_color = "#106EBE", 
                                            text_color="white",
                                            width = 220, height = 45, font = button_font, corner_radius = 8, command = self.show_attendance)
        self.attendance_btn.pack(pady=10)

        self.register_btn = ctk.CTkButton(self.sidebar, text = "Register Student", fg_color = "#0078D4", hover_color = "#106EBE",
                                          text_color = "white", width = 220, height = 45,
                                          font = button_font, corner_radius = 8, command = self.show_register)
        self.register_btn.pack(pady = 10)

        self.settings_btn = ctk.CTkButton(self.sidebar, text = "Settings", fg_color = "#0078D4", hover_color = "#106EBE",
                                          text_color = "white", width = 220, height = 45,
                                          font = button_font, corner_radius = 8, command = self.show_settings)
        self.settings_btn.pack(pady = 10)

        # Top bar
        self.topbar = ctk.CTkFrame(self, height = 120, fg_color = "#F3F2F1")
        self.topbar.pack(side = "top", fill = "x")

        self.title_label = ctk.CTkLabel(self.topbar, text = "Dashboard",
                                        text_color = "#201F1E", font = ("Segoe UI", 24, "bold"))
        self.title_label.pack(side = "left", padx = 30, pady = 15)

        # Date and time frame
        self.datetime_frame = ctk.CTkFrame(self.topbar, fg_color = "#F3F2F1")
        self.datetime_frame.pack(side = "right", padx = 20, pady = 10)

        # Date Label
        self.date_label = ctk.CTkLabel(self.datetime_frame, text = "", text_color = "#201F1E", font = ("Segoe UI", 16))
        self.date_label.pack()
        
        # Time Label
        self.time_label = ctk.CTkLabel(self.datetime_frame, text = "", text_color = "#201F1E", font = ("Segoe UI", 18, "bold"))
        self.time_label.pack() 

        self.update_datetime()  

        # Main content area
        self.content_frame = ctk.CTkFrame(self, fg_color = "#FFFFFF")
        self.content_frame.pack(side = "right", fill = "both", expand = True)

        self.update_dashboard()

        # Bind window close event to properly release camera
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    #######################################
    
    # FN: on_closing
    # Purpose: Properly close camera and cleanup when application is closed
    def on_closing(self):
        try:
            # Release camera if it exists
            if hasattr(self, 'camera_obj') and self.camera_obj.cap.isOpened():
                self.camera_obj.cap.release()
                print("Camera released on application close")
            
            # Close all OpenCV windows
            cv2.destroyAllWindows()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            # Destroy the main window
            self.destroy()

    #######################################

    # FN: update_datetime
    # Purpose: Keep updating date and time in top bar
    def update_datetime(self):
        now = datetime.now()
        date_str = now.strftime("%B, %d, %Y")
        time_str = now.strftime("%I:%M:%S %p")
    
        self.date_label.configure(text = date_str)
        self.time_label.configure(text = time_str)
    
        self.after(1000, self.update_datetime)   # Refresh every second

    #######################################

    # FN: show_dashboard
    # Purpose: Display dashboard content in content frame
    def show_dashboard(self):
        self.title_label.configure(text = "Dashboard")
        self.clear_content()

        # Update stats first
        self.update_dashboard()

        # Create a frame for summary cards
        summary_frame = ctk.CTkFrame(self.content_frame, fg_color = "#FFFFFF")
        summary_frame.pack(fill = "x", padx = 30, pady = 20)

        # Card Styles
        card_width = 250
        card_height = 120
        card_font = ("Segoe UI", 18, "bold")

        # Total Students Card
        total_students_card = ctk.CTkFrame(summary_frame, width = card_width, height = card_height, fg_color = "#0078D4", corner_radius = 10)
        total_students_card.pack(side = "left", padx = 10)
        total_students_card.pack_propagate(False)
        total_label = ctk.CTkLabel(total_students_card, text = "Total Students", font = ("Segoe UI", 20), text_color = "white")
        total_label.pack(pady = (15, 5))
        self.total_value = ctk.CTkLabel(total_students_card, text = str(self.total_students), font = card_font, text_color = "white")
        self.total_value.pack()

        # Today's Attendance Card
        attendance_card = ctk.CTkFrame(summary_frame, width = card_width, height = card_height, fg_color = "#107C41", corner_radius = 10)
        attendance_card.pack(side = "left", padx = 10)
        attendance_card.pack_propagate(False)
        attendance_label = ctk.CTkLabel(attendance_card, text = "Today's Attendance", font = ("Segoe UI", 20), text_color = "white")
        attendance_label.pack(pady = (15, 5))
        self.attendance_value = ctk.CTkLabel(attendance_card, text = str(self.today_present), font = card_font, text_color = "white")
        self.attendance_value.pack()

        # Absent Students Card
        absent_card = ctk.CTkFrame(summary_frame, width = card_width, height = card_height, fg_color = "#D83B01", corner_radius = 10)
        absent_card.pack(side = "left", padx = 10)
        absent_card.pack_propagate(False)
        absent_label = ctk.CTkLabel(absent_card, text = "Absent Students", font = ("Segoe UI", 20), text_color = "white")
        absent_label.pack(pady = (15, 5))
        self.absent_value = ctk.CTkLabel(absent_card, text = str(self.today_absent), font = card_font, text_color = "white")
        self.absent_value.pack() 

        # Placeholder for future graph or logs
        graph_frame = ctk.CTkFrame(self.content_frame, fg_color="#F3F2F1", corner_radius=10)
        graph_frame.pack(fill = "both", expand = True, padx = 30, pady = 20)
        graph_label = ctk.CTkLabel(graph_frame, text = "Attendance Overview (Coming Soon)", font = ("Segoe UI", 16), text_color = "#201F1E")
        graph_label.place(relx = 0.5, rely = 0.5, anchor = "center")

    #######################################

    # FN: update_dashboard
    # Purpose: Refresh dashboard statistics (Total Students, Present, Absent)
    def update_dashboard(self):
        from logic.db_handler import get_all_students, get_attendance_by_date
    
        # Fetch total students from DB
        success, students = get_all_students()
        if success:
            total = len(students)
        else:
            total = 0

        # Fetch today's attendance
        success, attendance_records = get_attendance_by_date()
        if success:
            present_count = len([r for r in attendance_records if r['status'] == 'Present'])
        else:
            present_count = 0

        self.total_students = total
        self.today_present = present_count
        self.today_absent = total - self.today_present

        # Update labels
        if hasattr(self, "total_value"):
            self.total_value.configure(text = str(self.total_students))
        if hasattr(self, "attendance_value"):
            self.attendance_value.configure(text = str(self.today_present))
        if hasattr(self, "absent_value"):
            self.absent_value.configure(text = str(self.today_absent))

    #######################################

    # FN: show_attendance
    # Purpose: Display attendance module with single capture and attendance records
    def show_attendance(self):
        self.title_label.configure(text = "Take Attendance")
        self.clear_content()

        # Main container for Attendance Section
        attendance_frame = ctk.CTkFrame(self.content_frame, fg_color = "#FFFFFF")
        attendance_frame.pack(fill = "both", expand = True, padx = 30, pady = 20)

        # Left Side: Camera Capture Section
        camera_frame = ctk.CTkFrame(attendance_frame, fg_color = "#F3F2F1", corner_radius = 12)
        camera_frame.pack(side = "left", fill = "both", expand = True, padx = 10, pady = 10)

        camera_label = ctk.CTkLabel(camera_frame, text = "Face Recognition Attendance", font = ("Segoe UI", 18, "bold"), text_color = "#201F1E")
        camera_label.pack(pady = 10)

        # Instructions
        instructions = ctk.CTkLabel(camera_frame, 
                                   text = "Align your face with the camera.\nClick Capture & Recognize to mark attendance.\nNote: Train the model first if you haven't already",
                                   font = ("Segoe UI", 14, "italic"), text_color = "#5A5A5A")
        instructions.pack(pady = 10)

        # Camera Preview Placeholder
        self.camera_placeholder = ctk.CTkLabel(camera_frame, text = "Click to capture", width = 400, height = 300,
                                           fg_color = "#D0D0D0", corner_radius = 10, text_color = "#201F1E",
                                           font = ("Segoe UI", 16, "italic"))
        self.camera_placeholder.pack(pady = 20)

        # Capture Button
        self.capture_btn = ctk.CTkButton(camera_frame, text = "Capture & Recognize", fg_color = "#0078D4", hover_color = "#106EBE",
                               text_color = "white", width = 200, height = 50, font = ("Segoe UI", 18, "bold"),
                               command = self.capture_and_recognize) 
        self.capture_btn.pack(pady = 20)

        # Status Label
        self.status_label = ctk.CTkLabel(camera_frame, text = "Ready to capture", font = ("Segoe UI", 14),
                                     text_color = "#201F1E")
        self.status_label.pack(pady = 10)

        # Right Side: itAttendance Records
        records_frame = ctk.CTkFrame(attendance_frame, fg_color = "#F3F2F1", corner_radius = 12)
        records_frame.pack(side = "right", fill = "both", expand = True, padx = 10, pady = 10)

        records_label = ctk.CTkLabel(records_frame, text = "Today's Attendance Record", font = ("Segoe UI", 18, "bold"), text_color = "#201F1E")
        records_label.pack(pady = 10)

        # Refresh button
        refresh_btn = ctk.CTkButton(records_frame, text = "Refresh Records", fg_color = "#107C41", hover_color = "#0E6F37",
                               text_color = "white", width = 150, height = 35, font = ("Segoe UI", 14),
                               command = self.refresh_attendance_records)
        refresh_btn.pack(pady = 10)

        # Attendance Records Table
        self.attendance_tree = ctk.CTkScrollableFrame(records_frame, width = 400, height = 350)
        self.attendance_tree.pack(padx = 10, pady = 10, fill = "both", expand = True)

        # Load today's attendance records
        self.refresh_attendance_records()

    #######################################

    # FN: capture_and_recognize
    # Purpose: Capture a single image and recognize the face for attendance
    def capture_and_recognize(self):
        # Prevent multiple rapid clicks
        if hasattr(self, '_capturing') and self._capturing:
            return
        
        if not os.path.exists("trainer.yml"):
            messagebox.showerror("Error", "No trained model found! Please train the model first.")
            return
        
        self._capturing = True
        # Disable button and show processing state
        self.capture_btn.configure(text = "Processing...", state = "disabled")
        try:
            # Initialize camera if not already done
            if not hasattr(self, 'camera_obj'):
                self.camera_obj = Camera()
            elif not self.camera_obj.cap.isOpened():
                # Reinitialize camera if it was closed
                self.camera_obj = Camera()
            
            # Initialize authenticator if not already done
            if not hasattr(self, 'authenticator'):
                self.authenticator = Authenticator()
            
            # Check if authenticator is ready
            if not self.authenticator.is_ready():
                messagebox.showerror("Error", "No trained model found! Please train the model first.")
                return
            
            self.status_label.configure(text = "Opening camera...", text_color = "blue")
            
            # Capture a single frame
            ret, frame = self.camera_obj.cap.read()
            if not ret:
                messagebox.showerror("Error", "Failed to capture image from camera!")
                return
            
            # Show captured image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((400, 300))
            imgtk = ImageTk.PhotoImage(img)
            self.camera_placeholder.configure(image = imgtk, text = "")
            self.camera_placeholder.image = imgtk
            
            # Perform face recognition
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.authenticator.face_cascade.detectMultiScale(
                gray, scaleFactor = 1.3, minNeighbors = 5, minSize = (50, 50)
            )
            
            if len(faces) == 0:
                messagebox.showwarning("No Face Detected", "No face detected in the image. Please try again.")
                self.status_label.configure(text = "No face detected", text_color = "red")
                return
            
            # Get the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            face_img = gray[y:y+h, x:x+w]
            
            # Predict ID and confidence
            student_id, confidence = self.authenticator.recognizer.predict(face_img)
            
            if confidence < 70:  # Good match
                # Get student details
                from logic.db_handler import get_student_by_roll, mark_attendance
                success, student = get_student_by_roll(str(student_id))
                
                if success:
                    # Mark attendance
                    success, msg = mark_attendance(str(student_id), "Present")
                    if success:
                        # Show success popup
                        messagebox.showinfo("Attendance Marked", 
                                          f"✅ {student['name']} (ID: {student_id})\nAttendance marked successfully!")
                        
                        # Update status
                        self.status_label.configure(text = f"{student['name']} - Present", text_color = "green")
                        
                        # Refresh attendance records
                        self.refresh_attendance_records()
                        
                        # Update dashboard
                        self.update_dashboard()
                    else:
                        if "already marked" in msg.lower():
                            messagebox.showinfo("Already Marked", 
                                              f"ℹ️ {student['name']} (ID: {student_id})\nAttendance already marked today!")
                            self.status_label.configure(text = f"{student['name']} - Already marked", text_color = "orange")
                        else:
                            messagebox.showerror("Error", f"Failed to mark attendance: {msg}")
                else:
                    messagebox.showerror("Error", f"Student with ID {student_id} not found in database!")
            else:
                messagebox.showwarning("Unknown Face", f"Face not recognized (Confidence: {confidence:.1f})\nPlease make sure the person is registered.")
                self.status_label.configure(text = "Face not recognized", text_color = "red")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.configure(text = "Error occurred", text_color = "red")
        finally:
            # Reset capturing flag and re-enable button
            self._capturing = False
            self.capture_btn.configure(text = "Capture & Recognize", state = "normal")
            
            # Always release camera after use
            if hasattr(self, 'camera_obj') and self.camera_obj.cap.isOpened():
                self.camera_obj.cap.release()
                print("Camera released after capture.")
                self.status_label.configure(text = "Camera closed", text_color = "gray")
    
    #######################################

    # FN: refresh_attendance_records
    # Purpose: Refresh the attendance records display
    def refresh_attendance_records(self):
        try:
            # Clear existing records
            for widget in self.attendance_tree.winfo_children():
                widget.destroy()
            
            # Get today's attendance records
            from logic.db_handler import get_attendance_by_date
            success, records = get_attendance_by_date()
            
            if success and records:
                # Create header
                header_frame = ctk.CTkFrame(self.attendance_tree, fg_color = "#0078D4")
                header_frame.pack(fill = "x", pady = 2)
                
                ctk.CTkLabel(header_frame, text = "Time", font = ("Segoe UI", 14, "bold"), text_color = "white").pack(side = "left", padx = 5)
                ctk.CTkLabel(header_frame, text = "Name", font = ("Segoe UI", 14, "bold"), text_color = "white").pack(side = "left", padx = 5, expand = True)
                ctk.CTkLabel(header_frame, text = "Roll No.", font = ("Segoe UI", 14, "bold"), text_color = "white").pack(side = "left", padx = 5)
                ctk.CTkLabel(header_frame, text = "Status", font = ("Segoe UI", 14, "bold"), text_color = "white").pack(side = "left", padx = 5)
                
                # Add records
                for record in records:
                    record_frame = ctk.CTkFrame(self.attendance_tree, fg_color = "#F3F2F1")
                    record_frame.pack(fill = "x", pady = 1)
                    
                    # Format timestamp
                    timestamp = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%I:%M:%S %p') 
                    
                    ctk.CTkLabel(record_frame, text = timestamp, font = ("Segoe UI", 13)).pack(side = "left", padx = 5)
                    ctk.CTkLabel(record_frame, text = record['name'], font = ("Segoe UI", 13)).pack(side = "left", padx = 5, expand = True)
                    ctk.CTkLabel(record_frame, text = record['roll'], font = ("Segoe UI", 13)).pack(side = "left", padx = 5)
                    
                    status_color = "#107C41" if record['status'] == 'Present' else "#D83B01"
                    ctk.CTkLabel(record_frame, text = record['status'], font = ("Segoe UI", 13), text_color = status_color).pack(side = "left", padx = 5)
            else:
                # No records message
                no_records_label = ctk.CTkLabel(self.attendance_tree, text = "No attendance records for today", 
                                              font = ("Segoe UI", 14, "italic"), text_color = "#5A5A5A")
                no_records_label.pack(pady = 20)
                
        except Exception as e:
            print(f"Error refreshing attendance records: {e}")

    #######################################

    # FN: show_register
    # Purpose: Display student registration form
    def show_register(self):
        self.title_label.configure(text = "Register Student")
        self.clear_content()

        # Main Container (Horizontal Split: Left = Form, Right = Photo Preview)
        main_frame = ctk.CTkFrame(self.content_frame, fg_color = "#FFFFFF")
        main_frame.pack(fill = "both", expand = True, padx = 30, pady = 20)

        # ---------------- LEFT PANEL: Registration Form ----------------
        form_frame = ctk.CTkFrame(main_frame, fg_color = "#F3F2F1", corner_radius = 12)
        form_frame.pack(side = "left", fill = "both", expand = True, padx = 20, pady = 20)

        # Form Title
        form_title = ctk.CTkLabel(form_frame, text = "Student Registration",
                              font = ("Segoe UI", 22, "bold"), text_color = "#201F1E")
        form_title.pack(pady = (20, 10)) 

        subtitle = ctk.CTkLabel(form_frame, text = "Fill the details and capture a photo for registration.",
                            font = ("Segoe UI", 14, "italic"), text_color = "#5A5A5A")
        subtitle.pack(pady = (0, 20))

        # Input Fields
        label_font = ("Segoe UI", 16, 'bold')
        entry_font = ("Segoe UI", 14, "italic")

        # Name
        name_label = ctk.CTkLabel(form_frame, text = "Full Name:", font = label_font)
        name_label.pack(pady = (10, 2))
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text = "Enter full name", width = 400, font = entry_font)
        self.name_entry.pack(pady = (8, 8))

        # Roll Number
        roll_label = ctk.CTkLabel(form_frame, text = "Roll Number / ID:", font = label_font)
        roll_label.pack(pady = (10, 2))
        self.roll_entry = ctk.CTkEntry(form_frame, placeholder_text = "Enter roll number", width = 400, font = entry_font)
        self.roll_entry.pack(pady = (8, 8))

        # Department
        dept_label = ctk.CTkLabel(form_frame, text = "Department:", font = label_font)
        dept_label.pack(pady = (10, 2))
        self.dept_entry = ctk.CTkOptionMenu(form_frame, values = ["BCA", "BBA", "MBA", "MCA",],
                                    width = 400, font = entry_font)
        self.dept_entry.pack(pady = (8, 8))
        self.dept_entry.set("Select Department")  # Default text

        # Register Button
        register_btn = ctk.CTkButton(form_frame, text = "Register Student",
                                 fg_color = "#0078D4", hover_color = "#106EBE",
                                 text_color = "white", width = 250, height = 45,
                                 font = ("Segoe UI", 18, "bold"), command = self.save_student)
        register_btn.pack(pady = (20, 10))

        # Status Label
        self.register_status = ctk.CTkLabel(form_frame, text = "", font = ("Segoe UI", 14), text_color = "#201F1E")
        self.register_status.pack(pady = (20, 10))

        # ---------------- RIGHT PANEL: Photo Preview ----------------
        photo_frame = ctk.CTkFrame(main_frame, fg_color = "#F3F2F1", corner_radius = 12)
        photo_frame.pack(side = "right", fill = "both", expand = True, padx = 20, pady = 20)

        # Photo Title
        photo_label = ctk.CTkLabel(photo_frame, text = "Photo Preview", font = ("Segoe UI", 22, "bold"), text_color = "#201F1E")
        photo_label.pack(pady = (20, 10))

        # Photo Placeholder
        self.photo_placeholder = ctk.CTkLabel(photo_frame, text = "No Photo", width = 320, height = 320,
                                      fg_color = "#E0E0E0", corner_radius = 140,
                                      text_color = "#201F1E", font = ("Segoe UI", 16, "italic"))
        self.photo_placeholder.pack(pady = (8, 8))

        # Capture Button
        capture_btn = ctk.CTkButton(photo_frame, text = "Capture 50 Face Images", fg_color = "#107C41", hover_color = "#0E6F37",
                                text_color = "white", width = 250, height = 40, font = ("Segoe UI", 16, "bold"),
                                command = self.capture_photo)
        capture_btn.pack(pady = (8, 8))

        # Train image
        train_btn = ctk.CTkButton(form_frame, text = "Train Model",
                           fg_color = "#107C41", hover_color = "#0E6F37",
                           text_color ="white", width = 250, height = 45,
                           font = ("Segoe UI", 18, "bold"),
                           command = self.train_faces)
        train_btn.pack(pady = (10, 10))


        # Note
        note_label = ctk.CTkLabel(photo_frame, text = "Captures 50 images for training.\nEnsure good lighting and a clear face.\nPress 'q' to stop capturing early.",
                              font = ("Segoe UI", 14,"italic"), text_color = "#5A5A5A")
        note_label.pack(pady = (10, 20))
 
    #######################################

    def train_faces(self):
        try:
            self.trainer_obj.train_model(images_path = os.path.join("data", "images"))
            
            # Reload authenticator if it exists
            if hasattr(self, 'authenticator'):
                self.authenticator.reload_model()
            
            messagebox.showinfo("Training Complete", "Face recognition model trained successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    #######################################

    # FN: capture_photo
    # Purpose: Capture 50 face images for training the face recognition model.
    def capture_photo(self):
        roll = self.roll_entry.get().strip()
        if not roll:
            self.register_status.configure(text = "Enter Roll Number first!", text_color = "red")
            return

        self.register_status.configure(text = "Starting face capture...", text_color = "blue")
        
        # Start face capture in a separate thread to avoid blocking UI
        def capture_faces_thread():
            try:
                # Initialize camera for capture
                if not hasattr(self, 'camera_obj'):
                    self.camera_obj = Camera()
                elif not self.camera_obj.cap.isOpened():
                    self.camera_obj = Camera()
                
                # Use the camera object to capture 50 face images
                count = self.camera_obj.capture_faces(
                    student_id = roll, 
                    save_dir = os.path.join("data", "images"),
                    max_images = 50
                )
                
                # Update UI in main thread
                self.after(0, lambda: self.register_status.configure(
                    text = f"Captured {count} face images successfully!", 
                    text_color = "green"
                ))
                
                # Update photo preview with last captured image
                if count > 0:
                    last_image_path = os.path.join("data", "images", f"{roll}_{count}.jpg")
                    if os.path.exists(last_image_path):
                        self.after(0, lambda: self.update_photo_preview(last_image_path))
                        
            except Exception as e:
                self.after(0, lambda: self.register_status.configure(
                    text=f"Error: {str(e)}", 
                    text_color="red"
                ))
        
        # Start the capture in a separate thread
        import threading
        threading.Thread(target = capture_faces_thread, daemon = True).start()
    
    #######################################

    # FN: update_photo_preview
    # Purpose: Update the photo preview with the captured image
    def update_photo_preview(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((250, 250))
            imgtk = ImageTk.PhotoImage(img)
            self.photo_placeholder.configure(image = imgtk, text = "")
            self.photo_placeholder.image = imgtk
        except Exception as e:
            print(f"Error updating photo preview: {e}")

    #######################################

    # FN: upload_photo
    # Purpose: Save student details to a CSV file and update dashboard stats.
    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            title = "Select Student Photo",
            filetypes = [("Image Files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.selected_photo_path = file_path  # save globally or in class
            # Display preview
            img = Image.open(file_path)
            img = img.resize((100, 100))  # adjust size as needed
            img_tk = ImageTk.PhotoImage(img)
            self.photo_placeholder.configure(image = img_tk, text = "")
            self.photo_placeholder.image = img_tk  # keep reference

        # Note: Upload photo functionality removed as it's not needed for face capture

        # Save captured frame for registration
        self.captured_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    #######################################

    # FN: save_student
    # Purpose: Save student details to a CSV file and update dashboard stats.
    def save_student(self):
        from logic.db_handler import add_student

        name = self.name_entry.get().strip()
        roll = self.roll_entry.get().strip()
        dept = self.dept_entry.get().strip()

        if not name or not roll:
            self.register_status.configure(text = "Name and Roll Number are required!", text_color = "red")
            return

        if dept == "Select Department":
            self.register_status.configure(text = "Please select a department!", text_color = "red")
            return

        # Check if face images were captured
        img_dir = os.path.join("data", "images")
        face_images = [f for f in os.listdir(img_dir) if f.startswith(f"{roll}_") and f.endswith(".jpg")]
        
        if len(face_images) == 0:
            self.register_status.configure(text = "Please capture face images before registering!", text_color = "red")
            return

        # Use the first captured image as the main photo
        img_path = os.path.join(img_dir, face_images[0])

        # Save to DB call
        success, msg = add_student(name, roll, dept, f"{roll}@example.com", "0000000000", img_path)
        if success:
            self.register_status.configure(text = "Student Registered Successfully!", text_color = "green")
            # Clear fields...
        else:
            self.register_status.configure(text = msg, text_color = "red")
            return

        self.name_entry.delete(0, "end")
        self.roll_entry.delete(0, "end")
        self.dept_entry.set("Select Department")
        self.photo_placeholder.configure(image = None, text = "No Photo")

        # update dashboard count
        self.update_dashboard()

    #######################################

    # FN: show_settings
    # Purpose: Display settings page
    def show_settings(self):
        self.title_label.configure(text = "Settings")
        self.clear_content()

        settings_frame = ctk.CTkFrame(self.content_frame, fg_color = "#FFFFFF")
        settings_frame.pack(fill = "both", expand = True, padx = 30, pady = 20)

        # Title
        settings_title = ctk.CTkLabel(settings_frame, text = "Application Settings",
                                  font = ("Segoe UI", 24, "bold"), text_color = "#201F1E")
        settings_title.pack(pady = (20, 10))

        # ================= THEME SELECTION =================

        theme_frame = ctk.CTkFrame(settings_frame, fg_color = "#F3F2F1", corner_radius = 12)
        theme_frame.pack(fill = "x", padx = 20, pady = 10)

        theme_label = ctk.CTkLabel(theme_frame, text = "Theme", font = ("Segoe UI", 18, "bold"), text_color = "#201F1E")
        theme_label.pack(side = "left", padx = 15, pady = 15)

        self.theme_menu = ctk.CTkOptionMenu(theme_frame, values = ["Light", "Dark", "System"],
                                        width = 200, font = ("Segoe UI", 14), command = lambda choice: ctk.set_appearance_mode(choice.lower()))
        self.theme_menu.pack(side = "right", padx = 15, pady = 15)
        self.theme_menu.set("System")  # default

        # ================= LANGUAGE SELECTION =================

        language_frame = ctk.CTkFrame(settings_frame, fg_color = "#F3F2F1", corner_radius = 12)
        language_frame.pack(fill = "x", padx = 20, pady = 10)

        language_label = ctk.CTkLabel(language_frame, text = "Language", font = ("Segoe UI", 18, "bold"), text_color = "#201F1E")
        language_label.pack(side = "left", padx = 15, pady = 15)

        self.language_menu = ctk.CTkOptionMenu(language_frame, values = ["English", "Hindi", "French"],
                                           width = 200, font = ("Segoe UI", 14), command = lambda choice: print(f"Language selected: {choice}"))
        self.language_menu.pack(side = "right", padx = 15, pady = 15)
        self.language_menu.set("English")

        # ================= TIME FORMAT =================

        time_format_frame = ctk.CTkFrame(settings_frame, fg_color = "#F3F2F1", corner_radius = 12)
        time_format_frame.pack(fill = "x", padx = 20, pady = 10)

        time_format_label = ctk.CTkLabel(time_format_frame, text = "Time Format", font = ("Segoe UI", 18, "bold"),
                                     text_color = "#201F1E")
        time_format_label.pack(side = "left", padx = 15, pady = 15)

        self.time_format_menu = ctk.CTkOptionMenu(time_format_frame, values = ["12-hour", "24-hour"],
                                              width = 200, font = ("Segoe UI", 14))
        self.time_format_menu.pack(side = "right", padx = 15, pady = 15)
        self.time_format_menu.set("12-hour")

        # ================= NOTIFICATIONS =================

        notification_frame = ctk.CTkFrame(settings_frame, fg_color = "#F3F2F1", corner_radius = 12)
        notification_frame.pack(fill = "x", padx = 20, pady = 10)

        notification_label = ctk.CTkLabel(notification_frame, text = "Enable Notifications", font = ("Segoe UI", 18, "bold"),
                                      text_color = "#201F1E")
        notification_label.pack(side = "left", padx = 15, pady = 15)

        self.notification_switch = ctk.CTkSwitch(notification_frame, text = "", onvalue = "on", offvalue = "off")
        self.notification_switch.pack(side = "right", padx = 15, pady = 15)

        # ================= DATA MANAGEMENT =================

        data_frame = ctk.CTkFrame(settings_frame, fg_color = "#F3F2F1", corner_radius = 12)
        data_frame.pack(fill = "x", padx = 20, pady = 10)

        data_label = ctk.CTkLabel(data_frame, text = "Data Management", font = ("Segoe UI", 18, "bold"), text_color = "#201F1E")
        data_label.pack(anchor = "w", padx = 15, pady = (15, 5))

        # Buttons for Reset & Export
        btn_container = ctk.CTkFrame(data_frame, fg_color = "#F3F2F1")
        btn_container.pack(pady = 10)

        reset_btn = ctk.CTkButton(btn_container, text = "Clear All Data", fg_color = "#D83B01", hover_color = "#A52A00",
                              text_color = "white", width = 200, font = ("Segoe UI", 14), command = self.clear_all_data)
        reset_btn.pack(side = "left", padx = 10)

        export_btn = ctk.CTkButton(btn_container, text = "Export Attendance (CSV)", fg_color = "#0078D4", hover_color = "#106EBE",
                               text_color = "white", width = 250, font = ("Segoe UI", 14), command = self.export_data)
        export_btn.pack(side = "left", padx = 10)

        clean_btn = ctk.CTkButton(btn_container, text = "Clean Duplicates", fg_color = "#D83B01", hover_color = "#A52A00",
                               text_color = "white", width = 200, font = ("Segoe UI", 14), command = self.clean_duplicates)
        clean_btn.pack(side = "left", padx = 10)

        # Second row of buttons
        btn_container2 = ctk.CTkFrame(data_frame, fg_color = "#F3F2F1")
        btn_container2.pack(pady = 10)

        reset_btn = ctk.CTkButton(btn_container2, text = "Reset Project", fg_color = "#FF6B35", hover_color = "#E55A2B",
                               text_color = "white", width = 200, font = ("Segoe UI", 14), command = self.reset_project)
        reset_btn.pack(side = "left", padx = 10)

        # ================= APP INFO =================

        info_frame = ctk.CTkFrame(settings_frame, fg_color = "#F3F2F1", corner_radius = 12)
        info_frame.pack(fill = "x", padx = 20, pady = 10)

        info_label = ctk.CTkLabel(info_frame, text = "App Info", font = ("Segoe UI", 18, "bold"), text_color = "#201F1E")
        info_label.pack(anchor = "w", padx = 15, pady = (15, 5))

        version_label = ctk.CTkLabel(info_frame, text = "Version: 1.0.0", font = ("Segoe UI", 14), text_color = "#201F1E")
        version_label.pack(anchor = "w", padx = 15, pady = 5)

        developer_label = ctk.CTkLabel(info_frame, text = "Developer: FaceTrack Team", font = ("Segoe UI", 14),
                                   text_color = "#201F1E")
        developer_label.pack(anchor = "w", padx = 15, pady = (0, 15))
    
    ######################################

    # FN: clear_all_data
    # Purpose: Clear all stored data, including student details, attendance logs, and files.
    def clear_all_data(self):
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Confirm Clear All Data", 
            "⚠️ WARNING: This will permanently delete ALL data!\n\n"
            "This includes:\n"
            "• All student records\n"
            "• All attendance records\n"
            "• All captured face images\n"
            "• Trained model files\n\n"
            "This action cannot be undone!\n\n"
            "Are you sure you want to continue?"
        )
        
        if not result:
            return
        
        try:
            from logic.db_handler import clear_all_data
            
            # Clear database records
            success, msg = clear_all_data()
            if not success:
                messagebox.showerror("Error", f"Failed to clear database: {msg}")
                return
            
            # Clear face images
            images_cleared = 0
            if os.path.exists("data/images"):
                for file in os.listdir("data/images"):
                    if file.endswith(('.jpg', '.jpeg', '.png')):
                        os.remove(os.path.join("data/images", file))
                        images_cleared += 1
            
            # Clear trained model
            model_cleared = False
            if os.path.exists("trainer.yml"):
                os.remove("trainer.yml")
                model_cleared = True
            
            # Clear dataset folder
            dataset_cleared = 0
            if os.path.exists("dataset"):
                for file in os.listdir("dataset"):
                    if file.endswith(('.jpg', '.jpeg', '.png')):
                        os.remove(os.path.join("dataset", file))
                        dataset_cleared += 1
            
            # Show success message
            success_msg = f"✅ Project Reset Complete!\n\n"
            success_msg += f"Database: {msg}\n"
            success_msg += f"Face Images: {images_cleared} files removed\n"
            success_msg += f"Dataset: {dataset_cleared} files removed\n"
            if model_cleared:
                success_msg += f"Trained Model: Removed\n"
            
            # Reset project structure
            from logic.db_handler import reset_project_structure
            reset_success, reset_msg = reset_project_structure()
            
            if reset_success:
                success_msg += f"\nProject Structure: Reset"
            else:
                success_msg += f"\nProject Structure: {reset_msg}"
            
            messagebox.showinfo("Reset Complete", success_msg)
            
            # Update dashboard if we're on it
            if hasattr(self, 'update_dashboard'):
                self.update_dashboard()
            
            # Refresh attendance records if we're on attendance page
            if hasattr(self, 'refresh_attendance_records'):
                self.refresh_attendance_records()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear all data: {str(e)}")

    ######################################

    # FN: export_data
    # Purpose: Placeholder for exporting attendance data into a CSV file for external use or backup.
    def export_data(self):
        print("Export Attendance Data functionality will be implemented later.")

    ######################################

    # FN: clean_duplicates
    # Purpose: Clean duplicate attendance records for today
    def clean_duplicates(self):
        from logic.db_handler import clean_duplicate_attendance
        
        try:
            success, msg = clean_duplicate_attendance()
            if success:
                messagebox.showinfo("Success", msg)
                # Refresh attendance records if we're on the attendance page
                if hasattr(self, 'refresh_attendance_records'):
                    self.refresh_attendance_records()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean duplicates: {e}")

    ######################################

    # FN: reset_project
    # Purpose: Complete project reset - clear all data and recreate structure
    def reset_project(self):
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Confirm Project Reset", 
            "🔄 PROJECT RESET\n\n"
            "This will completely reset the project to initial state:\n\n"
            "• Clear all database records\n"
            "• Delete all face images\n"
            "• Remove trained models\n"
            "• Recreate project structure\n"
            "• Reset all counters\n\n"
            "This action cannot be undone!\n\n"
            "Are you sure you want to reset the project?"
        )
        
        if not result:
            return
        
        try:
            # Clear all data first
            self.clear_all_data()
            
            # Show additional success message
            messagebox.showinfo("Project Reset", 
                              "🎉 Project has been completely reset!\n\n"
                              "You can now:\n"
                              "• Register new students\n"
                              "• Train the face recognition model\n"
                              "• Start fresh with attendance tracking")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset project: {str(e)}")

    ######################################

    # FN: clear_content
    # Purpose: Remove previous widgets from content frame
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    ######################################

    # FN: on_add_student
    # Purpose: button here should call each function of db
    def on_add_student(self):
        name = self.name_entry.get()
        roll = self.roll_entry.get()
        dept = self.dept_entry.get()
        photo_path = self.captured_frame if hasattr(self, 'captured_frame') else None

        if not name or not roll:
            messagebox.showerror("Error", "Name and Roll required")
            return

        success, msg = db_handler.add_student(name, roll, dept, f"{roll}@example.com", "0000000000", photo_path)
        if success:
            messagebox.showinfo("Success", "Student added successfully!")
            self.refresh_student_table()
        else:
            messagebox.showerror("Error", msg)

    ######################################

    # FN: refresh_student_table
    # Purpose: Refresh student table (placeholder for future implementation)
    def refresh_student_table(self):
        # This function is a placeholder for future table implementation
        # Currently not used in the current UI design
        pass

    ######################################

    # FN: load_settings
    # Purpose:
    def load_settings(self):
        try:
            with open("data/settings.txt", "r") as f:
                theme, lang = f.read().splitlines()
            ctk.set_appearance_mode(theme)
            # Apply language text changes here
        except:
            pass  # Use defaults

######################################

# Entry Point
#if __name__ == "__main__":
#    app = AttendanceApp()
#    app.mainloop()
