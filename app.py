import streamlit as st
from core import process

st.set_page_config(page_title="Guarded Health Assistant", page_icon="🛡️")
st.title("🛡️ Guarded Health Assistant")
st.caption("Every message is screened by Shieldstral before and after the model.")

if "history" not in st.session_state:
    st.session_state.history = []

# Replay the conversation so far
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Continuous chat input (keeps running turn after turn)
prompt = st.chat_input("Ask a health question...")
if prompt:
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Screening + generating..."):
            # pass prior turns (excluding the message we just added) for context
            result = process(prompt, st.session_state.history[:-1])
        if result["blocked"]:
            st.warning(f"{result['reply']}\n\n_(blocked by guardrail at the {result['stage']} stage)_")
        else:
            st.write(result["reply"])

    st.session_state.history.append({"role": "assistant", "content": result["reply"]})
