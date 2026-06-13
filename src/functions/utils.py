import uuid

class utils:
    """
    Utility class for handling endpoint strings and logging properties.

    Methods:
        slashCheck(endpoint): Removes leading slash if present.
        slashConverter(endpoint): Converts forward slashes to backslashes.
        createUuid(): Generates a unique UUID string.
        joinPath(endpoint, separator): Joins last 3 parts of a path with a separator.
        disablePayloadProp(endpoint, separator): Builds a log property string.
    """
    def slashCheck(self, endpoint: str) -> str:
        """
        Remove leading slash from the endpoint if it exists.

        Parameters:
            endpoint (str): The API endpoint string (e.g., "/a/b/c").

        Returns:
            str: Endpoint without leading slash.
        """
        if(endpoint.startswith("/")):
            return endpoint[1:]
        else:
            return endpoint
        
    def slashConverter(self, endpoint: str) -> str:
        """
        Convert forward slashes to backslashes in the endpoint.

        Parameters:
            endpoint (str): The API endpoint string (e.g., "/a/b/c").

        Returns:
            str: Endpoint with backslashes (e.g., "\a\b\c").
        """
        return endpoint.replace("/", "\\")

    def createUuid(self) -> str:
        """
        Generate a random UUID string.

        Returns:
            str: A unique identifier (e.g., "123e4567-e89b-12d3-a456-426614174000").
        """
        return str(uuid.uuid4())

    def joinPath(self, endpoint: str, separator: str = ".") -> str:
        """
        Join the last 3 parts of the endpoint path using a separator.

        Parameters:
            endpoint (str): The API endpoint string (e.g., "/a/b/c/d/e").
            separator (str): The character to join with (default is ".").

        Returns:
            str: Joined path (e.g., "c.d.e").
        """
        endpointSplit= [p for p in endpoint.split("/")[-3:] if p] 
        return separator.join(endpointSplit)
    
    def disablePayloadProp(self, endpoint: str, separator: str = ".") -> str:
        """
        Build a log property string for disabling payload logs.

        Parameters:
            endpoint (str): The API endpoint string.
            separator (str): The character to join with (default is ".").

        Returns:
            str: Log property string (e.g., "a.f.disable.payload.logs").
        """
        result = self.joinPath(endpoint, separator)
        return result + ".disable.payload.logs"

    def implFlowName(self, endpoint: str) -> str:
        """
        Generate a standardized implementation flow name for MuleSoft subflows.

        Parameters:
            endpoint (str): The API endpoint string (e.g., "/a/b/c/d/e").

        Returns:
            str: Flow name in the format "impl-x-y-z-subflow",
                 where x-y-z are the last three parts of the endpoint joined by "-".

        Example:
            >>> utilsObj = Utils()
            >>> utilsObj.implFlowName("/a/b/c/d/e")
            'impl-c-d-e-subflow'
        """
        return f"impl-{self.joinPath(endpoint, "-")}-subflow"
    
    def implFileName(self, endpoint: str) -> str:
        """
        Generate a standardized implementation file name for MuleSoft subflows.

        Parameters:
            endpoint (str): The API endpoint string (e.g., "/a/b/c/d/e").

        Returns:
            str: Flow name in the format "impl-x-y-z-subflow",
                 where x-y-z are the last three parts of the endpoint joined by "-".

        Example:
            >>> utilsObj = Utils()
            >>> utilsObj.implFileName("/a/b/c/d/e")
            'impl-c-d-e-flows'
        """
        return f"impl-{self.joinPath(endpoint, "-")}-flows.xml"