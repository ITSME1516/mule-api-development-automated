from .utils import utils
from functions.flowCreation import flowCreation
import os
import re

createFlowObj = flowCreation()

utilsObj = utils()

class configCreation():
    """
    Class responsible for generating MuleSoft XML configuration definitions
    and managing dev.properties file entries.
    """ 
    ################################################
    #########                              #########
    ######     Configuration declaration      ######
    #########                              #########
    ################################################

    def createRequestConfig(self,project_path: str, backendUrl: str,endpoint : str , backendType:str = "request") -> str:
        if utilsObj.isExistingBackend(project_path, backendUrl, backendType):
            print("Existing backend configuration found. Skipping creation.")
            return None
        else:
            configName = f"HTTP_Request_configuration_{utilsObj.getBackendDetails(backendUrl, backendType).hostname}-config"
            xmlCode = f"""
    <http:request-config name="{configName}" doc:name="{configName}" doc:id="bc0d1f13-0adb-4527-a826-b5846877ea92" basePath="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["basePath"]}}}" responseTimeout="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["responseTimeout"]}}}" >
        <http:request-connection protocol="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["protocol"]}}}" host="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["hostname"]}}}" port="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["port"]}}}" usePersistentConnections="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["usePersistentConnections"]}}}" connectionIdleTimeout="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["connectionTimeout"]}}}" >
            <tls:context >
                <tls:trust-store insecure="${{{utilsObj.backendPropName(backendUrl, backendType, endpoint)["insecure"]}}}" />
            </tls:context>
        </http:request-connection>
    </http:request-config>
            """
            return xmlCode
    
    ################################################
    #########                              #########
    ######     Properties File Management     ######
    #########                              #########
    ################################################
    
    def addNewPathInConfigProp(self, path: str, backendHost: str, backendType: str, propKey: str, propValue: str) -> str:
        """
        Add a new path property to dev.properties if backend config already exists.
        
        Parameters:
            path (str): Path to the project directory
            backendHost (str): Backend hostname
            backendType (str): Type of backend ("request", "database", etc.)
            propKey (str): Property key (e.g., "hostname.endpoint.path")
            propValue (str): Property value (e.g., "/api/v1/users")
            
        Returns:
            str: Status message
        """
        try:
            # Remove trailing backslash/slash if present
            path = path.rstrip("\\").rstrip("/")
            
            # Standard MuleSoft project structure
            prop_file = os.path.join(path, "src", "main", "resources", "config", "dev", "config.properties")
            
            if not os.path.exists(prop_file):
                return f"❌ dev.properties file not found at: {prop_file}"
            
            with open(prop_file, "r", encoding="utf-8") as f:
                content = f.read()

            if backendType == "request":
                # Check if property key already exists in file
                if re.search(fr"^{re.escape(propKey)}=", content, re.MULTILINE):
                    return f"⚠️ Property already exists: {propKey}"
                
                # Find the last path line for this backend
                matches = re.findall(fr"{backendHost}\..*\.path=.*\n", content)
                if not matches:
                    return "No existing paths found for this backend"

                lastPath = matches[-1]
                indexToStart = content.find(lastPath) + len(lastPath)

                # Insert new property right after the last .path line
                content = content[:indexToStart] + f"{propKey}={propValue}\n" + content[indexToStart:]
                
                with open(prop_file, "w", encoding="utf-8") as f:
                    f.write(content)
                
                return "✅ Path property added successfully"
            else:
                raise ValueError(f"Invalid backend type: {backendType}")
                
        except Exception as e:
            return f"❌ Error adding path property: {str(e)}"

    def addNewConfigProp(self, path: str, backendHost: str, backendType: str, properties: str) -> str:
        """
        Add new configuration properties to dev.properties file.
        
        Parameters:
            path (str): Path to the project directory
            backendHost (str): Backend hostname
            backendType (str): Type of backend ("request", "database", etc.)
            properties (str): Configuration properties to add
            
        Returns:
            str: Status message
        """
        try:
            # Remove trailing backslash/slash if present
            path = path.rstrip("\\").rstrip("/")
            
            # Standard MuleSoft project structure
            prop_file = os.path.join(path, "src", "main", "resources", "config", "dev", "config.properties")
            
            if not os.path.exists(prop_file):
                return f"❌ dev.properties file not found at: {prop_file}"

            if backendType == "request":
                with open(prop_file, "r+", encoding="utf-8") as f:
                    content = f.read()
                    
                    # Extract property keys from the new properties to check for duplicates
                    prop_keys = re.findall(r"^([^=\n#]+)=", properties, re.MULTILINE)
                    
                    # Check if any property already exists
                    existing_keys = []
                    for key in prop_keys:
                        if re.search(fr"^{re.escape(key)}=", content, re.MULTILINE):
                            existing_keys.append(key)
                    
                    if existing_keys:
                        return f"⚠️ Properties already exist: {', '.join(existing_keys)}"

                    # Find the last header (e.g., "#SYS-MOBILE-API PROPERTIES")
                    headers = re.findall(r"#.*PROPERTIES", content)
                    if not headers:
                        raise ValueError("No PROPERTIES header found in dev.properties")

                    last_header = headers[-1]
                    header_index = content.find(last_header)

                    # From that header onward, look for a blank line separator
                    after_header = content[header_index:]
                    match = re.search(r"\n\s*\n", after_header)

                    if match:
                        # Found a separator → insert before it
                        insert_pos = header_index + match.start() + 1
                        finalContent = content[:insert_pos] + properties + content[insert_pos:]
                    else:
                        # No separator → append at end of file
                        finalContent = content.rstrip() + "\n" + properties + "\n"

                # Write back to file
                with open(prop_file, "w", encoding="utf-8") as f:
                    f.write(finalContent)

                return "✅ Configuration properties added successfully"
            else:
                raise ValueError(f"Invalid backend type: {backendType}")
                
        except Exception as e:
            return f"❌ Error adding config properties: {str(e)}"
    
    def generateBackendProperties(self, backendUrl: str, endpoint: str, backendConfig: dict) -> str:
        """
        Generate property entries for dev.properties based on backend configuration.
        
        Parameters:
            backendUrl (str): Backend URL
            endpoint (str): API endpoint
            backendConfig (dict): Backend configuration with values from UI
            
        Returns:
            str: Formatted property string to add to dev.properties
        """
        backendType = "request"
        propNames = utilsObj.backendPropName(backendUrl, backendType, endpoint)
        hostname = utilsObj.getBackendDetails(backendUrl, backendType).hostname
        
        # Extract backend details from URL
        parsed = utilsObj.getBackendDetails(backendUrl, backendType)
        protocol = parsed.scheme or "https"
        port = parsed.port or ("443" if protocol == "https" else "8081")
        basePath = parsed.path or "/"
        
        # Build properties string with user-provided values or defaults
        properties = f"""\n# {hostname.upper()} PROPERTIES
{propNames['protocol']}={protocol}
{propNames['hostname']}={parsed.hostname}
{propNames['port']}={port}
{propNames['basePath']}={backendConfig.get('base_path', basePath)}
{propNames['path']}={backendConfig.get('endpoint_path', '/api')}
{propNames['connectionTimeout']}={backendConfig.get('connection_timeout', 60000)}
{propNames['responseTimeout']}={backendConfig.get('response_timeout', 60000)}
{propNames['usePersistentConnections']}={str(backendConfig.get('use_persistent', True)).lower()}
{propNames['insecure']}={str(backendConfig.get('insecure_tls', True)).lower()}
"""
        return properties