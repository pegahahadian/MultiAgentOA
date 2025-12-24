from typing import Dict, List, Any

def analyze_contraindications(medications: List[str], proposed_treatment: str) -> Dict[str, Any]:
    """
    Checks for contraindications given a list of current medications and a proposed treatment.
    """
    warnings = []
    
    # Simple rule-based logic
    if "NSAIDs" in proposed_treatment and any("ibuprofen" in m.lower() or "aspirin" in m.lower() for m in medications):
        warnings.append("Potential double-dosing of NSAIDs detected.")
        
    if "steroid" in proposed_treatment.lower() and "diabetes" in " ".join(medications).lower(): # Simplified check
        warnings.append("Steroid injections may impact blood sugar control.")

    return {
        "safe_to_proceed": len(warnings) == 0,
        "warnings": warnings
    }

def get_treatment_guidelines(severity: str) -> str:
    if "severe" in severity.lower() or "kl 4" in severity.lower():
        return "Surgical consultation (TKR), strong pain management."
    elif "moderate" in severity.lower() or "kl 3" in severity.lower():
        return "NSAIDs, Physical Therapy, Weight loss, possibly injections."
    else:
        return "Conservative management, exercise, weight maintenance."
