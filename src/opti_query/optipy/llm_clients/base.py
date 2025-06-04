import abc
import typing

from ..definitions import DbContext, QueryTypes, LlmTypes, OptimizationResponse, DbTypes
from ..exceptions import OutOfSchemaRequest
from ..queries.base import QUERY_TYPE_TO_QUERY_CLASS


class ILLMClient(abc.ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        LLM_TYPE_TO_LLM_CLIENT[cls.get_llm_type()] = cls

    @abc.abstractmethod
    def __init__(self, *, system_instruction: str, model_name: str, **llm_auth) -> None:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get_llm_type(cls) -> LlmTypes:
        raise NotImplementedError

    @abc.abstractmethod
    def get_optimization(self, *, query: str, db_context: DbContext, db_type: DbTypes) -> OptimizationResponse:
        raise NotImplementedError

    @classmethod
    def _handle_llm_request(cls, *, msg_from_llm: typing.Mapping[str, typing.Any], db_context: DbContext) -> typing.Any:
        if "query_type" not in msg_from_llm:
            raise OutOfSchemaRequest(reason="Your message does not contain a query_type. Your messages must follow that schema.")

        query_type = msg_from_llm["query_type"]
        if query_type not in QueryTypes:
            raise OutOfSchemaRequest(reason=f"{query_type} is not a valid query type.")

        if "data" not in msg_from_llm:
            raise OutOfSchemaRequest(reason="Your message does not contain a data. Your messages must follow that schema.")

        elif msg_from_llm["query_type"] == QueryTypes.OPTIMIZE_FINISHED:
            OptimizationResponse.validate_request(data=msg_from_llm["data"])
            return OptimizationResponse(**msg_from_llm["data"])

        query_runner_cls = QUERY_TYPE_TO_QUERY_CLASS[query_type]
        query_data = msg_from_llm["data"]

        query_runner_cls.validate_request(data=query_data)
        query_runner = query_runner_cls(**query_data)
        db_response = query_runner.get_parsed_response(db_context=db_context)
        return db_response


LLM_TYPE_TO_LLM_CLIENT: typing.Dict[LlmTypes, typing.Type[ILLMClient]] = {}
