"""System Health Agent with MongoDB persistence."""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient

from src.tools import ALL_TOOLS
from src.agent.prompts import SYSTEM_PROMPT


def create_health_agent(thread_id: str = "default"):
    """Creates the System Health Agent with MongoDB persistence."""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )
    
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB", "agent_health_db")
    
    client = MongoClient(mongodb_uri)
    checkpointer = MongoDBSaver(client, db_name=db_name)
    
    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        checkpointer=checkpointer,
        state_modifier=SYSTEM_PROMPT
    )
    
    return agent, {"configurable": {"thread_id": thread_id}}
