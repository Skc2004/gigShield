import random
from datetime import datetime

def check_fraud_confidence(exif_data, live_lat, live_lon, is_ela_simulated=False):
    """
    Simulates checking an image through Dual-Domain Forgery Detection (ELA + Generative AI footprints) 
    and EXIF analysis. Returns a confidence score of authenticity (0-100%).
    """
    confidence = 100.0
    audit_trail = []

    # 1. ELA & Generative AI Scan (Simulated)
    if is_ela_simulated:
        ela_penalty = random.uniform(50, 95)
        confidence -= ela_penalty
        audit_trail.append(f"AI Forensics: Generative or ELA Tampering detected (Penalty: -{ela_penalty:.1f}%)")

    # 2. EXIF Cross-referencing
    if not exif_data:
        confidence -= 50
        audit_trail.append("EXIF Metadata Scrubbed or Missing")
    else:
        ex_lat = exif_data.get('lat')
        ex_lon = exif_data.get('lon')
        
        if ex_lat is None or ex_lon is None:
            confidence -= 30
            audit_trail.append("GPS Coordinates missing from EXIF")
        else:
            diff = ((ex_lat - live_lat)**2 + (ex_lon - live_lon)**2)**0.5
            if diff > 0.05:
                penalty = min(diff * 500, 80) # scale penalty with distance
                confidence -= penalty
                audit_trail.append(f"GPS Spoofing. Device > 5km from image origin (Penalty: -{penalty:.1f}%)")

        ex_time_str = exif_data.get('timestamp')
        if ex_time_str:
            try:
                ex_time = datetime.fromisoformat(ex_time_str)
                time_diff = (datetime.now() - ex_time).total_seconds()
                if time_diff > 3600:
                    penalty = min((time_diff / 3600) * 10, 60)
                    confidence -= penalty
                    audit_trail.append(f"Temporal Mismatch. Image is outdated (Penalty: -{penalty:.1f}%)")
            except:
                confidence -= 10
                audit_trail.append("Invalid Timestamp format")

    final_confidence = max(0.0, round(confidence, 2))
    return final_confidence, audit_trail


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
