from typing import List, Dict, Any

def calculate_score(telemetry_data: List[Dict[str, Any]]) -> float:
    """
    Calculates a user's score based on their telemetry data.
    For now, it simply sums up the 'potentiometer_value' from the payload.
    """
    score = 0.0
    for record in telemetry_data:
        payload = record.get("payload", {})
        # Handle case where payload might be a string (if not automatically parsed) or dict
        if isinstance(payload, str):
            import json
            try:
                payload = json.loads(payload)
            except:
                payload = {}
                
        val = payload.get("potentiometer_value", 0.0)
        if isinstance(val, (int, float)):
            score += val
            
    return round(score, 2)
