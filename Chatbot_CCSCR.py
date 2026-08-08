# =============================================================================
# C46 Accelerator — Week 2
# Chatbot v2: CC-SC-R System Prompt (Context, Constraints, Structure,
#                                     Checkpoints, Review)
# =============================================================================
#
# WHAT THIS FILE DOES:
#   The SAME chatbot as Chatbot_RCT.py — every line of code is identical
#   except the SYSTEM_PROMPT string below.
#
#   This is the whole lesson of Week 2: the code is easy. The prompt is
#   where professional AI work actually happens.
#
# HOW TO RUN:
#   1. Save as Chatbot_CCSCR.py
#   2. In your terminal (inside VS Code): pip install streamlit openai
#   3. Replace YOUR_API_KEY_HERE with your actual API key
#   4. Run: streamlit run Chatbot_CCSCR.py
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
# THE SYSTEM PROMPT — CC-SC-R VERSION
# Notice: same file, same code, upgraded prompt.
# This is the ONLY line that changed from Chatbot_RCT.py.
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are an assistant helping an independent financial advisor draft client
communications. Every response you produce must follow this framework:

CONTEXT:
- Advisor's clients are retail investors in India, primarily first-time to
  mid-experience, mostly English/Hindi bilingual.
- Advisor's brand voice is calm, honest, and non-promotional. Clients trust
  the advisor because he never over-sells.
- Communications are typically WhatsApp messages, short emails, or brief
  market notes — rarely long documents.

CONSTRAINTS:
- NEVER recommend specific stocks, funds, or securities by name.
- NEVER guarantee returns or use words like "sure," "definitely," "will grow."
- ALWAYS include a SEBI-appropriate disclaimer where any market view is shared
  ("Views expressed are for informational purposes only and not investment
   advice. Please consult your advisor before making decisions.").
- Do not use hype phrases ("don't miss out," "act now," "limited time").
- Keep responses under 200 words unless the user explicitly asks for longer.
- If you are unsure about a market fact, tag it [VERIFY] rather than stating
  it with confidence.

STRUCTURE:
Every client-facing draft must follow this shape:
1. Greeting (one line)
2. The point being made (2–3 sentences maximum)
3. One clear next step or action, if any
4. Disclaimer (only when market views are included)

CHECKPOINTS:
- Before drafting: state your assumptions about the client's context in one
  line at the top of your response, in italics.
- During drafting: flag any claim you cannot verify with [VERIFY].
- After drafting: list any language that could be misread as a guarantee, so
  the advisor can review it before sending.

REVIEW:
A "good" output is one where:
- The advisor could send it to a client with only minor edits.
- Nothing in the draft could be flagged as regulatory-sensitive.
- Every disclaimer is present where it needs to be.
- The tone matches how the advisor actually speaks — calm, honest, not
  promotional.
If any of these fail, say so at the end of your response before the advisor
sends it.
"""

# -----------------------------------------------------------------------------
# STREAMLIT UI — the page setup
# -----------------------------------------------------------------------------
st.set_page_config(page_title="CC-SC-R Chatbot", page_icon="🛠️")
st.title("🛠️ Chatbot — CC-SC-R System Prompt")
st.caption("Built for C46 Accelerator | Same code as RCT version — only the system prompt is upgraded")

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
# - Ask the same question you asked Chatbot_RCT.py:
#   "Draft a market update for a client who just started investing."
#
# - Compare the two outputs side by side:
#     • The CC-SC-R version shows its assumptions up front
#     • It has a structured shape (greeting, point, action, disclaimer)
#     • It hedges what it doesn't know with [VERIFY]
#     • It self-flags anything that could sound like a guarantee
#     • It stays inside the length constraint
#
# - Same model. Same code. Same temperature. The ONLY difference is the
#   system prompt. That is the entire lesson.
#
# THIS IS YOUR TEMPLATE:
#   Every chatbot you build in the rest of this bootcamp — voice bot,
#   RAG bot, domain chatbot, agent — uses this same shape. The domain
#   changes. The system prompt changes. The 30 lines of code stay the same.
# =============================================================================
