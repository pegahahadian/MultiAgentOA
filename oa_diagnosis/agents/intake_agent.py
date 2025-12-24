from autogen import AssistantAgent
from oa_diagnosis.agents.config import llm_config
from oa_diagnosis.tools.oai_data_loader import load_patient_data
from oa_diagnosis.tools.imaging_analysis import analyze_imaging

def create_assessment_agent():
    # Update config with temperature 0.3
    specific_config = llm_config.copy()
    specific_config["temperature"] = 0.3

    agent = AssistantAgent(
        name="Assessment_Agent",
        system_message="""You are the Assessment_Agent (Intake).
        Role: Patient intake and baseline analysis.
        Capabilities: 
        1. Collect demographics and WOMAC scores using 'load_patient_data'.
        2. Run simulated ResNet-50 analysis on X-rays using 'analyze_imaging'.

        Output: Present a Structured JSON patient profile summarizing the findings.

        Response style: Return only the required JSON profile. Avoid extra narrative, repetitions, or closing pleasantries.
        """,
        llm_config=specific_config
    )
    
    # Register tools
    agent.register_for_llm(name="load_patient_data", description="Load OAI patient data")(load_patient_data)
    agent.register_for_llm(name="analyze_imaging", description="Run simulated ResNet-50 analysis details on X-rays")(analyze_imaging)
    
    return agent
