from autogen import AssistantAgent
from oa_diagnosis.agents.config import llm_config
from oa_diagnosis.tools.clinical_analysis import analyze_contraindications, get_treatment_guidelines

def create_physiologist_agent():
    # Update config with temperature 0.3
    specific_config = llm_config.copy()
    specific_config["temperature"] = 0.3

    agent = AssistantAgent(
        name="Physiologist_Agent",
        system_message="""You are the Physiologist_Agent (Clinical/Biomarker Specialist).
        Role: Focuses on pain (WOMAC), BMI, and molecular biomarkers (uCTXII, uNTXI).

        Logic:
        - Primary Stage: Estimate risk based on Pain + BMI.
        - Follow-up Stage: Confirm progression if biomarkers are elevated.

        Conflict Trigger: If imaging is mild (KL<2) but biomarkers/risk are high, argue for "Pre-Radiographic Progressor".

        Use 'analyze_contraindications' when proposing medications.

        Response style: Keep outputs terse. Report metrics once (short list or JSON), then a one-line conclusion (risk/phenotype). Do not repeat metrics or add closing pleasantries.
        """,
        llm_config=specific_config
    )
    
    agent.register_for_llm(name="analyze_contraindications", description="Check for medication contraindications")(analyze_contraindications)
    agent.register_for_llm(name="get_treatment_guidelines", description="Get OA treatment guidelines based on severity")(get_treatment_guidelines)
    
    return agent
