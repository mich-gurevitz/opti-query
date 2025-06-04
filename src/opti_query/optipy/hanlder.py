from .definitions import (
    DbContext,
    DB_TYPE_TO_SYSTEM_INSTRUCTIONS,
    LlmTypes,
    DbTypes,
    OptimizationResponse,
)
from .llm_clients.base import LLM_TYPE_TO_LLM_CLIENT


class OptiQueryHandler:
    @classmethod
    def optimize_query(
        cls,
        *,
        db_type: DbTypes,
        host: str,
        username: str,
        password: str,
        query: str,
        database: str,
        llm_type: LlmTypes,
        model_name: str,
        **llm_auth,
    ) -> OptimizationResponse:
        # print(llm_auth)
        db_context = DbContext(host=host, username=username, password=password, database=database)
        system_instruction = DB_TYPE_TO_SYSTEM_INSTRUCTIONS[db_type]
        llm_client_cls = LLM_TYPE_TO_LLM_CLIENT[llm_type]
        client = llm_client_cls(system_instruction=system_instruction, model_name=model_name, **llm_auth)
        optimization = client.get_optimization(query=query, db_context=db_context, db_type=db_type)
        return optimization
