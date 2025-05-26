import streamlit as st
from Agent import multi_agent_system
import html

st.set_page_config(page_title="Historical Monuments AI", page_icon="🏛️")

# Add custom CSS for sticky header and input bar
st.markdown("""
    <style>
    .sticky-header {
        position: sticky;
        top: -10px; /* Move header slightly up */
        background: #111;
        z-index: 100;
        padding-top: 10px;
        padding-bottom: 8px;
        color: #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .sticky-header h2, .sticky-header hr {
        color: #fff !important;
        border-color: #fff !important;
    }
    .sticky-input {
        position: fixed;
        bottom: -10px; /* Move input bar slightly down */
        left: 0;
        width: 100vw;
        background: white;
        z-index: 100;
        padding-top: 8px;
        padding-bottom: 24px; /* More space at bottom */
        box-shadow: 0 -2px 8px rgba(0,0,0,0.04);
    }
    .chat-scroll {
        max-height: 68vh; /* More space for chat */
        overflow-y: auto;
        margin-bottom: 90px; /* More space for input bar */
        margin-top: 20px; /* Space below header */
    }
    </style>
""", unsafe_allow_html=True)

# Sticky header
st.markdown("<div class='sticky-header'><h2>🏛️ Historical Monuments Conversational AI</h2><hr></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def send_message():
    user_input = st.session_state["user_input"].strip()
    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        state = {"messages": st.session_state["messages"]}
        response = ""
        for step in multi_agent_system.stream(state):
            for agent_name, agent_data in step.items():
                if not agent_data:
                    continue
                messages = agent_data.get("messages", [])
                if messages:
                    last_msg = messages[-1]
                    if hasattr(last_msg, "content"):
                        response = last_msg.content
                    elif isinstance(last_msg, dict) and "content" in last_msg:
                        response = last_msg["content"]
            if response:
                st.session_state["messages"].append({"role": "assistant", "content": response})
                break
        st.session_state["user_input"] = ""  # This is safe inside the callback

st.markdown("---")

# Scrollable chat area
st.markdown("<div class='chat-scroll'>", unsafe_allow_html=True)
for i, msg in enumerate(st.session_state["messages"]):
    safe_content = html.escape(msg["content"])
    if msg["role"] == "user":
        st.markdown(f"<div style='display: flex; justify-content: flex-start; margin-bottom: 8px;'><div style='background-color: #e1ffc7; color: #222; padding: 10px 16px; border-radius: 16px 16px 16px 0; max-width: 70%;'>{safe_content}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='display: flex; justify-content: flex-end; margin-bottom: 8px;'><div style='background-color: #d2e3fc; color: #222; padding: 10px 16px; border-radius: 16px 16px 0 16px; max-width: 70%;'>{safe_content}</div></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Sticky input bar
st.markdown("<div class='sticky-input'>", unsafe_allow_html=True)
st.text_input(
    "Type your message and press Enter...",
    key="user_input",
    on_change=send_message,
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)