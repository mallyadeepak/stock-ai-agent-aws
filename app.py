#!/usr/bin/env python3
"""Simple Streamlit UI for the Stock AI Agent."""

import sys
import re
import ast
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
from stock_agent.agent import create_stock_agent, run_query
from stock_agent.config import AgentConfig


def format_response(response: str) -> str:
    """Parse and format the agent response for display."""
    # Try to extract text from the response structure
    # Response often looks like: {'role': 'assistant', 'content': [{'text': '...'}]}

    try:
        # Check if it's a string representation of a dict
        if response.strip().startswith("{") and "'content'" in response:
            # Try to parse it
            parsed = ast.literal_eval(response)
            if isinstance(parsed, dict) and "content" in parsed:
                content = parsed["content"]
                if isinstance(content, list):
                    texts = []
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            texts.append(item["text"])
                    if texts:
                        return "\n\n".join(texts)
    except (ValueError, SyntaxError):
        pass

    # Try regex extraction as fallback
    match = re.search(r"'text':\s*['\"](.+?)['\"]}", response, re.DOTALL)
    if match:
        text = match.group(1)
        # Unescape newlines
        text = text.replace("\\n", "\n")
        return text

    # If response contains the raw dict at the end, try to extract just the text before it
    if "{'role': 'assistant'" in response:
        parts = response.split("{'role': 'assistant'")
        if len(parts) > 1 and parts[0].strip():
            return parts[0].strip()

    # Return as-is if we can't parse it
    return response

# Page config
st.set_page_config(
    page_title="Stock AI Agent",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .agent-message {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📈 Stock AI Agent")
st.caption("Powered by AWS Bedrock & Yahoo Finance")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    with st.spinner("Initializing agent..."):
        try:
            config = AgentConfig()
            st.session_state.agent = create_stock_agent(config)
            st.session_state.agent_ready = True
        except Exception as e:
            st.session_state.agent_ready = False
            st.session_state.agent_error = str(e)

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This AI agent can help you with:
    - 📊 Stock quotes and metrics
    - 🔍 Finding stocks by sector
    - ⚖️ Comparing multiple stocks
    - 📰 News and analyst recommendations
    - 📈 Stock valuation analysis
    """)

    st.header("Example Questions")
    examples = [
        "What is the current price of AAPL?",
        "Compare MSFT and GOOGL",
        "What are the top healthcare stocks?",
        "What do analysts say about NVDA?",
        "Analyze Tesla stock value",
    ]

    for example in examples:
        if st.button(example, key=example):
            st.session_state.pending_question = example

    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Check agent status
if not st.session_state.get("agent_ready", False):
    st.error(f"Failed to initialize agent: {st.session_state.get('agent_error', 'Unknown error')}")
    st.info("Make sure you have AWS credentials configured and access to Bedrock.")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle pending question from sidebar
if "pending_question" in st.session_state:
    prompt = st.session_state.pending_question
    del st.session_state.pending_question

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            raw_response = run_query(st.session_state.agent, prompt)
            response = format_response(raw_response)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask about stocks..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            raw_response = run_query(st.session_state.agent, prompt)
            response = format_response(raw_response)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
