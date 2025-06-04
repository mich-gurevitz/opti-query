import os
from pathlib import Path

import questionary

from opti_query.optipy.definitions import LlmTypes, DbTypes, OptimizationResponse
from opti_query.optipy.hanlder import OptiQueryHandler
from .struct import ProviderManager, AiProvider, Database
from ..optipy.exceptions import UnsupportedModelName


class OptiQueryCliRunner:
    CONFIG_PATH = Path("config.json")

    @classmethod
    def _clear_screen(cls) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    @classmethod
    def run_cli(cls) -> None:
        while True:
            cls._clear_screen()
            choice = questionary.select(
                "Welcome to OptiQuery. Please choose an action:",
                choices=[
                    "Start Optimization",
                    "Configure a Database",
                    "Update an existing Database",
                    "Configure an AI Provider",
                    "Update an existing AI Provider",
                    "Exit",
                ],
            ).ask()

            if choice == "Start Optimization":
                cls._start_optimization_flow()

            elif choice == "Configure a Database":
                cls._configure_database()

            elif choice == "Configure an AI Provider":
                cls._configure_provider()

            elif choice == "Update an existing Database":
                cls._update_database()

            elif choice == "Update an existing AI Provider":
                cls._update_provider()

            elif choice == "Exit":
                print("\nGoodbye.\n")
                break

    @classmethod
    def _configure_database(cls) -> None:
        cls._clear_screen()
        db_type = questionary.select("Choose database type:", choices=["Neo4j"]).ask()
        uri = questionary.text("Enter the database URI (e.g., bolt://localhost:7687):").ask()
        username = questionary.text("Username:").ask()
        password = questionary.password("Password:").ask()
        db_name = questionary.text("Database name:").ask()
        friendly_name = questionary.text("Choose a name for this database configuration:").ask()

        db = Database(uri=uri, username=username, password=password, db_name=db_name, db_type=DbTypes(db_type.upper()), friendly_name=friendly_name)
        ProviderManager.add_database(db=db)

        print(f"\nDatabase '{friendly_name}' has been successfully saved.")
        input("Press Enter to continue...")

    @classmethod
    def _update_database(cls) -> None:
        cls._clear_screen()
        friendly_name = questionary.select("Select a database to update:", choices=ProviderManager.list_dbs()).ask()
        db_type = ProviderManager.get_database(db=friendly_name).db_type
        uri = questionary.text("Enter the database URI (e.g., bolt://localhost:7687):").ask()
        username = questionary.text("Username:").ask()
        password = questionary.password("Password:").ask()
        db_name = questionary.text("Database name:").ask()

        db = Database(uri=uri, username=username, password=password, db_name=db_name, db_type=db_type, friendly_name=friendly_name)
        ProviderManager.update_database(db=db)

        print(f"\nDatabase '{friendly_name}' has been successfully saved.")
        input("Press Enter to continue...")

    @classmethod
    def _configure_provider(cls) -> None:
        cls._clear_screen()
        llm_type = questionary.select("Choose AI provider:", choices=["Gemini", "ChatGPT"]).ask()
        llm_type = LlmTypes(llm_type.upper())
        model_name = questionary.text("Model Name:").ask()
        token = questionary.password("Enter API token for the provider:").ask()
        friendly_name = questionary.text("Choose a name for this AI provider:").ask()
        ai_provider = AiProvider(
            llm_auth={"api_key": token},
            friendly_name=friendly_name,
            llm_type=llm_type,
            model_name=model_name,
        )
        ProviderManager.add_ai_provider(ai_provider=ai_provider)

        print(f"\nAI provider '{friendly_name}' has been successfully saved.")
        input("Press Enter to continue...")

    @classmethod
    def _update_provider(cls) -> None:
        cls._clear_screen()
        friendly_name = questionary.select("Select an AI provider to update:", choices=ProviderManager.list_ai_providers()).ask()
        llm_type = ProviderManager.get_ai_provider(ai_provider=friendly_name).llm_type
        model_name = questionary.text("Model Name:").ask()
        token = questionary.password("Enter API token for the provider:").ask()
        ai_provider = AiProvider(
            llm_auth={"api_key": token},
            friendly_name=friendly_name,
            llm_type=llm_type,
            model_name=model_name,
        )
        ProviderManager.update_ai_provider(ai_provider=ai_provider)

        print(f"\nAI provider '{friendly_name}' has been successfully saved.")
        input("Press Enter to continue...")

    @classmethod
    def _start_optimization_flow(cls) -> None:
        cls._clear_screen()
        databases_friendly_names = ProviderManager.list_dbs()
        ai_providers_friendly_names = ProviderManager.list_ai_providers()

        if not databases_friendly_names:
            print("No databases have been configured yet. Please add a database first.")
            input("Press Enter to return.")
            return

        if not ai_providers_friendly_names:
            print("No AI providers have been configured yet. Please add an AI provider first.")
            input("Press Enter to return.")
            return

        db_choice = questionary.select("Select a database to use:", choices=databases_friendly_names).ask()
        db = ProviderManager.get_database(db=db_choice)

        provider_choice = questionary.select("Select an AI provider to use:", choices=ai_providers_friendly_names).ask()
        provider = ProviderManager.get_ai_provider(ai_provider=provider_choice)

        query = questionary.text("Enter the query you want to optimize:").ask()
        cls._clear_screen()
        print("Running optimization, please wait...\n")

        try:
            result = OptiQueryHandler.optimize_query(
                query=query,
                host=db.uri,
                database=db.db_name,
                username=db.username,
                password=db.password,
                llm_type=provider.llm_type,
                db_type=db.db_type,
                model_name=provider.model_name,
                **provider.llm_auth,
            )
            print("Optimization completed successfully.\n")
            cls._print_result(result=result)

        except UnsupportedModelName as e:
            cls._clear_screen()
            print(f"\nThe model '{e.model_name}' is not supported for the selected AI provider ({e.llm_type}).")
            print("Please configure a different model or update the existing provider.")

        except Exception as e:
            print("An error occurred:")
            print(e)

        input("\nPress Enter to return to main menu...")

    @classmethod
    def _print_result(cls, *, result: OptimizationResponse) -> None:
        print("=" * 80)
        print("Optimization Results")
        print("=" * 80)
        for i, item in enumerate(result.optimized_queries_and_explains, start=1):
            print(f"\nQuery {i}")
            print("-" * 80)
            print("Query:")
            print(item.query)
            print("\nExplanation:")
            print(item.explanation)
            print("-" * 80)

        suggestions = result.suggestions
        if suggestions:
            print("\nAdditional Suggestions")
            print("=" * 80)
            for suggestion in suggestions:
                print(f"- {suggestion}")
        print()
