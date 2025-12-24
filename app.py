from flask import Flask, request, jsonify
import base64
import io
from PIL import Image

from severity import calculate_severity_and_priority

app = Flask(__name__)

@app.route("/")
def home():
    return "Civic-Eye AI Service is running"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    image_base64 = data.get("image_base64")
    issue_type = data.get("issue_type")

    if not image_base64 or not issue_type:
        return jsonify({"error": "Invalid input"}), 400

    # Decode image
    image_bytes = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # 🔍 SIMPLE TRUST LOGIC (ELA-like heuristic)
    width, height = image.size
    trust_score = max(30, min(100, (width * height) % 100))

    base_severity, priority = calculate_severity_and_priority(
        issue_type, trust_score
    )

    return jsonify({
        "trust_score": trust_score,
        "base_severity": base_severity,
        "priority": priority
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7000))
    app.run(host="0.0.0.0", port=port)
