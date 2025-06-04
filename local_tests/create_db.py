import random

from neo4j import GraphDatabase, ManagedTransaction

from opti_query.optipy.definitions import DbTypes, LlmTypes
from opti_query.optipy.hanlder import OptiQueryHandler

# Neo4j connection info
NEO4J_URI = "neo4j+ssc://e7544395.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "TjTTXTYzsk8GUmV4BRCITZ0lEJ-C_Lds4GcxCUaCht8"
GEMINI_API_KEY = "AIzaSyA1UseCuLXOYyhuoHWA8GlAG0JAqIxNhoU"
CHATGPT_API_KEY = (
    "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"
)
model_name = "gemini-1.5-flash"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
query = "MATCH (child:Child)-[]-(country:Country) WHERE child.gender = 'Male' RETURN child.name AS name, country.name AS country_name"

# Expanded sample data
countries = [
    "USA",
    "Germany",
    "Japan",
    "Brazil",
    "India",
    "Canada",
    "France",
    "UK",
    "Italy",
    "Australia",
    "Spain",
    "Mexico",
    "South Korea",
    "Netherlands",
    "Sweden",
    "Switzerland",
    "Norway",
    "Russia",
    "China",
    "Argentina",
    "South Africa",
    "Turkey",
    "Poland",
    "Indonesia",
    "Thailand",
    "Vietnam",
    "New Zealand",
    "Israel",
    "Egypt",
    "Greece",
]

occupations = [
    "Engineer",
    "Doctor",
    "Teacher",
    "Artist",
    "Chef",
    "Developer",
    "Nurse",
    "Scientist",
    "Writer",
    "Mechanic",
    "Pilot",
    "Electrician",
    "Plumber",
    "Dentist",
    "Architect",
    "Lawyer",
    "Musician",
    "Pharmacist",
    "Psychologist",
    "Veterinarian",
    "Accountant",
    "Journalist",
    "Police Officer",
    "Firefighter",
    "Bartender",
    "Designer",
    "Translator",
    "Economist",
    "Analyst",
    "Salesperson",
]

genders = ["Male", "Female", "Non-Binary", "Other", "Prefer Not to Say"]


def create_schema(tx):
    tx.run("MATCH (n) DETACH DELETE n")
    tx.run("CREATE INDEX IF NOT EXISTS FOR (c:Country) ON (c.name)")
    tx.run("CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.country_name)")
    tx.run("CREATE INDEX IF NOT EXISTS FOR (o:Occupation) ON (o.name)")


def create_countries(tx):
    for country in countries:
        tx.run(
            "CREATE (:Country {name: $name, population: $pop, code: $code, continent: $continent})",
            name=country,
            pop=random.randint(5_000_000, 300_000_000),
            code=country[:3].upper(),
            continent=random.choice(["Asia", "Europe", "North America", "South America", "Africa", "Oceania"]),
        )


def create_occupations(tx):
    for job in occupations:
        tx.run(
            "CREATE (:Occupation {name: $name, industry: $industry, avg_salary: $salary})",
            name=job,
            industry=random.choice(["Tech", "Health", "Art", "Education", "Trades", "Law", "Finance", "Media"]),
            salary=random.randint(25_000, 200_000),
        )


def create_people(tx, start, end):
    for i in range(start, end):
        country = random.choice(countries)
        gender = random.choice(genders)
        person_id = f"person_{i}"
        is_child = random.random() < 0.25

        props = {
            "id": person_id,
            "name": f"Person_{i}",
            "age": random.randint(1, 80),
            "gender": gender,
            "country_name": country,
            "email": f"user{i}@example.com",
            "active": random.choice([True, False]),
        }

        if is_child:
            props["grade"] = random.randint(1, 12)
            props["favorite_cartoon"] = random.choice(["SpongeBob", "Naruto", "Peppa Pig", "Frozen", "Cars"])
            props["school"] = f"School_{random.randint(1, 500)}"
            labels = ":Person:Child"
        else:
            props["hobbies"] = random.sample(["reading", "gaming", "sports", "music", "hiking", "cooking"], 3)
            props["married"] = random.choice([True, False])
            labels = ":Person"

        tx.run(
            f"""
            MATCH (c:Country {{name: $country}})
            CREATE (p{labels} $props)-[:LIVES_IN]->(c)
            """,
            country=country,
            props=props,
        )

        if not is_child and random.random() < 0.5:
            occupation = random.choice(occupations)
            tx.run(
                """
                MATCH (p:Person {id: $id}), (o:Occupation {name: $occ})
                CREATE (p)-[:WORKS_AS]->(o)
                """,
                id=person_id,
                occ=occupation,
            )


def show_indexes(tx: ManagedTransaction):
    return tx.run("SHOW INDEXES").single()


def main():
    # total_people = 10000
    # batch_size = 100
    # db_context = DbContext(host=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD, database='neo4j')
    # query_runner_cls = QUERY_TYPE_TO_QUERY_CLASS[QueryTypes.NEO4j_EXPLAIN_QUERY]
    # d = {"query": "MATCH (child:Child:Person {gender:'Male'})-[:LIVES_IN]->(country:Country)\nRETURN child.name AS name, country.name AS country_name"}
    # query_runner = query_runner_cls(**d)
    # db_response = query_runner.get_parsed_response(db_context=db_context)
    # print(db_response)
    # def get_optimization(*, query: str, db_context2: DbContext, db_type: str, query_type: QueryTypes):
    #     history = []
    #     print(DB_TYPE_TO_OPENING_QUERY.keys())
    #     query_cls = QUERY_TYPE_TO_QUERY_CLASS[query_type]
    #     first_msg_dict = query_cls().get_parsed_response(db_context=db_context2)
    #     first_msg_dict["query"] = query
    #     print(first_msg_dict)
    #
    # get_optimization(query="BLA BLA", db_context2=db_context, db_type="NEO4J", query_type=QueryTypes.NEO4J_COUNT_NODES_WITH_LABELS)
    # def run_query():
    #     # driver = GraphDatabase.driver(db_context.host, auth=(db_context.username, db_context.password))
    #     with driver.session(default_access_mode=READ_ACCESS, database=db_context.database) as session:
    #         tx = session.begin_transaction()
    #         query_to_run = """
    #         EXPLAIN
    #         CALL {
    #             MATCH (c:Child)-[:LIVES_IN]->(cnt:Country) RETURN c.id AS child_name, cnt.name AS country_name
    #             UNION ALL
    #             MATCH (c:Child) RETURN c.country_name AS country_name, c.id AS child_name
    #         }
    #         RETURN country_name, child_name
    #         """
    #         return tx.run(query_to_run).consume().plan
    #
    #         tx.close()
    #
    # def print_plan(plan, indent=0):
    #     prefix = "  " * indent
    #     print(prefix + f"- {plan["operatorType"]} ({plan['identifiers']})")
    #     if args := plan["args"]:
    #         for k, v in args.items():
    #             print(f"{prefix}    > {k}: {v}")
    #
    #     for child in plan.get('children', []):
    #         print_plan(child, indent + 1)
    #
    # res = run_query()
    # print(res["args"]['string-representation'])
    # def _run_query(queries: typing.List[str]) -> typing.Generator[typing.Any, None, None]:
    #     with driver.session(default_access_mode=READ_ACCESS, database="neo4j") as session2:
    #         tx = session2.begin_transaction()
    #         for query in queries:
    #             yield tx.run(query).data()
    #
    #         tx.close()
    # for i in _run_query(["SHOW INDEXES"]):
    #     print(i)
    # with driver.session() as session:
    #     # session.execute_write(create_schema)
    #     x = session.execute_read(show_indexes)
    #     print(x)
    # print("Creating countries...")
    # session.execute_write(create_countries)
    # print("Creating occupations...")
    # session.execute_write(create_occupations)
    #
    # for start in range(0, total_people, batch_size):
    #     end = min(start + batch_size, total_people)
    #     print(f"Creating persons {start} to {end}...")
    #     session.execute_write(create_people, start, end)
    query1 = "MATCH (child:Child {gender: 'Male'})-[]-(Country) RETURN child.name AS child_name, country.name AS country_name"
    query2 = "MATCH (person:Person)-[]->(occupation:Occupation) RETURN distinct occupation.name"

    query3 = "MATCH (o:Occupation)<-[:WORKS_AS]-(p:Person) WITH p MATCH (p)-[:LIVES_IN]->(c:Country) RETURN p.name AS person_name, c.name AS country_name"
    OptiQueryHandler.optimize_query(
        db_type=DbTypes.NEO4J,
        host=NEO4J_URI,
        password=NEO4J_PASSWORD,
        username=NEO4J_USER,
        database="neo4j",
        llm_type=LlmTypes.CHATGPT,
        api_key=CHATGPT_API_KEY,
        query=query1,
        model_name="o3-2025-04-16",
    )
    # print("✅ Finished paginated generation!")


if __name__ == "__main__":
    main()
