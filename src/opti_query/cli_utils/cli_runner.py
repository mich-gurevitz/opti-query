import os
import typing
from pathlib import Path

import questionary

from .struct import ProviderManager, AiProvider, Database
from opti_query.optipy.definitions import LlmTypes, DbTypes, OptimizationResponse
from opti_query.optipy.hanlder import OptiQueryHandler  # must be implemented by you


class OptiQueryCliRunner:
    CONFIG_PATH = Path("config.json")

    @classmethod
    def _clear_screen(cls):
        os.system("cls" if os.name == "nt" else "clear")

    @classmethod
    def run_cli(cls):
        while True:
            cls._clear_screen()
            choice = questionary.select(
                "Welcome to OptiQuery. What would you like to do?",
                choices=[
                    "Start Optimization",
                    "Configure a Database",
                    "Configure an AI Provider",
                    "Exit"
                ]
            ).ask()

            if choice == "Start Optimization":
                cls._start_optimization_flow()
            elif choice == "Configure a Database":
                cls._configure_database()
            elif choice == "Configure an AI Provider":
                cls._configure_provider()
            elif choice == "Exit":
                print("\nGoodbye!\n")
                break

    @classmethod
    def _configure_database(cls):
        cls._clear_screen()
        db_type = questionary.select("Choose database type:", choices=["Neo4j"]).ask()
        uri = questionary.text("Enter database URI (e.g., bolt://localhost:7687):").ask()
        username = questionary.text("Username:").ask()
        password = questionary.password("Password:").ask()
        db_name = questionary.text("Database name:").ask()
        friendly_name = questionary.text("Friendly name to identify this DB:").ask()

        db = Database(uri=uri, username=username, password=password, db_name=db_name, db_type=DbTypes(db_type.upper()), friendly_name=friendly_name)
        ProviderManager.add_database(db=db)

        print(f"\nDatabase '{friendly_name}' saved.")
        input("Press Enter to continue...")

    @classmethod
    def _configure_provider(cls):
        cls._clear_screen()
        model = questionary.select("Choose AI provider:", choices=["Gemini"]).ask()
        token = questionary.text("Enter API token for the provider:").ask()
        friendly_name = questionary.text("Friendly name to identify this provider:").ask()
        ai_provider = AiProvider(
            llm_auth={"api_key": token},
            friendly_name=friendly_name,
            llm_type=LlmTypes(model.upper()),
        )
        ProviderManager.add_ai_provider(ai_provider=ai_provider)

        print(f"\nAI Provider '{friendly_name}' saved.")
        input("Press Enter to continue...")

    @classmethod
    def _start_optimization_flow(cls):
        cls._clear_screen()
        databases_friendly_names = ProviderManager.list_dbs()
        ai_providers_friendly_names = ProviderManager.list_ai_providers()

        if not databases_friendly_names:
            print("No databases found. Please configure one first.")
            input("Press Enter to return.")
            return

        if not ai_providers_friendly_names:
            print("No AI providers found. Please configure one first.")
            input("Press Enter to return.")
            return

        db_choice = questionary.select(
            "Select a database to use:",
            choices=databases_friendly_names
        ).ask()
        db = ProviderManager.get_database(db=db_choice)

        provider_choice = questionary.select(
            "Select an AI provider to use:",
            choices=ai_providers_friendly_names
        ).ask()
        provider = ProviderManager.get_ai_provider(ai_provider=provider_choice)

        query = questionary.text("Enter the query you want to optimize:").ask()
        cls._clear_screen()
        print("Running optimization...\n")

        try:
            result = OptiQueryHandler.optimize_query(
                query=query,
                host=db.uri,
                database=db.db_name,
                username=db.username,
                password=db.password,
                llm_type=provider.llm_type,
                db_type=db.db_type,
                **provider.llm_auth
            )
            print("Optimization result:\n")
            cls._print_result(result=result)

        except Exception as e:
            print("An error occurred:")
            print(e)

        input("\nPress Enter to return to main menu...")

    @classmethod
    def _print_result(cls, *, result: OptimizationResponse):
        print("=" * 80)
        print("Optimized Queries and Explanations")
        print("=" * 80)
        for i, item in enumerate(result.optimized_queries_and_explains, start=1):
            print(f"\nQuery #{i}")
            print("-" * 80)
            print("Query:")
            print(item.query)
            print("\nExplanation:")
            print(item.explanation)
            print("-" * 80)

        suggestions = result.suggestions
        if suggestions:
            print("\nSuggestions")
            print("=" * 80)
            for suggestion in suggestions:
                print(f"- {suggestion}")
        print()

