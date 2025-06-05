import unittest
from typing import Dict, Any
from pydantic import ValidationError

from ..src.opti_query.optipy.definitions import OptimizedQuery, OptimizationResponse
from ..src.opti_query.optipy.exceptions import OutOfSchemaRequest


# from src.optipy.definitions import OptiModel, OptimizedQuery, OptimizationResponse, OutOfSchemaRequest


class TestOptimizedQuery(unittest.TestCase):
    def test_validate_request_success(self):
        data: Dict[str, Any] = {"query": "test query", "explanation": "test explanation"}
        try:
            OptimizedQuery.validate_request(data)
        except Exception as e:
            self.fail(f"validate_request raised {e} unexpectedly")

    def test_validate_request_missing_query(self):
        data: Dict[str, Any] = {"explanation": "test explanation"}
        with self.assertRaises(OutOfSchemaRequest) as context:
            OptimizedQuery.validate_request(data)
        self.assertEqual(
            str(context.exception.reason),
            "Request with query_type: OPTIMIZE_FINISHED data must contain 'query' key its optimized_queries_and_explains field.",
        )

    def test_validate_request_invalid_query_type(self):
        data: Dict[str, Any] = {"query": 123, "explanation": "test explanation"}
        with self.assertRaises(OutOfSchemaRequest) as context:
            OptimizedQuery.validate_request(data)
        self.assertEqual(
            str(context.exception.reason),
            "'query' key in data of request type OPTIMIZE_FINISHED must be str",
        )

    def test_validate_request_missing_explanation(self):
        data: Dict[str, Any] = {"query": "test query"}
        with self.assertRaises(OutOfSchemaRequest) as context:
            OptimizedQuery.validate_request(data)
        self.assertEqual(
            str(context.exception.reason),
            "Request with query_type: OPTIMIZE_FINISHED data must contain 'explanation' key its optimized_queries_and_explains field.",
        )

    def test_validate_request_invalid_explanation_type(self):
        data: Dict[str, Any] = {"query": "test query", "explanation": 123}
        with self.assertRaises(OutOfSchemaRequest) as context:
            OptimizedQuery.validate_request(data)
        self.assertEqual(
            str(context.exception.reason),
            "'explanation' key in data of request type OPTIMIZE_FINISHED must be str",
        )


class TestOptimizationResponse(unittest.TestCase):
    def test_validate_request_success(self):
        data: Dict[str, Any] = {
            "optimized_queries_and_explains": [{"query": "test query", "explanation": "test explanation"}],
            "suggestions": ["test suggestion"],
        }
        try:
            OptimizationResponse.validate_request(data)
        except Exception as e:
            self.fail(f"validate_request raised {e} unexpectedly")

    def test_validate_request_missing_optimized_queries(self):
        data: Dict[str, Any] = {"suggestions": ["test suggestion"]}
        with self.assertRaises(OutOfSchemaRequest) as context:
            OptimizationResponse.validate_request(data)
        self.assertEqual(
            str(context.exception.reason),
            "Request with query_type: OPTIMIZE_FINISHED must contain 'optimized_queries_and_explains' key in data.",
        )

    def test_validate_request_missing_suggestions(self):
        data: Dict[str, Any] = {
            "optimized_queries_and_explains": [{"query": "test query", "explanation": "test explanation"}]
        }
        with self.assertRaises(OutOfSchemaRequest) as context:
            OptimizationResponse.validate_request(data)
        self.assertEqual(
            str(context.exception.reason),
            "Request with query_type: OPTIMIZE_FINISHED must contain 'suggestions' key in data.",
        )

    def test_validate_request_invalid_suggestions_type(self):
        data: Dict[str, Any] = {"optimized_queries_and_explains": [], "suggestions": 123}
        with self.assertRaises(OutOfSchemaRequest) as context:
            OptimizationResponse.validate_request(data)
        self.assertEqual(
            str(context.exception.reason),
            "Value of key 'labels' in data of request with query_type: OPTIMIZE_FINISHED must be list of str.",
        )

    def test_validate_request_invalid_optimized_queries_content(self):
        data: Dict[str, Any] = {"optimized_queries_and_explains": [{"query": 123, "explanation": "test"}], "suggestions": []}
        with self.assertRaises(OutOfSchemaRequest) as context:
            OptimizationResponse.validate_request(data)
        self.assertEqual(
            str(context.exception.reason),
            "'query' key in data of request type OPTIMIZE_FINISHED must be str",
        )