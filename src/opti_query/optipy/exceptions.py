class OutOfSchemaRequest(Exception):
    def __init__(self, *, reason: str):
        self._reason = reason

    @property
    def reason(self) -> str:
        return self._reason


class UnsupportedModelName(Exception):
    def __init__(self, *, model_name: str, llm_type: str):
        self._model_name = model_name
        self._llm_type = llm_type

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def llm_type(self) -> str:
        return self._llm_type
