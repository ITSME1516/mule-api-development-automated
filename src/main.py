import time
import streamlit as st
from functions.apiCreation import apiCreation
from functions.configCreation import configCreation
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
existingBackend = st.checkbox("Use Existing Backend Configuration", value=True)
backendUrl = st.text_input("Enter Backend URL:", placeholder="e.g., http://backend-service/api")

if existingBackend:
    st.markdown("#### Select Existing Backend Configuration:")
    # existingConfig = st.text_input("Enter Existing Backend Config Name:", placeholder="e.g., flight-service-config")
else:
    if (backendType == "request") :
        if (len(backendUrl) > 0) and (st.checkbox("Show Auto-Generated Backend Properties")):
            st.markdown("#### New Backend Configuration:")
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
st.markdown("### Select Components to Develop:")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("#### Flows:")
    create_main_flow = st.checkbox("Main Flow", value=True)
    create_impl_flow = st.checkbox("Implementation Flow", value=True)
    create_system_flow = st.checkbox("System Flow", value=True)
with col2:
    st.markdown("#### Configuration:")
with col3:
    st.markdown("#### Test Files")
with col4:
    st.markdown("#### Global Config:")
    create_global_config = st.checkbox("Global Config", value=not existingBackend)

st.markdown("---")

col1, col2, col3 = st.columns([4,2,4])
with col2:
    createButton = st.button("Create API")
if createButton:
    
    message_placeholder = st.empty()
    # Validate at least one component is selected
    if not (create_main_flow or create_impl_flow or create_system_flow or create_global_config):
        message_placeholder.error("Please select at least one component to develop.")
    elif endpoint and projectPath:
        with st.spinner("Creating API..."):
            try:
                status = apiCreator.createApi(
                    endpoint, 
                    projectPath, 
                    backendUrl, 
                    method, 
                    backendType, 
                    existingBackend,
                    create_main_flow,
                    create_impl_flow,
                    create_system_flow,
                    create_global_config
                )
                
                # Display status in centered, clean format
                with message_placeholder.container():
                    st.markdown("---")
                    st.markdown("<h2 style='text-align: center;'>✅ API Created Successfully</h2>", unsafe_allow_html=True)
                    st.markdown("---")
                    
                    # Display component status
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("<h4 style='text-align: center;'>Main Flow</h4>", unsafe_allow_html=True)
                        if status["main_flow"] == "Developed":
                            st.markdown("<p style='text-align: center; color: green; font-size: 18px;'><b>Developed</b></p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='text-align: center; color: orange; font-size: 18px;'><b>{status['main_flow']}</b></p>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("<h4 style='text-align: center;'>Impl Flow</h4>", unsafe_allow_html=True)
                        if status["impl_flow"] == "Developed":
                            st.markdown("<p style='text-align: center; color: green; font-size: 18px;'><b>Developed</b></p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='text-align: center; color: orange; font-size: 18px;'><b>{status['impl_flow']}</b></p>", unsafe_allow_html=True)
                    
                    col3, col4 = st.columns([1, 1])
                    
                    with col3:
                        st.markdown("<h4 style='text-align: center;'>Sys Flow</h4>", unsafe_allow_html=True)
                        if status["sys_flow"] == "Developed":
                            st.markdown("<p style='text-align: center; color: green; font-size: 18px;'><b>Developed</b></p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='text-align: center; color: orange; font-size: 18px;'><b>{status['sys_flow']}</b></p>", unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown("<h4 style='text-align: center;'>Global Config</h4>", unsafe_allow_html=True)
                        if status["global_config"] == "Developed":
                            st.markdown("<p style='text-align: center; color: green; font-size: 18px;'><b>Developed</b></p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='text-align: center; color: orange; font-size: 18px;'><b>{status['global_config']}</b></p>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                
                # Auto-close after 5 seconds
                time.sleep(10)
                message_placeholder.empty()
                
            except ValueError as ve:
                # Show user-friendly error message in Streamlit
                message_placeholder.warning(str(ve))
            except Exception as e:
                # Show other errors
                message_placeholder.error(f"An error occurred: {str(e)}")
    else:
        message_placeholder.error("Please fill in all fields to create the API.")
