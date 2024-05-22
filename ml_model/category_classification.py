from ultralytics import YOLO
import matplotlib.pyplot as plt
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'ml_model', 'models', 'best.pt')


def predict(image):
    # print("hello1")
    # use best.pt to get best results
    model = YOLO(MODEL_PATH)

    print("Model loaded successfully")

    # predict the objects in the image
    results = model.predict(image, conf=0.4, save=False, line_thickness=2)

    # Extract the Results object from the list
    results = results[0]

    # Instantiate a list of dictionaries to store the detected objects
    detected_objects = []

    # Print the detected labels and confidence scores
    for label_idx, label_name in results.names.items():
        # Check if the label index corresponds to a detected object
        if label_idx in results.boxes.cls:
            # Get the confidence score for the detected object, then store each label and confidence score in a dictionary
            confidence_score_tensor = results.boxes.conf[results.boxes.cls == label_idx][0]
            confidence_score = confidence_score_tensor.item()

            # store the detected object in a dictionary
            # if label exists already, check if the confidence score is higher than the previous one
            for obj in detected_objects:
                if obj["label"] == label_name:
                    if obj["confidence"] < confidence_score:
                        obj["confidence"] = confidence_score
                        break
            else:
                # # if confidence score is < 0.6, ignore the object
                if confidence_score < 0.6:
                    continue
                else:
                    detected_objects.append({"label": label_name, "confidence": confidence_score})

    # Sort the detected objects by confidence score
    detected_objects = sorted(detected_objects, key=lambda k: k['confidence'], reverse=True)
    # print each detected object
    counter = 0
    for obj in detected_objects:
        counter += 1
        print(f"Iteration {counter}: {obj}")
        print(f"Detected: {obj['label']} (Confidence: {obj['confidence']:.2f})")

    print("hello2")

    # covert the detected objects to a json object
    detected_objects_json = {"detected_objects": detected_objects}
    print(detected_objects_json)
    return detected_objects_json


# predict("./images/white-tshirt-test-2.jpg")
