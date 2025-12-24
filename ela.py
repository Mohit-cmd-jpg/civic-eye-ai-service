from PIL import Image, ImageChops, ImageEnhance
import os

def perform_ela(image_path, quality=90):
    """
    Generates Error Level Analysis (ELA) image
    """

    original = Image.open(image_path).convert("RGB")

    # Temporary recompressed image
    temp_path = "temp_ela.jpg"
    original.save(temp_path, "JPEG", quality=quality)

    compressed = Image.open(temp_path)

    # Difference between original and compressed
    diff = ImageChops.difference(original, compressed)

    # Enhance difference to make artifacts visible
    enhancer = ImageEnhance.Brightness(diff)
    ela_image = enhancer.enhance(20)

    # Cleanup temp file
    os.remove(temp_path)

    return ela_image
