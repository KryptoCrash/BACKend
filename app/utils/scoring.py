from typing import List, Dict, Any

def calculate_score(telemetry_data: List[Dict[str, Any]]) -> float:
    """
    Calculates a user's score based on their telemetry data.
    It averages the 'potentiometer_value' from the payload.
    """
    if not telemetry_data:
        return 0.0
        
    total_score = 0.0
    count = 0
    
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
            total_score += val
            count += 1
            
    if count == 0:
        return 0.0
        
    return round(total_score / count, 2)
