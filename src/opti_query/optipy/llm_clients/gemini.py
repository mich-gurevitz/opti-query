import json
import typing
from json import JSONDecodeError

import google.generativeai as genai
from google.api_core.exceptions import NotFound
from google.generativeai.types import ContentDict

from .base import ILLMClient
from ..definitions import DbContext, LlmTypes, OptimizationResponse, DbTypes
from ..exceptions import OutOfSchemaRequest, UnsupportedModelName, LlmReachedTryCount


class GeminiClient(ILLMClient):
    def __init__(self, *, system_instruction: str, model_name: str, **llm_auth) -> None:
        if "api_key" not in llm_auth.keys():
            raise ValueError("llm_auth for gemini must contain only api_key, not {}".format(list(llm_auth.keys())))

        if len(llm_auth.keys()) > 1:
            raise ValueError("llm_auth for gemini must contain only api_key, not {}".format(list(llm_auth.keys())))

        genai.configure(**llm_auth)
        self._model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
        self._model_name = model_name

    @classmethod
    def get_llm_type(cls) -> LlmTypes:
        return LlmTypes.GEMINI

    def get_optimization(self, *, query: str, db_context: DbContext, db_type: DbTypes) -> OptimizationResponse:
        history: list[ContentDict] = []
        msg_from_llm = {"query_type": f"{db_type.value}_OPENING_QUERY", "data": {"query": query}}
        msg_to_llm = self._handle_llm_request(msg_from_llm=msg_from_llm, db_context=db_context)
        msg_from_llm = self._send_msg(history=history, msg=f"{msg_to_llm}")
        while True:
            try:
                msg_to_llm = self._handle_llm_request(msg_from_llm=msg_from_llm, db_context=db_context)

            except OutOfSchemaRequest as e:
                msg_to_llm = e.reason

            if isinstance(msg_to_llm, OptimizationResponse):
                return msg_to_llm

            msg_from_llm = self._send_msg(history=history, msg=msg_to_llm)

    def _send_msg(self, *, history: typing.List[ContentDict], msg: str, try_count: int = 0) -> typing.Mapping[str, typing.Any]:
        chat_session = self._model.start_chat(history=history)
        try:
            response = chat_session.send_message(msg)

        except NotFound as e:
            raise UnsupportedModelName(model_name=self._model_name, llm_type=LlmTypes.GEMINI.value.title()) from e

        try:
            text = response.text[7:-4]
            msg_from_llm = json.loads(text)

        except JSONDecodeError as e:
            text = response.text
            try:
                msg_from_llm = json.loads(text)

            except JSONDecodeError as e:
                if try_count > 5:
                    raise LlmReachedTryCount

                history.append(ContentDict(role="user", parts=[msg]))
                history.append(ContentDict(role="model", parts=[response.text]))
                failed_to_parse_msg = "Your message is not a valid json. Please send only a **valid json** message."
                return self._send_msg(history=history, msg=failed_to_parse_msg, try_count=try_count + 1)

        history.append(ContentDict(role="user", parts=[msg]))
        history.append(ContentDict(role="model", parts=[response.text]))
        return msg_from_llm
