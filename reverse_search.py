"""
Reverse Image Search Module
Integrates with reverse image search APIs to detect if an image has been used before
"""

import requests
import base64
import os
from typing import Dict, Optional

# Optional: Add API keys here or use environment variables
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "")
TINEYE_API_KEY = os.getenv("TINEYE_API_KEY", "")


def reverse_search_google_vision(image_data: bytes) -> Dict[str, any]:
    """
    Use Google Vision API for reverse image search
    Requires: pip install google-cloud-vision
    """
    try:
        # This is a placeholder - actual implementation requires Google Cloud Vision API
        # from google.cloud import vision
        
        # For now, return a mock response
        # In production, implement actual API call:
        # client = vision.ImageAnnotatorClient()
        # image = vision.Image(content=image_data)
        # response = client.web_detection(image=image)
        
        return {
            "found": False,
            "similar_images": 0,
            "trust_penalty": 0,
            "method": "google_vision",
            "note": "Google Vision API not configured"
        }
    except Exception as e:
        return {
            "found": False,
            "error": str(e),
            "trust_penalty": 0
        }


def reverse_search_tineye(image_data: bytes) -> Dict[str, any]:
    """
    Use TinEye API for reverse image search
    Requires: TinEye API key
    """
    try:
        if not TINEYE_API_KEY:
            return {
                "found": False,
                "similar_images": 0,
                "trust_penalty": 0,
                "method": "tineye",
                "note": "TinEye API key not configured"
            }
        
        # Encode image to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # TinEye API endpoint (example - check actual TinEye API docs)
        # This is a placeholder structure
        headers = {
            "Authorization": f"Bearer {TINEYE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Actual API call would go here
        # response = requests.post(
        #     "https://api.tineye.com/rest/search/",
        #     headers=headers,
        #     json={"image": image_b64}
        # )
        
        return {
            "found": False,
            "similar_images": 0,
            "trust_penalty": 0,
            "method": "tineye",
            "note": "TinEye API not fully implemented"
        }
    except Exception as e:
        return {
            "found": False,
            "error": str(e),
            "trust_penalty": 0
        }


def perform_reverse_search(image_data: bytes) -> Dict[str, any]:
    """
    Perform reverse image search using available services
    Returns trust penalty based on findings
    """
    results = {
        "found_duplicates": False,
        "similar_images_count": 0,
        "trust_penalty": 0,
        "details": []
    }
    
    # Try Google Vision if available
    if GOOGLE_VISION_API_KEY:
        google_result = reverse_search_google_vision(image_data)
        if google_result.get("found"):
            results["found_duplicates"] = True
            results["similar_images_count"] += google_result.get("similar_images", 0)
            results["details"].append(google_result)
    
    # Try TinEye if available
    if TINEYE_API_KEY:
        tineye_result = reverse_search_tineye(image_data)
        if tineye_result.get("found"):
            results["found_duplicates"] = True
            results["similar_images_count"] += tineye_result.get("similar_images", 0)
            results["details"].append(tineye_result)
    
    # Calculate trust penalty
    if results["found_duplicates"]:
        # If similar images found, reduce trust score
        # More similar images = higher penalty
        penalty = min(30, results["similar_images_count"] * 5)
        results["trust_penalty"] = penalty
    
    return results


def check_image_metadata_for_duplicates(image_path: str) -> Dict[str, any]:
    """
    Check image metadata (EXIF) for signs of being a duplicate
    This is a simpler check that doesn't require external APIs
    """
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        
        image = Image.open(image_path)
        exifdata = image.getexif()
        
        metadata_checks = {
            "has_metadata": bool(exifdata),
            "creation_date": None,
            "software": None,
            "suspicious": False
        }
        
        if exifdata:
            for tag_id in exifdata:
                tag = TAGS.get(tag_id, tag_id)
                data = exifdata.get(tag_id)
                
                if tag == "DateTimeOriginal" or tag == "DateTime":
                    metadata_checks["creation_date"] = str(data)
                
                if tag == "Software":
                    metadata_checks["software"] = str(data)
                    # Check for image editing software
                    if any(editor in str(data).lower() for editor in ["photoshop", "gimp", "paint.net"]):
                        metadata_checks["suspicious"] = True
        
        return metadata_checks
    except Exception as e:
        return {
            "error": str(e),
            "has_metadata": False
        }

