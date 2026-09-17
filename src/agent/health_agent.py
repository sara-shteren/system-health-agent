"""System Health Agent - Basic version."""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent

from src.tools import ALL_TOOLS
from src.agent.prompts import SYSTEM_PROMPT


def create_health_agent(thread_id: str = "default"):
    """Creates the System Health Agent with in-memory persistence."""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )
    
    memory = MemorySaver()
    
    agent = create_agent(
        llm,
        ALL_TOOLS,
        checkpointer=memory
    )
    
    return agent, {"configurable": {"thread_id": thread_id}}
