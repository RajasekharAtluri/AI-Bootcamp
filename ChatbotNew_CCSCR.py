"""CC-SC-R Streamlit chatbot with browser-based OpenAI API-key entry.

Install dependencies: pip install streamlit openai
Run: streamlit run Chatbot_CCSCR.py
"""

import os

import streamlit as st
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError


# -----------------------------------------------------------------------------
# THE SYSTEM PROMPT — CC-SC-R VERSION
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
# STREAMLIT UI — page setup and API settings
# -----------------------------------------------------------------------------
st.set_page_config(page_title="CC-SC-R Chatbot", page_icon="🛠️")

with st.sidebar:
    st.header("Settings")
    environment_key = os.getenv("OPENAI_API_KEY", "")
    browser_key = st.text_input(
        "OpenAI API key",
        type="password",
        help="Used for this browser session only. It is not saved in this file.",
    ).strip()
    if environment_key:
        st.caption("An API key was found in OPENAI_API_KEY.")
    model = st.text_input("Model", value="gpt-4o-mini").strip() or "gpt-4o-mini"

# An entered key takes priority; otherwise use OPENAI_API_KEY if it was set.
api_key = browser_key or environment_key

st.title("🛠️ Chatbot — CC-SC-R System Prompt")
st.caption(
    "Built for C46 Accelerator | Same code as RCT version — only the system prompt is upgraded"
)

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
    if not api_key:
        st.error(
            "Add an OpenAI API key in the sidebar, or set OPENAI_API_KEY before "
            "starting the app."
        )
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # PROCESS — send system prompt + conversation history to the model.
    messages_to_send = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages_to_send.extend(st.session_state.messages)

    try:
        client = OpenAI(api_key=api_key)
        with st.chat_message("assistant"):
            with st.spinner("Writing a response..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=messages_to_send,
                    temperature=0.7,
                )
            assistant_reply = response.choices[0].message.content
            if not assistant_reply:
                raise ValueError("The model returned an empty response.")
            st.markdown(assistant_reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_reply}
        )
    except AuthenticationError:
        st.error("OpenAI could not authenticate this API key. Check it and try again.")
    except RateLimitError:
        st.error("The request was rate-limited or your API account has no available quota.")
    except APIConnectionError:
        st.error("Could not connect to OpenAI. Check your internet connection and try again.")
    except APIError as error:
        st.error(f"OpenAI returned an error: {error}")
    except Exception as error:
        st.error(f"Something unexpected went wrong: {error}")
