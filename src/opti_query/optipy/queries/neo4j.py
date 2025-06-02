import abc
import json
import typing
from collections import defaultdict, Counter

from neo4j.exceptions import ClientError

from .base import IQueryRunner
from ..definitions import DbContext, QueryTypes
from ..exceptions import OutOfSchemaRequest
from ..utils.neo4j import Neo4jUtils


class Neo4jQueryRunner(IQueryRunner, abc.ABC):
    def _run_query(self, *, db_context: DbContext) -> typing.Generator[typing.Any, None, None]:
        with Neo4jUtils.acquire_tx(db_context=db_context) as tx:
            for query in self.build_queries():
                try:
                    yield tx.run(query).data()

                except Exception as e:
                    yield f"Please try again, error was raised while running query: {e}. \nThe error might be related to you."


class Neo4jOpeningQueryRunner(Neo4jQueryRunner):
    query: str

    @classmethod
    def get_query_type(cls) -> QueryTypes:
        return QueryTypes.NEO4J_OPENING_QUERY

    def build_queries(self) -> typing.List[str]:
        return [
            """
            CALL {
                CALL apoc.meta.stats() YIELD labels, relTypes
                UNWIND keys(labels) AS label
                WITH 'node_count' AS section, label AS name, labels[label] AS count, relTypes
                RETURN section, name, count
                UNION ALL
                CALL apoc.meta.stats() YIELD relTypes
                UNWIND keys(relTypes) AS relType
                WITH 'relationship_count' AS section, relType AS name, relTypes[relType] AS count
                RETURN section, name, count
            }
            RETURN section, name, count
            """,
            """
            SHOW INDEXES YIELD labelsOrTypes AS labels, properties
            RETURN labels, properties
            """,
            """
            SHOW CONSTRAINTS YIELD labelsOrTypes AS labels, properties
            RETURN labels, properties
            """,
        ]

    @classmethod
    def validate_request(cls, data: typing.Mapping[str, typing.Any]) -> None:
        if "query" not in data.keys():
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain 'query' key in data.")

        if not isinstance(data["query"], str):
            raise OutOfSchemaRequest(reason=f"Value of key 'labels' in data of request with query_type: {cls.get_query_type().value} must be str.")

        if len(data.keys()) > 1:
            keys = ", ".join(key for key in data.keys() if key != "query")
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain only 'query' key in data, request contains {keys}.")

    def get_parsed_response(self, *, db_context: DbContext) -> str:
        stats_response, indexes_response, constraints_response = tuple(self._run_query(db_context=db_context))
        response: typing.Dict[str, typing.Any] = {
            "node_count": [],
            "relationship_count": [],
            "indexes": [],
            "constraints": [],
        }
        for item in stats_response:
            response[item["section"]].append({item["name"]: item["count"]})

        for record in indexes_response:
            labels = record.get("labels") or []
            properties = record.get("properties") or []
            for label in labels:
                for prop in properties:
                    response["indexes"].append({"label": label, "property": prop})

        for record in constraints_response:
            labels = record.get("labels") or []
            properties = record.get("properties") or []
            for label in labels:
                for prop in properties:
                    response["constraints"].append({"label": label, "property": prop})
        response["query"] = self.query
        return json.dumps(response)


class Neo4jLabelCountQueryRunner(Neo4jQueryRunner):
    labels: typing.Iterable[str]

    @classmethod
    def get_query_type(cls) -> QueryTypes:
        return QueryTypes.NEO4J_COUNT_NODES_WITH_LABELS

    def build_queries(self) -> typing.List[str]:
        labels = ":".join(self.labels)
        return [f"MATCH (n:{labels}) RETURN COUNT(n) AS count"]

    def get_parsed_response(self, *, db_context: DbContext) -> str:
        count = next(self._run_query(db_context=db_context))[0]
        return str(count["count"])

    @classmethod
    def validate_request(cls, data: typing.Mapping[str, typing.Any]) -> None:
        if "labels" not in data.keys():
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain 'labels' key in data.")

        if not isinstance(data["labels"], list):
            raise OutOfSchemaRequest(reason=f"Value of key 'labels' in data of request with query_type: {cls.get_query_type().value} must be list.")

        if len(data.keys()) > 1:
            keys = ", ".join(key for key in data.keys() if key != "labels")
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain only 'labels' key in data, request contains {keys}.")


class Neo4jRelBetweenLabelsCountQueryRunner(Neo4jQueryRunner):
    from_node_labels: typing.Iterable[str]
    to_node_labels: typing.Iterable[str]
    rel_type: str

    @classmethod
    def get_query_type(cls) -> QueryTypes:
        return QueryTypes.NEO4J_REL_BETWEEN_NODES_COUNT

    def build_queries(self) -> typing.List[str]:
        from_node_labels = ":".join(self.from_node_labels)
        to_node_labels = ":".join(self.to_node_labels)
        return [f"MATCH (:{from_node_labels})-[r:{self.rel_type}]->(:{to_node_labels}) RETURN COUNT(r) AS count"]

    def get_parsed_response(self, *, db_context: DbContext) -> str:
        count = next(self._run_query(db_context=db_context))[0]
        return str(count["count"])

    @classmethod
    def validate_request(cls, data: typing.Mapping[str, typing.Any]) -> None:
        if "from_node_labels" not in data.keys():
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain 'from_node_labels' key in data.")

        if not isinstance(data["from_node_labels"], list):
            raise OutOfSchemaRequest(reason=f"Value of key 'from_node_labels' in data of request with query_type: {cls.get_query_type().value} must be list.")

        if "to_node_labels" not in data.keys():
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain 'to_node_labels' key in data.")

        if not isinstance(data["to_node_labels"], list):
            raise OutOfSchemaRequest(reason=f"Value of key 'to_node_labels' in data of request with query_type: {cls.get_query_type().value} must be list.")

        if "rel_type" not in data.keys():
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain 'rel_type' key in data.")

        if not data["rel_type"]:
            raise OutOfSchemaRequest(reason=f"In request type {cls.get_query_type().value} 'rel_type' value must not be empty.")

        if not isinstance(data["rel_type"], str):
            raise OutOfSchemaRequest(reason=f"Value of key 'to_node_labels' in data of request with query_type: {cls.get_query_type().value} must be list.")

        if len(data.keys()) > 3:
            keys = ", ".join(key for key in data.keys() if key not in ["from_node_labels", "to_node_labels", "rel_type"])
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain only 'labels' key in data, request contains {keys}.")


class Neo4jExplainQueryRunner(Neo4jQueryRunner):
    query: str

    def _run_query(self, *, db_context: DbContext) -> typing.Generator[typing.Any, None, None]:
        with Neo4jUtils.acquire_tx(db_context=db_context) as tx:
            for query in self.build_queries():
                yield tx.run(query).consume().plan

    @classmethod
    def get_query_type(cls) -> QueryTypes:
        return QueryTypes.NEO4J_EXPLAIN_QUERY

    def build_queries(self) -> typing.List[str]:
        return [f"EXPLAIN {self.query}"]

    def get_parsed_response(self, *, db_context: DbContext) -> str:
        plan = next(self._run_query(db_context=db_context))
        return plan["args"]["string-representation"]

    @classmethod
    def validate_request(cls, data: typing.Mapping[str, typing.Any]) -> None:
        if "query" not in data.keys():
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain 'query' key in data.")

        if not isinstance(data["query"], str):
            raise OutOfSchemaRequest(reason=f"Value of key 'labels' in data of request with query_type: {cls.get_query_type().value} must be str.")

        if len(data.keys()) > 1:
            keys = ", ".join(key for key in data.keys() if key != "query")
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain only 'query' key in data, request contains {keys}.")


class Neo4jPropertiesForLabelsRunner(Neo4jQueryRunner):
    labels: typing.Iterable[str]

    @classmethod
    def get_query_type(cls) -> QueryTypes:
        return QueryTypes.NEO4J_PROPERTIES_FOR_LABELS

    def build_queries(self) -> typing.List[str]:
        labels = ":".join(self.labels)
        return [f"MATCH (n:{labels}) WITH n limit 5000 RETURN properties(n) AS props"]

    def get_parsed_response(self, *, db_context: DbContext) -> str:
        nodes_properties = next(self._run_query(db_context=db_context))
        prop_type_counter: typing.DefaultDict[str, Counter] = defaultdict(Counter)
        total_nodes = 0

        for node_properties in nodes_properties:
            total_nodes += 1
            props = node_properties["props"]
            for prop_name, value in props.items():
                typ = type(value).__name__
                prop_type_counter[prop_name][typ] += 1

        stats: typing.Dict[str, typing.List[typing.Mapping[str, str]]] = {}
        for prop, type_counter in prop_type_counter.items():
            stats[prop] = [{"type": typ, "percentage": f"{round((count / total_nodes) * 100, 2)}%"} for typ, count in type_counter.items()]

        return json.dumps(stats)

    @classmethod
    def validate_request(cls, data: typing.Mapping[str, typing.Any]) -> None:
        if "labels" not in data.keys():
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain 'labels' key in data.")

        if not isinstance(data["labels"], list):
            raise OutOfSchemaRequest(reason=f"Value of key 'labels' in data of request with query_type: {cls.get_query_type().value} must be list.")

        if len(data.keys()) > 1:
            keys = ", ".join(key for key in data.keys() if key != "labels")
            raise OutOfSchemaRequest(reason=f"Request with query_type: {cls.get_query_type().value} must contain only 'labels' key in data, request contains {keys}.")
