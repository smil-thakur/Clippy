from agno.agent import Agent
from agno.models.google import Gemini

from agentTools.agentTools import AgentTools


class AgentsUtility:
    @staticmethod
    def terminalAgent(id: str, apiKey: str) -> Agent:
        return Agent(model=Gemini(api_key=apiKey, id=id), markdown=True, description="You are a smart terminal agent designed to execute shell commands based on natural language prompts. Before starting any task, proactively identify and request all necessary user confirmations or decisions to ensure seamless, uninterrupted execution.")

    @staticmethod
    def generalPurposeAgent(id: str, apiKey: str) -> Agent:
        return Agent(
            model=Gemini(id=id, api_key=apiKey),
            tools=[AgentTools.searchWeb()],
            description=(
                "You are an intelligent assistant embedded in a search interface. "
                "In addition to helping with searches, you can summarize information, define words, and write small, precise code snippets. "
                "Keep all responses brief and focused, as this assistant is designed for quick, lightweight tasks."
            ),
            markdown=True)
