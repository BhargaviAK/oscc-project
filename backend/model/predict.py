import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import cv2
import numpy as np

# ============================================
# DEVICE
# ============================================

device = torch.device("cpu")

# ============================================
# LOAD MODEL
# ============================================

model = models.efficientnet_b0(weights=None)

model.classifier[1] = nn.Linear(
    in_features=1280,
    out_features=2
)

# ============================================
# LOAD TRAINED WEIGHTS
# ============================================

model.load_state_dict(
    torch.load(
        "model/best_efficientnet_b0.pth",
        map_location=device
    )
)

model = model.to(device)

model.eval()

# ============================================
# CLASS NAMES
# ============================================

class_names = [
    "Normal",
    "OSCC"
]

# ============================================
# IMAGE TRANSFORM
# ============================================

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ============================================
# HISTOPATHOLOGY VALIDATION
# ============================================

def is_histopathology_image(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return False

    image = cv2.resize(image, (224, 224))

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # Pink / Purple stain range
    lower = np.array([120, 20, 20])
    upper = np.array([170, 255, 255])

    mask = cv2.inRange(
        hsv,
        lower,
        upper
    )

    stain_ratio = np.sum(mask > 0) / (224 * 224)

    # Threshold
    if stain_ratio > 0.10:
        return True

    return False

# ============================================
# PREDICTION FUNCTION
# ============================================

def predict_oscc(image_path):

    # ----------------------------------------
    # VALIDATE HISTOPATHOLOGY IMAGE
    # ----------------------------------------

    if not is_histopathology_image(image_path):

        return {
            "error": "Please upload valid histopathology image"
        }

    # ----------------------------------------
    # LOAD IMAGE
    # ----------------------------------------

    image = Image.open(image_path).convert("RGB")
    image = image.resize((224, 224))

    image = transform(image)

    image = image.unsqueeze(0)

    image = image.to(device)

    # ----------------------------------------
    # MODEL PREDICTION
    # ----------------------------------------

    with torch.no_grad():

        outputs = model(image)

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        confidence, predicted = torch.max(
            probabilities,
            1
        )

    prediction = class_names[predicted.item()]

    confidence = round(
        confidence.item() * 100,
        2
    )

    result = {
        "prediction": prediction,
        "confidence": confidence
    }

    return result