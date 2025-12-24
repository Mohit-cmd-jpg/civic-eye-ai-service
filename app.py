from flask import Flask, request, jsonify
import os
import numpy as np
from ela import perform_ela
from severity import get_base_severity

app = Flask(__name__)

UPLOAD_FOLDER = "../backend/uploads"
ELA_FOLDER = "ela_outputs"

os.makedirs(ELA_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Civic-Eye AI Service is running"

def calculate_trust_score(ela_image):
    """
    Calculate trust score based on ELA intensity
    """
    ela_array = np.array(ela_image)
    mean_intensity = np.mean(ela_array)

    trust_score = max(0, 100 - int(mean_intensity / 2))
    return trust_score

def calculate_priority(base_severity, trust_score):
    """
    Combine severity and trust into final priority
    """
    final_severity = (base_severity * trust_score) / 100

    if final_severity >= 75:
        return "CRITICAL"
    elif final_severity >= 50:
        return "HIGH"
    elif final_severity >= 30:
        return "MEDIUM"
    else:
        return "LOW"

@app.route("/analyze", methods=["POST"])
def analyze_image():
    data = request.get_json()

    if not data or "filename" not in data or "issue_type" not in data:
        return jsonify({"error": "filename and issue_type required"}), 400

    filename = data["filename"]
    issue_type = data["issue_type"]

    image_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(image_path):
        return jsonify({"error": "Image not found"}), 404

    # Perform ELA
    ela_image = perform_ela(image_path)

    ela_filename = f"ela_{filename}"
    ela_path = os.path.join(ELA_FOLDER, ela_filename)
    ela_image.save(ela_path)

    # Scores
    trust_score = calculate_trust_score(ela_image)
    base_severity = get_base_severity(issue_type)
    priority = calculate_priority(base_severity, trust_score)

    return jsonify({
        "status": "analysis_complete",
        "filename": filename,
        "issue_type": issue_type,
        "trust_score": trust_score,
        "base_severity": base_severity,
        "priority": priority,
        "message": "Severity and trust analysis completed"
    })

if __name__ == "__main__":
    app.run(port=7000, debug=True)
