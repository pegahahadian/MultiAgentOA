import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from oa_diagnosis.agents.clinical_agent import create_physiologist_agent
from oa_diagnosis.agents.intake_agent import create_assessment_agent
from oa_diagnosis.agents.imaging_agent import create_structuralist_agent
from oa_diagnosis.agents.case_retrieval_agent import create_case_retrieval_agent
from oa_diagnosis.agents.therapy_agent import create_therapy_group_manager
from oa_diagnosis.agents.orchestrator_agent import create_lead_consultant_agent

agents = [
    ("Physiologist_Agent", create_physiologist_agent()),
    ("Assessment_Agent", create_assessment_agent()),
    ("Structuralist_Agent", create_structuralist_agent()),
    ("Case_Retrieval_Agent", create_case_retrieval_agent()),
    ("Therapy_Group_Manager", create_therapy_group_manager()),
]

# Lead consultant requires a GroupChat; skip instantiation to avoid extra deps

for name, agent in agents:
    print("----- {} -----".format(name))
    sm = getattr(agent, 'system_message', None)
    if sm:
        print(sm)
    else:
        print(repr(agent))
    print()
