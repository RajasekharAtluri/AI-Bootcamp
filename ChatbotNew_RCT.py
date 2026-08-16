"""A Streamlit RCT chatbot using the OpenAI Python client.

Run with:
    pip install streamlit openai
    streamlit run Chatbot_RCT.py

Set OPENAI_API_KEY before starting the app, or enter a key in the sidebar.
"""

import os

import streamlit as st
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError


# -----------------------------------------------------------------------------
# THE SYSTEM PROMPT — RCT VERSION
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
# STREAMLIT UI — page setup and configuration
# -----------------------------------------------------------------------------
st.set_page_config(page_title="RCT Chatbot", page_icon="💬")

with st.sidebar:
    st.header("Settings")
    environment_key = os.getenv("OPENAI_API_KEY", "")
    api_key = st.text_input(
        "OpenAI API key",
        value="",
        type="password",
        help="Used only for this app session. You can also set OPENAI_API_KEY before running the app.",
    ).strip()
    if environment_key:
        st.caption("An API key was found in OPENAI_API_KEY.")
    model = st.text_input("Model", value="gpt-4o-mini").strip() or "gpt-4o-mini"
    st.caption("Your key is not saved in this file.")

# Prefer the key entered for this session; otherwise use the environment variable.
api_key = api_key or environment_key

st.title("💬 Chatbot — RCT System Prompt")
st.caption("Built for C46 Accelerator | System prompt uses Role, Context, Task only")

# Initialize message history in Streamlit's session state.
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
            "No OpenAI API key is available. Enter one in the sidebar or set the "
            "OPENAI_API_KEY environment variable, then try again."
        )
        st.stop()

    # Show the user's message immediately.
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # -------------------------------------------------------------------------
    # PROCESS — send system prompt + conversation history to the model
    # -------------------------------------------------------------------------
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
                raise APIError("The model returned an empty response.", request=None, body=None)
            st.markdown(assistant_reply)

        # OUTPUT — retain and show the model response in the conversation.
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


# =============================================================================
# WHAT TO NOTICE WHEN YOU RUN THIS:
# - Try: "Draft a market update for a client who just started investing."
# - The output will be reasonable but generic: RCT gives the model only role,
#   context, and task. A stronger prompt can add verification and safeguards.
# =============================================================================
