import os
from .utils import utils

utilsObj = utils()

VALID_INSERT_PLACES = {"main", "implementation", "system", "globalConfig"}
CLOSING_TAG = "</mule>"


def _get_file_path(project_path: str, insert_place: str, endpoint_url: str, backend_url: str, backend_type: str) -> str:
    """
    Construct the file path based on insert location.
    
    Parameters:
        project_path (str): Path to the project directory.
        insert_place (str): The location where the flow should be inserted.
        endpoint_url (str): The URL of the endpoint.
        backend_url (str): The URL of the backend.
        backend_type (str): The type of the backend.
    
    Returns:
        str: The constructed file path.
    """
    project_name = os.path.basename(project_path)
    base_path = os.path.join(project_path, "src", "main", "mule")
    
    if insert_place == "main":
        return os.path.join(base_path, f"{project_name}.xml")
    elif insert_place == "implementation":
        return os.path.join(base_path, "implementation", utilsObj.implFileName(endpoint_url))
    elif insert_place == "system":
        return os.path.join(base_path, "system", utilsObj.sysFileName(backend_url, backend_type))
    elif insert_place == "globalConfig":
        return os.path.join(base_path, "common", "global-config.xml")


def _read_xml_file(file_path: str) -> str:
    """Read XML file and validate it contains closing tag."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if CLOSING_TAG not in content:
        raise ValueError("The XML file does not contain a closing </mule> tag.")
    
    return content


def _write_xml_file(file_path: str, content: str) -> None:
    """Write content to XML file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def _insert_flow_into_content(content: str, flow_code: str) -> str:
    """Insert flow code before closing tag."""
    return content.replace(CLOSING_TAG, f"{flow_code}\n{CLOSING_TAG}")


def _handle_new_file(file_path: str, flow_code: str, backend_type: str, location_type: str) -> None:
    """Create new file with default template and insert flow."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    content = utilsObj.defaultFile(backend_type, flow_code)
    _write_xml_file(file_path, content)
    print(f"New {location_type} file created and flow inserted into {file_path}")


def _handle_existing_file(file_path: str, flow_code: str, location_type: str) -> None:
    """Update existing file with new flow."""
    content = _read_xml_file(file_path)
    updated_content = _insert_flow_into_content(content, flow_code)
    _write_xml_file(file_path, updated_content)
    print(f"Flow successfully inserted into {file_path}")


def insert_flow_into_xml(project_path: str, flow_code: str, endpoint_url: str, backend_url: str, insert_place: str, backend_type: str) -> None:
    """
    Insert a MuleSoft flow block into an XML file just before the closing </mule> tag.

    Parameters:
        project_path (str): Path to the project directory.
        flow_code (str): The flow XML string to insert.
        endpoint_url (str): The URL of the endpoint.
        backend_url (str): The URL of the backend.
        insert_place (str): The location where the flow should be inserted [main/implementation/system].
        backend_type (str): The type of the backend.
    
    Returns:
        None. The file is updated in place.
    
    Raises:
        ValueError: If insert_place is invalid or XML file is malformed.
    """
    if insert_place not in VALID_INSERT_PLACES:
        raise ValueError(f"Invalid insert_place '{insert_place}'. Please choose from {VALID_INSERT_PLACES}.")
    
    file_path = _get_file_path(project_path, insert_place, endpoint_url, backend_url, backend_type)
    
    if os.path.exists(file_path):
        _handle_existing_file(file_path, flow_code, insert_place)
    else:
        _handle_new_file(file_path, flow_code, backend_type, insert_place)

#Write Global Configurations
def insert_global_config(project_path: str, flow_code: str, backend_type: str) -> None:
    file_path = _get_file_path(project_path, "globalConfig", "", "", backend_type)
    
    _handle_existing_file(file_path, flow_code, "globalConfig")
    
