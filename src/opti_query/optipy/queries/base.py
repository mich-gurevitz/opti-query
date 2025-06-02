import abc
import inspect
import typing

from ..definitions import DbContext, QueryTypes, OptiModel


class IQueryRunner(OptiModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

        if not inspect.isabstract(cls):
            QUERY_TYPE_TO_QUERY_CLASS[cls.get_query_type()] = cls

    @abc.abstractmethod
    def build_queries(self) -> typing.List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def _run_query(self, *, db_context: DbContext) -> typing.Generator[typing.Any, None, None]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get_query_type(cls) -> QueryTypes:
        raise NotImplementedError

    @abc.abstractmethod
    def get_parsed_response(self, *, db_context: DbContext) -> str:
        raise NotImplementedError


QUERY_TYPE_TO_QUERY_CLASS: typing.Dict[QueryTypes, typing.Type[IQueryRunner]] = {}
