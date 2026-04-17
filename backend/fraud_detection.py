import random
from datetime import datetime

def perform_ela_check(image_file):
    # Simulates Error Level Analysis (ELA) check on an uploaded image
    # In a real enterprise app, we'd use OpenCV or a DL model here.
    # We will simulate a 10% chance of detecting digital tampering.
    score = random.uniform(0, 100)
    is_tampered = score > 90 
    return is_tampered, round(score, 2)

def verify_exif_data(exif_data, live_lat, live_lon):
    """
    Simulates cross-referencing EXIF data with live coordinates.
    exif_data might contain {"lat": ..., "lon": ..., "timestamp": ...}
    """
    if not exif_data:
        return False, "No EXIF data provided - potential screenshot or edited file"
    
    ex_lat = exif_data.get('lat')
    ex_lon = exif_data.get('lon')
    
    if ex_lat is None or ex_lon is None:
        return False, "Missing GPS metadata in image"
        
    # Simulate a distance check using basic Pythagorean (mocking haversine)
    diff = ((ex_lat - live_lat)**2 + (ex_lon - live_lon)**2)**0.5
    
    # If the distance is significant (e.g. diff > 0.05 approx 5km)
    if diff > 0.05:
        return True, f"Image GPS spoofed. EXIF location is far from live ping (diff: {diff:.3f})"
        
    # Time check simulation
    ex_time_str = exif_data.get('timestamp')
    if ex_time_str:
        try:
            ex_time = datetime.fromisoformat(ex_time_str)
            time_diff = (datetime.now() - ex_time).total_seconds()
            if time_diff > 3600: # 1 hour old
                return True, "Image is outdated. Timestamp > 1h ago"
        except Exception:
            pass

    return False, "Clean"

def process_voice_claim(audio_text):
    """
    Simulates NLP intent extraction. 
    """
    text = audio_text.lower()
    intents = []
    if "rain" in text or "flood" in text or "storm" in text:
        intents.append("rain")
    if "traffic" in text or "stuck" in text or "accident" in text:
        intents.append("traffic")
    if "hot" in text or "sun" in text or "heat" in text:
        intents.append("heat")
    
    intent = intents[0] if intents else "unknown"
    return intent
