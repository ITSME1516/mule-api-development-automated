import uuid
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

class utils:
    """
    Utility class for handling endpoint strings and logging properties.

    Methods:
        slashCheck(endpoint): Removes leading slash if present.
        slashConverter(endpoint): Converts forward slashes to backslashes.
        createUuid(): Generates a unique UUID string.
        joinPath(endpoint, separator): Joins last 3 parts of a path with a separator.
        disablePayloadProp(endpoint, separator): Builds a log property string.
    """

    def __init__(self):
        self.ns = {
            'http': 'http://www.mulesoft.org/schema/mule/http',
            'ee': 'http://www.mulesoft.org/schema/mule/ee/core',
            'mule': 'http://www.mulesoft.org/schema/mule/core'
        }

    ##############################################
    #########                            #########
    ######     Common Utility Methods      ######
    #########                            #########
    ##############################################

    # Get Package Name: Extract the last part of the endpoint path
    def getPackageName(self, projectPath: str) -> str:
        """
        Extract the last part of the project path.

        Parameters:
            projectPath (str): The path to the project directory.

        Returns:
            str: The last part of the project path.
        """
        return projectPath.split("\\")[-1]
    
    # Slash Check: Remove leading slash if present
    def slashCheck(self, endpoint: str) -> str:
        """
        Remove leading slash from the endpoint if it exists.

        Parameters:
            endpoint (str): The API endpoint string (e.g., "/a/b/c").

        Returns:
            str: Endpoint without leading slash.
        """
        if(endpoint.startswith("/")):
            return endpoint[1:]
        else:
            return endpoint
    
    # Slash Converter: Convert forward slashes to backslashes
    def slashConverter(self, endpoint: str) -> str:
        """
        Convert forward slashes to backslashes in the endpoint.

        Parameters:
            endpoint (str): The API endpoint string (e.g., "/a/b/c").

        Returns:
            str: Endpoint with backslashes (e.g., "\\a\\b\\c").
        """
        return endpoint.replace("/", "\\")

    # UUID Generation: Generate a unique identifier
    def createUuid(self) -> str:
        """
        Generate a random UUID string.

        Returns:
            str: A unique identifier (e.g., "123e4567-e89b-12d3-a456-426614174000").
        """
        return str(uuid.uuid4())

    # Join Path: Join last 3 parts of the endpoint with a separator
    def joinPath(self, endpoint: str, separator: str = ".") -> str:
        """
        Join the last 3 parts of the endpoint path using a separator.

        Parameters:
            endpoint (str): The API endpoint string (e.g., "/a/b/c/d/e").
            separator (str): The character to join with (default is ".").

        Returns:
            str: Joined path (e.g., "c.d.e").
        """
        endpointSplit= [p for p in endpoint.split("/")[-3:] if p] 
        return separator.join(endpointSplit)
    
    # Disable Payload Property: Build a log property string for disabling payload logs
    def disablePayloadProp(self, endpoint: str, separator: str = ".") -> str:
        """
        Build a log property string for disabling payload logs.

        Parameters:
            endpoint (str): The API endpoint string.
            separator (str): The character to join with (default is ".").

        Returns:
            str: Log property string (e.g., "a.f.disable.payload.logs").
        """
        result = self.joinPath(endpoint, separator)
        return result + ".disable.payload.logs"

    # Get Backend Details
    def getBackendDetails(self, backendURL, backendType):
        if(backendType == "request"):
            return urlparse(backendURL)
        else:
            raise ValueError("Define proper backend type")
            
    # Get backend endpoint for logger message
    def sysLoggerMessage(self, backendURL, backendType):
        if (backendType == "request"):
            return f"{urlparse(backendURL).path}"
        else:
            raise ValueError("Define proper backend type")
    
    # Find is the backend configuration is existing or new
    def isExistingBackend(self, projectPath: str, backendUrl: str, backendType: str) -> bool:
        """
        Determine if the backend configuration is existing or new.

        Parameters:
            projectPath (str): The path to the project directory.
            backendUrl (str): The backend URL (e.g., "http://backend-service/api").
            backendType (str): The type of the backend (e.g., "request").

        Returns:
            bool: True if existing, False if new.
        """
        if backendType == "request":
            with open(f"{projectPath}\\src\\main\\mule\\common\\global-config.xml", 'r') as file:
                content = file.read()
                data = ET.fromstring(content).findall("http:request-config", self.ns)
            httpRequestConfigNames = [config.get("name") for config in data]
            result = any([self.getBackendDetails(backendUrl, backendType).hostname in configName for configName in httpRequestConfigNames])
            return result
        else:
            raise ValueError("Define proper backend type")
    
    # Find the main flow existing or new
    def isExistingMainFlow(self, projectPath: str, endpoint: str) -> bool:
        """
        Check if a main flow already exists for the given endpoint.
        
        Parameters:
            projectPath (str): Path to the project
            endpoint (str): The endpoint to check
            
        Returns:
            bool: True if main flow exists, False otherwise
        """
        try:
            with open(f"{projectPath}\\src\\main\\mule\\{self.getPackageName(projectPath)}.xml", 'r') as file:
                content = file.read()
                data = ET.fromstring(content).findall("mule:flow", self.ns)
            
            flowNames = [flow.get("name") for flow in data]
            endpoint_pattern = self.slashConverter(endpoint)
            result = any([endpoint_pattern in flowName for flowName in flowNames])
            return result
        except Exception as e:
            print(f"Error checking for existing main flow: {e}")
            return False
        
    ##############################################
    #########                            #########
    ###### Flow Name & File Name Generation ######
    #########                            #########
    ##############################################

    # Implementation Flow Name: Generate a standardized implementation flow name
    def implFlowName(self, endpoint: str) -> str:
        """
        Generate a standardized implementation flow name for MuleSoft subflows.

        Parameters:
            endpoint (str): The API endpoint string (e.g., "/a/b/c/d/e").

        Returns:
            str: Flow name in the format "impl-x-y-z-subflow",
                 where x-y-z are the last three parts of the endpoint joined by "-".

        Example:
            >>> utilsObj = Utils()
            >>> utilsObj.implFlowName("/a/b/c/d/e")
            'impl-c-d-e-subflow'
        """
        return f"impl-{self.joinPath(endpoint, "-")}-subflow"
    
    # Implementation File Name: Generate a standardized implementation file name
    def implFileName(self, endpoint: str) -> str:
        """
        Generate a standardized implementation file name for MuleSoft subflows.

        Parameters:
            endpoint (str): The API endpoint string (e.g., "/a/b/c/d/e").

        Returns:
            str: Flow name in the format "impl-x-y-z-subflow",
                 where x-y-z are the last three parts of the endpoint joined by "-".

        Example:
            >>> utilsObj = Utils()
            >>> utilsObj.implFileName("/a/b/c/d/e")
            'impl-c-d-e-flows'
        """
        return f"impl-{self.joinPath(endpoint, "-")}-flows.xml"
                
    # System File Name: Generate a standardized system file name
    def sysFileName(self, backendUrl: str, backendType: str) -> str:
        return f"{self.getBackendDetails(backendUrl, backendType).hostname}-flows.xml"

    # System Flow Name: Generate a standardized system flow name
    def sysFlowName(self,backendUrl: str , endpoint: str, backendType: str) -> str:
        return f"{self.getBackendDetails(backendUrl, backendType).hostname}-api-{self.joinPath(endpoint, "-")}-subflow"
    

    ################################################
    #########                              #########
    ######      Connector Preparation         ######
    #########                              #########
    ################################################

    def prepareHttpConnector(self, backendUrl: str,endpoint: str, method: str = "POST", backendType: str = "request") -> str:
        """
        Prepare the HTTP connector configuration for MuleSoft.

        Parameters:
            backendUrl (str): The backend URL (e.g., "http://backend-service/api").
            endpoint (str): The API endpoint path (e.g., "/a/b/c").
            method (str): The HTTP method (default is "POST").
            backendType (str): The type of the backend (default is "request").

        Returns:
            str: A formatted MuleSoft HTTP connector configuration string.

        Example:
            >>> utilsObj = Utils()
            >>> config = utilsObj.prepareHttpConnector("http://backend-service/api")
            >>> print(config)
            <http:request-config name="http-request-config" ...>
                ...
            </http:request-config>
        """
        http_connector_config = f"""
        <http:request method="{method}" doc:name="Request to {self.sysLoggerMessage(backendUrl, backendType)}"  doc:id="{self.createUuid()}" config-ref="HTTP_Request_configuration_{self.getBackendDetails(backendUrl, 'request').hostname}-config" path='${{{self.backendPropName(backendUrl, 'request', endpoint).get('path')}}}' >
			<http:headers ><![CDATA[#[%dw 2.0
output application/json
---
{{}}]]]></http:headers>
		</http:request>
        """
        return http_connector_config
    
    ################################################
    #########                              #########
    ######      property name generation      ######
    #########                              #########
    ################################################

    def backendPropName(self, backendUrl: str, backendType: str, endpoint: str) -> dict:
        """
        Generate a standardized property name for backend configurations.

        Parameters:
            backendUrl (str): The backend URL (e.g., "http://backend-service/api").
            backendType (str): The type of property (e.g., "request").
            endpoint (str): The API endpoint path (e.g., "/a/b/c").

        Returns:
            dict: A dictionary of standardized property names.

        Example:
            >>> utilsObj = Utils()
            >>> propName = utilsObj.backendPropName("http://backend-service/api", "request", "/a/b/c")
            >>> print(propName)
            'backend-service-request-config'
        """
        result  = {
            "protocol": f"{self.getBackendDetails(backendUrl, backendType).hostname}.protocol",
            "hostname": f"{self.getBackendDetails(backendUrl, backendType).hostname}.hostname",
            "port": f"{self.getBackendDetails(backendUrl, backendType).hostname}.port",
            "basePath": f"{self.getBackendDetails(backendUrl, backendType).hostname}.basePath",
            "path": f"{self.getBackendDetails(backendUrl, backendType).hostname}.{self.joinPath(endpoint, '.')}.path",
            "connectionTimeout": f"{self.getBackendDetails(backendUrl, backendType).hostname}.connectionTimeout",
            "responseTimeout": f"{self.getBackendDetails(backendUrl, backendType).hostname}.responseTimeout",
            "usePersistentConnections": f"{self.getBackendDetails(backendUrl, backendType).hostname}.usePersistentConnections",
            "insecure": f"{self.getBackendDetails(backendUrl, backendType).hostname}.insecure",
        }
        return result
    


    ################################################
    #########                              #########
    ######            Default File            ######
    #########                              #########
    ################################################

    def defaultFile(self, backendType: str, flowCode: str) -> str:
        if backendType == "request":
            result = f"""<?xml version="1.0" encoding="UTF-8"?>
<mule xmlns:http="http://www.mulesoft.org/schema/mule/http" 
    xmlns:ee="http://www.mulesoft.org/schema/mule/ee/core" 
    xmlns="http://www.mulesoft.org/schema/mule/core" 
    xmlns:doc="http://www.mulesoft.org/schema/mule/documentation" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mulesoft.org/schema/mule/core http://www.mulesoft.org/schema/mule/core/current/mule.xsd
http://www.mulesoft.org/schema/mule/ee/core http://www.mulesoft.org/schema/mule/ee/core/current/mule-ee.xsd
http://www.mulesoft.org/schema/mule/http http://www.mulesoft.org/schema/mule/http/current/mule-http.xsd">
{flowCode}
</mule>
            """
            return result
        else:
            raise ValueError("Define proper backend type")
    