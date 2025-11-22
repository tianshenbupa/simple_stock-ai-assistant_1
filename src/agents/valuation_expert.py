from langchain.agents import create_agent
from src.core.llm import llm
from src.tools.valuation import calculate_pe_ratio, calculate_intrinsic_value
from config.prompts import VALUATION_EXPERT_PROMPT

def create_valuation_expert():
    return create_agent(
        model=llm,
        tools=[calculate_pe_ratio, calculate_intrinsic_value],
        system_prompt=VALUATION_EXPERT_PROMPT,
    )

_expert = None

def get_valuation_expert():
    global _expert
    if _expert is None:
        _expert = create_valuation_expert()
    return _expert