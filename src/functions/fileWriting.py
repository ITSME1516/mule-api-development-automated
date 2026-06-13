import os
from .utils import utils

utilsObj = utils()

def insert_flow_into_xml(project_path: str, flow_code: str,endpointUrl: str, insert_place: str) -> None:
    """
    Insert a MuleSoft flow block into an XML file just before the closing </mule> tag.

    Parameters:
        project_path (str): Path to the project directory.
        flow_code (str): The flow XML string to insert.
        endpointUrl (str): The URL of the endpoint.
        insert_place (str): The location where the flow should be inserted.[main/implementation/system]
    Returns:
        None. The file is updated in place.
    """
    projectName = os.path.basename(project_path)
    if insert_place == "main":
        filePath = os.path.join(project_path, "src", "main", "mule", f"{projectName}.xml")
    elif insert_place == "implementation":
        filePath = os.path.join(
            project_path,
            "src",
            "main",
            "mule",
            "implementation",
            f"{utilsObj.implFileName(endpointUrl)}",
        )
    else:
        raise ValueError("Invalid insert_place. Please choose 'main', 'implementation', or 'system'.")

    if insert_place == "implementation" and not os.path.exists(filePath):
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
        with open(filePath, "w", encoding="utf-8") as f:
            f.write(flow_code)
        print(f"New implementation file created and flow inserted into {filePath}")
        return 
    elif insert_place == "implementation" and os.path.exists(filePath): 
        print(f"Implementation file already exists. Inserting flow into {filePath}")
        return

    # Read the existing XML file
    with open(filePath, "r", encoding="utf-8") as f:
        content = f.read()

    # Ensure the file ends with </mule>
    if "</mule>" not in content:
        raise ValueError("The XML file does not contain a closing </mule> tag.")

    # Insert the flow code before </mule>
    updated_content = content.replace("</mule>", f"{flow_code}\n</mule>")

    # Write back to the file
    with open(filePath, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Main Flow successfully inserted into {filePath}")
