"""Interactive CLI for System Health Agent."""

import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load env from config folder
env_path = Path(__file__).parent / "config" / "local.env"
load_dotenv(env_path)

from src.agent import create_health_agent


def main():
    print("\n" + "=" * 50)
    print("  🏥 System Health Agent")
    print("=" * 50)
    print("Commands: 'quit' to exit, 'new' for new thread")
    print("=" * 50 + "\n")
    
    thread_id = str(uuid.uuid4())[:8]
    print(f"Thread ID: {thread_id}\n")
    
    try:
        agent, config = create_health_agent(thread_id)
        print("✅ Agent ready\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit"):
                print("👋 Bye!")
                break
            if user_input.lower() == "new":
                thread_id = str(uuid.uuid4())[:8]
                agent, config = create_health_agent(thread_id)
                print(f"\n📌 New thread: {thread_id}\n")
                continue
            
            print("\n🔄 Processing...\n")
            
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
                stream_mode="updates"
            ):
                for node, output in chunk.items():
                    if "messages" in output:
                        for msg in output["messages"]:
                            if hasattr(msg, "content") and msg.content:
                                print(f"🤖 {msg.content}\n")
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                for tc in msg.tool_calls:
                                    print(f"🔧 {tc['name']}: {tc['args']}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted!")
            break


if __name__ == "__main__":
    main()
