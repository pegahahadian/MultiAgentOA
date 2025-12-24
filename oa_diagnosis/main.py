import os
import autogen
from oa_diagnosis.agents import (
    create_assessment_agent,
    create_structuralist_agent,
    create_physiologist_agent,
    create_case_retrieval_agent,
    create_lead_consultant_agent,
    create_therapy_group_manager
)

# Tool imports for registration
from oa_diagnosis.tools.oai_data_loader import load_patient_data
from oa_diagnosis.tools.imaging_analysis import analyze_imaging
from oa_diagnosis.tools.clinical_analysis import analyze_contraindications, get_treatment_guidelines
from oa_diagnosis.tools.similarity_search import find_similar_cases

def main():
    print("Initializing OA Diagnosis Multi-Agent System (Refactored)...")
    
    # 1. Create the User Proxy (Tool Executor)
    user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        system_message="A human admin. Execute the tools proposed by the agents.",
        code_execution_config=False,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
    )

    # 2. Create Agents
    assessment_agent = create_assessment_agent()
    structuralist_agent = create_structuralist_agent()
    physiologist_agent = create_physiologist_agent()
    # Retrieval agent kept for completeness, though not explicitly in new plan's core logic, it's good to have.
    retrieval_agent = create_case_retrieval_agent() 
    therapy_manager = create_therapy_group_manager()

    # 3. Register Tools for Execution on UserProxy
    user_proxy.register_for_execution(name="load_patient_data")(load_patient_data)
    user_proxy.register_for_execution(name="analyze_imaging")(analyze_imaging)
    user_proxy.register_for_execution(name="analyze_contraindications")(analyze_contraindications)
    user_proxy.register_for_execution(name="get_treatment_guidelines")(get_treatment_guidelines)
    user_proxy.register_for_execution(name="find_similar_cases")(find_similar_cases)
    
    # 4. Create Group Chat for Diagnosis
    # We include therapy manager in the group but the orchestrator will manage the flow.
    groupchat = autogen.GroupChat(
        agents=[user_proxy, assessment_agent, structuralist_agent, physiologist_agent, therapy_manager], 
        messages=[], 
        max_round=30,
        speaker_selection_method="auto" # Orchestrator determines order usually or auto
    )
    
    # 5. Create Lead Consultant (Orchestrator)
    lead_consultant = create_lead_consultant_agent(groupchat)
    
    # 6. Start the process - Real Data Mode
    print("\n--- STAGE 1: Primary Consultation ---")
    patient_id = input("Enter Patient ID (e.g., 9003406, 9005932, 9001695): ")
    if not patient_id:
        patient_id = "9001695" # Default to a known ID if empty
    
    print(f"Starting diagnosis for Patient ID: {patient_id}...")
    
    initial_message = f"""
    START DIAGNOSIS for Patient ID: {patient_id}.
    
    STAGE 1 GOAL: 
    1. Assessment_Agent: Use 'load_patient_data' tool to fetch demographics, history, and biomarker data for Patient {patient_id}.
    2. Structuralist & Physiologist: Analyze the retrieved data.
    3. Structuralist: Compare Imaging findings (simulate reading "IMG_Baseline" if specific IDs missing).
    
    Determine if there is a conflict between Structural/Imaging status and Clinical/Biomarker risk.
    
    Lead Consultant: Monitor for conflict and organize the debate if needed.
    """
    
    user_proxy.initiate_chat(
        lead_consultant,
        message=initial_message
    )
    
    # Optional: We can still do the simulated follow-up or try to fetch real longitudinal data if available.
    # For now, we will simulate the follow-up 'time jump' but using the REAL baseline we just found as context.
    
    print("\n--- STAGE 2: Follow-Up Consultation (Simulated 4-year jump) ---")
    follow_up_message = """
    STAGE 2: FOLLOW-UP (4 YEARS LATER)
    
    Scenario Injection:
    - Assume 4 years have passed.
    - New Imaging (Simulated): JSN has increased by 0.8mm.
    - Biomarkers: Remain elevated.
    
    Task: Re-evaluate phenotype based on this progression. 
    Lead Consultant: Finalize phenotype (Rapid Progressor vs Others).
    """
    
    user_proxy.initiate_chat(
        lead_consultant,
        message=follow_up_message,
        clear_history=False # Keep context
    )

    print("\n--- STAGE 3: Therapy Generation ---")
    therapy_message = """
    STAGE 3: THERAPY GENERATION
    
    Task: Therapy_Group_Manager, please generate a comprehensive management plan based on the Final Phenotype.
    """
    
    user_proxy.initiate_chat(
        lead_consultant,
        message=therapy_message,
        clear_history=False
    )

if __name__ == "__main__":
    main()
