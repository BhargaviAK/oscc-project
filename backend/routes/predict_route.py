from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os

from model.predict import predict_oscc
from model.gradcam import generate_gradcam

from config import UPLOAD_FOLDER

router = APIRouter()


@router.post(
    "/predict",
    summary="Predict OSCC from histopathology image",
    description="Upload a histopathology image to detect OSCC and generate explainability outputs.",
)
async def predict(file: UploadFile = File(...)):

    # -----------------------------
    # VALIDATE IMAGE
    # -----------------------------
    if not file.content_type.startswith("image/"):
        return JSONResponse(
            content={"error": "Only image files are allowed"},
            status_code=400
        )

    # -----------------------------
    # SAVE UPLOADED FILE
    # -----------------------------
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # -----------------------------
    # PREDICTION
    # -----------------------------
    prediction_result = predict_oscc(file_path)

    # -----------------------------
    # GENERATE GRADCAM
    # -----------------------------
    heatmap_path, contour_path, comparison_path = generate_gradcam(
        file_path
    )

    # -----------------------------
    # RESPONSE
    # -----------------------------
    result = {
        "success": True,
        "filename": file.filename,
        "prediction": prediction_result["prediction"],
        "confidence": prediction_result["confidence"],

        # Explainability outputs
        "heatmap": heatmap_path,
        "contour_image": contour_path,
        "comparison_image": comparison_path
    }

    return JSONResponse(content=result)