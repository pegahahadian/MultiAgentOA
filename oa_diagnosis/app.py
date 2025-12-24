
import os
import sys

# Add the parent directory to sys.path to ensure 'oa_diagnosis' module can be found
# regardless of where the script is run from.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import autogen
import chainlit as cl
import json
import ast
from oa_diagnosis.agents import (
    create_assessment_agent,
    create_structuralist_agent,
    create_physiologist_agent,
    create_case_retrieval_agent,
    create_lead_consultant_agent,
    create_therapy_group_manager
)

# Tool imports
from oa_diagnosis.tools.oai_data_loader import load_patient_data
from oa_diagnosis.tools.imaging_analysis import analyze_imaging
from oa_diagnosis.tools.clinical_analysis import analyze_contraindications, get_treatment_guidelines
from oa_diagnosis.tools.similarity_search import find_similar_cases

# -------------------------------------------------------------------------
# Custom UserProxy to Intercept Messages for UI
# -------------------------------------------------------------------------
class ChainlitUserProxyAgent(autogen.UserProxyAgent):
    """
    A UserProxyAgent that acts as an interface to Chainlit.
    It overrides 'receive' to print incoming messages from other agents to the UI.
    """
    def receive(self, message, sender, request_reply=None, silent=False):
        # 'message' can be a dict (standard) or string
        content = message.get("content") if isinstance(message, dict) else str(message)
        
        # Only display if there is content
        if content and content.strip():
            # Attempt to get the actual speaker name if available in the message dict
            # This is crucial for GroupChat where the Manager is often the 'sender'
            actual_author = sender.name
            if isinstance(message, dict) and "name" in message:
                actual_author = message["name"]

            # *** IMAGE RENDERING: Delegated to analyze_imaging_with_display() wrapper ***
            # Do NOT attempt to extract and display images here.
            # Reason: The wrapper has the authoritative dict result and displays images reliably.
            # Parsing tool_responses is fragile (content is often Python dict with single quotes, not valid JSON).
            # Trying to parse here causes:
            # - Duplicate images (wrapper already sent them)
            # - Missing images (parsing fails, wrapper didn't find preview either)
            # - Text spam (raw tool output printed again)
            # Single source of truth: analyze_imaging_with_display() in the tool execution layer.

            # Normalize dict-like content into valid JSON for display (fix raw reprs)
            #  - If content is a dict, pretty-print JSON
            #  - If content is a string that looks like a dict (single quotes), attempt to parse
            parsed = None
            try:
                if isinstance(message, dict) and isinstance(message.get("content"), dict):
                    parsed = message.get("content")
                    content = json.dumps(parsed, indent=2, ensure_ascii=False)
                elif isinstance(content, str) and content.strip().startswith("{"):
                    # Try JSON first, then fall back to Python literal (single-quoted dicts)
                    try:
                        parsed = json.loads(content)
                        content = json.dumps(parsed, indent=2, ensure_ascii=False)
                    except Exception:
                        try:
                            parsed = ast.literal_eval(content)
                            content = json.dumps(parsed, indent=2, ensure_ascii=False)
                        except Exception:
                            # leave content as-is if parsing fails
                            parsed = None
            except Exception:
                # Be defensive: if anything goes wrong, revert to original content
                parsed = None

            # Skip printing raw tool result dicts to avoid spam (these are handled by tool wrapper)
            is_tool_response = isinstance(message, dict) and "tool_responses" in message

            if is_tool_response:
                # These are already handled by the wrapper. Pass to parent without printing.
                super().receive(message, sender, request_reply, silent)
                return

            # Suppress repeated patient profile dumps from Assessment_Agent
            # Track shown profiles by patient_id to allow displaying once at the start.
            try:
                if actual_author == "Assessment_Agent" and isinstance(parsed, dict):
                    # Initialize storage lazily
                    if not hasattr(self, "_shown_patient_profiles"):
                        self._shown_patient_profiles = set()

                    # Heuristic keys that indicate a patient profile
                    profile_keys = {"patient_id", "age", "gender", "bmi", "imaging_ids", "biomarkers"}
                    if profile_keys.intersection(set(parsed.keys())):
                        pid = parsed.get("patient_id") or parsed.get("id")
                        if pid and pid in self._shown_patient_profiles:
                            # Already shown, skip displaying this repeated profile
                            super().receive(message, sender, request_reply, silent)
                            return
                        else:
                            if pid:
                                self._shown_patient_profiles.add(pid)
            except Exception:
                # Non-fatal if tracking fails; continue to display message
                pass
            
            # For regular agent messages, display them
            display_content = f"**{actual_author}**: {content}"
            
            cl.run_sync(
                cl.Message(
                    content=display_content, 
                    author=actual_author
                ).send()
            )
            
        # Pass to the parent handle logic
        super().receive(message, sender, request_reply, silent)

# -------------------------------------------------------------------------
# Main Logic
# -------------------------------------------------------------------------
def setup_and_run_workflow(patient_id: str):
    """
    Sets up the agents and runs the 3-stage diagnosis workflow.
    """
    print(f"DEBUG: Starting workflow for {patient_id}")
    
    # 1. Create the User Proxy (The Bridge)
    # This agent will sit in the GroupChat and "hear" everything, printing it to Chainlit.
    user_proxy = ChainlitUserProxyAgent(
        name="Admin_User",
        system_message="A human admin. Execute the tools proposed by the agents.",
        code_execution_config=False,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
    )

    # 2. Create Agents
    assessment_agent = create_assessment_agent()
    structuralist_agent = create_structuralist_agent()
    physiologist_agent = create_physiologist_agent()
    therapy_manager = create_therapy_group_manager()

    # 3. Register Tools with Image Display Wrapper
    def analyze_imaging_with_display(image_id: str):
        print(f"DEBUG: analyze_imaging_with_display called with image_id: {image_id}")
        result = analyze_imaging(image_id)
        print(f"DEBUG: Result keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
        
        # Check if this was skipped (non-knee image)
        if isinstance(result, dict) and result.get("status") == "Skipped - Not a knee image":
            print(f"DEBUG: Skipping non-knee image: {result.get('body_part')}")
            # Still display a message about the skipped image
            cl.run_sync(
                cl.Message(
                    content=f"⏭️ **Skipped** (Not a knee image): {result.get('body_part')} - Image ID: {image_id}",
                    author="Imaging System"
                ).send()
            )
            return result
        
        # If result contains an image path, display it with analysis
        if isinstance(result, dict):
            image_path = result.get("image_path")
            kl_grade = result.get("kl_grade", "Unknown")
            prediction = result.get("resnet_prediction", "Unknown")
            modality = result.get("metadata", {}).get("Modality", "Unknown")
            
            print(f"DEBUG: image_path = {image_path}, KL Grade = {kl_grade}")
            
            # Create analysis summary
            analysis_text = f"**Analysis of Image ID: {image_id}**\n\n"
            analysis_text += f"🔍 **Prediction**: {prediction}\n"
            analysis_text += f"📊 **Modality**: {modality}\n"
            
            if image_path and os.path.exists(image_path):
                print(f"DEBUG: Image exists, displaying: {image_path}")
                try:
                    # Send image with analysis to UI
                    cl.run_sync(
                        cl.Message(
                            content=analysis_text,
                            elements=[
                                cl.Image(
                                    path=image_path, 
                                    name=f"Knee Image - KL Grade {kl_grade}",
                                    display="inline",
                                    size="large"
                                )
                            ],
                            author="Imaging System"
                        ).send()
                    )
                    print(f"DEBUG: Image and analysis sent to UI successfully")
                except Exception as e:
                    print(f"DEBUG: Error sending image: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"DEBUG: Image file does not exist: {image_path}")
                # Still show analysis even if no image file
                cl.run_sync(
                    cl.Message(
                        content=analysis_text + f"\n(Image file not available at {image_path})",
                        author="Imaging System"
                    ).send()
                )
        
        return result
    
    user_proxy.register_for_execution(name="load_patient_data")(load_patient_data)
    user_proxy.register_for_execution(name="analyze_imaging")(analyze_imaging_with_display)
    user_proxy.register_for_execution(name="analyze_contraindications")(analyze_contraindications)
    user_proxy.register_for_execution(name="get_treatment_guidelines")(get_treatment_guidelines)
    user_proxy.register_for_execution(name="find_similar_cases")(find_similar_cases)
    
    # 4. Create Group Chat
    groupchat = autogen.GroupChat(
        agents=[user_proxy, assessment_agent, structuralist_agent, physiologist_agent, therapy_manager], 
        messages=[], 
        max_round=30,
        speaker_selection_method="auto"
    )
    
    # 5. Create Lead Consultant (Orchestrator)
    lead_consultant = create_lead_consultant_agent(groupchat)

    # ---------------------------------------------------------------------
    # STAGE 1: Primary Consultation
    # ---------------------------------------------------------------------
    cl.run_sync(cl.Message(content=f"### Stage 1: Primary Consultation for {patient_id}", author="System").send())
    
    initial_message = f"""
    START DIAGNOSIS for Patient ID: {patient_id}.
    
    STAGE 1 GOAL: 
    1. Assessment_Agent: Use 'load_patient_data' tool to fetch demographics, history, biomarker data, and imaging_ids for Patient {patient_id}.
    2. Structuralist_Agent: IMPORTANT - Use the 'analyze_imaging' tool with EACH imaging_id returned in the patient data (found in the 'imaging_ids' field). Analyze ALL knee images for this patient.
    3. Physiologist_Agent: Analyze the biomarker and clinical data.
    
    Determine if there is a conflict between Structural/Imaging status and Clinical/Biomarker risk.
    
    Lead Consultant: Monitor for conflict and organize the debate if needed.
    """
    
    # Initiate Chat
    user_proxy.initiate_chat(
        lead_consultant,
        message=initial_message
    )

    # ---------------------------------------------------------------------
    # STAGE 2: Follow-Up
    # ---------------------------------------------------------------------
    cl.run_sync(cl.Message(content="### Stage 2: Follow-Up (Simulated 4 Years Later)", author="System").send())
    
    # NOTE: We use clear_history=True to avoid '400' errors from dangling tool calls in previous chat.
    # We restate the context (Patient ID) so agents know what to work on.
    follow_up_message = f"""
    STAGE 2: FOLLOW-UP (4 YEARS LATER) for Patient {patient_id}.
    
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
        clear_history=True # Reset chat to avoid tool call errors
    )

    # ---------------------------------------------------------------------
    # STAGE 3: Therapy
    # ---------------------------------------------------------------------
    cl.run_sync(cl.Message(content="### Stage 3: Therapy Generation", author="System").send())
    
    therapy_message = f"""
    STAGE 3: THERAPY GENERATION for Patient {patient_id}.
    
    Task: Therapy_Group_Manager, please generate a comprehensive management plan based on the Final Phenotype determined in Stage 2.
    """
    
    user_proxy.initiate_chat(
        lead_consultant,
        message=therapy_message,
        clear_history=True # Reset chat
    )
    
    cl.run_sync(cl.Message(content="### Diagnosis Complete", author="System").send())


# -------------------------------------------------------------------------
# Chainlit Events
# -------------------------------------------------------------------------
@cl.on_chat_start
async def start():
    # 1. Greet User
    await cl.Message(content="Welcome to the OA Diagnosis System. Please enter a Patient ID (e.g., 9001695) to begin.").send()
    
    # 2. Ask for Patient ID
    res = await cl.AskUserMessage(content="Patient ID:", timeout=120).send()
    
    if res:
        patient_id = res['output'].strip()
        # 3. Run the synchronous workflow in an async way to avoid blocking the event loop
        # We use cl.make_async explicitly on the wrapper
        await cl.make_async(setup_and_run_workflow)(patient_id)
    else:
        await cl.Message(content="Timed out. Please restart.").send()

