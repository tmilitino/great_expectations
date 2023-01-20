from great_expectations.expectations.regex_based_column_map_expectation import (
    RegexBasedColumnMapExpectation,
)


class ExpectColumnValuesToBeValidArn(RegexBasedColumnMapExpectation):
    """Expect values in this column to be a valid amazon arn."""

    # These values will be used to configure the metric created by your expectation
    regex_camel_name = "AmazonResourceName"
    regex = r"^arn:([^:\n]*):([^:\n]*):([^:\n]*):([^:\n]*):(([^:\/\n]*)[:\/])?(.*)$"
    semantic_type_name_plural = "arns"

    # These examples will be shown in the public gallery.
    # They will also be executed as unit tests for your Expectation.
    examples = [
        {
            "data": {
                "valid_arns": [
                    "arn:aws:s3:::my-bucket/my-object",
                    "arn:partition:service:region:account-id:resource",
                ],
                "invalid_alphanumeric": [
                    "apz8",
                    "bubba:arn:123",
                ],
                "invalid_arn": [
                    "arn:aws:::::::my-bucket/my-object",
                    "arn::::",
                ],
                "empty": ["", None],
            },
            "suppress_test_for": ["mssql", "bigquery", "snowflake"],
            "tests": [
                {
                    "title": "basic_positive_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "valid_arns"},
                    "out": {
                        "success": True,
                    },
                },
                {
                    "title": "basic_negative_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "invalid_alphanumeric", "mostly": 1},
                    "out": {
                        "success": False,
                    },
                },
                {
                    "title": "invalid_non_alphanumeric",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "invalid_arn", "mostly": 1},
                    "out": {
                        "success": False,
                    },
                },
                {
                    "title": "empty",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "empty", "mostly": 1},
                    "out": {
                        "success": False,
                    },
                },
            ],
        }
    ]

    # Here your regex is used to create a custom metric for this expectation
    map_metric = RegexBasedColumnMapExpectation.register_metric(
        regex_camel_name=regex_camel_name,
        regex_=regex,
    )

    # This object contains metadata for display in the public Gallery
    library_metadata = {
        "maturity": "experimental",
        "tags": [
            "amazon",
            "arn",
            "expectation",
        ],  # Tags for this Expectation in the Gallery
        "contributors": [  # Github handles for all contributors to this Expectation.
            "@rdodev",  # Don't forget to add your github handle here!
            "@mkopec87",
        ],
    }


if __name__ == "__main__":
    ExpectColumnValuesToBeValidArn().print_diagnostic_checklist()
