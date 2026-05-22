import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2

from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

# -----------------------------
# DEVICE
# -----------------------------
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# -----------------------------
# LOAD MODEL
# -----------------------------
model = models.efficientnet_b0(weights=None)

model.classifier[1] = nn.Linear(
    in_features=1280,
    out_features=2
)

model.load_state_dict(
    torch.load(
        "model/best_efficientnet_b0.pth",
        map_location=device
    )
)

model = model.to(device)

model.eval()

# -----------------------------
# IMAGE TRANSFORM
# -----------------------------
transform = transforms.Compose([

    transforms.Resize((224, 224)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225)
    )
])

# -----------------------------
# GENERATE GRADCAM
# -----------------------------
def generate_gradcam(image_path):

    # -----------------------------
    # LOAD IMAGE
    # -----------------------------
    image = Image.open(image_path).convert("RGB")

    image = image.resize((224, 224))

    rgb_img = np.array(image).astype(np.float32) / 255.0

    input_tensor = transform(image).unsqueeze(0).to(device)

    # -----------------------------
    # TARGET LAYER
    # -----------------------------
    target_layers = [model.features[-1]]

    # -----------------------------
    # GRADCAM
    # -----------------------------
    cam = GradCAM(
        model=model,
        target_layers=target_layers
    )

    grayscale_cam = cam(
        input_tensor=input_tensor
    )[0]

    visualization = show_cam_on_image(
        rgb_img,
        grayscale_cam,
        use_rgb=True
    )

    # -----------------------------
    # BOUNDARY LOCALIZATION
    # -----------------------------
    heatmap_uint8 = np.uint8(
        grayscale_cam * 255
    )

    _, threshold = cv2.threshold(
        heatmap_uint8,
        120,
        255,
        cv2.THRESH_BINARY
    )

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    boundary_image = visualization.copy()

    cv2.drawContours(
        boundary_image,
        contours,
        -1,
        (0, 255, 0),
        2
    )

    # -----------------------------
    # CREATE OUTPUT DIRECTORIES
    # -----------------------------
    os.makedirs(
        "outputs/heatmaps",
        exist_ok=True
    )

    os.makedirs(
        "outputs/contours",
        exist_ok=True
    )

    # -----------------------------
    # OUTPUT FILENAMES
    # -----------------------------
    filename = os.path.basename(
        image_path
    ).split(".")[0]

    heatmap_path = (
        f"outputs/heatmaps/{filename}_heatmap.jpg"
    )

    contour_path = (
        f"outputs/contours/{filename}_contour.jpg"
    )

    # -----------------------------
    # SAVE OUTPUTS
    # -----------------------------
    cv2.imwrite(
        heatmap_path,
        cv2.cvtColor(
            visualization,
            cv2.COLOR_RGB2BGR
        )
    )

    cv2.imwrite(
        contour_path,
        cv2.cvtColor(
            boundary_image,
            cv2.COLOR_RGB2BGR
        )
    )

    # -----------------------------
    # RETURN PATHS
    # -----------------------------
    return (
        heatmap_path,
        contour_path
    )