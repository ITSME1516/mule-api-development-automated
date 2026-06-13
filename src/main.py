import time
import streamlit as st
from functions.apiCreaation import apiCreation
from functions.configCreaation import configCreation
from functions.utils import utils

apiCreator = apiCreation()
configCreator = configCreation()
utilsObj = utils()

st.title("MuleSoft API Creation")
projectPath =  st.text_input("Enter Project Path (e.g., C:/path/to/project):", placeholder="C:/path/to/project")
endpoint =  st.text_input("Enter API Endpoint (e.g., /Services/flight-service):", placeholder="/Services/flight-service")
st.markdown("---")
st.markdown("### Backend Configuration:")
backendType = st.selectbox("Select Backend Type:", ["HTTP", "Database", "SOAP"])
if backendType == "HTTP":
    backendType = "request"
method = st.selectbox("Select HTTP Method:", ["GET", "POST", "PUT", "DELETE"])
existingBackend = st.checkbox("Use Existing Backend Configuration")
backendUrl = st.text_input("Enter Backend URL:", placeholder="e.g., http://backend-service/api")

if existingBackend:
    st.markdown("#### Select Existing Backend Configuration:")
    # existingConfig = st.text_input("Enter Existing Backend Config Name:", placeholder="e.g., flight-service-config")
else:
    st.markdown("#### New Backend Configuration:")
if backendType == "request":
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Optional Backend Properties:")
        basePath = st.text_input("Base Path:", placeholder="e.g., /api", value="/*")
        connectionTimeout = st.text_input("Connection Timeout (ms):", placeholder="e.g., 60000", value="60000")
        responseTimeout = st.text_input("Response Timeout (ms):", placeholder="e.g., 60000", value="60000")
        insecure = st.checkbox("Insecure TLS (Skip SSL Validation)", value=True)
        usePersistentConnections = st.checkbox("Use Persistent Connections", value=True)
    with col2:
        st.markdown("##### Auto-Generated Backend Properties:")
        data = utilsObj.backendPropName(backendUrl, backendType, endpoint)
        for key, value in data.items():
            st.markdown(f"**{key}** : {value}")
        

else:
    raise ValueError("Currently, only HTTP backend type is supported for new configurations.")

st.markdown("---")

col1, col2, col3 = st.columns([4,2,4])
with col2:
    createButton = st.button("Create API")
if createButton:
    
    message_placeholder = st.empty()
    if endpoint and projectPath:
        with st.spinner("Creating API..."):
            apiCreator.createApi(endpoint, projectPath, backendUrl, method, backendType)
            if not existingBackend:
                configCreator.createRequestConfig(projectPath, backendUrl, endpoint, backendType)
        for seconds in range(5, 0, -1):
            message_placeholder.success(f"API created successfully! Closing in {seconds}...")
            time.sleep(1)
        message_placeholder.empty()
    else:
        message_placeholder.error("Please fill in all fields to create the API.")
