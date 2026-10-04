"""LocalLens - Streamlit Frontend."""

import os
import streamlit as st
from backend import stream, set_folder, get_current_folder

st.set_page_config(page_title="LocalLens", layout="centered")

st.title("🔍 LocalLens")
st.markdown("Private document search assistant - search your local files with AI")

# Session state
if "history" not in st.session_state:
    st.session_state.history = []
if "folder_set" not in st.session_state:
    st.session_state.folder_set = False

# Sidebar - folder selection
with st.sidebar:
    st.header("📁 Select Folder")
    folder_path = st.text_input(
        "Folder path:",
        value="./my_vault",
        help="Enter the path to the folder you want to search"
    )
    
    if st.button("Set Folder", type="primary"):
        if os.path.isdir(folder_path):
            result = set_folder(folder_path)
            st.session_state.folder_set = True
            st.session_state.history = []
            st.success(f"✅ {result}")
        else:
            st.error(f"❌ Folder not found: {folder_path}")
    
    if st.session_state.folder_set:
        st.info(f"Current: {get_current_folder()}")
    
    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.history = []
        st.rerun()

# Main chat area
if not st.session_state.folder_set:
    st.warning("👈 Please select a folder in the sidebar to start")
else:
    # Render chat history
    for msg in st.session_state.history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif msg["role"] == "tool_call":
            with st.expander(f"🛠️ {msg['name']}", expanded=False):
                st.code(msg["args"], language="json")
        elif msg["role"] == "tool_response":
            with st.expander("📄 Tool Response", expanded=False):
                st.text(msg["content"][:500] + "..." if len(msg["content"]) > 500 else msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
    
    # User input
    if prompt := st.chat_input("Ask about your documents..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.history.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            thinking = st.empty()
            thinking.markdown("🔍 Searching...")
            
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                for chunk in stream(prompt, "locallens_session"):
                    thinking.empty()
                    
                    if "model" in chunk:
                        model_msg = chunk["model"]["messages"][0]
                        
                        # Tool calls
                        if getattr(model_msg, "tool_calls", None):
                            for tc in model_msg.tool_calls:
                                with st.expander(f"🛠️ {tc['name']}", expanded=False):
                                    st.json(tc["args"])
                                st.session_state.history.append({
                                    "role": "tool_call",
                                    "name": tc["name"],
                                    "args": str(tc["args"])
                                })
                        
                        # Text response
                        if getattr(model_msg, "content", None):
                            if isinstance(model_msg.content, str):
                                full_response = model_msg.content
                            elif isinstance(model_msg.content, list):
                                for part in model_msg.content:
                                    if isinstance(part, dict) and part.get("type") == "text":
                                        full_response += part.get("text", "")
                            response_placeholder.markdown(full_response)
                    
                    elif "tools" in chunk:
                        tool_msg = chunk["tools"]["messages"][0]
                        content = str(tool_msg.content) if hasattr(tool_msg, "content") else str(tool_msg)
                        with st.expander("📄 Tool Response", expanded=False):
                            st.text(content[:500] + "..." if len(content) > 500 else content)
                        st.session_state.history.append({
                            "role": "tool_response",
                            "content": content
                        })
                
                if full_response:
                    st.session_state.history.append({"role": "assistant", "content": full_response})
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
