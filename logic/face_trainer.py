############### IMPORTS ###############
import cv2
import os
import numpy as np

############### TRAINING CLASS ###############
class Trainer:
    def __init__(self, dataset_path = "dataset", model_path = "trainer.yml"):
        self.dataset_path = dataset_path
        self.model_path = model_path
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

    def train_model(self, images_path = None):
        if images_path:
            self.dataset_path = images_path
        faces, ids = self.load_images()
        if len(faces) == 0:
            raise Exception("❌ No face images found in dataset.")
    
        print("⏳ Training model, please wait...")
        self.recognizer.train(faces, np.array(ids))
        self.recognizer.save(self.model_path)
        print(f"✅ Training complete. Model saved as {self.model_path}")

    def load_images(self):
        faces = []
        ids = []
        for filename in os.listdir(self.dataset_path):
            if filename.endswith(".jpg"):
                path = os.path.join(self.dataset_path, filename)
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                
                if img is not None:
                    # Extract student ID from filename (before "_" or just the filename without extension)
                    if "_" in filename:
                        student_id = int(filename.split("_")[0])
                    else:
                        # For single images, use filename without extension as ID
                        student_id = int(filename.split(".")[0])

                    faces.append(img)
                    ids.append(student_id)
        return faces, ids

############### MAIN TEST ###############
if __name__ == "__main__":
    trainer = Trainer()
    trainer.train_model()
