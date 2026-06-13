from .utils import utils
from functions.flowCreation import flowCreation
import functions.fileWriting as fileWriting
createFlowObj = flowCreation()

utilsObj = utils()

class configCreation():
    """
    Class responsible for generating MuleSoft XML configuration definitions.
    """ 
    ################################################
    #########                              #########
    ######     Configuration declaration      ######
    #########                              #########
    ################################################

    def createRequestConfig(self,project_path: str, backendUrl: str,endpoint : str , backendType:str = "request") -> str:
        configName = f"HTTP_Request_configuration_{utilsObj.getBackendDetails(backendUrl, backendType).hostname}-config"
        xmlCode = f"""<http:request-config name="{configName}" doc:name="{configName}" doc:id="bc0d1f13-0adb-4527-a826-b5846877ea92" basePath="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["basePath"]}}}" responseTimeout="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["responseTimeout"]}}}" >
		<http:request-connection protocol="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["protocol"]}}}" host="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["hostname"]}}}" port="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["port"]}}}" usePersistentConnections="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["usePersistentConnections"]}}}" connectionIdleTimeout="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["connectionTimeout"]}}}" >
			<tls:context >
				<tls:trust-store insecure="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["insecure"]}}}" />
			</tls:context>
		</http:request-connection>
	</http:request-config>
        """
        fileWriting.insert_global_config(project_path, xmlCode, backendType)
        return 