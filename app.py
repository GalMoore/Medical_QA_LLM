import streamlit as st
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import os
import PyPDF2
from io import BytesIO
import openai
import time
import os

st.title("Let's explores session states and callback functions") 
uploaded_files = st.sidebar.file_uploader("",accept_multiple_files=True, type=['pdf'])
if uploaded_files:
        data = []
        filenames = []
        st.sidebar.write("You have uploaded the following files:")
        for file in uploaded_files:
                st.sidebar.write(file.name)
                file_stream = BytesIO(file.read())
                pdf_reader = PyPDF2.PdfFileReader(file_stream)
                text = ""
                for page in range(pdf_reader.getNumPages()):
                    text += pdf_reader.getPage(page).extract_text()
                data.append(text)
                filenames.append(file.name)

        time.sleep(5)
        st.write(data[0][:50])

        # Update the random_numbers in the session state only when new files are uploaded
        st.session_state.random_numbers = np.random.rand(100)

# If the random_numbers are available in the session state, plot them
if "random_numbers" in st.session_state:
    plt.plot(st.session_state.random_numbers)
    st.pyplot(plt)

openai.api_key = st.secrets["openai_password"]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] =  "gpt-3.5-turbo-16k" 
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# prompt is the latest text input into the chat bar
if prompt := st.chat_input("What is up?"):
    # If the user inputs a message, clear previous messages and append the new one with the role "user"
    st.session_state.messages = [{"role": "user", "content": prompt}]
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
