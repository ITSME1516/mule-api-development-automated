from functions.flowCreation import flowCreation
import functions.fileWriting as fileWriting
from functions.configCreation import configCreation
from functions.utils import utils

createFlowObj = flowCreation()
configCreationObj = configCreation()
utilsObj = utils()

class apiCreation():
    def createApi(self, endpoint: str, projectPath: str, backendUrl: str, method: str, backendType: str, existingBackend: bool = True, 
                  create_main_flow: bool = True, create_impl_flow: bool = True, 
                  create_system_flow: bool = True, create_global_config: bool = True):
        """
        Create MuleSoft API with selectable components.
        
        Returns:
            dict: Status of each component
        """
        apiName = utilsObj.getPackageName(projectPath)
        
        # Check if main flow already exists - if yes, stop everything
        if utilsObj.isExistingMainFlow(projectPath, endpoint):
            raise ValueError("⚠️ Main flow already exists for this endpoint. No changes will be made.")
        
        # Initialize status dictionary
        status = {
            "main_flow": "Skipped",
            "impl_flow": "Skipped",
            "sys_flow": "Skipped",
            "global_config": "Skipped"
        }
        
        try:
            # Generate XML for selected components
            main_flow_xml = None
            impl_flow_xml = None
            sys_flow_xml = None
            backendConfigXml = None
            
            if create_main_flow:
                main_flow_xml = createFlowObj.createMainFlow(apiName, endpoint)
                status["main_flow"] = "Generated"
            
            if create_impl_flow:
                impl_flow_xml = createFlowObj.createImplFlow(endpoint, backendUrl, backendType)
                status["impl_flow"] = "Generated"
            
            if create_system_flow:
                sys_flow_xml = createFlowObj.createSystemFlow(endpoint, backendUrl, method, backendType)
                status["sys_flow"] = "Generated"
            
            if create_global_config and not existingBackend:
                backendConfigXml = configCreationObj.createRequestConfig(projectPath, backendUrl, endpoint, backendType)
                status["global_config"] = "Generated"
            elif create_global_config and existingBackend:
                status["global_config"] = "Skipped (Using Existing)"
            
        except Exception as e:
            raise Exception(f"Error generating flow XML: {e}")

        try:
            # Write selected components to files
            if create_main_flow and main_flow_xml:
                fileWriting.insert_flow_into_xml(projectPath, main_flow_xml, endpoint, backendUrl, "main", backendType)
                status["main_flow"] = "Developed"
            
            if create_impl_flow and impl_flow_xml:
                fileWriting.insert_flow_into_xml(projectPath, impl_flow_xml, endpoint, backendUrl, "implementation", backendType)
                status["impl_flow"] = "Developed"

            if create_system_flow and sys_flow_xml:
                fileWriting.insert_flow_into_xml(projectPath, sys_flow_xml, endpoint, backendUrl, "system", backendType)
                status["sys_flow"] = "Developed"
            
            if create_global_config and backendConfigXml is not None:
                fileWriting.insert_global_config(projectPath, backendConfigXml, backendType)
                status["global_config"] = "Developed"
        
        except Exception as e:
            raise Exception(f"Error writing flows to files: {e}")
        
        return status