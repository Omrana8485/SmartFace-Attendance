############### IMPORTS ###############
import cv2
import os

############### AUTHENTICATION CLASS ###############
class Authenticator:
    def __init__(self, model_path = "trainer.yml"):
        self.model_path = model_path
        self.recognizer = None
        self.face_cascade = None
        self.cap = None
        
        # Only initialize if model exists
        if os.path.exists(model_path):
            self._initialize_recognizer()
        else:
            print("⚠️ No trained model found. Please train the model first.")
    
    def _initialize_recognizer(self):
        """Initialize the face recognizer and cascade classifier"""
        try:
            # Load trained recognizer
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.recognizer.read(self.model_path)

            # Load Haar Cascade for face detection
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            
            print("✅ Face recognizer initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing recognizer: {e}")
            self.recognizer = None
            self.face_cascade = None
    
    def is_ready(self):
        """Check if the authenticator is ready to recognize faces"""
        return (self.recognizer is not None and 
                self.face_cascade is not None and 
                os.path.exists(self.model_path))
    
    def reload_model(self):
        """Reload the trained model (useful after training)"""
        if os.path.exists(self.model_path):
            self._initialize_recognizer()
            return True
        else:
            print("⚠️ Model file not found. Please train the model first.")
            return False

    def recognize(self):
        """
        Recognize face in real-time using trained model.
        Press 'q' to quit.
        """
        if not self.is_ready():
            print("❌ Authenticator not ready. Please train the model first.")
            return
            
        # Open webcam for recognition
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Could not open camera.")
            return
            
        print("🎥 Starting face recognition. Press 'q' to quit.")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor = 1.3, minNeighbors = 5, minSize = (50, 50)
            )

            for (x, y, w, h) in faces:
                face_img = gray[y:y+h, x:x+w]

                # Predict ID and confidence
                student_id, confidence = self.recognizer.predict(face_img)

                if confidence < 70:  # smaller = better match
                    text = f"ID: {student_id} ✅"
                    color = (0, 255, 0)
                else:
                    text = "Unknown ❌"
                    color = (0, 0, 255)

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, text, (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            cv2.imshow("FaceTrack - Authentication", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

############### MAIN TEST ###############
if __name__ == "__main__":
    auth = Authenticator()
    auth.recognize()
