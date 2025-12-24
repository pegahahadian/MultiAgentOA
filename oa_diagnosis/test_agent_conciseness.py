import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import autogen
from oa_diagnosis.agents import (
    create_assessment_agent,
    create_structuralist_agent,
    create_physiologist_agent,
    create_case_retrieval_agent,
    create_lead_consultant_agent,
    create_therapy_group_manager
)

from oa_diagnosis.tools.oai_data_loader import load_patient_data
from oa_diagnosis.tools.imaging_analysis import analyze_imaging
from oa_diagnosis.tools.clinical_analysis import analyze_contraindications, get_treatment_guidelines
from oa_diagnosis.tools.similarity_search import find_similar_cases

def test_workflow(patient_id: str):
    """
    Test the diagnosis workflow with concise agent outputs.
    """
    print(f"\n{'='*70}")
    print(f"Testing workflow for Patient ID: {patient_id}")
    print(f"{'='*70}\n")
    
    # Create the User Proxy (The Bridge)
    user_proxy = autogen.UserProxyAgent(
        name="Admin_User",
        system_message="A human admin. Execute the tools proposed by the agents.",
        code_execution_config=False,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
    )

    # Create Agents
    assessment_agent = create_assessment_agent()
    structuralist_agent = create_structuralist_agent()
    physiologist_agent = create_physiologist_agent()
    therapy_manager = create_therapy_group_manager()

    # Register Tools
    user_proxy.register_for_execution(name="load_patient_data")(load_patient_data)
    user_proxy.register_for_execution(name="analyze_imaging")(analyze_imaging)
    user_proxy.register_for_execution(name="analyze_contraindications")(analyze_contraindications)
    user_proxy.register_for_execution(name="get_treatment_guidelines")(get_treatment_guidelines)
    user_proxy.register_for_execution(name="find_similar_cases")(find_similar_cases)
    
    # Create Group Chat
    groupchat = autogen.GroupChat(
        agents=[user_proxy, assessment_agent, structuralist_agent, physiologist_agent, therapy_manager], 
        messages=[], 
        max_round=15,  # Reduced rounds to speed up test
        speaker_selection_method="auto"
    )
    
    # Create Lead Consultant (Orchestrator)
    lead_consultant = create_lead_consultant_agent(groupchat)

    # STAGE 1: Primary Consultation
    print("\n" + "="*70)
    print("STAGE 1: Primary Consultation")
    print("="*70 + "\n")
    
    initial_message = f"""
    START DIAGNOSIS for Patient ID: {patient_id}.
    
    STAGE 1 GOAL: 
    1. Assessment_Agent: Use 'load_patient_data' tool to fetch demographics, history, biomarker data, and imaging_ids for Patient {patient_id}.
    2. Structuralist_Agent: IMPORTANT - Use the 'analyze_imaging' tool with EACH imaging_id returned in the patient data. Analyze ALL knee images for this patient. For each image, report the KL Grade and findings. The UI will display each image with its corresponding KL Grade.
    3. Physiologist_Agent: Analyze the biomarker and clinical data concisely.
    
    Keep outputs SHORT. Report metrics once, then one-line conclusion. No repetition.
    When reporting imaging results, reference the KL Grade from each image analysis.
    """
    
    user_proxy.initiate_chat(
        lead_consultant,
        message=initial_message,
        max_turns=15
    )

    print("\n" + "="*70)
    print("STAGE 1 Complete")
    print("="*70 + "\n")
    
    print("\n✓ Workflow test completed. Check above output for conciseness.")
    print("  - Assessment should have returned JSON profile (no extra narrative)")
    print("  - Physiologist should have listed metrics once + short conclusion")
    print("  - Structuralist should have reported imaging once + interpretation")
    print("  - No 'Feel free to reach out' or repeated summaries\n")

if __name__ == "__main__":
    # Use a sample patient ID from the dataset
    patient_id = "9001695"
    test_workflow(patient_id)
