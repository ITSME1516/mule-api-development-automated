"""
Configuration Classes Module
=============================
Defines dataclasses for managing API creation configuration parameters.
Provides clean, structured way to pass configuration throughout the application.

Classes:
- BackendConfig: Backend service configuration
- ComponentConfig: Component selection flags
- ApiConfig: Complete API configuration
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class BackendConfig:
    """
    Encapsulates Backend Configuration Parameters
    =============================================
    Stores all backend-related settings for API integration.
    
    Attributes:
        backend_type (str): Type of backend - "request", "database", "soap"
        backend_url (str): Base URL of the backend service (e.g., "http://api.example.com:8080/path")
        method (str): HTTP method - "GET", "POST", "PUT", "DELETE"
        base_path (str): Base path for requests (default: "/*")
        connection_timeout (int): Connection timeout in milliseconds (default: 60000)
        response_timeout (int): Response timeout in milliseconds (default: 60000)
        insecure_tls (bool): Allow insecure TLS certificates (default: True)
        use_persistent_connections (bool): Use persistent HTTP connections (default: True)
        use_existing (bool): Use existing backend config instead of creating new (default: True)
        disable_payload_logs (bool): Disable payload logging for security (default: False)
    """
    backend_type: str  # "request", "database", "soap"
    backend_url: str
    method: str  # GET, POST, PUT, DELETE
    base_path: str = "/*"
    connection_timeout: int = 60000
    response_timeout: int = 60000
    insecure_tls: bool = True
    use_persistent_connections: bool = True
    use_existing: bool = True
    disable_payload_logs: bool = False

    def to_dict(self) -> dict:
        """
        Convert BackendConfig to dictionary for logging and serialization.
        
        Returns:
            dict: Dictionary representation of backend configuration
        """
        return asdict(self)


@dataclass
class ComponentConfig:
    """
    Encapsulates Component Selection Flags
    ======================================
    Tracks which components (flows, configs) should be created.
    User has complete control - whatever is selected will be created.
    
    Attributes:
        main_flow (bool): Create main API flow (default: True)
        impl_flow (bool): Create implementation flow (default: True)
        system_flow (bool): Create system flow (default: True)
        global_config (bool): Create global backend configuration (default: True)
        config_properties (bool): Add properties to dev.properties file (default: True)
    
    Note:
        All selections are independent. User can select any combination.
        The API creation process will handle each component based on what's selected.
        No automatic disabling or enabling of components occurs.
    """
    main_flow: bool = True
    impl_flow: bool = True
    system_flow: bool = True
    global_config: bool = True
    config_properties: bool = True

    def to_dict(self) -> dict:
        """
        Convert ComponentConfig to dictionary for logging and serialization.
        
        Returns:
            dict: Dictionary representation of component configuration
        """
        return asdict(self)

    def has_any_selected(self) -> bool:
        """
        Check if at least one component is selected for creation.
        
        Returns:
            bool: True if any component is selected, False otherwise
        """
        return any([self.main_flow, self.impl_flow, self.system_flow, self.global_config, self.config_properties])


@dataclass
class ApiConfig:
    """
    Complete API Configuration Container
    ====================================
    Consolidates all parameters needed for API creation into a single object,
    making function calls cleaner and more maintainable. This is passed to the
    apiCreation.createApi() method.
    
    Attributes:
        endpoint (str): API endpoint path (e.g., "/Services/flight-service")
        project_path (str): Absolute path to MuleSoft project
        backend (BackendConfig): Backend service configuration
        components (ComponentConfig): Components to create
    
    Example:
        >>> backend = BackendConfig(backend_type="request", backend_url="http://api.service:8080")
        >>> components = ComponentConfig(main_flow=True, impl_flow=True)
        >>> config = ApiConfig(
        ...     endpoint="/api/resource",
        ...     project_path="C:/mule/projects/my-api",
        ...     backend=backend,
        ...     components=components
        ... )
    """
    # Required parameters
    endpoint: str
    project_path: str
    
    # Backend configuration
    backend: BackendConfig
    
    # Components to develop
    components: ComponentConfig

    def to_dict(self) -> dict:
        """
        Convert ApiConfig to dictionary for logging and display.
        Useful for debugging and displaying configuration to users.
        
        Returns:
            dict: Complete configuration as nested dictionary
        """
        return {
            "endpoint": self.endpoint,
            "project_path": self.project_path,
            "backend": self.backend.to_dict(),
            "components": self.components.to_dict(),
        }

    def is_valid(self) -> tuple[bool, str]:
        """
        Validate configuration with comprehensive checks.
        
        Validates:
        - Endpoint is not empty
        - Project path is not empty
        - Backend URL is not empty
        - At least one component is selected
        
        Returns:
            tuple: (is_valid: bool, error_message: str)
                - If valid: (True, "")
                - If invalid: (False, descriptive error message)
        
        Example:
            >>> config = ApiConfig(...)
            >>> is_valid, error = config.is_valid()
            >>> if not is_valid:
            ...     print(f"Configuration error: {error}")
        """
        # Validate endpoint
        if not self.endpoint or not self.endpoint.strip():
            return False, "Endpoint cannot be empty"
        
        # Validate project path
        if not self.project_path or not self.project_path.strip():
            return False, "Project path cannot be empty"
        
        # Validate backend URL
        if not self.backend.backend_url or not self.backend.backend_url.strip():
            return False, "Backend URL cannot be empty"
        
        # Validate at least one component selected
        if not self.components.has_any_selected():
            return False, "Please select at least one component to develop"
        
        return True, ""
