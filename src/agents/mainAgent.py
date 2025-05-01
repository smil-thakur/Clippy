from functools import partial
from agno.agent import Agent
from agno.models.google import Gemini
from agents.agentsUtility import *


class MainAgent:
    def __init__(self, apiKey: str, model: str):
        self.apiKey = apiKey
        self.model = model

    async def invoke_general_agent(self, prompt: str) -> str:
        print("Invoking general-purpose agent")
        agent = AgentsUtility.generalPurposeAgent(self.model, self.apiKey)
        res = await agent.arun(prompt)
        print("Response from general-purpose agent:", res.content)
        return res.content

    async def invoke_terminal_agent(self, prompt: str) -> str:
        print("Invoking terminal agent")
        agent = AgentsUtility.terminalAgent(self.model, self.apiKey)
        res = await agent.arun(prompt)
        print("Response from terminal agent:", res.content)
        return res.content

    async def initiateMainAgent(self, prompt: str) -> str:
        router_agent = Agent(
            model=Gemini(api_key=self.apiKey, id=self.model),
            description=(
                '''You are a routing agent. Based on the user's input, choose the correct tool from the available ones.'''
                '''If the input is a general-purpose query, invoke the general-purpose agent.'''
                '''If it relates to command-line execution or terminal operations, invoke the terminal agent.'''
                '''Use the appropriate tool and return ONLY the tool’s result as your final response.'''
                '''Do NOT alter, summarize, modify, enhance, or reduce the tool output. Just return it exactly as received.'''
            ),
            tools=[
                self.invoke_general_agent,
                self.invoke_terminal_agent
            ]
        )
        res = await router_agent.arun(prompt)
        return str(res.content)
