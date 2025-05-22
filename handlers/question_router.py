
from agents.psi_scenario_agent import *
from agents.supervisor_agent import supervisor_agent

def route_question(user_q, suffix):
    s = suffix.strip()
    ql = user_q.lower()
    if "max sr" in ql and "main sp" in ql:
        return scenario_max_sr_vs_main_sp(s), "maxsr"
    elif "bod start" in ql:
        return scenario_bod_start_reason(s), "bod"
    elif "delay" in ql and "shortage" in ql:
        return scenario_delay_allocation(s), "delay"
    else:
        return supervisor_agent(user_q), "fallback"
