############### IMPORTS ###############
import cv2
import os

############### CAMERA CLASS ###############
class Camera:
    def __init__(self, cam_index=0):
        """Initialize the camera (default webcam index = 0)."""
        self.cap = cv2.VideoCapture(cam_index)
        if not self.cap.isOpened():
            raise Exception("❌ Could not open camera.")

        # Load Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def capture_faces(self, student_id, save_dir="dataset", max_images=50):
        """
        Capture and save face images for a given student ID.
        Press 'q' to stop capturing.
        """
        # Create dataset folder if not exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        count = 0
        print(f"📸 Starting face capture for Student ID: {student_id}")
        print("Press 'q' to stop capturing or wait for automatic completion...")
        
        while count < max_images:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to grab frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50)
            )

            for (x, y, w, h) in faces:
                count += 1
                face_img = gray[y:y + h, x:x + w]

                # Save face image with unique filename
                filename = os.path.join(save_dir, f"{student_id}_{count}.jpg")
                cv2.imwrite(filename, face_img)

                # Draw rectangle & show count
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Saved: {count}/{max_images}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Show progress
            cv2.putText(frame, f"Captured: {count}/{max_images}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, "Press 'q' to stop", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("FaceTrack - Capture Faces", frame)

            # Stop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        print(f"✅ Saved {count} face images for Student ID: {student_id}")
        cv2.destroyAllWindows()
        
        # Release camera after capture
        self.cap.release()
        print("Camera released after face capture")
        
        return count

############### MAIN TEST ###############
if __name__ == "__main__":
    cam = Camera()
    cam.capture_faces(student_id = 1)
