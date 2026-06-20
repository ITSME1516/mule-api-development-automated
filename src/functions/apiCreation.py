"""
API Creation Handler Module
============================
Orchestrates the creation of MuleSoft APIs with configurable components.
Handles XML generation, file writing, and property file management.

Main Responsibilities:
- Validate API configuration
- Generate XML for selected components
- Write XML to project files
- Manage dev.properties file
- Track creation status for each component
- Provide comprehensive logging for debugging
"""

from functions.flowCreation import flowCreation
from functions.config import ApiConfig
import functions.fileWriting as fileWriting
from functions.configCreation import configCreation
from functions.utils import utils
from functions.logger_config import setup_logger
import logging

# Initialize module logger
logger = setup_logger(__name__)

# Create instances of helper classes
createFlowObj = flowCreation()
configCreationObj = configCreation()
utilsObj = utils()


class apiCreation():
    """
    MuleSoft API Creation Handler
    =============================
    Orchestrates the creation of MuleSoft APIs with configurable components.
    Uses ApiConfig for clean parameter management and provides comprehensive
    logging for tracking the entire creation process.
    
    Attributes:
        None (all methods are instance methods)
    
    Methods:
        createApi(api_config: ApiConfig) -> dict: Main method to create API
    """
    
    def createApi(self, api_config: ApiConfig) -> dict:
        """
        Create MuleSoft API with selectable components.
        
        This method orchestrates the entire API creation process:
        1. Validates inputs and checks for existing components
        2. Generates XML for selected components
        3. Writes XML to project files
        4. Manages dev.properties file and disable payload logger property
        5. Returns status of each component
        
        Args:
            api_config (ApiConfig): Configuration object containing:
                - endpoint: API endpoint path
                - project_path: Path to MuleSoft project
                - backend: Backend configuration (URL, method, timeouts, etc.)
                - components: Which components to create (flows, configs, etc.)
            
        Returns:
            dict: Status dictionary with keys:
                - main_flow: Status of main flow creation
                - impl_flow: Status of implementation flow
                - sys_flow: Status of system flow
                - global_config: Status of global config
                - config_properties: Status of config properties
            
        Raises:
            ValueError: If validation fails or component already exists
            Exception: If XML generation or file writing fails
        """
        logger.info("=" * 80)
        logger.info("STARTING API CREATION PROCESS")
        logger.info("=" * 80)
        
        # Extract configuration parameters for easier access
        endpoint = api_config.endpoint
        projectPath = api_config.project_path
        api_method = api_config.api_method
        backendUrl = api_config.backend.backend_url
        method = api_config.backend.method
        backendType = api_config.backend.backend_type
        existingBackend = api_config.backend.use_existing
        
        logger.debug(f"Configuration extracted: endpoint={endpoint}, project={projectPath}, api_method={api_method}, backend_url={backendUrl}, backend_method={method}")
        
        # Get API name from project path
        apiName = utilsObj.getPackageName(projectPath)
        logger.debug(f"API name derived from project path: {apiName}")
        
        # Initialize status dictionary for tracking each component with descriptive skip reasons
        status = {
            "main_flow": "Disabled" if not api_config.components.main_flow else "Not Started",
            "impl_flow": "Disabled" if not api_config.components.impl_flow else "Not Started",
            "sys_flow": "Disabled" if not api_config.components.system_flow else "Not Started",
            "global_config": "Disabled" if not api_config.components.global_config else "Not Started",
            "config_properties": "Disabled" if not api_config.components.config_properties else "Not Started"
        }
        logger.debug(f"Initialized status tracking: {status}")
        logger.info(f"User selected components - main_flow: {api_config.components.main_flow}, impl_flow: {api_config.components.impl_flow}, sys_flow: {api_config.components.system_flow}, global_config: {api_config.components.global_config}, config_properties: {api_config.components.config_properties}")
        
        # ====================================================================
        # PHASE 1: PRE-CREATION VALIDATION
        # ====================================================================
        logger.info("PHASE 1: Pre-creation validation")
        
        # Check if main flow already exists (only if user wants to create it)
        if api_config.components.main_flow:
            logger.info(f"Checking if main flow already exists for endpoint: {endpoint}")
            if utilsObj.isExistingMainFlow(projectPath, endpoint):
                error_msg = "⚠️ Main flow already exists for this endpoint. Please select a different endpoint or use 'Use Existing' option."
                logger.error(error_msg)
                raise ValueError(error_msg)
            logger.debug("Main flow does not already exist - safe to proceed")
        
        # Check if backend configuration already exists (BEFORE any creation)
        logger.info(f"Checking if backend already exists for URL: {backendUrl}")
        backend_already_exists = utilsObj.isExistingBackend(projectPath, backendUrl, backendType)
        logger.info(f"Backend already exists: {backend_already_exists}")
        
        try:
            # ================================================================
            # PHASE 2: XML GENERATION
            # ================================================================
            logger.info("PHASE 2: XML generation for selected components")
            
            # Initialize XML holders
            main_flow_xml = None
            impl_flow_xml = None
            sys_flow_xml = None
            backendConfigXml = None
            
            # Generate Main Flow XML if selected
            if api_config.components.main_flow:
                logger.info("Generating main flow XML...")
                try:
                    main_flow_xml = createFlowObj.createMainFlow(apiName, endpoint, api_method)
                    status["main_flow"] = "Generated"
                    logger.debug("Main flow XML generated successfully")
                except Exception as e:
                    error_msg = f"Error generating main flow: {e}"
                    logger.error(error_msg, exc_info=True)
                    raise ValueError(error_msg)
            
            # Generate Implementation Flow XML if selected
            if api_config.components.impl_flow:
                logger.info("Generating implementation flow XML...")
                try:
                    impl_flow_xml = createFlowObj.createImplFlow(endpoint, backendUrl, backendType)
                    status["impl_flow"] = "Generated"
                    logger.debug("Implementation flow XML generated successfully")
                except Exception as e:
                    error_msg = f"Error generating implementation flow: {e}"
                    logger.error(error_msg, exc_info=True)
                    raise ValueError(error_msg)
            
            # Generate System Flow XML if selected
            if api_config.components.system_flow:
                logger.info("Generating system flow XML...")
                try:
                    sys_flow_xml = createFlowObj.createSystemFlow(endpoint, backendUrl, method, backendType)
                    status["sys_flow"] = "Generated"
                    logger.debug("System flow XML generated successfully")
                except Exception as e:
                    error_msg = f"Error generating system flow: {e}"
                    logger.error(error_msg, exc_info=True)
                    raise ValueError(error_msg)
            
            # Generate Global Config XML if selected (CRITICAL: Only if explicitly enabled)
            if api_config.components.global_config:
                logger.info("Generating global config XML...")
                logger.info(f"useExistingBackend flag: {existingBackend}")
                
                if not existingBackend:
                    logger.info("Creating new backend configuration...")
                    try:
                        backendConfigXml = configCreationObj.createRequestConfig(projectPath, backendUrl, endpoint, backendType)
                        
                        if backendConfigXml is None:
                            # Backend already exists - don't create new one
                            status["global_config"] = "Exists"
                            logger.info("Backend config already exists - skipping generation")
                        else:
                            status["global_config"] = "Generated"
                            logger.debug("Global config XML generated successfully")
                    except Exception as e:
                        error_msg = f"Error generating backend configuration: {e}"
                        logger.error(error_msg, exc_info=True)
                        raise ValueError(error_msg)
                else:
                    # User selected to use existing backend
                    status["global_config"] = "Using Existing"
                    logger.info("Using existing backend - global config generation skipped")
            else:
                logger.info("Global config generation SKIPPED (user disabled this component)")
                status["global_config"] = "Disabled"
            
        except ValueError as ve:
            logger.error(f"ValueError during XML generation: {str(ve)}")
            raise ve
        except Exception as e:
            error_msg = f"Error generating component XML: {e}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
        
        try:
            # ================================================================
            # PHASE 3: FILE WRITING
            # ================================================================
            logger.info("PHASE 3: Writing generated components to files")
            
            errors = []
            
            # Write Main Flow to file if generated
            if api_config.components.main_flow and main_flow_xml:
                logger.info("Writing main flow to file...")
                try:
                    fileWriting.insert_flow_into_xml(projectPath, main_flow_xml, endpoint, backendUrl, "main", backendType)
                    status["main_flow"] = "Developed"
                    logger.info("Main flow successfully written to file")
                except Exception as e:
                    error_msg = f"Main Flow: {str(e)}"
                    errors.append(error_msg)
                    status["main_flow"] = "Failed"
                    logger.error(f"Failed to write main flow: {str(e)}", exc_info=True)
            
            # Write Implementation Flow to file if generated
            if api_config.components.impl_flow and impl_flow_xml:
                logger.info("Writing implementation flow to file...")
                try:
                    fileWriting.insert_flow_into_xml(projectPath, impl_flow_xml, endpoint, backendUrl, "implementation", backendType)
                    status["impl_flow"] = "Developed"
                    logger.info("Implementation flow successfully written to file")
                except Exception as e:
                    error_msg = f"Implementation Flow: {str(e)}"
                    errors.append(error_msg)
                    status["impl_flow"] = "Failed"
                    logger.error(f"Failed to write implementation flow: {str(e)}", exc_info=True)
            
            # Write System Flow to file if generated
            if api_config.components.system_flow and sys_flow_xml:
                logger.info("Writing system flow to file...")
                try:
                    fileWriting.insert_flow_into_xml(projectPath, sys_flow_xml, endpoint, backendUrl, "system", backendType)
                    status["sys_flow"] = "Developed"
                    logger.info("System flow successfully written to file")
                except Exception as e:
                    error_msg = f"System Flow: {str(e)}"
                    errors.append(error_msg)
                    status["sys_flow"] = "Failed"
                    logger.error(f"Failed to write system flow: {str(e)}", exc_info=True)
            
            # Write Global Config to file if generated (CRITICAL: Only if XML was generated)
            if api_config.components.global_config and backendConfigXml is not None:
                logger.info("Writing global config to file...")
                try:
                    fileWriting.insert_global_config(projectPath, backendConfigXml, backendType)
                    status["global_config"] = "Developed"
                    logger.info("Global config successfully written to file")
                except Exception as e:
                    error_msg = f"Global Config: {str(e)}"
                    errors.append(error_msg)
                    status["global_config"] = "Failed"
                    logger.error(f"Failed to write global config: {str(e)}", exc_info=True)
            elif api_config.components.global_config and backendConfigXml is None:
                logger.info("Skipping global config file write - backend configuration already exists")
            
            # Report any errors encountered
            if errors:
                error_summary = "\n".join(errors)
                logger.warning(f"⚠️ Some components failed during file writing:\n{error_summary}")
        
        except Exception as e:
            error_msg = f"Error writing flows to files: {e}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
        
        try:
            # ================================================================
            # PHASE 4: CONFIGURATION PROPERTIES MANAGEMENT
            # ================================================================
            logger.info("PHASE 4: Managing dev.properties file")
            
            # Add config properties and disable payload logger to dev.properties
            # These are only added when config_properties is enabled
            if api_config.components.config_properties:
                logger.info("Config properties enabled - adding properties to dev.properties")
                
                # First, add backend configuration properties (if global_config is enabled)
                if api_config.components.global_config:
                    logger.info("Adding backend configuration properties...")
                    
                    try:
                        # Prepare backend configuration dictionary
                        # Extract backend path from the backendUrl (not the API endpoint)
                        backend_path = utilsObj.getBackendDetails(backendUrl, backendType).path or "/"
                        
                        backend_config_dict = {
                            "base_path": api_config.backend.base_path,
                            "connection_timeout": api_config.backend.connection_timeout,
                            "response_timeout": api_config.backend.response_timeout,
                            "use_persistent": api_config.backend.use_persistent_connections,
                            "insecure_tls": api_config.backend.insecure_tls,
                            "endpoint_path": backend_path,
                        }
                        logger.debug(f"Backend config dict: {backend_config_dict}")
                        logger.info(f"Extracted backend path from URL: {backend_path}")
                        
                        hostname = utilsObj.getBackendDetails(backendUrl, backendType).hostname
                        logger.debug(f"Extracted hostname: {hostname}")
                        
                        # CRITICAL: Use the pre-creation check result, not re-checking now
                        if backend_already_exists:
                            # Backend was ALREADY EXISTING → Add only path property
                            logger.info("Backend already existed - adding only path property")
                            propNames = utilsObj.backendPropName(backendUrl, backendType, endpoint)
                            prop_result = configCreationObj.addNewPathInConfigProp(
                                projectPath, 
                                hostname, 
                                backendType,
                                propNames['path'],
                                endpoint
                            )
                            logger.debug(f"Path property result: {prop_result}")
                            
                            if "already exists" in prop_result:
                                status["config_properties"] = "Exists"
                                logger.info("Path property already exists - skipping")
                            elif "✅" in prop_result:
                                status["config_properties"] = "Developed"
                                logger.info("Path property added successfully")
                            else:
                                status["config_properties"] = "Failed"
                                logger.warning("Failed to add path property")
                        else:
                            # Backend is NEW (we just created it) → Create complete configuration properties
                            logger.info("Backend is new - generating complete configuration properties")
                            props = configCreationObj.generateBackendProperties(
                                backendUrl, 
                                endpoint, 
                                backend_config_dict
                            )
                            logger.debug(f"Generated properties:\n{props}")
                            
                            prop_result = configCreationObj.addNewConfigProp(
                                projectPath,
                                hostname,
                                backendType,
                                props
                            )
                            logger.debug(f"Config properties result: {prop_result}")
                            
                            if "already exists" in prop_result.lower():
                                status["config_properties"] = "Exists"
                                logger.info("Config properties already exist - skipping")
                            elif "✅" in prop_result:
                                status["config_properties"] = "Developed"
                                logger.info("Config properties added successfully")
                            elif "❌" in prop_result or "error" in prop_result.lower():
                                status["config_properties"] = "Failed"
                                logger.error(f"Failed to add config properties: {prop_result}")
                            else:
                                status["config_properties"] = "Failed"
                                logger.warning(f"Unexpected result adding config properties: {prop_result}")
                    except Exception as backend_prop_error:
                        logger.warning(f"Could not add backend properties: {str(backend_prop_error)}", exc_info=True)
                        status["config_properties"] = "Failed"
                else:
                    # Global config not enabled - cannot add backend properties because it's a dependency
                    # config_properties depends on global_config being created first
                    logger.info("Config properties - backend properties SKIPPED (global_config is disabled/not selected)")
                    logger.warning("⚠️ Config properties requires global_config to be enabled. To add configuration properties, you must also enable global config.")
                    status["config_properties"] = "Needs Global Config"
                
                # Second, add disable payload logger property (ALWAYS when config_properties is enabled)
                # This runs independently, even if backend properties fail
                logger.info("Adding disable payload logger property...")
                try:
                    propValue = "true" if api_config.backend.disable_payload_logs else "false"
                    logger.debug(f"Disable payload logs setting: {api_config.backend.disable_payload_logs} -> property value: {propValue}")
                    
                    disable_payload_result = utilsObj.addNewDisablePayloadProp(
                        projectPath,
                        endpoint,
                        propValue
                    )
                    logger.debug(f"Disable payload logger result: {disable_payload_result}")
                    
                    if "✅" in disable_payload_result:
                        logger.info(f"✅ Disable payload logger property added: {propValue}")
                    elif "already exists" in disable_payload_result.lower():
                        logger.info("Disable payload logger property already exists (keeping existing value)")
                    else:
                        logger.warning(f"Could not add disable payload logger property: {disable_payload_result}")
                except Exception as disable_payload_error:
                    logger.warning(f"Could not add disable payload logger property: {str(disable_payload_error)}", exc_info=True)
            else:
                # Config properties disabled - skip all property management
                # Also explain that disable_payload_logger depends on config_properties
                logger.info("Config properties SKIPPED (user disabled this component)")
                logger.info("Since config_properties is disabled, disable_payload_logger property will NOT be added (dependency)")
                status["config_properties"] = "Disabled"
                logger.warning("⚠️ Note: Disabling config_properties also prevents disable_payload_logger property from being added. If you want to manage payload logging, enable config_properties.")
                
        except Exception as prop_error:
            logger.error(f"Unexpected error in properties management: {str(prop_error)}", exc_info=True)
        # ====================================================================
        # SUMMARY AND COMPLETION
        # ====================================================================
        logger.info("=" * 80)
        logger.info("API CREATION PROCESS COMPLETED")
        logger.info(f"Final status: {status}")
        logger.info("=" * 80)
        
        return status