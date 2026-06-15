from functions.flowCreation import flowCreation
import functions.fileWriting as fileWriting
from functions.configCreation import configCreation
from functions.utils import utils

createFlowObj = flowCreation()
configCreationObj = configCreation()
utilsObj = utils()

class apiCreation():
    def createApi(self, endpoint: str, projectPath: str, backendUrl: str, method: str, backendType: str, existingBackend: bool = True):
        apiName = utilsObj.getPackageName(projectPath)
        if utilsObj.isExistingMainFlow(projectPath, endpoint):
            print("Main flow already exists. Skipping creation.")
            return

        try:
            main_flow_xml = createFlowObj.createMainFlow(apiName, endpoint)
            impl_flow_xml = createFlowObj.createImplFlow(endpoint, backendUrl, backendType)
            sys_flow_xml = createFlowObj.createSystemFlow(endpoint, backendUrl, method, backendType)
            backendConfigXml = None
            if not existingBackend:
                backendConfigXml = configCreationObj.createRequestConfig(projectPath, backendUrl, endpoint, backendType)
            else:
                print("Existing backend configuration found. Skipping creation.")
        except Exception as e:
            print(f"Error generating flow XML: {e}")
            return

        # Write the flow XML into the main XML file
        fileWriting.insert_flow_into_xml(projectPath, main_flow_xml, endpoint, backendUrl, "main", backendType)
        
        #Write the flow XML into the implementation XML file
        fileWriting.insert_flow_into_xml(projectPath, impl_flow_xml, endpoint, backendUrl, "implementation", backendType)

        #Write the flow XML into the system XML file
        fileWriting.insert_flow_into_xml(projectPath, sys_flow_xml, endpoint, backendUrl, "system", backendType)
        #Write the backend configuration XML into the global XML file
        if (not existingBackend) and (backendConfigXml is not None):
            fileWriting.insert_global_config(projectPath, backendConfigXml, backendType)