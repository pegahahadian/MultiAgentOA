from autogen import AssistantAgent, GroupChatManager, GroupChat
from oa_diagnosis.agents.config import llm_config

def create_lead_consultant_agent(groupchat: GroupChat):
    # Update config with temperature 0.3
    specific_config = llm_config.copy()
    specific_config["temperature"] = 0.3

    agent = GroupChatManager(
        groupchat=groupchat,
        name="Lead_Consultant_Agent",
        llm_config=specific_config,
        system_message="""You are the Lead_Consultant_Agent (Judge/Orchestrator).
        Role: Debate moderator and final decision maker.

        Logic:
        1. Access estimates from Structuralist (Struct_Risk) and Physiologist (Physio_Risk).
        2. Detect conflict: If abs(Struct_Risk - Physio_Risk) > 30% or SIGNIFICANT disagreement on phenotype.
        3. Manage Debate: If conflict, trigger debate rounds (Physio presents -> Struct rebuts -> Judge decides).

        Output: Final 4-class phenotype (Non-Progressor, Rapid Progressor (RP), Slow Progressor (SP), Combined) and summary.

        Response style: Provide the final phenotype and a maximal two-sentence rationale. Do not repeat metrics or include closing pleasantries.
        """
    )
    return agent
