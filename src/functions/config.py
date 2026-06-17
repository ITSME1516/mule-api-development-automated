"""
API Configuration Class - Encapsulates all API creation parameters
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class BackendConfig:
    """Encapsulates Backend Configuration Parameters"""
    backend_type: str  # "request", "database", "soap"
    backend_url: str
    method: str  # GET, POST, PUT, DELETE
    base_path: str = "/*"
    connection_timeout: int = 60000
    response_timeout: int = 60000
    insecure_tls: bool = True
    use_persistent_connections: bool = True
    use_existing: bool = True

    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ComponentConfig:
    """Encapsulates Component Selection"""
    main_flow: bool = True
    impl_flow: bool = True
    system_flow: bool = True
    global_config: bool = True
    config_properties: bool = True

    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)

    def has_any_selected(self) -> bool:
        """Check if at least one component is selected"""
        return any([self.main_flow, self.impl_flow, self.system_flow, self.global_config])


@dataclass
class ApiConfig:
    """
    Complete API Configuration Class
    
    Consolidates all parameters needed for API creation into a single object,
    making function calls cleaner and more maintainable.
    """
    # Required parameters
    endpoint: str
    project_path: str
    
    # Backend configuration
    backend: BackendConfig
    
    # Components to develop
    components: ComponentConfig

    def to_dict(self):
        """Convert to dictionary for logging/display"""
        return {
            "endpoint": self.endpoint,
            "project_path": self.project_path,
            "backend": self.backend.to_dict(),
            "components": self.components.to_dict(),
        }

    def is_valid(self) -> tuple[bool, str]:
        """
        Validate configuration
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not self.endpoint or not self.endpoint.strip():
            return False, "Endpoint cannot be empty"
        
        if not self.project_path or not self.project_path.strip():
            return False, "Project path cannot be empty"
        
        if not self.backend.backend_url or not self.backend.backend_url.strip():
            return False, "Backend URL cannot be empty"
        
        if not self.components.has_any_selected():
            return False, "Please select at least one component to develop"
        
        return True, ""
