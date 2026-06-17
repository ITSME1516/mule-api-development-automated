"""
UI Helper Module for Streamlit Interface
Provides reusable UI components and templates for a clean interface
"""

import streamlit as st
from typing import Dict, Any


def setup_page_config():
    """Configure page settings"""
    st.set_page_config(
        page_title="MuleSoft API Creator",
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def render_header():
    """Render page header"""
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1>⚙️ MuleSoft API Creator</h1>
        <p style='color: #666; font-size: 16px;'>
            Automated API Development for MuleSoft Integration Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


def render_basic_info_section() -> tuple[str, str]:
    """
    Render Basic Information Section
    
    Returns:
        tuple: (project_path, endpoint)
    """
    st.subheader("📋 Basic Information")
    st.markdown("<span style='color: #d32f2f;'>* Required fields</span>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_path = st.text_input(
            "Project Path *",
            placeholder="C:/path/to/mule/project",
            help="Full path to your MuleSoft project directory"
        )
    
    with col2:
        endpoint = st.text_input(
            "API Endpoint *",
            placeholder="/Services/flight-service",
            help="API endpoint path (e.g., /Services/resource-name)"
        )
    
    return project_path, endpoint


def render_backend_section() -> Dict[str, Any]:
    """
    Render Backend Configuration Section
    
    Returns:
        dict: Backend configuration parameters
    """
    st.subheader("🔗 Backend Configuration")
    st.markdown("<span style='color: #d32f2f;'>* Required field</span>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        backend_type_display = st.selectbox(
            "Backend Type",
            ["HTTP", "Database", "SOAP"],
            help="Type of backend service"
        )
        backend_type = "request" if backend_type_display == "HTTP" else backend_type_display
    
    with col2:
        method = st.selectbox(
            "HTTP Method",
            ["GET", "POST", "PUT", "DELETE"],
            help="HTTP method for API calls"
        )
    
    with col3:
        use_existing = st.checkbox(
            "Use Existing Backend",
            value=False,
            help="Check this if you already have a backend configuration. Uncheck to create a new one."
        )
    
    backend_url = st.text_input(
        "Backend URL *",
        placeholder="http://backend-service:8080/api",
        help="Base URL of your backend service"
    )
    
    st.info("💡 After global config is created, properties will be automatically added to dev.properties")
    
    # Advanced backend options (collapsible)
    with st.expander("⚙️ Advanced Backend Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            base_path = st.text_input("Base Path", value="/*", placeholder="/api")
            connection_timeout = st.number_input("Connection Timeout (ms)", value=60000, min_value=1000)
        
        with col2:
            response_timeout = st.number_input("Response Timeout (ms)", value=60000, min_value=1000)
            insecure_tls = st.checkbox("Insecure TLS (Skip SSL Validation)", value=True)
        
        use_persistent = st.checkbox("Use Persistent Connections", value=True)
    
    return {
        "backend_type": backend_type,
        "backend_url": backend_url,
        "method": method,
        "use_existing": use_existing,
        "base_path": base_path,
        "connection_timeout": connection_timeout,
        "response_timeout": response_timeout,
        "insecure_tls": insecure_tls,
        "use_persistent": use_persistent,
    }


def render_components_section() -> Dict[str, bool]:
    """
    Render Components Selection Section
    
    Returns:
        dict: Selected components
    """
    # Initialize session state for components
    if "main_flow" not in st.session_state:
        st.session_state.main_flow = True
    if "impl_flow" not in st.session_state:
        st.session_state.impl_flow = True
    if "system_flow" not in st.session_state:
        st.session_state.system_flow = True
    if "global_config" not in st.session_state:
        st.session_state.global_config = True
    if "config_properties" not in st.session_state:
        st.session_state.config_properties = True
    
    st.subheader("🔧 Components to Develop")
    st.markdown("Select which components you want to generate for your API:")
    st.warning("⚠️ Please select at least one component", icon="⚠️")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### Flows")
        main_flow = st.checkbox("✅ Main Flow", value=st.session_state.main_flow, key="cb_main_flow", help="HTTP Listener triggered flow")
        impl_flow = st.checkbox("✅ Implementation Flow", value=st.session_state.impl_flow, key="cb_impl_flow", help="Sub-flow handling request transformations")
        system_flow = st.checkbox("✅ System Flow", value=st.session_state.system_flow, key="cb_system_flow", help="Backend service invocation flow")
    
    with col2:
        st.markdown("#### Configuration Properties")
        config_properties = st.checkbox("✅ Config Properties", value=st.session_state.config_properties, key="cb_config_properties", help="Add backend properties to config.properties")
    
    with col3:
        st.markdown("#### Documentation")
        st.info("✓ API documentation is auto-generated from flow definitions")
    
    with col4:
        st.markdown("#### Global Config")
        global_config = st.checkbox("✅ Global Config", value=st.session_state.global_config, key="cb_global_config", help="Backend HTTP request configurations")
    
    return {
        "main_flow": main_flow,
        "impl_flow": impl_flow,
        "system_flow": system_flow,
        "global_config": global_config,
        "config_properties": config_properties,
    }


def render_summary_section(config_dict: Dict[str, Any]):
    """
    Render Configuration Summary
    
    Args:
        config_dict: Configuration dictionary
    """
    with st.expander("📊 Configuration Summary", expanded=False):
        st.json(config_dict)


def render_success_message(status: Dict[str, str]):
    """
    Render success message with component status as JSON
    
    Args:
        status: Component creation status dictionary
    """
    # st.markdown("---")
    
    # Check if all components succeeded or just some
    all_succeeded = all(s in ["Developed", "Skipped (Using Existing)", "Skipped (Already Exists)"] for s in status.values())
    
    if all_succeeded:
        st.markdown(
            "<h2 style='text-align: center; color: #28a745;'>✅ API Created Successfully!</h2>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<h2 style='text-align: center; color: #28a745;'>✅ API Creation Completed</h2>",
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Display status as JSON
    with st.expander("📊 Creation Results", expanded=True):
        st.json(status)
    
    st.markdown("---")
    st.success("Your API is now ready for integration. Check your project directory for the generated files.")


def render_error_message(message: str):
    """
    Render error message
    
    Args:
        message: Error message to display
    """
    st.error(f"❌ {message}")


def render_info_message(message: str):
    """
    Render info message
    
    Args:
        message: Info message to display
    """
    st.info(f"ℹ️ {message}")
