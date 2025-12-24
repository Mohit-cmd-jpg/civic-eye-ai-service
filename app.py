from flask import Flask, request, jsonify
import os

from ela import perform_ela_analysis
from severity import calculate_severity_and_priority

app = Flask(__name__)

@app.route("/")
def home():
    return "Civic-Eye AI Service is running"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    filename = data.get("filename")
    issue_type = data.get("issue_type")

    if not filename or not issue_type:
        return jsonify({"error": "filename and issue_type required"}), 400

    # Perform ELA analysis
    trust_score = perform_ela_analysis(filename)

    # Severity & priority logic
    base_severity, priority = calculate_severity_and_priority(
        issue_type, trust_score
    )

    return jsonify({
        "filename": filename,
        "issue_type": issue_type,
        "trust_score": trust_score,
        "base_severity": base_severity,
        "priority": priority
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7000))
    app.run(host="0.0.0.0", port=port)
