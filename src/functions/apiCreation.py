from functions.flowCreation import flowCreation
from functions.config import ApiConfig
import functions.fileWriting as fileWriting
from functions.configCreation import configCreation
from functions.utils import utils

createFlowObj = flowCreation()
configCreationObj = configCreation()
utilsObj = utils()


class apiCreation():
    """
    MuleSoft API Creation Handler
    
    Handles the creation of MuleSoft APIs with configurable components.
    Uses ApiConfig for cleaner parameter management.
    """
    
    def createApi(self, api_config: ApiConfig) -> dict:
        """
        Create MuleSoft API with selectable components.
        
        Args:
            api_config (ApiConfig): Configuration object containing all API parameters
            
        Returns:
            dict: Status of each component
        """
        endpoint = api_config.endpoint
        projectPath = api_config.project_path
        backendUrl = api_config.backend.backend_url
        method = api_config.backend.method
        backendType = api_config.backend.backend_type
        existingBackend = api_config.backend.use_existing
        
        apiName = utilsObj.getPackageName(projectPath)
        
        # Initialize status dictionary
        status = {
            "main_flow": "Skipped",
            "impl_flow": "Skipped",
            "sys_flow": "Skipped",
            "global_config": "Skipped",
            "config_properties": "Skipped"
        }
        
        # Check if main flow already exists only if user wants to create it
        if api_config.components.main_flow and utilsObj.isExistingMainFlow(projectPath, endpoint):
            raise ValueError("⚠️ Main flow already exists for this endpoint. Please select a different endpoint or use 'Use Existing' option.")
        
        # CHECK if backend already exists BEFORE any creation
        backend_already_exists = utilsObj.isExistingBackend(projectPath, backendUrl, backendType)
        
        try:
            # Generate XML for selected components independently
            main_flow_xml = None
            impl_flow_xml = None
            sys_flow_xml = None
            backendConfigXml = None
            
            # Main Flow
            if api_config.components.main_flow:
                try:
                    main_flow_xml = createFlowObj.createMainFlow(apiName, endpoint)
                    status["main_flow"] = "Generated"
                except Exception as e:
                    raise ValueError(f"Error generating main flow: {e}")
            
            # Implementation Flow
            if api_config.components.impl_flow:
                try:
                    impl_flow_xml = createFlowObj.createImplFlow(endpoint, backendUrl, backendType)
                    status["impl_flow"] = "Generated"
                except Exception as e:
                    raise ValueError(f"Error generating implementation flow: {e}")
            
            # System Flow
            if api_config.components.system_flow:
                try:
                    sys_flow_xml = createFlowObj.createSystemFlow(endpoint, backendUrl, method, backendType)
                    status["sys_flow"] = "Generated"
                except Exception as e:
                    raise ValueError(f"Error generating system flow: {e}")
            
            # Global Config
            if api_config.components.global_config:
                if not existingBackend:
                    try:
                        backendConfigXml = configCreationObj.createRequestConfig(projectPath, backendUrl, endpoint, backendType)
                        if backendConfigXml is None:
                            # Existing backend was found
                            status["global_config"] = "Skipped (Already Exists)"
                        else:
                            status["global_config"] = "Generated"
                    except Exception as e:
                        raise ValueError(f"Error generating backend configuration: {e}")
                else:
                    status["global_config"] = "Skipped (Using Existing)"
            
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise Exception(f"Error generating component XML: {e}")

        try:
            # Write selected components to files independently
            errors = []
            
            if api_config.components.main_flow and main_flow_xml:
                try:
                    fileWriting.insert_flow_into_xml(projectPath, main_flow_xml, endpoint, backendUrl, "main", backendType)
                    status["main_flow"] = "Developed"
                except Exception as e:
                    errors.append(f"Main Flow: {str(e)}")
                    status["main_flow"] = "Failed"
            
            if api_config.components.impl_flow and impl_flow_xml:
                try:
                    fileWriting.insert_flow_into_xml(projectPath, impl_flow_xml, endpoint, backendUrl, "implementation", backendType)
                    status["impl_flow"] = "Developed"
                except Exception as e:
                    errors.append(f"Implementation Flow: {str(e)}")
                    status["impl_flow"] = "Failed"

            if api_config.components.system_flow and sys_flow_xml:
                try:
                    fileWriting.insert_flow_into_xml(projectPath, sys_flow_xml, endpoint, backendUrl, "system", backendType)
                    status["sys_flow"] = "Developed"
                except Exception as e:
                    errors.append(f"System Flow: {str(e)}")
                    status["sys_flow"] = "Failed"
            
            if api_config.components.global_config and backendConfigXml is not None:
                try:
                    fileWriting.insert_global_config(projectPath, backendConfigXml, backendType)
                    status["global_config"] = "Developed"
                except Exception as e:
                    errors.append(f"Global Config: {str(e)}")
                    status["global_config"] = "Failed"
            
            # If there were errors but some succeeded, report them
            if errors:
                error_summary = "\n".join(errors)
                print(f"⚠️ Some components failed:\n{error_summary}")
        
        except Exception as e:
            raise Exception(f"Error writing flows to files: {e}")
        
        # ============================================================================
        # SEPARATE LOGIC: Add properties to dev.properties (independent of global config)
        # ============================================================================
        # This runs regardless of whether global config was created or already existed
        try:
            if api_config.components.global_config:
                if api_config.components.config_properties:
                    backend_config_dict = {
                        "base_path": api_config.backend.base_path,
                        "connection_timeout": api_config.backend.connection_timeout,
                        "response_timeout": api_config.backend.response_timeout,
                        "use_persistent": api_config.backend.use_persistent_connections,
                        "insecure_tls": api_config.backend.insecure_tls,
                        "endpoint_path": endpoint,
                    }
                    
                    hostname = utilsObj.getBackendDetails(backendUrl, backendType).hostname
                    
                    # Use the STORED result from BEFORE creation
                    if backend_already_exists:
                        # Backend was ALREADY EXISTING → Add only path property
                        propNames = utilsObj.backendPropName(backendUrl, backendType, endpoint)
                        prop_result = configCreationObj.addNewPathInConfigProp(
                            projectPath, 
                            hostname, 
                            backendType,
                            propNames['path'],
                            endpoint
                        )
                        print(f"Path property result: {prop_result}")
                        if "already exists" in prop_result:
                            status["config_properties"] = "Skipped (Already Exists)"
                        elif "✅" in prop_result:
                            status["config_properties"] = "Developed"
                        else:
                            status["config_properties"] = "Failed"
                    else:
                        # Backend is NEW (we just created it) → Create complete configuration properties
                        props = configCreationObj.generateBackendProperties(
                            backendUrl, 
                            endpoint, 
                            backend_config_dict
                        )
                        prop_result = configCreationObj.addNewConfigProp(
                            projectPath,
                            hostname,
                            backendType,
                            props
                        )
                        print(f"Config properties result: {prop_result}")
                        if "already exists" in prop_result:
                            status["config_properties"] = "Skipped (Already Exists)"
                        elif "✅" in prop_result:
                            status["config_properties"] = "Developed"
                        else:
                            status["config_properties"] = "Failed"
                else:
                    # User disabled config properties
                    status["config_properties"] = "Skipped (User Disabled)"
        except Exception as prop_error:
            print(f"⚠️ Warning: Could not add properties to dev.properties: {str(prop_error)}")
            status["config_properties"] = "Failed"
        
        return status