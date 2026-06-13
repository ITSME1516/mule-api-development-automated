from functions.flowCreation import flowCreation
import functions.fileWriting as fileWriting

createFlowObj = flowCreation()
class apiCreation():
    def createApi(self, endpoint: str, projectPath: str, backendUrl: str, method: str, whichType: str):
        apiName = projectPath.split("\\")[-1]
        try:
            main_flow_xml = createFlowObj.createMainFlow(apiName, endpoint)
            impl_flow_xml = createFlowObj.createImplFlow(endpoint, backendUrl, whichType)
            sys_flow_xml = createFlowObj.createSystemFlow(endpoint, backendUrl, method, whichType)
        except Exception as e:
            print(f"Error generating flow XML: {e}")
            return


        #Write the flow XML into the main XML file
        fileWriting.insert_flow_into_xml(projectPath, main_flow_xml, endpoint, backendUrl, "main", whichType)
        
        #Write the flow XML into the implementation XML file
        fileWriting.insert_flow_into_xml(projectPath, impl_flow_xml, endpoint, backendUrl, "implementation", whichType)

        #Write the flow XML into the system XML file
        fileWriting.insert_flow_into_xml(projectPath, sys_flow_xml, endpoint, backendUrl, "system", whichType)
        