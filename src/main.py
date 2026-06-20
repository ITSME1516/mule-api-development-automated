"""
MuleSoft API Creator - Main Application
=============================================
A user-friendly interface for automated MuleSoft API development.
Provides Streamlit-based UI for configuring and creating MuleSoft APIs with
proper validation, logging, and error handling.

Main Responsibilities:
- Render UI components for API configuration
- Collect user input for project details, backend config, and component selection
- Validate user inputs with comprehensive checks
- Handle component interdependencies (e.g., config_properties requires global_config)
- Orchestrate API creation process
- Display progress and status messages to users
"""

import time
import logging
import streamlit as st
from functions.apiCreation import apiCreation
from functions.config import ApiConfig, BackendConfig, ComponentConfig
from functions.logger_config import setup_logger
from ui_helper import (
    setup_page_config,
    render_header,
    render_basic_info_section,
    render_backend_section,
    render_components_section,
    render_summary_section,
    render_success_message,
    render_error_message,
    render_info_message,
)

# Initialize logger for this module
logger = setup_logger(__name__)

# Page configuration
logger.info("Initializing Streamlit page configuration")
setup_page_config()

# Initialize session state for better UX persistence across reruns
if "api_created" not in st.session_state:
    logger.debug("Initializing session state - api_created flag")
    st.session_state.api_created = False

# Create API creator instance
logger.debug("Creating API creator instance")
api_creator = apiCreation()

# ============================================================================
# PAGE LAYOUT - Render UI Components
# ============================================================================
logger.info("Rendering page header and sections")

# Header
render_header()

# Create main form for all inputs
with st.form("api_creation_form", clear_on_submit=False):
    # Section 1: Basic Information (Project Path, API Endpoint, API Method)
    project_path, endpoint, api_method = render_basic_info_section()
    
    st.markdown("---")
    
    # Section 2: Backend Configuration (URL, Method, Timeouts, etc.)
    backend_config_data = render_backend_section()
    
    st.markdown("---")
    
    # Section 3: Components Selection (Which flows/configs to generate)
    components_data = render_components_section()
    
    st.markdown("---")
    
    # Create button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        create_button = st.form_submit_button(
            "🚀 Create API",
            use_container_width=True,
            type="primary"
        )

# ============================================================================
# FORM PROCESSING - Validation and API Creation
# ============================================================================

if create_button:
    logger.info("=== API CREATION PROCESS STARTED ===")
    
    # Debug: Log selected components for tracking
    selected_components = [k for k, v in components_data.items() if v and k != "config_properties"]
    logger.debug(f"User selected components: {selected_components}")
    
    # ========================================================================
    # INPUT VALIDATION LAYER
    # ========================================================================
    logger.info("Starting input validation")
    
    # Validate basic required fields
    if not project_path.strip() or not endpoint.strip() or not backend_config_data["backend_url"].strip():
        error_msg = "Please fill in all required fields: Project Path, API Endpoint, and Backend URL"
        logger.warning(f"Validation failed - missing required fields: project_path={bool(project_path.strip())}, endpoint={bool(endpoint.strip())}, backend_url={bool(backend_config_data['backend_url'].strip())}")
        render_error_message(error_msg)
    
    # Validate at least one component is selected
    elif not any([components_data.get("main_flow"), components_data.get("impl_flow"), 
                   components_data.get("system_flow"), components_data.get("global_config"),
                   components_data.get("config_properties")]):
        error_msg = "❌ Please select at least one component to develop:\n- Main Flow\n- Implementation Flow\n- System Flow\n- Global Config\n- Config Properties"
        logger.warning("Validation failed - no components selected")
        render_error_message(error_msg)
    
    else:
        logger.info("Basic validation passed")
        logger.info(f"User selected components: main_flow={components_data.get('main_flow')}, impl_flow={components_data.get('impl_flow')}, system_flow={components_data.get('system_flow')}, global_config={components_data.get('global_config')}, config_properties={components_data.get('config_properties')}")
        
        # ====================================================================
        # BUILD CONFIGURATION OBJECTS
        # ====================================================================
        logger.info("Building configuration objects from user input")
        
        backend_config = BackendConfig(
            backend_type=backend_config_data["backend_type"],
            backend_url=backend_config_data["backend_url"],
            method=backend_config_data["method"],
            base_path=backend_config_data["base_path"],
            connection_timeout=backend_config_data["connection_timeout"],
            response_timeout=backend_config_data["response_timeout"],
            insecure_tls=backend_config_data["insecure_tls"],
            use_persistent_connections=backend_config_data["use_persistent"],
            use_existing=backend_config_data["use_existing"],
            disable_payload_logs=backend_config_data["disable_payload_logs"],
        )
        logger.debug(f"Backend config created: {backend_config.to_dict()}")
        
        component_config = ComponentConfig(
            main_flow=components_data["main_flow"],
            impl_flow=components_data["impl_flow"],
            system_flow=components_data["system_flow"],
            global_config=components_data["global_config"],
            config_properties=components_data["config_properties"],
        )
        logger.debug(f"Component config created: {component_config.to_dict()}")
        
        api_config = ApiConfig(
            endpoint=endpoint,
            project_path=project_path,
            api_method=api_method,
            backend=backend_config,
            components=component_config,
        )
        logger.debug(f"API config created: {api_config.to_dict()}")
        
        # ====================================================================
        # FINAL CONFIGURATION VALIDATION
        # ====================================================================
        logger.info("Running final configuration validation")
        is_valid, error_msg = api_config.is_valid()
        
        if not is_valid:
            logger.error(f"Configuration validation failed: {error_msg}")
            render_error_message(error_msg)
        
        else:
            logger.info("Configuration validation passed - ready to create API")
            
            # Display configuration summary
            render_summary_section(api_config.to_dict())
            
            # ================================================================
            # API CREATION EXECUTION
            # ================================================================
            progress_placeholder = st.empty()
            message_placeholder = st.empty()
            
            with progress_placeholder.container():
                st.info("⏳ Processing your API creation request...")
            
            logger.info("Starting API creation process with configuration")
            
            try:
                # Call API creation with single config object
                status = api_creator.createApi(api_config)
                
                # Clear progress message
                progress_placeholder.empty()
                
                logger.info(f"API creation completed successfully. Status: {status}")
                
                # Display success message
                render_success_message(status)
                
                # Auto-close success message after 15 seconds
                time.sleep(15)
                progress_placeholder.empty()
                
                logger.info("=== API CREATION PROCESS COMPLETED SUCCESSFULLY ===")
                
            except ValueError as ve:
                progress_placeholder.empty()
                logger.error(f"Validation error during API creation: {str(ve)}")
                render_error_message(str(ve))
                
            except Exception as e:
                progress_placeholder.empty()
                logger.error(f"Unexpected error during API creation: {str(e)}", exc_info=True)
                render_error_message(f"An unexpected error occurred: {str(e)}")

# ============================================================================
# SIDEBAR INFORMATION
# ============================================================================

with st.sidebar:
    st.markdown("### 📚 About")
    st.markdown("""
    **MuleSoft API Creator** automates the generation of:
    - API flows (Main, Implementation, System)
    - Backend configurations
    - Global configurations
    
    This tool saves time and ensures consistency across your API projects.
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Quick Tips")
    st.markdown("""
    1. **Project Path**: Use absolute path to your Mule project
    2. **Endpoint**: Start with `/` (e.g., `/Services/resource`)
    3. **Backend URL**: Include protocol (http/https)
    4. **Components**: Select all needed components
    5. **Advanced Settings**: Only change if you know what you're doing
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔗 Resources")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 Documentation"):
            st.info("Documentation link would go here")
    with col2:
        if st.button("🐛 Report Issue"):
            st.info("Issue tracking link would go here")
