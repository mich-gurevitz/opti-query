class OutOfSchemaRequest(Exception):
    def __init__(self, *, reason: str):
        self._reason = reason

    @property
    def reason(self) -> str:
        return self._reason
