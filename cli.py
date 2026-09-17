"""
Interactive CLI Harness for System Health Agent
Option A: Lightweight terminal execution loop
"""

import sys
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load env from config folder
env_path = Path(__file__).parent / "config" / "local.env"
load_dotenv(env_path)

from src.agent import create_health_agent


def print_banner():
    print("\n" + "=" * 60)
    print("  🏥 SYSTEM HEALTH AGENT - Interactive CLI")
    print("=" * 60)
    print("Commands:")
    print("  • Type your diagnostic request")
    print("  • 'new' - Start a new conversation thread")
    print("  • 'thread' - Show current thread ID")
    print("  • 'quit' or 'exit' - Exit the CLI")
    print("=" * 60 + "\n")


def stream_agent_response(agent, config, user_input: str):
    """Stream agent response with tool execution visibility."""
    print("\n🔄 Processing...\n")
    
    messages = [HumanMessage(content=user_input)]
    
    try:
        for event in agent.stream({"messages": messages}, config, stream_mode="updates"):
            # Handle different event types
            for node_name, node_output in event.items():
                if node_name == "agent":
                    # Agent's response
                    if "messages" in node_output:
                        for msg in node_output["messages"]:
                            if hasattr(msg, "content") and msg.content:
                                print(f"🤖 Agent: {msg.content}")
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                for tc in msg.tool_calls:
                                    print(f"🔧 Calling tool: {tc['name']}")
                                    print(f"   Args: {tc['args']}")
                
                elif node_name == "tools":
                    # Tool execution results
                    if "messages" in node_output:
                        for msg in node_output["messages"]:
                            if hasattr(msg, "content"):
                                print(f"📊 Tool result: {msg.content[:500]}...")
                                if len(msg.content) > 500:
                                    print("   (truncated)")
        
        print()
    
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    print_banner()
    
    # Generate or use existing thread ID
    thread_id = str(uuid.uuid4())[:8]
    print(f"📌 Thread ID: {thread_id}")
    print("   (Use same ID after restart to recover conversation)\n")
    
    # Ask if user wants to use existing thread
    existing = input("Enter existing thread ID (or press Enter for new): ").strip()
    if existing:
        thread_id = existing
        print(f"📌 Using thread: {thread_id}\n")
    
    # Create agent
    try:
        agent, config = create_health_agent(thread_id)
        print("✅ Agent initialized with MongoDB persistence\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        print("   Make sure MongoDB is running (docker-compose up -d)")
        sys.exit(1)
    
    # Main loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ("quit", "exit"):
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == "new":
                thread_id = str(uuid.uuid4())[:8]
                agent, config = create_health_agent(thread_id)
                print(f"\n📌 New thread: {thread_id}\n")
                continue
            
            if user_input.lower() == "thread":
                print(f"\n📌 Current thread: {thread_id}\n")
                continue
            
            stream_agent_response(agent, config, user_input)
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted! State saved to MongoDB.")
            print(f"   Restart with thread ID '{thread_id}' to resume.")
            break


if __name__ == "__main__":
    main()
