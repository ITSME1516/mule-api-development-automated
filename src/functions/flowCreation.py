"""
MuleSoft XML Flow Generation Module
====================================
Generates MuleSoft XML flow definitions for different flow types.
Each flow is customized based on API endpoint, backend configuration, and method.

Classes:
- flowCreation: Generates XML for main, implementation, and system flows
"""

from .utils import utils
from functions.logger_config import setup_logger

utilsObj = utils()
logger = setup_logger(__name__)


class flowCreation():
    """
    MuleSoft XML Flow Definition Generator
    ======================================
    Generates properly formatted MuleSoft XML flow definitions.
    Supports three types of flows: Main, Implementation, and System flows.
    
    Methods:
        createMainFlow(apiName, endpoint) -> str
        createImplFlow(endpoint, backendUrl, whichType) -> str
        createSystemFlow(endpoint, backendUrl, method, whichType) -> str
    """
    
    def createMainFlow(self, apiName: str, endpoint: str) -> str:
        """
        Generate MuleSoft Main Flow XML Definition
        =========================================
        Creates the main API flow that serves as the entry point for API requests.
        Includes logging for request/response with conditional payload masking.

        Parameters:
            apiName (str): The name of the API derived from project name (e.g., "flights-api")
            endpoint (str): The API endpoint path (e.g., "/a/b/c" or "/Services/resource")

        Returns:
            str: Formatted MuleSoft XML flow string containing:
                 - Flow name with endpoint and API name
                 - Start logger (logs incoming request)
                 - Flow reference to implementation flow
                 - End logger (logs outgoing response)
                 - Payload masking based on disable_payload_logs property

        Architecture:
            Main Flow (entry point)
                ↓
            Start Logger (request logging)
                ↓
            Implementation Flow Reference
                ↓
            End Logger (response logging)

        Example:
            >>> flowGen = flowCreation()
            >>> xml = flowGen.createMainFlow("flights-api", "/Services/flight-list")
            >>> # Returns XML with flow name: post:Services\\flight-list:application\\json:flights-api-config

        Note:
            - Flow names use backslashes for endpoint path conversion
            - Payload logging is controlled by disable_payload_logs property
            - Both loggers respect the disable.payload.logs property
        """
        logger.debug(f"Generating main flow: apiName={apiName}, endpoint={endpoint}")
        
        flowCode = f"""
    <flow name="post:{utilsObj.slashCheck(utilsObj.slashConverter(endpoint))}:application\\json:{apiName}-config">
        <logger level="INFO" doc:name="Start Main Process - {(endpoint)}" 
                doc:id="{utilsObj.createUuid()}" 
                message='#[%dw 2.0
output application/json
---
if (Mule::p("{utilsObj.disablePayloadProp(endpoint)}") default false) {{}} else payload]'/>
        
        <flow-ref doc:name="{utilsObj.implFlowName(endpoint)}" 
                    doc:id="{utilsObj.createUuid()}" 
                    name="{utilsObj.implFlowName(endpoint)}"/>
        
        <logger level="INFO" doc:name="End Main Process - {(endpoint)}" 
                doc:id="{utilsObj.createUuid()}" 
                message='#[%dw 2.0
output application/json
 ---
if (Mule::p("{utilsObj.disablePayloadProp(endpoint)}") default false) {{}} else payload]'/>
    </flow>
        """
        logger.debug("Main flow XML generated successfully")
        return flowCode
    
    def createImplFlow(self, endpoint: str, backendUrl: str, whichType: str) -> str:
        """
        Generate MuleSoft Implementation Flow XML Definition
        ==================================================
        Creates the implementation flow that processes the request/response.
        Handles payload transformation and flow orchestration.

        Parameters:
            endpoint (str): The API endpoint path (e.g., "/a/b/c")
            backendUrl (str): The backend service URL (e.g., "http://backend:8080/api")
            whichType (str): The type of backend ("request", "database", "soap")

        Returns:
            str: Formatted MuleSoft XML sub-flow containing:
                 - Sub-flow name with endpoint
                 - Request payload transformation (from DWL file)
                 - Reference to system flow
                 - Response transformation
                 - Status code variable extraction

        Architecture:
            Implementation Flow (sub-flow)
                ↓
            Request Transformation (dwl/endpoint)
                ↓
            System Flow Reference
                ↓
            Response Transformation
                ↓
            Status Code Variable

        Example:
            >>> xml = flowGen.createImplFlow("/api/resource", "http://backend:8080", "request")
            >>> # Creates sub-flow with transformations

        Note:
            - Uses external DWL files for transformations (dwl/endpoint)
            - Extracts status code from system flow response
            - Acts as middleware between main and system flows
        """
        logger.debug(f"Generating implementation flow: endpoint={endpoint}, backend_url={backendUrl}, type={whichType}")
        
        flowCode = f"""
    <sub-flow name="{utilsObj.implFlowName(endpoint)}">
        <ee:transform doc:name="Request Payload Transformation" doc:id="{utilsObj.createUuid()}" >
			<ee:message >
				<ee:set-payload resource="dwl/{endpoint}" />
			</ee:message>
		</ee:transform>
        <flow-ref doc:name="{utilsObj.sysFlowName(backendUrl, endpoint, whichType)}" doc:id="{utilsObj.createUuid()}" name="{utilsObj.sysFlowName(backendUrl, endpoint, whichType)}"/>
		<ee:transform doc:name="Response Status Code" doc:id="{utilsObj.createUuid()}" >
			<ee:message>
			</ee:message>
			<ee:variables >
				<ee:set-variable resource="dwl/common/statusCode.dwl" variableName="statusCode" />
			</ee:variables>
		</ee:transform>
    </sub-flow>
        """
        logger.debug("Implementation flow XML generated successfully")
        return flowCode

    def createSystemFlow(self, endpoint: str, backendUrl: str, method: str, whichType: str) -> str:
        """
        Generate MuleSoft System Flow XML Definition
        ==========================================
        Creates the system flow that communicates with backend service.
        Handles actual HTTP communication and logging.

        Parameters:
            endpoint (str): The API endpoint path (e.g., "/a/b/c")
            backendUrl (str): The URL of the backend service (e.g., "http://backend:8080")
            method (str): The HTTP method ("GET", "POST", "PUT", "DELETE")
            whichType (str): The type of backend ("request", "database", "soap")

        Returns:
            str: Formatted MuleSoft XML sub-flow containing:
                 - Sub-flow name with backend details
                 - Before-request logger
                 - HTTP request connector (auto-configured)
                 - After-response logger
                 - Payload logging for debugging

        Architecture:
            System Flow (sub-flow)
                ↓
            Before Request Logger
                ↓
            HTTP Request Connector
                ↓
            After Response Logger

        Example:
            >>> xml = flowGen.createSystemFlow("/api/users", "http://api.service:8080", "GET", "request")
            >>> # Creates system flow with HTTP GET connector

        Note:
            - HTTP connector is auto-configured by utilsObj.prepareHttpConnector()
            - Logs request details before sending and response after receiving
            - Uses backend URL path for logging messages
            - Essential for backend communication
        """
        logger.debug(f"Generating system flow: endpoint={endpoint}, backend_url={backendUrl}, method={method}, type={whichType}")
        
        flowCode = f"""
    <sub-flow name="{utilsObj.sysFlowName(backendUrl, endpoint, whichType)}" doc:name="System - Get All Customers" doc:id="2ece1ed8-83d3-4fc4-b820-c8297e2d3da7">
        <logger level="INFO" 
            message="Request to {utilsObj.sysLoggerMessage(backendUrl, whichType)}" 
            doc:name="Before Request"/>
        {utilsObj.prepareHttpConnector(backendUrl, endpoint, method)}
        <logger level="INFO" 
            message="Response from {utilsObj.sysLoggerMessage(backendUrl, whichType)}" 
            doc:name="After Request"/>
    </sub-flow>

        """
        logger.debug("System flow XML generated successfully")
        return flowCode