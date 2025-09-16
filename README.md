SmartFace - Face Recognition Attendance System

An advanced attendance tracking application developed using Python, OpenCV, and CustomTkinter, designed to replace traditional roll-call methods with an automated, accurate, and user-friendly solution.

🚀 Core Features
   1. Student Enrollment: Register students with personal details and capture images via webcam
   2. Face Detection & Recognition: Identify and verify students in real time
   3. Auto Attendance: Instantly mark attendance once the face is recognized
   4. Dashboard Overview: View key statistics like total students, present count, and absentees
   5. Database Integration: Securely store student details and attendance records in SQLite
   6. Modern Interface: Simple, responsive UI powered by CustomTkinter

📋 Requirements

   Make sure these dependencies are installed before running:
   1. pip install opencv-python
   2. pip install customtkinter
   3. pip install pillow
   4. pip install numpy

🛠️ Setup & Installation

   1. Clone or download this repository
   2. Open the project folder in your IDE/terminal
   3. Install the required dependencies

🛠️ Run the application:

   python main.py

📖 User Guide

1. Add Students

   1. Navigate to Register Student
   2. Fill details: Name, Roll No, Department
   3. Capture 50 sample face images for training
   4. Save details → Train the model

2. Take Attendance

   1. Go to Take Attendance
   2. Use Capture & Recognize to scan faces
   3. Recognition result will pop up instantly
   4. Attendance updates automatically in records

3. Dashboard

   1. Displays overall stats:
   2. Number of registered students
   3. Count of present students
   4. Absentees for the day

4. Settings & Management

   1. Remove Duplicates – Delete duplicate records
   2. Clear Database – Reset all stored records
   3. Full Reset – Restore project to initial state

🔧 Project Structure
SmartFace/
├── main.py                 # Main entry point
├── gui.py                 # User interface (CustomTkinter)
├── logic/
│   ├── user_auth.py       # Face recognition & login
│   ├── camera.py          # Camera and image capture
│   ├── db_con.py       # Database schema
│   ├── db_handler.py      # Database operations
│   └── face_trainer.py   # Training the recognition model
├── data/
│   ├── dataset/           # Student face images
│   ├── attendance/        # Attendance records
└── trainer.yml            # Trained face recognition model

🐛 Troubleshooting

   1. Webcam not working – Ensure no other app is using the camera
   2. Faces not recognized – Train the model again with clearer images
   3. DB errors – Database auto-creates on first run
   4. Import errors – Reinstall missing Python packages

📝 Database Design

   1. Students Table
   2. id, name, roll, department, email, phone, photo_path
   3. Attendance Table
   4. id, student_id, timestamp, status (Present/Absent)

🔄 Workflow

   1. Install & run the system
   2. Enroll students
   3. rain model
   4. Capture & recognize faces for attendance
   5. Track results via dashboard

🎯 Technical Insights

   1. Uses LBPH face recognizer in OpenCV for reliable recognition
   2. Needs 50+ face images per student for accuracy
   3. Attendance marking works with single image capture
   4.Database ensures consistency and prevents duplicate records

🚨 Usage Notes

   Always retrain after adding new students
   Works best with proper lighting conditions
   Clear, front-facing images improve accuracy significantly

🔄 Latest Improvements

   ✅ Enhanced registration with 50-image capture workflow
   ✅ One-photo attendance marking with popup confirmation
   ✅ Added list view for attendance records
   ✅ Duplicate prevention & improved database handling
   ✅ Camera auto-release after recognition
   ✅ Full project reset option

SmartFace – A smarter way to handle attendance with AI! ✨