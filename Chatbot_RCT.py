# =============================================================================
# C46 Accelerator — Week 2
# Chatbot v1: RCT System Prompt (Role, Context, Task)
# =============================================================================
#
# WHAT THIS FILE DOES:
#   A minimal Streamlit chatbot that talks to a language model using a
#   system prompt built with the RCT framework only.
#
# HOW TO RUN:
#   1. Save this file as Chatbot_RCT.py
#   2. In your terminal (inside VS Code): pip install streamlit openai
#   3. Replace YOUR_API_KEY_HERE with your actual API key
#      (we cover the SAFE way to store this in the next section)
#   4. Run: streamlit run Chatbot_RCT.py
#
# READ THIS CODE LOOKING FOR THREE THINGS — IPO:
#   INPUT   → where the user types
#   PROCESS → where the model is called with the system prompt
#   OUTPUT  → where the response is shown back
# =============================================================================

import streamlit as st
from openai import OpenAI

# -----------------------------------------------------------------------------
# API KEY — WE WILL REPLACE THIS WITH A SECURE METHOD IN THE NEXT SECTION
# -----------------------------------------------------------------------------
API_KEY = "YOUR_API_KEY_HERE"

client = OpenAI(api_key=API_KEY)

# -----------------------------------------------------------------------------
# THE SYSTEM PROMPT — RCT VERSION
# This is the ONLY thing that differs between Chatbot_RCT.py and Chatbot_CCSCR.py
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = """
ROLE:
You are an assistant helping an independent financial advisor draft client
communications.

CONTEXT:
The advisor works with retail investors in India. Clients ask about market
updates, portfolio queries, and general financial planning.

TASK:
Draft short, clear responses to the advisor's client-communication questions.
Keep the tone professional and easy to understand.
"""

# -----------------------------------------------------------------------------
# STREAMLIT UI — the page setup
# -----------------------------------------------------------------------------
st.set_page_config(page_title="RCT Chatbot", page_icon="💬")
st.title("💬 Chatbot — RCT System Prompt")
st.caption("Built for C46 Accelerator | System prompt uses Role, Context, Task only")

# Initialize message history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------------------------
# OUTPUT — display the running conversation history
# -----------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------------------------------------------------------
# INPUT — capture what the user types
# -----------------------------------------------------------------------------
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Show the user's message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # -------------------------------------------------------------------------
    # PROCESS — send system prompt + conversation history to the model
    # -------------------------------------------------------------------------
    messages_to_send = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages_to_send.extend(st.session_state.messages)

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # your CREAM choice: fast-tier for chat interaction
        messages=messages_to_send,
        temperature=0.7,
    )

    assistant_reply = response.choices[0].message.content

    # -------------------------------------------------------------------------
    # OUTPUT — show the model's response back to the user
    # -------------------------------------------------------------------------
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

# =============================================================================
# WHAT TO NOTICE WHEN YOU RUN THIS:
# - Try asking: "Draft a market update for a client who just started investing."
# - The output will be reasonable, but generic — no verification, no structure,
#   no risk flagging, no compliance awareness.
# - This is exactly what the RCT framework leaves out — and exactly what
#   Chatbot_CCSCR.py fixes with the same code and a stronger system prompt.
# =============================================================================