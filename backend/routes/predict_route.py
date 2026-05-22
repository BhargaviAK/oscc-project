from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os

from model.predict import (
    predict_oscc,
    is_histopathology_image
)

from model.gradcam import generate_gradcam

from config import UPLOAD_FOLDER

router = APIRouter()

# ---------------------------------
# RAILWAY BACKEND URL
# ---------------------------------

BASE_URL = "https://oscc-project-production.up.railway.app"


@router.post(
    "/predict",
    summary="Predict OSCC from histopathology image",
    description="Upload a histopathology image to detect OSCC and generate explainability outputs.",
)
async def predict(file: UploadFile = File(...)):

    # ---------------------------------
    # VALIDATE EXTENSION
    # ---------------------------------

    allowed_extensions = [
        "jpg",
        "jpeg",
        "png"
    ]

    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:

        return JSONResponse(
            content={
                "error": "Only image files (.jpg, .jpeg, .png) are allowed"
            },
            status_code=400
        )

    # ---------------------------------
    # SAVE FILE
    # ---------------------------------

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # ---------------------------------
    # VALIDATE HISTOPATHOLOGY IMAGE
    # ---------------------------------

    if not is_histopathology_image(file_path):

        return JSONResponse(
            content={
                "error": "Please upload valid histopathology image"
            },
            status_code=400
        )

    # ---------------------------------
    # PREDICTION
    # ---------------------------------

    prediction_result = predict_oscc(
        file_path
    )

    # ---------------------------------
    # GENERATE GRADCAM
    # ---------------------------------

    heatmap_path, contour_path = generate_gradcam(
        file_path
    )

    # ---------------------------------
    # CLEAN PATHS
    # ---------------------------------

    heatmap_path = heatmap_path.replace("\\", "/")

    contour_path = contour_path.replace("\\", "/")

    # ---------------------------------
    # FULL URLS
    # ---------------------------------

    heatmap_url = f"{BASE_URL}/{heatmap_path}"

    contour_url = f"{BASE_URL}/{contour_path}"

    # ---------------------------------
    # RESPONSE
    # ---------------------------------

    result = {

        "success": True,

        "filename": file.filename,

        "prediction":
            prediction_result["prediction"],

        "confidence":
            prediction_result["confidence"],

        "heatmap":
            heatmap_url,

        "contour_image":
            contour_url,
    }

    return JSONResponse(content=result)