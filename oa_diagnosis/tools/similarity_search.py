from typing import List, Dict, Any

def find_similar_cases(age: int, bmi: float, gender: str, kl_grade: int) -> List[Dict[str, Any]]:
    """
    Simulates retrieval of similar historical OAI cases.
    """
    # Simply return a static list of "similar" cases for now
    return [
        {
            "case_id": "OAI_HIST_104",
            "similarity_score": 0.92,
            "treatment": "Physical Therapy + NSAIDs",
            "outcome_2yr": "Pain reduced by 40%, stable KL grade"
        },
        {
            "case_id": "OAI_HIST_299",
            "similarity_score": 0.88,
            "treatment": "Intra-articular steroid injection",
            "outcome_2yr": "Temporary relief, progression to KL 4"
        },
        {
            "case_id": "OAI_HIST_055",
            "similarity_score": 0.85,
            "treatment": "Weight loss (10%) + Exercise",
            "outcome_2yr": "Significant improvement in WOMAC score"
        }
    ]
