############### IMPORTS ###############
import os
import sys

# Add logic folder to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "logic"))

from gui import AttendanceApp
from logic.camera import Camera
from logic.face_trainer import Trainer
from logic.user_auth import Authenticator


############### PROJECT SETUP ###############
def create_project_structure():
    folders = ["data", "data/images", "data/attendance", "dataset", "model"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)


############### MAIN APP ###############
if __name__ == "__main__":
    create_project_structure()

    # Example: Run backend (you can later link with buttons in UI)
    #cam = Camera()
    #cam.capture_faces(student_id=1)

    #trainer = Trainer()
    #trainer.train()

    #auth = Authenticator()
    #auth.recognize()

    # Launch UI
    app = AttendanceApp()
    app.mainloop()
