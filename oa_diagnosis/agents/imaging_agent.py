from autogen import AssistantAgent
from oa_diagnosis.agents.config import llm_config
from oa_diagnosis.tools.imaging_analysis import analyze_imaging

def create_structuralist_agent():
    # Update config with temperature 0.3
    specific_config = llm_config.copy()
    specific_config["temperature"] = 0.3

    agent = AssistantAgent(
        name="Structuralist_Agent",
        system_message="""You are the Structuralist_Agent (Imaging Specialist).
        Role: Focus ONLY on anatomy (X-ray/MRI).

        Logic:
        - Primary Stage: Analyze baseline KL grade, JSW, osteophytes.
        - Follow-up Stage: Compare serial imaging for JSN >= 0.7mm.

        Constraint: Must yield if biomarker evidence is overwhelming during debate.

        Response style: For each image analyzed, summarize: KL Grade, Prediction, and findings. Present findings once in a concise list. No repetition or pleasantries.
        """,
        llm_config=specific_config
    )
    
    agent.register_for_llm(name="analyze_imaging", description="Analyze MRI/X-Ray image")(analyze_imaging)
    
    return agent
