"""System Health Agent - Streamlit Frontend."""

import streamlit as st
from backend import stream
from waiting_messages import get_random_waiting_message

st.set_page_config(
    page_title="System Health Agent",
    layout="centered"
)

# Custom CSS for round avatars and thinking animation
st.markdown("""
<style>
    .stChatMessage img {
        border-radius: 50% !important;
    }
    
    @keyframes thinking-bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    @keyframes thinking-eyes {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .thinking-indicator {
        display: inline-block;
        animation: thinking-bounce 1s ease-in-out infinite;
        font-size: 1.5em;
    }
    
    .thinking-text {
        color: rgba(100, 100, 100, 0.6);
        font-style: italic;
        font-size: 0.9em;
        margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏥 System Health Agent")
st.markdown("Operational health checks: system metrics, endpoint status, directory inspection.")

# Setup history state by thread ID
if "history_by_thread" not in st.session_state:
    st.session_state.history_by_thread = {}

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Configuration")
    thread_id = st.text_input("Active Thread ID", value="health_session_1")
    
    st.markdown("---")
    if st.button("Clear Thread History"):
        st.session_state.history_by_thread[thread_id] = []
        st.rerun()

# Retrieve or create history for this thread
if thread_id not in st.session_state.history_by_thread:
    st.session_state.history_by_thread[thread_id] = []

messages = st.session_state.history_by_thread[thread_id]

# Render chat history
for msg in messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "tool_call":
        with st.status(f"🛠️ Tool Call: {msg['name']}", state="complete"):
            st.write("Parameters:")
            st.json(msg["args"])
    elif msg["role"] == "tool_response":
        with st.status("📥 Tool Response Received", state="complete"):
            st.code(msg["content"], language="json")
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# User prompt input
if prompt := st.chat_input("Ask: Check system metrics, endpoint health, directory metadata..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    messages.append({"role": "user", "content": prompt})
    st.session_state.history_by_thread[thread_id] = messages
    
    with st.chat_message("assistant"):
        # Show funny waiting message with bouncing thinking emoji
        waiting_placeholder = st.empty()
        waiting_msg = get_random_waiting_message()
        waiting_placeholder.markdown(
            f'<span class="thinking-indicator">🤔</span>'
            f'<span class="thinking-text">{waiting_msg}</span>',
            unsafe_allow_html=True
        )
        
        text_placeholder = st.empty()
        full_response = ""
        
        for chunk in stream(prompt, thread_id):
            # Clear waiting message once we get first chunk
            waiting_placeholder.empty()
            
            if "model" in chunk:
                model_msg = chunk["model"]["messages"][0]
                
                if getattr(model_msg, "tool_calls", None):
                    for tc in model_msg.tool_calls:
                        with st.status(f"🛠️ Tool Call: {tc['name']}", state="running") as status:
                            st.write("Parameters:")
                            st.json(tc["args"])
                            status.update(label=f"🛠️ Tool Call: {tc['name']}", state="complete")
                        
                        messages.append({
                            "role": "tool_call",
                            "name": tc["name"],
                            "args": tc["args"]
                        })
                        st.session_state.history_by_thread[thread_id] = messages
                
                if getattr(model_msg, "content", None):
                    text_content = ""
                    if isinstance(model_msg.content, str):
                        text_content = model_msg.content
                    elif isinstance(model_msg.content, list):
                        for part in model_msg.content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                text_content += part.get("text", "")
                            elif isinstance(part, str):
                                text_content += part
                    
                    if text_content:
                        full_response += text_content
                        text_placeholder.markdown(full_response)
                        
            elif "tools" in chunk:
                tool_msg = chunk["tools"]["messages"][0]
                with st.status("📥 Tool Response Received", state="complete"):
                    st.code(tool_msg.content, language="json")
                
                messages.append({
                    "role": "tool_response",
                    "content": tool_msg.content
                })
                st.session_state.history_by_thread[thread_id] = messages

        if full_response:
            messages.append({"role": "assistant", "content": full_response})
            st.session_state.history_by_thread[thread_id] = messages
