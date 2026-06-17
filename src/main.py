"""
MuleSoft API Creator - Main Application
A user-friendly interface for automated MuleSoft API development
"""

import time
import streamlit as st
from functions.apiCreation import apiCreation
from functions.config import ApiConfig, BackendConfig, ComponentConfig
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

# Page configuration
setup_page_config()

# Initialize session state for better UX
if "api_created" not in st.session_state:
    st.session_state.api_created = False

# Create API object
api_creator = apiCreation()

# ============================================================================
# PAGE LAYOUT
# ============================================================================

# Header
render_header()

# Create main form for all inputs
with st.form("api_creation_form", clear_on_submit=False):
    # Section 1: Basic Information
    project_path, endpoint = render_basic_info_section()
    
    st.markdown("---")
    
    # Section 2: Backend Configuration
    backend_config_data = render_backend_section()
    
    st.markdown("---")
    
    # Section 3: Components Selection
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
# FORM PROCESSING
# ============================================================================

if create_button:
    # Debug: Check what components are selected
    selected_components = [k for k, v in components_data.items() if v and k != "config_properties"]
    
    # Validate that at least one field is filled
    if not project_path.strip() or not endpoint.strip() or not backend_config_data["backend_url"].strip():
        render_error_message("Please fill in all required fields: Project Path, API Endpoint, and Backend URL")
    elif not any([components_data.get("main_flow"), components_data.get("impl_flow"), components_data.get("system_flow"), components_data.get("global_config"), components_data.get("config_properties")]):
        render_error_message("❌ Please select at least one component to develop:\n- Main Flow\n- Implementation Flow\n- System Flow\n- Global Config\n- Config Properties")
    else:
        # Auto-enable Global Config if Config Properties is selected
        if components_data.get("config_properties") and not components_data.get("global_config"):
            components_data["global_config"] = True
            render_info_message("ℹ️ Global Config has been automatically enabled (required for Config Properties)")
        
        # Create configuration objects
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
        )
        
        component_config = ComponentConfig(
            main_flow=components_data["main_flow"],
            impl_flow=components_data["impl_flow"],
            system_flow=components_data["system_flow"],
            global_config=components_data["global_config"],
            config_properties=components_data["config_properties"],
        )
        
        api_config = ApiConfig(
            endpoint=endpoint,
            project_path=project_path,
            backend=backend_config,
            components=component_config,
        )
        
        # Validate configuration
        is_valid, error_msg = api_config.is_valid()
        
        if not is_valid:
            render_error_message(error_msg)
        else:
            # Display configuration summary
            render_summary_section(api_config.to_dict())
            
            # Process API creation
            # st.markdown("---")
            progress_placeholder = st.empty()
            message_placeholder = st.empty()
            
            with progress_placeholder.container():
                st.info("⏳ Processing your API creation request...")
            
            try:
                # Call API creation with single config object
                status = api_creator.createApi(api_config)
                
                # Clear progress message
                progress_placeholder.empty()
                
                # Display success message
                render_success_message(status)
                
                # Auto-close success message after 15 seconds
                time.sleep(15)
                progress_placeholder.empty()
                
            except ValueError as ve:
                progress_placeholder.empty()
                render_error_message(str(ve))
            except Exception as e:
                progress_placeholder.empty()
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
