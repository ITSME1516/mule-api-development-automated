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
    
    def createImplFlow(self, apiName: str, endpoint: str) -> str:
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
<mule xmlns:ee="http://www.mulesoft.org/schema/mule/ee/core" xmlns="http://www.mulesoft.org/schema/mule/core"
xmlns:doc="http://www.mulesoft.org/schema/mule/documentation"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mulesoft.org/schema/mule/core http://www.mulesoft.org/schema/mule/core/current/mule.xsd
http://www.mulesoft.org/schema/mule/ee/core http://www.mulesoft.org/schema/mule/ee/core/current/mule-ee.xsd">
    <sub-flow name="{utilsObj.implFlowName(endpoint)}">
        <ee:transform doc:name="Request Payload Transformation" doc:id="{utilsObj.createUuid()}" >
			<ee:message >
				<ee:set-payload ><![CDATA[%dw 2.0
output application/json
---
payload
]]></ee:set-payload>
			</ee:message>
		</ee:transform>
    </sub-flow>
</mule>
        """
        return flowCode
