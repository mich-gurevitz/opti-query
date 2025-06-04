import typing

from pydantic import BaseModel

from opti_query.optipy.definitions import LlmTypes, DbTypes


class Database(BaseModel):
    uri: str
    password: str
    username: str
    db_name: str
    db_type: DbTypes
    friendly_name: str


class AiProvider(BaseModel):
    llm_type: LlmTypes
    llm_auth: typing.Mapping[str, str]
    friendly_name: str
    model_name: str


class ProviderManager:
    _DATABASES: typing.Dict[str, Database] = {}
    _AI_PROVIDERS: typing.Dict[str, AiProvider] = {}

    @classmethod
    def add_database(cls, *, db: Database) -> None:
        if db.friendly_name in cls._DATABASES.keys():
            raise Exception(f"Database {db.friendly_name} already exists")

        cls._DATABASES[db.friendly_name] = db

    @classmethod
    def update_database(cls, *, db: Database) -> None:
        if db.friendly_name not in cls._DATABASES.keys():
            raise Exception(f"Database {db.friendly_name} already exists")

        cls._DATABASES[db.friendly_name] = db

    @classmethod
    def add_ai_provider(cls, *, ai_provider: AiProvider) -> None:
        if ai_provider.friendly_name in cls._AI_PROVIDERS.keys():
            raise Exception(f"AI provider {ai_provider.friendly_name} already exists")

        cls._AI_PROVIDERS[ai_provider.friendly_name] = ai_provider

    @classmethod
    def update_ai_provider(cls, *, ai_provider: AiProvider) -> None:
        if ai_provider.friendly_name not in cls._AI_PROVIDERS.keys():
            raise Exception(f"AI provider {ai_provider.friendly_name} already exists")

        cls._AI_PROVIDERS[ai_provider.friendly_name] = ai_provider

    @classmethod
    def get_database(cls, *, db: str) -> Database:
        return cls._DATABASES[db]

    @classmethod
    def get_ai_provider(cls, *, ai_provider: str) -> AiProvider:
        return cls._AI_PROVIDERS[ai_provider]

    @classmethod
    def list_ai_providers(cls) -> typing.List[str]:
        return list(cls._AI_PROVIDERS.keys())

    @classmethod
    def list_dbs(cls) -> typing.List[str]:
        return list(cls._DATABASES.keys())
