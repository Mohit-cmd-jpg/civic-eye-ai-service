from PIL import Image, ImageChops, ImageEnhance
import os

def perform_ela_analysis(filename):
    """
    Simple ELA-based trust score calculation
    Returns an integer trust score (0–100)
    """

    try:
        original_path = os.path.join("uploads", filename)

        if not os.path.exists(original_path):
            # If image not found, return neutral score
            return 50

        original = Image.open(original_path).convert("RGB")

        # Save recompressed image
        temp_path = "temp_ela.jpg"
        original.save(temp_path, "JPEG", quality=90)

        recompressed = Image.open(temp_path)

        # Compute ELA image
        ela_image = ImageChops.difference(original, recompressed)
        enhancer = ImageEnhance.Brightness(ela_image)
        ela_image = enhancer.enhance(10)

        # Simple heuristic trust score
        extrema = ela_image.getextrema()
        max_diff = max([ex[1] for ex in extrema])

        # Map difference to trust score
        trust_score = max(0, min(100, 100 - max_diff))

        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return trust_score

    except Exception:
        return 50
