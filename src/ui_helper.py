"""
UI Helper Module for Streamlit Interface
=========================================
Provides reusable UI components and templates for clean, consistent interface.
All components are designed following Streamlit best practices with proper styling
and user experience considerations.

Functions:
- setup_page_config(): Initialize page-wide settings
- render_header(): Display page title and description
- render_basic_info_section(): Collect project path and API endpoint
- render_backend_section(): Configure backend service details
- render_components_section(): Select components to generate
- render_summary_section(): Display configuration overview
- render_success_message(): Show success with results
- render_error_message(): Display error messages
- render_info_message(): Display informational messages
"""

import streamlit as st
from typing import Dict, Any
from functions.logger_config import setup_logger

logger = setup_logger(__name__)


def setup_page_config():
    """
    Configure Streamlit Page Settings
    =================================
    Sets up page-wide configuration including title, layout, and sidebar state.
    This function should be called before any other Streamlit commands.
    
    Configuration:
    - Page title: "MuleSoft API Creator"
    - Layout: Wide (uses more screen space)
    - Sidebar: Expanded by default
    - Icon: ⚙️ (gear emoji)
    """
    logger.debug("Setting up Streamlit page configuration")
    st.set_page_config(
        page_title="MuleSoft API Creator",
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def render_header():
    """
    Render Page Header
    ==================
    Displays the main page title and descriptive subtitle.
    Uses HTML styling for better appearance.
    """
    logger.debug("Rendering page header")
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1>⚙️ MuleSoft API Creator</h1>
        <p style='color: #666; font-size: 16px;'>
            Automated API Development for MuleSoft Integration Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


def render_basic_info_section() -> tuple[str, str, str]:
    """
    Render Basic Information Input Section
    ======================================
    Collects essential information: project path, API endpoint, and HTTP method.
    All fields are marked as required (*).
    
    Returns:
        tuple: (project_path: str, endpoint: str, method: str)
            - project_path: Absolute path to MuleSoft project
            - endpoint: API endpoint path (e.g., "/Services/resource")
            - method: HTTP method (GET, POST, PUT, DELETE)
    
    Validation Notes:
        - All fields are validated in main.py
        - Endpoint should start with /
        - Project path should be absolute
        - Method must be one of: GET, POST, PUT, DELETE
    """
    logger.debug("Rendering basic information section")
    st.subheader("📋 Basic Information")
    st.markdown("<span style='color: #d32f2f;'>* Required fields</span>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        project_path = st.text_input(
            "Project Path *",
            placeholder="C:/path/to/mule/project",
            help="Full path to your MuleSoft project directory (absolute path)"
        )
    
    with col2:
        endpoint = st.text_input(
            "API Endpoint *",
            placeholder="/Services/flight-service",
            help="API endpoint path (must start with /, e.g., /Services/resource-name)"
        )
    
    with col3:
        method = st.selectbox(
            "API Method *",
            ["GET", "POST", "PUT", "DELETE"],
            help="HTTP method for the API endpoint"
        )
    
    return project_path, endpoint, method


def render_backend_section() -> Dict[str, Any]:
    """
    Render Backend Configuration Input Section
    ==========================================
    Collects all backend service configuration including URL, method, timeouts,
    and advanced TLS/connection options.
    
    Returns:
        dict: Backend configuration with keys:
            - backend_type: str - "request", "database", or "soap"
            - backend_url: str - Full URL with protocol and port
            - method: str - HTTP method for backend communication (GET, POST, PUT, DELETE)
            - use_existing: bool - Use existing backend config
            - base_path: str - Base path for requests
            - connection_timeout: int - Timeout in milliseconds
            - response_timeout: int - Timeout in milliseconds
            - insecure_tls: bool - Skip SSL validation
            - use_persistent: bool - Use persistent connections
            - disable_payload_logs: bool - Security flag for payload masking
    
    Validation Notes:
        - Backend URL is required and validated
        - Timeouts must be >= 1000 ms
        - Method here is for backend HTTP requests (separate from API endpoint method)
        - All values are passed to BackendConfig dataclass
    """
    logger.debug("Rendering backend configuration section")
    st.subheader("🔗 Backend Configuration")
    st.markdown("<span style='color: #d32f2f;'>* Required field</span>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        backend_type_display = st.selectbox(
            "Backend Type",
            ["HTTP", "Database", "SOAP"],
            help="Type of backend service to integrate with"
        )
        # Convert display value to internal representation
        backend_type = "request" if backend_type_display == "HTTP" else backend_type_display
    
    with col2:
        method = st.selectbox(
            "Backend HTTP Method",
            ["GET", "POST", "PUT", "DELETE"],
            help="HTTP method used for API calls to backend service (separate from API endpoint method)"
        )
    
    with col3:
        use_existing = st.checkbox(
            "Use Existing Backend",
            value=False,
            help="✓ Check if you already have a backend configuration\n✗ Uncheck to create a new one"
        )
    
    backend_url = st.text_input(
        "Backend URL *",
        placeholder="http://backend-service:8080/api",
        help="Full URL of your backend service (include protocol http/https)"
    )
    
    st.info("💡 After global config is created, properties will be automatically added to dev.properties")
    
    # Advanced backend options (collapsible section)
    with st.expander("⚙️ Advanced Backend Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            base_path = st.text_input("Base Path", value="/*", placeholder="/api", help="Base path for backend requests")
            connection_timeout = st.number_input("Connection Timeout (ms)", value=60000, min_value=1000, help="Connection establishment timeout")
        
        with col2:
            response_timeout = st.number_input("Response Timeout (ms)", value=60000, min_value=1000, help="Response waiting timeout")
            insecure_tls = st.checkbox("Insecure TLS (Skip SSL Validation)", value=True, help="Allow self-signed certificates")
        
        use_persistent = st.checkbox("Use Persistent Connections", value=True, help="Reuse HTTP connections for better performance")
        disable_payload_logs = st.checkbox(
            "🔒 Disable Payload Logging",
            value=False,
            help="Security feature: When checked → disable.payload.logs=true, When unchecked → disable.payload.logs=false"
        )
    
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
        "disable_payload_logs": disable_payload_logs,
    }


def render_components_section() -> Dict[str, bool]:
    """
    Render Components Selection Section
    ==================================
    Allows user to select which API components to generate.
    User has complete freedom - select any combination and all selected
    components will be created.
    
    Returns:
        dict: Component selection flags with keys:
            - main_flow: bool - Create main API flow
            - impl_flow: bool - Create implementation flow
            - system_flow: bool - Create system flow
            - global_config: bool - Create global backend configuration
            - config_properties: bool - Add properties to dev.properties
    
    Component Descriptions:
        - Main Flow: Entry point for HTTP requests
        - Implementation Flow: Handles request/response transformations
        - System Flow: Backend service invocation
        - Global Config: Backend HTTP request configurations
        - Config Properties: Properties in dev.properties file
    
    Note:
        All selections are independent. Select whatever combination you want.
        At least one component must be selected to proceed.
    """
    logger.debug("Rendering components selection section")
    
    # Initialize session state for component selections (persists across reruns)
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
        main_flow = st.checkbox("✅ Main Flow", value=st.session_state.main_flow, key="cb_main_flow", help="HTTP Listener triggered flow - entry point for API")
        impl_flow = st.checkbox("✅ Implementation Flow", value=st.session_state.impl_flow, key="cb_impl_flow", help="Sub-flow handling request transformations")
        system_flow = st.checkbox("✅ System Flow", value=st.session_state.system_flow, key="cb_system_flow", help="Backend service invocation flow")
    
    with col2:
        st.markdown("#### Configuration")
        config_properties = st.checkbox("✅ Config Properties", value=st.session_state.config_properties, key="cb_config_properties", help="Add backend properties to dev.properties (requires Global Config)")
    
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
    Render Configuration Summary Section
    ===================================
    Displays the complete configuration that will be used for API creation.
    Presented as a collapsible section with JSON formatting.
    
    Args:
        config_dict (dict): Configuration dictionary from ApiConfig.to_dict()
            Contains: endpoint, project_path, backend config, components config
    
    Usage:
        Called after validation passes and before API creation starts.
        Allows users to review configuration before committing.
    """
    logger.debug("Rendering configuration summary section")
    with st.expander("📊 Configuration Summary", expanded=False):
        st.json(config_dict)


def render_success_message(status: Dict[str, str]):
    """
    Render Success Message with Creation Results
    ===========================================
    Displays success notification and component creation status.
    Shows which components were created, skipped, or failed.
    
    Args:
        status (dict): Component creation status with keys:
            - main_flow: str - Status message
            - impl_flow: str - Status message
            - sys_flow: str - Status message
            - global_config: str - Status message
            - config_properties: str - Status message
    
    Status Values:
        - "Developed": Successfully created
        - "Generated": XML generated (intermediate state)
        - "Skipped (Already Exists)": Component already exists
        - "Skipped (Using Existing)": User selected to use existing
        - "Skipped (User Disabled)": User disabled this component
        - "Failed": Error occurred during creation
    
    Display Logic:
        - Green success banner for all-succeeded case
        - Info banner for partial success
        - Results shown in expandable JSON section
    """
    logger.debug(f"Rendering success message with status: {status}")
    
    # Check if all components succeeded or just some
    # Valid outcomes: Developed, Exists, Using Existing, Disabled, Requires Config, etc.
    all_succeeded = all(
        s in ["Developed", "Generated", "Exists", "Using Existing", "Disabled", "Requires Config", "Not Started"]
        or not any(x in s for x in ["Failed"])  # Fail only if "Failed" is in the status
        for s in status.values()
    )
    
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
    
    # Display status as JSON for detailed review
    with st.expander("📊 Creation Results", expanded=True):
        st.json(status)
    
    st.markdown("---")
    st.success("Your API is now ready for integration. Check your project directory for the generated files.")


def render_error_message(message: str):
    """
    Render Error Message
    ===================
    Displays error notification to user.
    
    Args:
        message (str): Error message to display
    
    Example:
        >>> render_error_message("Backend URL is required")
    """
    logger.warning(f"Rendering error message: {message}")
    st.error(f"❌ {message}")


def render_info_message(message: str):
    """
    Render Informational Message
    ===========================
    Displays informational notification to user.
    Used for warnings, tips, or status updates.
    
    Args:
        message (str): Information message to display
    
    Example:
        >>> render_info_message("Global Config has been automatically enabled")
    """
    logger.debug(f"Rendering info message: {message}")
    st.info(f"ℹ️ {message}")
