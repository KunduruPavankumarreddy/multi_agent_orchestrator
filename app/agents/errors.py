class AgentExecutionError(Exception):
    """Raised when an agent cannot complete its task."""

    def __init__(
        self,
        agent_name: str,
        message: str,
        *,
        retryable: bool = True,
    ) -> None:
        super().__init__(message)
        self.agent_name = agent_name
        self.retryable = retryable