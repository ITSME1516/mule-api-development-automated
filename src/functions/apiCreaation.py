from functions.flowCreation import flowCreation
import functions.fileWriting as fileWriting

createFlowObj = flowCreation()
class apiCreation():
    def createApi(self, endpoint: str, projectPath: str):
        apiName = projectPath.split("\\")[-1]
        try:
            main_flow_xml = createFlowObj.createMainFlow(apiName, endpoint)
            impl_flow_xml = createFlowObj.createImplFlow(apiName, endpoint)
        except Exception as e:
            print(f"Error generating flow XML: {e}")
            return


        #Write the flow XML into the main XML file
        fileWriting.insert_flow_into_xml(projectPath, main_flow_xml, endpoint, "main")
        
        #Write the flow XML into the implementation XML file
        fileWriting.insert_flow_into_xml(projectPath, impl_flow_xml, endpoint, "implementation")
