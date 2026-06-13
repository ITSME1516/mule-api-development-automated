from .utils import utils
utilsObj = utils()

class flowCreation():
    """
    Class responsible for generating MuleSoft XML flow definitions.
    """
    def createMainFlow(self, apiName: str, endpoint: str) -> str:
        """
        Create a MuleSoft XML flow definition for a given API.

        Parameters:
            apiName (str): The name of the API (e.g., "flights-api").
            endpoint (str): The API endpoint path (e.g., "/a/b/c").

        Returns:
            str: A formatted MuleSoft XML flow string containing:
                 - Flow name
                 - Start and end loggers
                 - Flow reference subflow
                 - Payload logging configuration

        Example:
            >>> flowGen = flowCreation()
            >>> xml = flowGen.createMainFlow("flights-api", "/a/b/c")
            >>> print(xml)
            <flow name="post:a\\b\\c:application\\json:flights-api-config">
                ...
            </flow>
        """
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
        return flowCode
    
    def createImplFlow(self, endpoint: str, backendUrl: str, whichType: str) -> str:
        """
        Create a MuleSoft XML flow definition for a given API.

        Parameters:
            apiName (str): The name of the API (e.g., "flights-api").
            endpoint (str): The API endpoint path (e.g., "/a/b/c").

        Returns:
            str: A formatted MuleSoft XML flow string containing:
                 - Flow name
                 - Start and end loggers
                 - Flow reference subflow
                 - Payload logging configuration

        Example:
            >>> flowGen = flowCreation()
            >>> xml = flowGen.createMainFlow("flights-api", "/a/b/c")
            >>> print(xml)
            <flow name="post:a\\b\\c:application\\json:flights-api-config">
                ...
            </flow>
        """
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
        return flowCode

    def createSystemFlow(self, endpoint: str, backendUrl: str, method: str , whichType: str) -> str:
        """
        Create a MuleSoft XML system flow definition for a given API.

        Parameters:
            apiName (str): The name of the API (e.g., "flights-api").
            endpoint (str): The API endpoint path (e.g., "/a/b/c").
            backendUrl (str): The URL of the backend service.
            method (str): The HTTP method for the request.
            whichType (str): The type of the system flow.

        Returns:
            str: A formatted MuleSoft XML flow string containing:
                 - Flow name
                 - Start and end loggers
                 - Flow reference subflow
                 - Payload logging configuration

        Example:
            >>> flowGen = flowCreation()
            >>> xml = flowGen.createSystemFlow("flights-api", "/a/b/c")
            >>> print(xml)
            <flow name="post:a\\b\\c:application\\json:flights-api-config">
                ...
            </flow>
        """
        
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
        return flowCode