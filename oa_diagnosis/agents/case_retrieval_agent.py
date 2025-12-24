from autogen import AssistantAgent
from oa_diagnosis.agents.config import llm_config
from oa_diagnosis.tools.similarity_search import find_similar_cases

def create_case_retrieval_agent():
    agent = AssistantAgent(
        name="Case_Retrieval_Agent",
        system_message="""You are the Case Retrieval Agent.
        Your role is to:
        1. Extract the patient's Age, BMI, Gender, and KL Grade (from Imaging).
        2. Use 'find_similar_cases' to find historical patients.
        3. Report the outcomes of similar cases to help refine the prognosis or treatment plan.

        Response style: Return a concise list of similar cases (IDs + key outcomes) and a one-line summary. No extra commentary or pleasantries.
        """,
        llm_config=llm_config
    )
    
    agent.register_for_llm(name="find_similar_cases", description="Find similar OAI cases")(find_similar_cases)
    
    return agent
