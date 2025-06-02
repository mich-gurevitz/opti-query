import json
import typing

import google.generativeai as genai
from google.generativeai.types import ContentDict

from .base import ILLMClient
from ..definitions import DbContext, QueryTypes, LlmTypes, OptimizationResponse, DbTypes
from ..exceptions import OutOfSchemaRequest


class GeminiClient(ILLMClient):
    def __init__(self, *, system_instruction: str, **llm_auth) -> None:
        if "api_key" not in llm_auth.keys():
            raise ValueError("llm_auth for gemini must contain only api_key, not {}".format(list(llm_auth.keys())))

        if len(llm_auth.keys()) > 1:
            raise ValueError("llm_auth for gemini must contain only api_key, not {}".format(list(llm_auth.keys())))

        genai.configure(**llm_auth)
        self._model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)

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

    def _send_msg(self, *, history: typing.List[ContentDict], msg: str) -> typing.Mapping[str, typing.Any]:
        # print("user says:")
        # self.pprint(msg)
        # print()
        chat_session = self._model.start_chat(history=history)
        response = chat_session.send_message(msg)
        text = response.text[7:-4]
        msg_from_llm = json.loads(text)
        # print("llm says:")
        # self.pprint(msg_from_llm)
        # print()
        history.append(ContentDict(role="user", parts=[msg]))
        history.append(ContentDict(role="model", parts=[response.text]))
        return msg_from_llm

    def pprint(self, d):
        print(json.dumps(d, sort_keys=True, indent=4))
