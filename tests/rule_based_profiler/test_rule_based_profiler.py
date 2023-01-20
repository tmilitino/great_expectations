from typing import Any, Dict, List, Optional
from unittest import mock
from unittest.mock import MagicMock

import pandas as pd
import pytest

import great_expectations.exceptions as gx_exceptions
from great_expectations.core.batch import BatchRequest
from great_expectations.data_context.data_context.cloud_data_context import (
    CloudDataContext,
)
from great_expectations.data_context.store.profiler_store import ProfilerStore
from great_expectations.data_context.types.resource_identifiers import (
    ConfigurationIdentifier,
    GXCloudIdentifier,
)
from great_expectations.exceptions.exceptions import InvalidConfigError
from great_expectations.rule_based_profiler import (
    BaseRuleBasedProfiler,
    RuleBasedProfiler,
    RuleBasedProfilerResult,
)
from great_expectations.rule_based_profiler.config import (
    DomainBuilderConfig,
    ParameterBuilderConfig,
    RuleBasedProfilerConfig,
)
from great_expectations.rule_based_profiler.domain_builder import TableDomainBuilder
from great_expectations.rule_based_profiler.expectation_configuration_builder import (
    DefaultExpectationConfigurationBuilder,
)
from great_expectations.rule_based_profiler.helpers.configuration_reconciliation import (
    ReconciliationDirectives,
    ReconciliationStrategy,
)
from great_expectations.rule_based_profiler.parameter_builder import (
    MetricMultiBatchParameterBuilder,
)
from great_expectations.rule_based_profiler.parameter_container import (
    ParameterContainer,
)
from great_expectations.rule_based_profiler.rule import Rule
from great_expectations.util import deep_filter_properties_iterable


@pytest.fixture()
def sample_rule_dict():
    return {
        "domain_builder": {
            "include_column_names": None,
            "module_name": "great_expectations.rule_based_profiler.domain_builder.column_domain_builder",
            "class_name": "ColumnDomainBuilder",
            "include_column_name_suffixes": ["_amount"],
        },
        "parameter_builders": [],
        "expectation_configuration_builders": [
            {
                "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                "condition": None,
                "expectation_type": "expect_column_values_to_not_be_null",
                "meta": {},
                "column": "$domain.domain_kwargs.column",
                "class_name": "DefaultExpectationConfigurationBuilder",
            }
        ],
    }


@pytest.mark.unit
def test_reconcile_profiler_variables_no_overrides(
    profiler_with_placeholder_args,
    variables_multi_part_name_parameter_container,
):
    variables: Dict[str, Any] = {}
    effective_variables: Optional[
        ParameterContainer
    ] = profiler_with_placeholder_args.reconcile_profiler_variables(variables=variables)
    assert effective_variables == variables_multi_part_name_parameter_container


@pytest.mark.unit
def test_reconcile_profiler_variables_with_overrides(
    profiler_with_placeholder_args,
):
    variables: Dict[str, Any] = {
        "false_positive_threshold": 2.0e-2,
        "estimator": "bootstrap",
        "mostly": 8.0e-1,
    }
    effective_variables: Optional[
        ParameterContainer
    ] = profiler_with_placeholder_args.reconcile_profiler_variables(variables=variables)
    assert effective_variables.to_dict()["parameter_nodes"]["variables"][
        "variables"
    ] == {
        "false_positive_threshold": 2.0e-2,
        "estimator": "bootstrap",
        "mostly": 8.0e-1,
    }


@pytest.mark.unit
def test_reconcile_profiler_rules_no_overrides(
    profiler_with_placeholder_args,
):
    rules: Dict[str, Dict[str, Any]] = {}

    effective_rules: List[
        Rule
    ] = profiler_with_placeholder_args.reconcile_profiler_rules(rules=rules)
    assert effective_rules == profiler_with_placeholder_args.rules


@pytest.mark.unit
def test_reconcile_profiler_rules_new_rule_override(
    profiler_with_placeholder_args,
):
    rules: Dict[str, Dict[str, Any]] = {
        "rule_0": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder",
                "class_name": "ColumnDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_metric",
                },
                {
                    "class_name": "NumericMetricRangeMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder",
                    "name": "my_other_parameter",
                    "metric_name": "my_other_metric",
                    "quantile_statistic_interpolation_method": "auto",
                    "include_estimator_samples_histogram_in_details": False,
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_one_arg": "$parameter.my_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder",
                    "expectation_type": "expect_column_min_to_be_between",
                    "column": "$domain.domain_kwargs.column",
                    "my_another_arg": "$parameter.my_other_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_other_parameter_estimator": "$parameter.my_other_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    expected_rules: Dict[str, dict] = {
        "rule_0": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder.column_domain_builder",
                "class_name": "ColumnDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.metric_multi_batch_parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_metric",
                    "single_batch_mode": False,
                    "enforce_numeric_metric": False,
                    "replace_nan_with_zero": False,
                    "reduce_scalar_metric": True,
                },
                {
                    "class_name": "NumericMetricRangeMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.numeric_metric_range_multi_batch_parameter_builder",
                    "name": "my_other_parameter",
                    "metric_name": "my_other_metric",
                    "estimator": "bootstrap",
                    "enforce_numeric_metric": True,
                    "replace_nan_with_zero": True,
                    "reduce_scalar_metric": True,
                    "false_positive_rate": 0.05,
                    "quantile_statistic_interpolation_method": "auto",
                    "quantile_bias_correction": False,
                    "include_estimator_samples_histogram_in_details": False,
                    "truncate_values": {},
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_one_arg": "$parameter.my_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_min_to_be_between",
                    "column": "$domain.domain_kwargs.column",
                    "my_another_arg": "$parameter.my_other_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_other_parameter_estimator": "$parameter.my_other_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder.table_domain_builder",
                "class_name": "TableDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.metric_multi_batch_parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_metric",
                    "single_batch_mode": False,
                    "enforce_numeric_metric": False,
                    "replace_nan_with_zero": False,
                    "reduce_scalar_metric": True,
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_arg": "$parameter.my_parameter.value[0]",
                    "my_other_arg": "$parameter.my_parameter.value[1]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    effective_rules: List[
        Rule
    ] = profiler_with_placeholder_args.reconcile_profiler_rules(rules=rules)

    rule: Rule
    effective_rule_configs_actual: Dict[str, dict] = {
        rule.name: rule.to_json_dict() for rule in effective_rules
    }
    deep_filter_properties_iterable(effective_rule_configs_actual, inplace=True)

    assert effective_rule_configs_actual == expected_rules


@pytest.mark.unit
def test_reconcile_profiler_rules_existing_rule_domain_builder_override(
    profiler_with_placeholder_args,
):
    rules: Dict[str, Dict[str, Any]] = {
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder",
                "class_name": "ColumnDomainBuilder",
                "include_column_name_suffixes": [
                    "_ts",
                ],
            },
        },
    }

    expected_rules: Dict[str, dict] = {
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder.column_domain_builder",
                "class_name": "ColumnDomainBuilder",
                "include_column_name_suffixes": [
                    "_ts",
                ],
            },
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.metric_multi_batch_parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_metric",
                    "single_batch_mode": False,
                    "enforce_numeric_metric": False,
                    "replace_nan_with_zero": False,
                    "reduce_scalar_metric": True,
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_arg": "$parameter.my_parameter.value[0]",
                    "my_other_arg": "$parameter.my_parameter.value[1]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    effective_rules: List[
        Rule
    ] = profiler_with_placeholder_args.reconcile_profiler_rules(rules=rules)

    rule: Rule
    effective_rule_configs_actual: Dict[str, dict] = {
        rule.name: rule.to_json_dict() for rule in effective_rules
    }
    deep_filter_properties_iterable(effective_rule_configs_actual, inplace=True)

    assert effective_rule_configs_actual == expected_rules


@pytest.mark.unit
def test_reconcile_profiler_rules_existing_rule_parameter_builder_overrides(
    profiler_with_placeholder_args,
):
    rules: Dict[str, Dict[str, Any]] = {
        "rule_1": {
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_special_metric",
                    "single_batch_mode": False,
                    "enforce_numeric_metric": True,
                    "replace_nan_with_zero": True,
                    "reduce_scalar_metric": True,
                },
                {
                    "class_name": "NumericMetricRangeMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder",
                    "name": "my_other_parameter",
                    "metric_name": "my_other_metric",
                    "enforce_numeric_metric": True,
                    "replace_nan_with_zero": False,
                    "reduce_scalar_metric": True,
                    "false_positive_rate": 0.025,
                    "quantile_statistic_interpolation_method": "auto",
                    "include_estimator_samples_histogram_in_details": False,
                },
            ],
        },
    }

    expected_rules: Dict[str, dict] = {
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder.table_domain_builder",
                "class_name": "TableDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.metric_multi_batch_parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_special_metric",
                    "single_batch_mode": False,
                    "enforce_numeric_metric": True,
                    "replace_nan_with_zero": True,
                    "reduce_scalar_metric": True,
                },
                {
                    "class_name": "NumericMetricRangeMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.numeric_metric_range_multi_batch_parameter_builder",
                    "name": "my_other_parameter",
                    "metric_name": "my_other_metric",
                    "estimator": "bootstrap",
                    "enforce_numeric_metric": True,
                    "replace_nan_with_zero": False,
                    "reduce_scalar_metric": True,
                    "false_positive_rate": 0.025,
                    "quantile_statistic_interpolation_method": "auto",
                    "quantile_bias_correction": False,
                    "include_estimator_samples_histogram_in_details": False,
                    "truncate_values": {},
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_arg": "$parameter.my_parameter.value[0]",
                    "my_other_arg": "$parameter.my_parameter.value[1]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    effective_rules: List[
        Rule
    ] = profiler_with_placeholder_args.reconcile_profiler_rules(rules=rules)

    rule: Rule
    effective_rule_configs_actual: Dict[str, dict] = {
        rule.name: rule.to_json_dict() for rule in effective_rules
    }
    deep_filter_properties_iterable(effective_rule_configs_actual, inplace=True)

    assert effective_rule_configs_actual == expected_rules


@pytest.mark.unit
def test_reconcile_profiler_rules_existing_rule_expectation_configuration_builder_overrides(
    profiler_with_placeholder_args,
):
    rules: Dict[str, Dict[str, Any]] = {
        "rule_1": {
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_one_arg": "$parameter.my_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder",
                    "expectation_type": "expect_column_min_to_be_between",
                    "column": "$domain.domain_kwargs.column",
                    "my_another_arg": "$parameter.my_other_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_other_parameter_estimator": "$parameter.my_other_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    expected_rules: Dict[str, dict] = {
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder.table_domain_builder",
                "class_name": "TableDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.metric_multi_batch_parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_metric",
                    "single_batch_mode": False,
                    "enforce_numeric_metric": False,
                    "replace_nan_with_zero": False,
                    "reduce_scalar_metric": True,
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_one_arg": "$parameter.my_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_min_to_be_between",
                    "column": "$domain.domain_kwargs.column",
                    "my_another_arg": "$parameter.my_other_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_other_parameter_estimator": "$parameter.my_other_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    effective_rules: List[
        Rule
    ] = profiler_with_placeholder_args.reconcile_profiler_rules(rules=rules)

    rule: Rule
    effective_rule_configs_actual: Dict[str, dict] = {
        rule.name: rule.to_json_dict() for rule in effective_rules
    }
    deep_filter_properties_iterable(effective_rule_configs_actual, inplace=True)

    assert effective_rule_configs_actual == expected_rules


@pytest.mark.unit
def test_reconcile_profiler_rules_existing_rule_full_rule_override_nested_update(
    profiler_with_placeholder_args,
):
    rules: Dict[str, Dict[str, Any]] = {
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder",
                "class_name": "ColumnDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_metric",
                },
                {
                    "class_name": "NumericMetricRangeMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder",
                    "name": "my_other_parameter",
                    "metric_name": "my_other_metric",
                    "quantile_statistic_interpolation_method": "auto",
                    "include_estimator_samples_histogram_in_details": False,
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_one_arg": "$parameter.my_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder",
                    "expectation_type": "expect_column_min_to_be_between",
                    "column": "$domain.domain_kwargs.column",
                    "my_another_arg": "$parameter.my_other_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_other_parameter_estimator": "$parameter.my_other_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    expected_rules: Dict[str, dict] = {
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder.column_domain_builder",
                "class_name": "ColumnDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.metric_multi_batch_parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_metric",
                    "single_batch_mode": False,
                    "enforce_numeric_metric": False,
                    "replace_nan_with_zero": False,
                    "reduce_scalar_metric": True,
                },
                {
                    "class_name": "NumericMetricRangeMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.numeric_metric_range_multi_batch_parameter_builder",
                    "name": "my_other_parameter",
                    "metric_name": "my_other_metric",
                    "estimator": "bootstrap",
                    "enforce_numeric_metric": True,
                    "replace_nan_with_zero": True,
                    "reduce_scalar_metric": True,
                    "false_positive_rate": 0.05,
                    "quantile_statistic_interpolation_method": "auto",
                    "quantile_bias_correction": False,
                    "include_estimator_samples_histogram_in_details": False,
                    "truncate_values": {},
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_arg": "$parameter.my_parameter.value[0]",
                    "my_other_arg": "$parameter.my_parameter.value[1]",
                    "my_one_arg": "$parameter.my_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_min_to_be_between",
                    "column": "$domain.domain_kwargs.column",
                    "my_another_arg": "$parameter.my_other_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_other_parameter_estimator": "$parameter.my_other_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    effective_rules: List[
        Rule
    ] = profiler_with_placeholder_args.reconcile_profiler_rules(
        rules=rules,
        reconciliation_directives=ReconciliationDirectives(
            domain_builder=ReconciliationStrategy.UPDATE,
            parameter_builder=ReconciliationStrategy.UPDATE,
            expectation_configuration_builder=ReconciliationStrategy.NESTED_UPDATE,
        ),
    )

    rule: Rule
    effective_rule_configs_actual: Dict[str, dict] = {
        rule.name: rule.to_json_dict() for rule in effective_rules
    }
    deep_filter_properties_iterable(effective_rule_configs_actual, inplace=True)

    assert effective_rule_configs_actual == expected_rules


@pytest.mark.unit
def test_reconcile_profiler_rules_existing_rule_full_rule_override_replace(
    profiler_with_placeholder_args,
):
    rules: Dict[str, Dict[str, Any]] = {
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder",
                "class_name": "ColumnDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "NumericMetricRangeMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder",
                    "name": "my_other_parameter",
                    "metric_name": "my_other_metric",
                    "quantile_statistic_interpolation_method": "auto",
                    "include_estimator_samples_histogram_in_details": False,
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder",
                    "expectation_type": "expect_column_min_to_be_between",
                    "column": "$domain.domain_kwargs.column",
                    "my_another_arg": "$parameter.my_other_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_other_parameter_estimator": "$parameter.my_other_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    expected_rules: Dict[str, Dict] = {
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder.column_domain_builder",
                "class_name": "ColumnDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "NumericMetricRangeMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.numeric_metric_range_multi_batch_parameter_builder",
                    "name": "my_other_parameter",
                    "metric_name": "my_other_metric",
                    "estimator": "bootstrap",
                    "enforce_numeric_metric": True,
                    "replace_nan_with_zero": True,
                    "reduce_scalar_metric": True,
                    "false_positive_rate": 0.05,
                    "quantile_statistic_interpolation_method": "auto",
                    "quantile_bias_correction": False,
                    "include_estimator_samples_histogram_in_details": False,
                    "truncate_values": {},
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_min_to_be_between",
                    "column": "$domain.domain_kwargs.column",
                    "my_another_arg": "$parameter.my_other_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_other_parameter_estimator": "$parameter.my_other_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    effective_rules: List[
        Rule
    ] = profiler_with_placeholder_args.reconcile_profiler_rules(
        rules=rules,
        reconciliation_directives=ReconciliationDirectives(
            domain_builder=ReconciliationStrategy.UPDATE,
            parameter_builder=ReconciliationStrategy.REPLACE,
            expectation_configuration_builder=ReconciliationStrategy.REPLACE,
        ),
    )

    rule: Rule
    effective_rule_configs_actual: Dict[str, dict] = {
        rule.name: rule.to_json_dict() for rule in effective_rules
    }
    deep_filter_properties_iterable(effective_rule_configs_actual, inplace=True)

    assert effective_rule_configs_actual == expected_rules


@pytest.mark.unit
def test_reconcile_profiler_rules_existing_rule_full_rule_override_update(
    profiler_with_placeholder_args,
):
    rules: Dict[str, Dict[str, Any]] = {
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder",
                "class_name": "ColumnDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_metric",
                },
                {
                    "class_name": "NumericMetricRangeMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder",
                    "name": "my_other_parameter",
                    "metric_name": "my_other_metric",
                    "quantile_statistic_interpolation_method": "auto",
                    "include_estimator_samples_histogram_in_details": False,
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_one_arg": "$parameter.my_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder",
                    "expectation_type": "expect_column_min_to_be_between",
                    "column": "$domain.domain_kwargs.column",
                    "my_another_arg": "$parameter.my_other_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_other_parameter_estimator": "$parameter.my_other_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    expected_rules: Dict[str, dict] = {
        "rule_1": {
            "variables": {},
            "domain_builder": {
                "module_name": "great_expectations.rule_based_profiler.domain_builder.column_domain_builder",
                "class_name": "ColumnDomainBuilder",
            },
            "parameter_builders": [
                {
                    "class_name": "MetricMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.metric_multi_batch_parameter_builder",
                    "name": "my_parameter",
                    "metric_name": "my_metric",
                    "single_batch_mode": False,
                    "enforce_numeric_metric": False,
                    "replace_nan_with_zero": False,
                    "reduce_scalar_metric": True,
                },
                {
                    "class_name": "NumericMetricRangeMultiBatchParameterBuilder",
                    "module_name": "great_expectations.rule_based_profiler.parameter_builder.numeric_metric_range_multi_batch_parameter_builder",
                    "name": "my_other_parameter",
                    "metric_name": "my_other_metric",
                    "estimator": "bootstrap",
                    "enforce_numeric_metric": True,
                    "replace_nan_with_zero": True,
                    "reduce_scalar_metric": True,
                    "false_positive_rate": 0.05,
                    "quantile_statistic_interpolation_method": "auto",
                    "quantile_bias_correction": False,
                    "include_estimator_samples_histogram_in_details": False,
                    "truncate_values": {},
                },
            ],
            "expectation_configuration_builders": [
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    "column_A": "$domain.domain_kwargs.column_A",
                    "column_B": "$domain.domain_kwargs.column_B",
                    "my_one_arg": "$parameter.my_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_parameter_estimator": "$parameter.my_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
                {
                    "class_name": "DefaultExpectationConfigurationBuilder",
                    "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
                    "expectation_type": "expect_column_min_to_be_between",
                    "column": "$domain.domain_kwargs.column",
                    "my_another_arg": "$parameter.my_other_parameter.value[0]",
                    "meta": {
                        "profiler_details": {
                            "my_other_parameter_estimator": "$parameter.my_other_parameter.details",
                            "note": "Important remarks about estimation algorithm.",
                        },
                    },
                },
            ],
        },
    }

    effective_rules: List[
        Rule
    ] = profiler_with_placeholder_args.reconcile_profiler_rules(rules=rules)

    rule: Rule
    effective_rule_configs_actual: Dict[str, dict] = {
        rule.name: rule.to_json_dict() for rule in effective_rules
    }
    deep_filter_properties_iterable(effective_rule_configs_actual, inplace=True)

    assert effective_rule_configs_actual == expected_rules


@mock.patch("great_expectations.rule_based_profiler.RuleBasedProfiler.run")
@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_run_profiler_without_dynamic_args(
    mock_data_context: mock.MagicMock,
    mock_profiler_run: mock.MagicMock,
    populated_profiler_store: ProfilerStore,
    profiler_name: str,
):
    RuleBasedProfiler.run_profiler(
        data_context=mock_data_context,
        profiler_store=populated_profiler_store,
        name=profiler_name,
    )

    assert mock_profiler_run.called
    assert mock_profiler_run.call_args == mock.call(
        variables=None,
        rules=None,
        batch_list=None,
        batch_request=None,
        runtime_configuration=None,
        reconciliation_directives=ReconciliationDirectives(
            variables=ReconciliationStrategy.UPDATE,
            domain_builder=ReconciliationStrategy.UPDATE,
            parameter_builder=ReconciliationStrategy.UPDATE,
            expectation_configuration_builder=ReconciliationStrategy.UPDATE,
        ),
        variables_directives_list=None,
        domain_type_directives_list=None,
        comment=None,
    )


@mock.patch("great_expectations.rule_based_profiler.RuleBasedProfiler.run")
@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_run_profiler_with_dynamic_args(
    mock_data_context: mock.MagicMock,
    mock_profiler_run: mock.MagicMock,
    populated_profiler_store: ProfilerStore,
    profiler_name: str,
):
    # Dynamic arguments used to override the profiler's attributes
    variables = {"foo": "bar"}
    rules = {"baz": "qux"}

    # noinspection PyUnusedLocal
    rule_based_profiler_result: RuleBasedProfilerResult = (
        RuleBasedProfiler.run_profiler(
            data_context=mock_data_context,
            profiler_store=populated_profiler_store,
            name=profiler_name,
            variables=variables,
            rules=rules,
        )
    )

    assert mock_profiler_run.called
    assert mock_profiler_run.call_args == mock.call(
        variables=variables,
        rules=rules,
        batch_list=None,
        batch_request=None,
        runtime_configuration=None,
        reconciliation_directives=ReconciliationDirectives(
            variables=ReconciliationStrategy.UPDATE,
            domain_builder=ReconciliationStrategy.UPDATE,
            parameter_builder=ReconciliationStrategy.UPDATE,
            expectation_configuration_builder=ReconciliationStrategy.UPDATE,
        ),
        variables_directives_list=None,
        domain_type_directives_list=None,
        comment=None,
    )


@mock.patch("great_expectations.rule_based_profiler.RuleBasedProfiler.run")
@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_run_profiler_on_data_creates_suite_with_dict_arg(
    mock_data_context: mock.MagicMock,
    mock_rule_based_profiler_run: mock.MagicMock,
    populated_profiler_store: ProfilerStore,
    profiler_name: str,
):
    batch_request: Dict[str, str] = {
        "datasource_name": "my_datasource",
        "data_connector_name": "my_data_connector",
        "data_asset_name": "my_data_asset",
    }

    RuleBasedProfiler.run_profiler_on_data(
        data_context=mock_data_context,
        profiler_store=populated_profiler_store,
        name=profiler_name,
        batch_request=batch_request,
    )

    assert mock_rule_based_profiler_run.called

    resulting_batch_request = mock_rule_based_profiler_run.call_args[1]["batch_request"]
    assert resulting_batch_request == batch_request


@mock.patch("great_expectations.rule_based_profiler.RuleBasedProfiler.run")
@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_run_profiler_on_data_creates_suite_with_batch_request_arg(
    mock_data_context: mock.MagicMock,
    mock_rule_based_profiler_run: mock.MagicMock,
    populated_profiler_store: ProfilerStore,
    profiler_name: str,
):
    batch_request: BatchRequest = BatchRequest(
        datasource_name="my_datasource",
        data_connector_name="my_data_connector",
        data_asset_name="my_data_asset",
    )

    RuleBasedProfiler.run_profiler_on_data(
        data_context=mock_data_context,
        profiler_store=populated_profiler_store,
        name=profiler_name,
        batch_request=batch_request,
    )

    assert mock_rule_based_profiler_run.called

    resulting_batch_request: dict = mock_rule_based_profiler_run.call_args[1][
        "batch_request"
    ].to_json_dict()
    deep_filter_properties_iterable(resulting_batch_request, inplace=True)
    expected_batch_request: dict = batch_request.to_json_dict()
    deep_filter_properties_iterable(expected_batch_request, inplace=True)
    assert resulting_batch_request == expected_batch_request


@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_get_profiler_with_too_many_args_raises_error(
    mock_data_context: mock.MagicMock,
    populated_profiler_store: ProfilerStore,
):
    with pytest.raises(AssertionError) as e:
        RuleBasedProfiler.get_profiler(
            data_context=mock_data_context,
            profiler_store=populated_profiler_store,
            name="my_profiler",
            ge_cloud_id="my_ge_cloud_id",
        )

    assert "either name or ge_cloud_id" in str(e.value)


@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_serialize_profiler_config(
    mock_data_context: mock.MagicMock,
    profiler_config_with_placeholder_args: RuleBasedProfilerConfig,
):
    profiler = BaseRuleBasedProfiler(
        profiler_config=profiler_config_with_placeholder_args,
        data_context=mock_data_context,
    )
    assert profiler.config == profiler_config_with_placeholder_args
    assert len(profiler.rules) == 1
    assert isinstance(profiler.rules[0].domain_builder, TableDomainBuilder)
    assert DomainBuilderConfig(
        **profiler.rules[0].domain_builder.to_json_dict()
    ).to_json_dict() == {
        "module_name": "great_expectations.rule_based_profiler.domain_builder.table_domain_builder",
        "class_name": "TableDomainBuilder",
    }
    assert isinstance(
        profiler.rules[0].parameter_builders[0], MetricMultiBatchParameterBuilder
    )
    assert ParameterBuilderConfig(
        **profiler.rules[0].parameter_builders[0].to_json_dict()
    ).to_json_dict() == {
        "module_name": "great_expectations.rule_based_profiler.parameter_builder.metric_multi_batch_parameter_builder",
        "class_name": "MetricMultiBatchParameterBuilder",
        "name": "my_parameter",
        "metric_name": "my_metric",
        "metric_domain_kwargs": None,
        "metric_value_kwargs": None,
        "single_batch_mode": False,
        "enforce_numeric_metric": False,
        "replace_nan_with_zero": False,
        "reduce_scalar_metric": True,
        "evaluation_parameter_builder_configs": None,
    }
    assert isinstance(
        profiler.rules[0].expectation_configuration_builders[0],
        DefaultExpectationConfigurationBuilder,
    )
    assert DefaultExpectationConfigurationBuilder(
        **profiler.rules[0].expectation_configuration_builders[0].to_json_dict()
    ).to_json_dict() == {
        "module_name": "great_expectations.rule_based_profiler.expectation_configuration_builder.default_expectation_configuration_builder",
        "class_name": "DefaultExpectationConfigurationBuilder",
        "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
        "validation_parameter_builder_configs": None,
        "column_A": "$domain.domain_kwargs.column_A",
        "column_B": "$domain.domain_kwargs.column_B",
        "condition": None,
        "my_arg": "$parameter.my_parameter.value[0]",
        "my_other_arg": "$parameter.my_parameter.value[1]",
        "meta": {
            "profiler_details": {
                "my_parameter_estimator": "$parameter.my_parameter.details",
                "note": "Important remarks about estimation algorithm.",
            },
        },
    }


@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_add_profiler(
    mock_data_context: mock.MagicMock,
    profiler_key: ConfigurationIdentifier,
    profiler_config_with_placeholder_args: RuleBasedProfilerConfig,
):
    mock_data_context.cloud_mode = False
    profiler: RuleBasedProfiler = RuleBasedProfiler.add_profiler(
        profiler_config_with_placeholder_args,
        data_context=mock_data_context,
        profiler_store=mock_data_context.profiler_store,
    )

    assert isinstance(profiler, RuleBasedProfiler)
    assert profiler.name == profiler_config_with_placeholder_args.name
    assert mock_data_context.profiler_store.set.call_args == mock.call(
        key=profiler_key, value=profiler_config_with_placeholder_args
    )


@pytest.mark.cloud
@pytest.mark.unit
def test_add_profiler_ge_cloud_mode(
    ge_cloud_profiler_id: str,
    ge_cloud_profiler_key: GXCloudIdentifier,
    profiler_config_with_placeholder_args: RuleBasedProfilerConfig,
):
    with mock.patch(
        "great_expectations.data_context.data_context.CloudDataContext",
        spec=CloudDataContext,
    ) as mock_data_context:
        profiler: RuleBasedProfiler = RuleBasedProfiler.add_profiler(
            profiler_config_with_placeholder_args,
            data_context=mock_data_context,
            profiler_store=mock_data_context.profiler_store,
        )

    assert isinstance(profiler, RuleBasedProfiler)
    assert profiler.name == profiler_config_with_placeholder_args.name
    assert mock_data_context.profiler_store.set.call_args == mock.call(
        key=ge_cloud_profiler_key, value=profiler_config_with_placeholder_args
    )


@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_add_profiler_with_batch_request_containing_batch_data_raises_error(
    mock_data_context: mock.MagicMock,
):
    profiler_config = RuleBasedProfilerConfig(
        name="my_profiler_config",
        config_version=1.0,
        rules={
            "rule_1": {
                "domain_builder": {
                    "class_name": "TableDomainBuilder",
                    "batch_request": {
                        "runtime_parameters": {
                            "batch_data": pd.DataFrame()  # Cannot be serialized in store
                        }
                    },
                },
                "parameter_builders": [
                    {
                        "class_name": "MetricMultiBatchParameterBuilder",
                        "name": "my_parameter",
                        "metric_name": "my_metric",
                    },
                ],
                "expectation_configuration_builders": [
                    {
                        "class_name": "DefaultExpectationConfigurationBuilder",
                        "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                    },
                ],
            }
        },
    )

    with pytest.raises(InvalidConfigError) as e:
        RuleBasedProfiler.add_profiler(
            profiler_config,
            data_context=mock_data_context,
            profiler_store=mock_data_context.profiler_store,
        )

    assert "batch_data found in batch_request" in str(e.value)


@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_get_profiler(
    mock_data_context: mock.MagicMock,
    populated_profiler_store: ProfilerStore,
    profiler_config_with_placeholder_args: RuleBasedProfilerConfig,
):
    with mock.patch(
        "great_expectations.data_context.store.profiler_store.ProfilerStore.get",
        return_value=profiler_config_with_placeholder_args,
    ):
        profiler: RuleBasedProfiler = RuleBasedProfiler.get_profiler(
            data_context=mock_data_context,
            profiler_store=populated_profiler_store,
            name="my_profiler",
            ge_cloud_id=None,
        )

    assert isinstance(profiler, RuleBasedProfiler)


@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_get_profiler_non_existent_profiler_raises_error(
    mock_data_context: mock.MagicMock, empty_profiler_store: ProfilerStore
):
    with pytest.raises(gx_exceptions.ProfilerNotFoundError) as e:
        RuleBasedProfiler.get_profiler(
            data_context=mock_data_context,
            profiler_store=empty_profiler_store,
            name="my_profiler",
            ge_cloud_id=None,
        )

    assert "Non-existent Profiler" in str(e.value)


@pytest.mark.unit
def test_delete_profiler(
    populated_profiler_store: ProfilerStore,
):
    with mock.patch(
        "great_expectations.data_context.store.profiler_store.ProfilerStore.remove_key",
    ) as mock_remove_key:
        RuleBasedProfiler.delete_profiler(
            profiler_store=populated_profiler_store,
            name="my_profiler",
            ge_cloud_id=None,
        )

    assert mock_remove_key.call_count == 1
    assert mock_remove_key.call_args == mock.call(
        key=ConfigurationIdentifier("my_profiler")
    )


@pytest.mark.unit
def test_delete_profiler_with_too_many_args_raises_error(
    populated_profiler_store: ProfilerStore,
):
    with pytest.raises(AssertionError) as e:
        RuleBasedProfiler.delete_profiler(
            profiler_store=populated_profiler_store,
            name="my_profiler",
            ge_cloud_id="my_ge_cloud_id",
        )

    assert "either name or ge_cloud_id" in str(e.value)


@pytest.mark.unit
def test_delete_profiler_non_existent_profiler_raises_error(
    populated_profiler_store: ProfilerStore,
):
    with pytest.raises(gx_exceptions.ProfilerNotFoundError) as e:
        RuleBasedProfiler.delete_profiler(
            profiler_store=populated_profiler_store,
            name="my_non_existent_profiler",
            ge_cloud_id=None,
        )

    assert "Non-existent Profiler" in str(e.value)


@mock.patch("great_expectations.data_context.store.ProfilerStore")
@pytest.mark.unit
def test_list_profilers(mock_profiler_store: mock.MagicMock):
    store = mock_profiler_store()
    keys = ["a", "b", "c"]
    store.list_keys.return_value = [ConfigurationIdentifier(char) for char in keys]
    res = RuleBasedProfiler.list_profilers(store, ge_cloud_mode=False)

    assert res == keys
    assert store.list_keys.called


@mock.patch("great_expectations.data_context.store.ProfilerStore")
@pytest.mark.cloud
@pytest.mark.unit
def test_list_profilers_in_cloud_mode(mock_profiler_store: mock.MagicMock):
    store = mock_profiler_store()
    keys = ["a", "b", "c"]
    store.list_keys.return_value = keys
    res = RuleBasedProfiler.list_profilers(store, ge_cloud_mode=True)

    assert res == keys
    assert store.list_keys.called


@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@mock.patch("great_expectations.rule_based_profiler.domain_builder.ColumnDomainBuilder")
@mock.patch(
    "great_expectations.rule_based_profiler.expectation_configuration_builder.DefaultExpectationConfigurationBuilder"
)
@pytest.mark.unit
def test_add_single_rule(
    mock_expectation_configuration_builder: mock.MagicMock,
    mock_domain_builder: mock.MagicMock,
    mock_data_context: mock.MagicMock,
    sample_rule_dict: dict,
):
    profiler: RuleBasedProfiler = RuleBasedProfiler(
        name="my_rbp",
        config_version=1.0,
        data_context=mock_data_context,
    )
    first_rule = Rule(
        name="first_rule",
        variables=None,
        domain_builder=mock_domain_builder,
        expectation_configuration_builders=mock_expectation_configuration_builder,
    )
    first_rule.to_json_dict = MagicMock(return_value=sample_rule_dict)
    profiler.add_rule(rule=first_rule)
    assert len(profiler.rules) == 1

    duplicate_of_first_rule = Rule(
        name="first_rule",
        variables=None,
        domain_builder=mock_domain_builder,
        expectation_configuration_builders=mock_expectation_configuration_builder,
    )
    duplicate_of_first_rule.to_json_dict = MagicMock(return_value=sample_rule_dict)
    profiler.add_rule(rule=duplicate_of_first_rule)
    assert len(profiler.rules) == 1


@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@mock.patch("great_expectations.rule_based_profiler.domain_builder.ColumnDomainBuilder")
@mock.patch(
    "great_expectations.rule_based_profiler.expectation_configuration_builder.DefaultExpectationConfigurationBuilder"
)
@pytest.mark.unit
def test_add_rule_overwrite_first_rule(
    mock_expectation_configuration_builder: mock.MagicMock,
    mock_domain_builder: mock.MagicMock,
    mock_data_context: mock.MagicMock,
    sample_rule_dict: dict,
):

    profiler: RuleBasedProfiler = RuleBasedProfiler(
        name="my_rbp",
        config_version=1.0,
        data_context=mock_data_context,
    )
    first_rule = Rule(
        name="first_rule",
        variables=None,
        domain_builder=mock_domain_builder,
        expectation_configuration_builders=mock_expectation_configuration_builder,
    )
    first_rule.to_json_dict = MagicMock(return_value=sample_rule_dict)
    profiler.add_rule(rule=first_rule)
    assert len(profiler.rules) == 1


@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@mock.patch("great_expectations.rule_based_profiler.domain_builder.ColumnDomainBuilder")
@mock.patch(
    "great_expectations.rule_based_profiler.expectation_configuration_builder.DefaultExpectationConfigurationBuilder"
)
@pytest.mark.unit
def test_add_rule_add_second_rule(
    mock_expectation_configuration_builder: mock.MagicMock,
    mock_domain_builder: mock.MagicMock,
    mock_data_context: mock.MagicMock,
    sample_rule_dict: dict,
):
    profiler: RuleBasedProfiler = RuleBasedProfiler(
        name="my_rbp",
        config_version=1.0,
        data_context=mock_data_context,
    )
    first_rule = Rule(
        name="first_rule",
        variables=None,
        domain_builder=mock_domain_builder,
        expectation_configuration_builders=mock_expectation_configuration_builder,
    )
    first_rule.to_json_dict = MagicMock(return_value=sample_rule_dict)
    profiler.add_rule(rule=first_rule)
    assert len(profiler.rules) == 1

    second_rule = Rule(
        name="second_rule",
        variables=None,
        domain_builder=mock_domain_builder,
        expectation_configuration_builders=mock_expectation_configuration_builder,
    )
    second_rule.to_json_dict = MagicMock(return_value=sample_rule_dict)
    profiler.add_rule(rule=second_rule)
    assert len(profiler.rules) == 2


@mock.patch("great_expectations.data_context.data_context.AbstractDataContext")
@pytest.mark.unit
def test_add_rule_bad_rule(
    mock_data_context: mock.MagicMock,
):
    profiler: RuleBasedProfiler = RuleBasedProfiler(
        name="my_rbp",
        config_version=1.0,
        data_context=mock_data_context,
    )
    not_a_rule: dict = {
        "name": "first_rule",
        "domain_builder": "domain_builder",
        "expectation_configuration_builder": "expectation_configuration_builder",
    }
    with pytest.raises(AttributeError) as e:
        # noinspection PyTypeChecker
        profiler.add_rule(rule=not_a_rule)
    assert "'dict' object has no attribute 'name'" in str(e.value)
