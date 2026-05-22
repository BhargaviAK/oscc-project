import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# ============================================
# DEVICE
# ============================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

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
# PREDICTION FUNCTION
# ============================================

def predict_oscc(image_path):

    image = Image.open(image_path).convert("RGB")

    image = transform(image)

    image = image.unsqueeze(0)

    image = image.to(device)

    with torch.no_grad():

        outputs = model(image)

        probabilities = torch.softmax(outputs, dim=1)

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