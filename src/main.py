import time
import streamlit as st
from functions.apiCreaation import apiCreation

apiCreator = apiCreation()

st.title("MuleSoft API Creation")
projectPath =  st.text_input("Enter Project Path (e.g., C:/path/to/project):", placeholder="C:/path/to/project")
endpoint =  st.text_input("Enter API Endpoint (e.g., /Services/flight-service):", placeholder="/Services/flight-service")



if st.button("Create API"):
    message_placeholder = st.empty()
    if endpoint and projectPath:
        with st.spinner("Creating API..."):
            apiCreator.createApi(endpoint, projectPath)
        for seconds in range(5, 0, -1):
            message_placeholder.success(f"API created successfully! Closing in {seconds}...")
            time.sleep(1)
        message_placeholder.empty()
    else:
        message_placeholder.error("Please fill in all fields to create the API.")
