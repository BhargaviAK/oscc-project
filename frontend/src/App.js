import { useState } from "react";
import "./App.css";

function App() {

  const [image, setImage] = useState(null);

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // -----------------------------
  // BACKEND URL
  // -----------------------------

  const BACKEND_URL =
    "https://oscc-project-production.up.railway.app";

  // -----------------------------
  // HANDLE IMAGE
  // -----------------------------

  const handleImageChange = (event) => {

    setImage(event.target.files[0]);

    setResult(null);
  };

  // -----------------------------
  // HANDLE PREDICTION
  // -----------------------------

  const handlePredict = async () => {

    if (!image) {

      alert("Please select an image");

      return;
    }

    const formData = new FormData();

    formData.append("file", image);

    try {
      setMessage("Analyzing histopathology image...");
      setLoading(true);

      setResult(null);

      const response = await fetch(
        `${BACKEND_URL}/api/v1/predict`,
        {
          method: "POST",
          body: formData,
        }
      );

      // ---------------------------------
      // HANDLE BACKEND ERRORS
      // ---------------------------------

      const data = await response.json();
      setMessage("Generating explainability outputs...");

      if (!response.ok) {

        alert(
          data.error ||
          "Prediction failed"
        );

        return;
      }

      console.log(
        "Backend Response:",
        data
      );

      setResult(data);

    } catch (error) {

      console.error(error);

      alert(
        "Backend is waking up. Please wait a few seconds and try again."
      );

    } finally {
      setMessage("Prediction completed");
      setLoading(false);
    }
  };

  // -----------------------------
  // UI
  // -----------------------------

  return (

    <div className="app-container">

      <div className="card">

        <h1 className="title">
          OSCC Detection System
        </h1>

        <p className="subtitle">
          Upload Histopathology Image for OSCC Detection
        </p>

        {/* FILE INPUT */}

        <input
          className="file-input"
          type="file"
          accept=".jpg,.jpeg,.png"
          onChange={handleImageChange}
        />

        {/* IMAGE PREVIEW */}

        {image && (

          <div>

            <p className="selected-file">
              Selected File: {image.name}
            </p>

            <img
              src={URL.createObjectURL(image)}
              alt="Preview"
              className="preview-image"
            />

            <div>

              <button
                className="predict-button"
                onClick={handlePredict}
              >
                Predict
              </button>

            </div>

          </div>

        )}

        {/* LOADING */}

        {loading && <p>{message}</p>}

        {/* RESULT */}

        {result && (

          <div className="result-box">

            <h2>
              Prediction Result
            </h2>

            <p>
              <strong>Prediction:</strong>
              {" "}
              {result.prediction}
            </p>

            <p>
              <strong>Confidence:</strong>
              {" "}
              {result.confidence}%
            </p>

            {/* HEATMAP */}

            {result.heatmap && (

              <div className="output-section">

                <h3>
                  GradCAM Heatmap
                </h3>

                <img
                  src={result.heatmap}
                  alt="Heatmap"
                  className="output-image"
                  onError={(e) => {

                    console.log(
                      "Heatmap failed:",
                      result.heatmap
                    );

                    e.target.style.display = "none";
                  }}
                />

              </div>

            )}

            {/* CONTOUR */}

            {result.contour_image && (

              <div className="output-section">

                <h3>
                  Boundary Contour
                </h3>

                <img
                  src={result.contour_image}
                  alt="Contour"
                  className="output-image"
                  onError={(e) => {

                    console.log(
                      "Contour failed:",
                      result.contour_image
                    );

                    e.target.style.display = "none";
                  }}
                />

              </div>

            )}

            {/* COMPARISON IMAGE */}

            {result.comparison_image && (

              <div className="output-section">

                <h3>
                  Comparison Output
                </h3>

                <img
                  src={result.comparison_image}
                  alt="Comparison"
                  className="output-image"
                  onError={(e) => {

                    console.log(
                      "Comparison failed:",
                      result.comparison_image
                    );

                    e.target.style.display = "none";
                  }}
                />

              </div>

            )}

          </div>

        )}

      </div>

    </div>
  );
}

export default App;