import json
import typing

from openai import OpenAI, NotFoundError

from .base import ILLMClient
from ..definitions import DbContext, LlmTypes, OptimizationResponse, DbTypes
from ..exceptions import OutOfSchemaRequest, UnsupportedModelName


class ChatGPTClient(ILLMClient):
    def __init__(self, *, system_instruction: str, model_name: str, **llm_auth) -> None:
        if "api_key" not in llm_auth.keys():
            raise ValueError("llm_auth for gemini must contain only api_key, not {}".format(list(llm_auth.keys())))

        if len(llm_auth.keys()) > 1:
            raise ValueError("llm_auth for gemini must contain only api_key, not {}".format(list(llm_auth.keys())))

        self._model_name = model_name
        self._conversation_history = [{"role": "system", "content": system_instruction}]
        self._client = OpenAI(**llm_auth)

    @classmethod
    def get_llm_type(cls) -> LlmTypes:
        return LlmTypes.CHATGPT

    def get_optimization(self, *, query: str, db_context: DbContext, db_type: DbTypes) -> OptimizationResponse:
        msg_from_llm = {"query_type": f"{db_type.value}_OPENING_QUERY", "data": {"query": query}}
        msg_to_llm = self._handle_llm_request(msg_from_llm=msg_from_llm, db_context=db_context)
        msg_from_llm = self._send_msg(msg=f"{msg_to_llm}")
        while True:
            try:
                msg_to_llm = self._handle_llm_request(msg_from_llm=msg_from_llm, db_context=db_context)

            except OutOfSchemaRequest as e:
                msg_to_llm = e.reason

            if isinstance(msg_to_llm, OptimizationResponse):
                return msg_to_llm

            msg_from_llm = self._send_msg(msg=msg_to_llm)

    def _send_msg(self, *, msg: str) -> typing.Mapping[str, typing.Any]:
        self._conversation_history.append({"role": "user", "content": msg})
        try:
            response = self._client.chat.completions.create(
                model=self._model_name,  # You can also use "gpt-3.5-turbo"
                messages=self._conversation_history,
            )

        except NotFoundError as e:
            raise UnsupportedModelName(model_name=self._model_name, llm_type=LlmTypes.CHATGPT.value.title()) from e

        text = response.choices[0].message.content
        msg_from_llm = json.loads(text)
        self._conversation_history.append({"role": "assistant", "content": text})
        return msg_from_llm

    @classmethod
    def pprint(cls, d):
        print(json.dumps(d, sort_keys=True, indent=4))
