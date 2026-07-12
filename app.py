import streamlit as st
from Rag_Pipeline import answer_question

st.set_page_config(page_title="Bacteremia Guideline Assistant", page_icon="🩺")
st.title("🩺 Bacteremia Guideline Assistant")
st.caption("Research and prototyping tool only — not for clinical decision-making.")

# Initialize chat history in Streamlit's session state so it persists across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []  # Without this, Streamlit would forget the conversation every time you type 

# Display all previous messages in the conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box at the bottom of the screen
if question := st.chat_input("Ask a question about bacteremia guidelines..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching guidelines..."):    #ives users feedback during the 2-5 second retrieval+generation delay, instead of a frozen screen
            answer = answer_question(question)
        st.markdown(answer)


    st.session_state.messages.append({"role": "assistant", "content": answer})