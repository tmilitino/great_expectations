from typing import Dict, Optional

from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.exceptions.exceptions import (
    InvalidExpectationConfigurationError,
)
from great_expectations.expectations.regex_based_column_map_expectation import (
    RegexBasedColumnMapExpectation,
    RegexColumnMapMetricProvider,
)


# <snippet name="tests/integration/docusaurus/expectations/creating_custom_expectations/expect_column_values_to_only_contain_vowels.py ExpectColumnValuesToOnlyContainVowels class_def">
class ExpectColumnValuesToOnlyContainVowels(RegexBasedColumnMapExpectation):
    # </snippet>
    """Values in this column should only contain vowels"""

    regex_camel_name = "Vowel"
    regex = "^[aeiouyAEIOUY]*$"
    semantic_type_name_plural = "vowels"

    examples = [
        {
            "data": {
                "only_vowels": ["a", "e", "I", "O", "U", "y", ""],
                "mixed": ["A", "b", "c", "D", "E", "F", "g"],
                "longer_vowels": ["aei", "YAY", "oYu", "eee", "", "aeIOUY", None],
                "contains_vowels_but_also_other_stuff": [
                    "baa",
                    "aba",
                    "aab",
                    "1a1",
                    "a a",
                    " ",
                    "*",
                ],
            },
            "tests": [
                {
                    "title": "positive_test",
                    "exact_match_out": False,
                    "in": {"column": "only_vowels"},
                    "out": {
                        "success": True,
                    },
                    "include_in_gallery": True,
                },
                {
                    "title": "negative_test",
                    "exact_match_out": False,
                    "in": {"column": "mixed"},
                    "out": {
                        "success": False,
                        "unexpected_index_list": [1, 2, 3, 5, 6],
                    },
                    "include_in_gallery": True,
                },
                {
                    "title": "another_postive_test",
                    "exact_match_out": False,
                    "in": {"column": "longer_vowels"},
                    "out": {
                        "success": True,
                    },
                    "include_in_gallery": True,
                },
                {
                    "title": "another_negative_test",
                    "exact_match_out": False,
                    "in": {"column": "contains_vowels_but_also_other_stuff"},
                    "out": {
                        "success": False,
                        "unexpected_index_list": [0, 1, 2, 3, 4, 5, 6],
                    },
                    "include_in_gallery": True,
                },
                {
                    "title": "mostly_positive_test",
                    "exact_match_out": False,
                    "in": {"column": "mixed", "mostly": 0.1},
                    "out": {
                        "success": True,
                    },
                    "include_in_gallery": True,
                },
                {
                    "title": "mostly_negative_test",
                    "exact_match_out": False,
                    "in": {"column": "mixed", "mostly": 0.3},
                    "out": {
                        "success": False,
                    },
                    "include_in_gallery": True,
                },
            ],
            "test_backends": [
                {
                    "backend": "pandas",
                    "dialects": None,
                },
                {
                    "backend": "sqlalchemy",
                    "dialects": ["sqlite", "postgresql"],
                },
                {
                    "backend": "spark",
                    "dialects": None,
                },
            ],
        }
    ]

    map_metric = RegexBasedColumnMapExpectation.register_metric(
        regex_camel_name=regex_camel_name,
        regex_=regex,
    )

    library_metadata = {
        "tags": ["regex"],
        "contributors": ["@joegargery"],
    }


# </snippet>
if __name__ == "__main__":
    ExpectColumnValuesToOnlyContainVowels().print_diagnostic_checklist()

# Note to users: code below this line is only for integration testing -- ignore!

diagnostics = ExpectColumnValuesToOnlyContainVowels().run_diagnostics()

for check in diagnostics["tests"]:
    assert check["test_passed"] is True
    assert check["error_diagnostics"] is None

for check in diagnostics["errors"]:
    assert check is None

for check in diagnostics["maturity_checklist"]["experimental"]:
    if check["message"] == "Passes all linting checks":
        continue
    assert check["passed"] is True
