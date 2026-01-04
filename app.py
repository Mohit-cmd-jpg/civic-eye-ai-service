"""
Civic-Eye AI Service
Explainable AI for image authenticity verification
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import io
from PIL.ExifTags import TAGS
import os

app = Flask(__name__)
CORS(app)

def perform_ela_analysis(image_array):
    """
    Error Level Analysis (ELA) - detects image manipulation
    Returns score 0-100 (higher = more authentic)
    """
    try:
        if len(image_array.shape) == 3:
            pil_image = Image.fromarray(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))
        else:
            pil_image = Image.fromarray(image_array)
        
        pil_image = pil_image.convert("RGB")
        
        # Save recompressed version
        temp_buffer = io.BytesIO()
        pil_image.save(temp_buffer, "JPEG", quality=90)
        temp_buffer.seek(0)
        recompressed = Image.open(temp_buffer)
        
        # Compute ELA
        ela_image = ImageChops.difference(pil_image, recompressed)
        enhancer = ImageEnhance.Brightness(ela_image)
        ela_image = enhancer.enhance(10)
        
        # Calculate max difference
        extrema = ela_image.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        
        # Convert to score (lower diff = higher score)
        ela_score = max(0, min(100, 100 - (max_diff / 2.55)))
        return ela_score
    except Exception as e:
        print(f"ELA error: {e}")
        return 50  # Neutral on error

def check_metadata(image_source):
    """
    Check EXIF metadata for editing indicators
    Returns score 0-100
    """
    try:
        # Handle different input types
        if isinstance(image_source, np.ndarray):
            # If numpy array, we can't get EXIF easily unless we have the original bytes
            # This path is fallback and will likely return default score
            if len(image_source.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image_source, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image_source)
        elif isinstance(image_source, Image.Image):
            pil_image = image_source
        else:
            return 70

        exifdata = pil_image.getexif()
        if not exifdata:
            return 60  # No metadata - slightly suspicious
        
        metadata_score = 100
        
        # Check for editing software
        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            
            if tag == "Software" and data:
                software_lower = str(data).lower()
                if any(editor in software_lower for editor in ["photoshop", "gimp", "paint", "editor"]):
                    metadata_score -= 25
        
        return max(50, metadata_score)
    except Exception as e:
        print(f"Metadata error: {e}")
        return 70

def analyze_shadows(image):
    """
    Shadow consistency analysis
    Returns score 0-100
    """
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) < 3:
            return 55  # Too few edges
        
        shadow_score = 80
        
        # Edge density analysis
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        if edge_density < 0.01 or edge_density > 0.5:
            shadow_score -= 20
        
        return max(50, shadow_score)
    except Exception as e:
        print(f"Shadow analysis error: {e}")
        return 70

def analyze_quality(image):
    """
    Image quality metrics (blur, noise, brightness)
    Returns score 0-100
    """
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Blur detection (Laplacian variance)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Noise estimation
        noise = np.std(gray)
        
        # Brightness
        brightness = np.mean(gray)
        
        quality_score = 100
        
        # Penalize excessive blur
        if blur_score < 50:
            quality_score -= 30
        elif blur_score < 100:
            quality_score -= 15
        
        # Penalize excessive noise
        if noise > 50:
            quality_score -= 20
        elif noise > 35:
            quality_score -= 10
        
        # Penalize poor brightness
        if brightness < 30 or brightness > 220:
            quality_score -= 15
        elif brightness < 50 or brightness > 200:
            quality_score -= 8
        
        return max(30, min(100, quality_score))
    except Exception as e:
        print(f"Quality analysis error: {e}")
        return 70

def calculate_trust_score(image_cv, image_pil, issue_type):
    """
    Main trust score calculation - explainable and dynamic
    """
    # Get individual scores
    ela_score = perform_ela_analysis(image_cv)
    metadata_score = check_metadata(image_pil)
    shadow_score = analyze_shadows(image_cv)
    quality_score = analyze_quality(image_cv)
    
    # Weighted combination (explainable weights)
    trust_score = (
        ela_score * 0.35 +      # ELA is most important (35%)
        metadata_score * 0.25 + # Metadata (25%)
        shadow_score * 0.20 +   # Shadow analysis (20%)
        quality_score * 0.20    # Quality metrics (20%)
    )
    
    # Issue-type adjustment (explainable logic)
    # Some issues are more likely to be real (accidents, fires)
    issue_weights = {
        "accident": 1.05,  # +5% boost (urgent, less likely fake)
        "fire": 1.08,      # +8% boost (critical, rarely faked)
        "road_block": 1.02, # +2% boost
        "pothole": 1.0,    # No adjustment
        "garbage": 0.98,   # -2% (more common, easier to fake)
        "water_leak": 1.0,
        "other": 1.0
    }
    
    weight = issue_weights.get(issue_type.lower(), 1.0)
    trust_score = trust_score * weight
    
    # Clamp to 0-100
    trust_score = max(0, min(100, trust_score))
    
    return {
        "trust_score": round(trust_score, 2),
        "explanation": {
            "ela_score": round(ela_score, 2),
            "metadata_score": round(metadata_score, 2),
            "shadow_score": round(shadow_score, 2),
            "quality_score": round(quality_score, 2),
            "issue_type_weight": weight
        }
    }

def calculate_severity_and_priority(trust_score, issue_type):
    """
    Calculate base severity and priority
    """
    severity_map = {
        "fire": 95,
        "accident": 90,
        "road_block": 80,
        "water_leak": 70,
        "pothole": 60,
        "garbage": 50,
        "other": 40
    }
    
    base_severity = severity_map.get(issue_type.lower(), 40)
    
    # Adjust by trust score
    if trust_score < 40:
        base_severity = max(20, base_severity - 30)
    elif trust_score < 60:
        base_severity = max(30, base_severity - 15)
    elif trust_score < 80:
        base_severity = max(40, base_severity - 5)
    
    base_severity = max(0, min(100, base_severity))
    
    if base_severity >= 85:
        priority = "HIGH"
    elif base_severity >= 60:
        priority = "MEDIUM"
    else:
        priority = "LOW"
    
    return base_severity, priority

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main analysis endpoint
    Expects: Raw image bytes in POST body
    Returns: JSON with trust_score, base_severity, priority, explanation
    """
    # #region agent log
    import json; log_data = {"location": "app.py:234", "message": "Analyze endpoint entry", "data": {"hasData": len(request.data) > 0, "dataSize": len(request.data), "issueType": request.args.get("issue_type", "other")}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}; open(r"c:\Users\HP\Civic-Eye\.cursor\debug.log", "a").write(json.dumps(log_data) + "\n")
    # #endregion
    try:
        # Get image from request
        data = np.frombuffer(request.data, np.uint8)
        # #region agent log
        import json; log_data = {"location": "app.py:243", "message": "Image buffer created", "data": {"bufferSize": len(data)}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}; open(r"c:\Users\HP\Civic-Eye\.cursor\debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        image_cv = cv2.imdecode(data, cv2.IMREAD_COLOR)
        
        # Create PIL image from raw bytes to preserve EXIF
        try:
            image_pil = Image.open(io.BytesIO(request.data))
        except Exception as e:
            print(f"PIL Image load error: {e}")
            image_pil = None

        # #region agent log
        import json; log_data = {"location": "app.py:245", "message": "Image decoded", "data": {"imageIsNone": image_cv is None, "imageShape": image_cv.shape if image_cv is not None else None}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}; open(r"c:\Users\HP\Civic-Eye\.cursor\debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        
        if image_cv is None:
            return jsonify({"error": "Invalid image data"}), 400
            
        if image_pil is None:
            # Fallback if PIL failed but CV succeeded (unlikely but possible)
            image_pil = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
        
        # Get issue type from query param (optional, defaults to "other")
        issue_type = request.args.get("issue_type", "other")
        # #region agent log
        import json; log_data = {"location": "app.py:252", "message": "Before trust score calculation", "data": {"issueType": issue_type}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}; open(r"c:\Users\HP\Civic-Eye\.cursor\debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        
        # Calculate trust score
        trust_result = calculate_trust_score(image_cv, image_pil, issue_type)
        trust_score = trust_result["trust_score"]
        # #region agent log
        import json; log_data = {"location": "app.py:256", "message": "Trust score calculated", "data": {"trustScore": trust_score}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}; open(r"c:\Users\HP\Civic-Eye\.cursor\debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        
        # Calculate severity and priority
        base_severity, priority = calculate_severity_and_priority(trust_score, issue_type)
        # #region agent log
        import json; log_data = {"location": "app.py:260", "message": "Severity and priority calculated", "data": {"baseSeverity": base_severity, "priority": priority}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}; open(r"c:\Users\HP\Civic-Eye\.cursor\debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        
        return jsonify({
            "trust_score": trust_score,
            "base_severity": base_severity,
            "priority": priority,
            "explanation": trust_result["explanation"]
        })
    
    except Exception as e:
        # #region agent log
        import json; log_data = {"location": "app.py:266", "message": "Exception in analyze", "data": {"errorMessage": str(e), "errorType": type(e).__name__}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}; open(r"c:\Users\HP\Civic-Eye\.cursor\debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        print(f"Analysis error: {e}")
        return jsonify({"error": "Failed to analyze image"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "civic-eye-ai"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
