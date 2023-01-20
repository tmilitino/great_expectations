from typing import Any, Dict, List

import pandas as pd
import pytest

from great_expectations.execution_engine.sparkdf_batch_data import SparkDFBatchData

try:
    sqlalchemy = pytest.importorskip("sqlalchemy")
except ImportError:
    sqlalchemy = None

import great_expectations.exceptions as gx_exceptions
from great_expectations.core.batch import (
    Batch,
    BatchDefinition,
    IDDict,
    RuntimeBatchRequest,
)
from great_expectations.core.yaml_handler import YAMLHandler
from great_expectations.data_context.util import instantiate_class_from_config
from great_expectations.datasource.new_datasource import Datasource

yaml = YAMLHandler()


@pytest.fixture
def datasource_with_runtime_data_connector_and_sparkdf_execution_engine(
    spark_session, test_backends
):
    if "sqlite" not in test_backends:
        pytest.skip("skipping fixture because sqlite not selected")

    basic_datasource: Datasource = instantiate_class_from_config(
        yaml.load(
            """
    class_name: Datasource

    execution_engine:
        class_name: SparkDFExecutionEngine

    data_connectors:
        test_runtime_data_connector:
            module_name: great_expectations.datasource.data_connector
            class_name: RuntimeDataConnector
            batch_identifiers:
                - pipeline_stage_name
                - airflow_run_id
                - custom_key_0
            assets:
                asset_a:
                    batch_identifiers:
                        - day
                        - month
                asset_b:
                    batch_identifiers:
                        - day
                        - month
                        - year
        """,
        ),
        runtime_environment={"name": "my_datasource"},
        config_defaults={"module_name": "great_expectations.datasource"},
    )
    return basic_datasource


#########################################
# Tests with data passed in as batch_data
#########################################

# Tests with SparkDFExecutionEngine : batch_data


def test_sparkdf_execution_engine_self_check(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    report = (
        datasource_with_runtime_data_connector_and_sparkdf_execution_engine.self_check()
    )
    assert report["data_connectors"] == {
        "count": 1,
        "test_runtime_data_connector": {
            "class_name": "RuntimeDataConnector",
            "data_asset_count": 2,
            "data_assets": {
                "asset_a": {
                    "batch_definition_count": 0,
                    "example_data_references": [],
                },
                "asset_b": {
                    "batch_definition_count": 0,
                    "example_data_references": [],
                },
            },
            "example_data_asset_names": ["asset_a", "asset_b"],
            "example_unmatched_data_references": [],
            "unmatched_data_reference_count": 0,
        },
    }
    assert report["execution_engine"]["caching"] is True
    assert report["execution_engine"]["class_name"] == "SparkDFExecutionEngine"
    assert (
        report["execution_engine"]["module_name"]
        == "great_expectations.execution_engine.sparkdf_execution_engine"
    )


def test_batch_data_sparkdf_execution_engine_unknown_datasource(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )  # noqa: F821
    # raised by _validate_batch_request() in Datasource
    with pytest.raises(ValueError):
        # Test for an unknown datasource
        # noinspection PyUnusedLocal
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=RuntimeBatchRequest(
                datasource_name="non_existent_datasource",
                data_connector_name="test_runtime_data_connector",
                data_asset_name="my_data_asset",
                runtime_parameters={"batch_data": test_df},
                batch_identifiers={"default_identifier_name": "identifier_name"},
            )
        )


def test_batch_data_sparkdf_execution_engine_unknown_data_connector(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )
    # raised by _validate_batch_request() in Datasource
    with pytest.raises(ValueError):
        # Test for an unknown data_connector
        # noinspection PyUnusedLocal
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=RuntimeBatchRequest(
                datasource_name=datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
                data_connector_name="non_existent_data_connector",
                data_asset_name="my_data_asset",
                runtime_parameters={"batch_data": test_df},
                batch_identifiers={"default_identifier_name": "identifier_name"},
            )
        )


def test_batch_data_sparkdf_execution_engine_no_batch_identifiers(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )

    # raised by _validate_runtime_batch_request_specific_init_parameters() in RuntimeBatchRequest.__init__()
    with pytest.raises(TypeError):
        # batch_identifiers missing (set to None)
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=RuntimeBatchRequest(
                datasource_name=datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
                data_connector_name="test_runtime_data_connector",
                data_asset_name="my_data_asset",
                runtime_parameters={"batch_data": test_df},
                batch_identifiers=None,
            )
        )

    # raised by _validate_runtime_batch_request_specific_init_parameters() in RuntimeBatchRequest.__init__()
    with pytest.raises(TypeError):
        # batch_identifiers missing
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=RuntimeBatchRequest(
                datasource_name=datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
                data_connector_name="test_runtime_data_connector",
                data_asset_name="my_data_asset",
                runtime_parameters={"batch_data": test_df},
            )
        )


def test_batch_data_sparkdf_execution_engine_incorrect_batch_identifiers(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )
    # raised by _validate_batch_identifiers_configuration() in RuntimeDataConnector
    with pytest.raises(gx_exceptions.DataConnectorError):
        # runtime_parameters are not configured in the DataConnector
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=RuntimeBatchRequest(
                datasource_name=datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
                data_connector_name="test_runtime_data_connector",
                data_asset_name="my_data_asset",
                runtime_parameters={"batch_data": test_df},
                batch_identifiers={"i_dont_exist": "i_dont_either"},
            )
        )


def test_batch_data_sparkdf_execution_engine_all_keys_present_for_batch_identifiers(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )
    batch_identifiers: Dict[str, int] = {
        "pipeline_stage_name": "core_processing",
        "airflow_run_id": 1234567890,
        "custom_key_0": "custom_value_0",
    }

    # Verify that all keys in batch_identifiers are acceptable as batch_identifiers (using batch count).
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "IN_MEMORY_DATA_ASSET",
        "runtime_parameters": {
            "batch_data": test_df,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1


def test_batch_data_sparkdf_execution_engine_batch_identifiers_error_mostly_legal_keys(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )
    batch_identifiers: Dict[str, int] = {
        "pipeline_stage_name": "core_processing",
        "airflow_run_id": 1234567890,
        "custom_key_0": "custom_value_0",
        "i_am_illegal_key": "i_am_illegal_value",
    }

    # Ensure that keys in batch_identifiers that are not among batch_identifiers declared in
    # configuration are not accepted.  In this test, all legal keys plus a single illegal key are present.
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "IN_MEMORY_DATA_ASSET",
        "runtime_parameters": {
            "batch_data": test_df,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)

    with pytest.raises(gx_exceptions.DataConnectorError):
        # noinspection PyUnusedLocal
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=batch_request
        )


def test_batch_data_sparkdf_execution_engine_batch_identifiers_error_one_illegal_key(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )

    batch_identifiers: Dict[str, str] = {"unknown_key": "some_value"}
    # Ensure that keys in batch_identifiers that are not among batch_identifiers declared in
    # configuration are not accepted.  In this test, a single illegal key is present.
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "IN_MEMORY_DATA_ASSET",
        "runtime_parameters": {
            "batch_data": test_df,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)

    with pytest.raises(gx_exceptions.DataConnectorError):
        # noinspection PyUnusedLocal
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=batch_request
        )


def test_batch_data_sparkdf_execution_engine_set_data_asset_name_for_runtime_data(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )
    batch_identifiers: Dict[str, int] = {
        "pipeline_stage_name": "core_processing",
        "airflow_run_id": 1234567890,
        "custom_key_0": "custom_value_0",
    }

    # set : my_runtime_data_asset
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_runtime_data_asset",
        "runtime_parameters": {
            "batch_data": test_df,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert batch_list[0].batch_definition.data_asset_name == "my_runtime_data_asset"


def test_batch_data_sparkdf_execution_engine_get_available_data_asset_names(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    expected_available_data_asset_names: Dict[str, List[str]] = {
        "test_runtime_data_connector": ["asset_a", "asset_b"]
    }
    available_data_asset_names: Dict[
        str, List[str]
    ] = (
        datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_available_data_asset_names()
    )
    assert available_data_asset_names == expected_available_data_asset_names


def test_batch_data_sparkdf_execution_engine_get_batch_definition_list_from_batch_request_length_one(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )

    batch_identifiers: Dict[str, int] = {
        "airflow_run_id": 1234567890,
    }

    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_data_asset",
        "runtime_parameters": {
            "batch_data": test_df,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )

    assert len(batch_list) == 1
    my_batch_1 = batch_list[0]

    assert my_batch_1.batch_spec is not None
    assert my_batch_1.batch_definition["data_asset_name"] == "my_data_asset"
    assert isinstance(my_batch_1.data, SparkDFBatchData)
    assert len(my_batch_1.data.dataframe.columns) == 2


def test_batch_data_sparkdf_execution_engine_get_batch_definitions_and_get_batch_basics(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )

    data_connector_name: str = "test_runtime_data_connector"
    data_asset_name: str = "test_asset_1"

    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": data_connector_name,
        "data_asset_name": data_asset_name,
        "runtime_parameters": {
            "batch_data": test_df,
        },
        "batch_identifiers": {
            "airflow_run_id": 1234567890,
        },
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)

    assert (
        len(
            datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_available_batch_definitions(
                batch_request=batch_request
            )
        )
        == 1
    )

    my_df: "pyspark.sql.dataframe.DataFrame" = (
        spark_session.createDataFrame(  # noqa: F821
            pd.DataFrame({"x": range(10), "y": range(10)})
        )
    )
    batch: Batch = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_from_batch_definition(
        batch_definition=BatchDefinition(
            "my_datasource",
            "_pipeline",
            "_pipeline",
            batch_identifiers=IDDict({"some_random_id": 1}),
        ),
        batch_data=my_df,
    )
    assert batch.batch_request == {}


def test_batch_data_sparkedf_execution_engine_get_batch_list_with_named_asset(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )

    batch_identifiers: Dict[str, int] = {"day": 1, "month": 12}
    # Verify that all keys in batch_identifiers are acceptable as batch_identifiers (using batch count).
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "asset_a",
        "runtime_parameters": {
            "batch_data": test_df,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    my_batch_1 = batch_list[0]

    assert my_batch_1.batch_spec is not None
    assert my_batch_1.batch_definition["data_asset_name"] == "asset_a"
    assert isinstance(my_batch_1.data, SparkDFBatchData)
    assert my_batch_1.data.dataframe.count() == 2
    assert len(my_batch_1.data.dataframe.columns) == 2
    assert my_batch_1.batch_definition.batch_identifiers == batch_identifiers


def test_batch_data_sparkdf_execution_engine_get_batch_list_with_named_asset_two_batch_requests(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, spark_session
):
    test_df: "pyspark.sql.dataframe.DataFrame" = (  # noqa: F821
        spark_session.createDataFrame(
            data=pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        )
    )

    batch_identifiers: Dict[str, int] = {"day": 1, "month": 12}
    # Verify that all keys in batch_identifiers are acceptable as batch_identifiers (using batch count).
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "asset_a",
        "runtime_parameters": {
            "batch_data": test_df,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    # batches are a little bit more difficult to test because of batch_markers
    # they are ones that uniquely identify the data
    assert len(batch_list) == 1
    my_batch_1 = batch_list[0]

    assert my_batch_1.batch_spec is not None
    assert my_batch_1.batch_definition["data_asset_name"] == "asset_a"
    assert isinstance(my_batch_1.data, SparkDFBatchData)
    assert my_batch_1.data.dataframe.count() == 2
    assert len(my_batch_1.data.dataframe.columns) == 2
    assert my_batch_1.batch_definition.batch_identifiers == batch_identifiers

    # second batch request
    batch_identifiers: Dict[str, int] = {"day": 2, "month": 12}
    # Verify that all keys in batch_identifiers are acceptable as batch_identifiers (using batch count).
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "asset_a",
        "runtime_parameters": {
            "batch_data": test_df,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    my_batch_2 = batch_list[0]

    assert my_batch_2.batch_spec is not None
    assert my_batch_2.batch_definition["data_asset_name"] == "asset_a"
    assert isinstance(my_batch_2.data, SparkDFBatchData)
    assert my_batch_2.data.dataframe.count() == 2
    assert len(my_batch_2.data.dataframe.columns) == 2
    assert my_batch_2.batch_definition.batch_identifiers == batch_identifiers


###################################
# Tests with data passed in as path
###################################
# Tests with SparkDF Execution Engine


def test_file_path_sparkdf_execution_engine_batch_list_from_batch_request_success_file_path(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine,
    taxi_test_file,
    spark_session,
):
    batch_identifiers: Dict[str, int] = {
        "airflow_run_id": 1234567890,
    }
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_data_asset",
        "runtime_parameters": {
            "path": taxi_test_file,
        },
        "batch_identifiers": batch_identifiers,
        "batch_spec_passthrough": {"reader_options": {"header": True}},
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    my_batch_1 = batch_list[0]
    assert my_batch_1.batch_spec is not None
    assert my_batch_1.batch_definition["data_asset_name"] == "my_data_asset"
    assert isinstance(my_batch_1.data, SparkDFBatchData)
    assert my_batch_1.data.dataframe.count() == 10000
    assert len(my_batch_1.data.dataframe.columns) == 18


def test_file_path_sparkdf_execution_engine_batch_list_from_batch_request_fail_directory_but_no_reader_method(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine,
    taxi_test_file_directory,
    spark_session,
):
    # The SparkDFExecutionEngine can only read in multiple files from a directory if the reader_method is specified
    batch_identifiers: Dict[str, int] = {
        "airflow_run_id": 1234567890,
    }
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_data_asset",
        "runtime_parameters": {
            "path": taxi_test_file_directory,
        },
        "batch_identifiers": batch_identifiers,
        "batch_spec_passthrough": {"reader_options": {"header": True}},
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)

    # raised by guess_reader_method_from_path() in SparkDFExecutionEngine
    with pytest.raises(gx_exceptions.ExecutionEngineError):
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=batch_request
        )


def test_file_path_sparkdf_execution_engine_batch_definition_list_from_batch_request_fail_directory_wrong_reader_method(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine,
    taxi_test_file_directory,
    spark_session,
):
    # The SparkDFExecutionEngine can only read in multiple files from a directory if the reader_method is specified
    batch_identifiers: Dict[str, int] = {
        "airflow_run_id": 1234567890,
    }
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_data_asset",
        "runtime_parameters": {
            "path": taxi_test_file_directory,
        },
        "batch_identifiers": batch_identifiers,
        "batch_spec_passthrough": {
            "reader_options": {"header": True},
            "reader_method": "i_am_invalid",
        },
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)

    # raised by guess_reader_method_from_path() in SparkDFExecutionEngine
    with pytest.raises(gx_exceptions.ExecutionEngineError):
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=batch_request
        )


def test_file_path_sparkdf_execution_engine_batch_list_from_batch_request_fail_file_path_wrong_reader_method(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine,
    taxi_test_file,
    spark_session,
):
    # The SparkDFExecutionEngine can only read in multiple files from a directory if the reader_method is specified
    batch_identifiers: Dict[str, int] = {
        "airflow_run_id": 1234567890,
    }
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_data_asset",
        "runtime_parameters": {
            "path": taxi_test_file,
        },
        "batch_identifiers": batch_identifiers,
        "batch_spec_passthrough": {
            "reader_options": {"header": True},
            "reader_method": "i_am_invalid",
        },
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)

    # raised by guess_reader_method_from_path() in SparkDFExecutionEngine
    with pytest.raises(gx_exceptions.ExecutionEngineError):
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=batch_request
        )


def test_file_path_sparkdf_execution_engine_batch_list_from_batch_request_success_directory(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine,
    taxi_test_file_directory,
    spark_session,
):
    batch_identifiers: Dict[str, int] = {
        "airflow_run_id": 1234567890,
    }
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_data_asset",
        "runtime_parameters": {
            "path": taxi_test_file_directory,
        },
        "batch_identifiers": batch_identifiers,
        "batch_spec_passthrough": {
            "reader_method": "csv",
            "reader_options": {"header": True},
        },
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    my_batch_1 = batch_list[0]
    assert my_batch_1.batch_spec is not None
    assert my_batch_1.batch_definition["data_asset_name"] == "my_data_asset"
    assert isinstance(my_batch_1.data, SparkDFBatchData)
    assert my_batch_1.data.dataframe.count() == 30000  # 3 files read in as 1
    assert len(my_batch_1.data.dataframe.columns) == 18


def test_file_path_sparkdf_execution_engine_batch_list_from_batch_request_success_file_path_no_headers(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine,
    taxi_test_file,
    spark_session,
):
    batch_identifiers: Dict[str, int] = {
        "airflow_run_id": 1234567890,
    }
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_data_asset",
        "runtime_parameters": {
            "path": taxi_test_file,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    my_batch_1 = batch_list[0]
    assert my_batch_1.batch_spec is not None
    assert my_batch_1.batch_definition["data_asset_name"] == "my_data_asset"
    assert isinstance(my_batch_1.data, SparkDFBatchData)
    assert (
        my_batch_1.data.dataframe.count() == 10001
    )  # headers are not read-in by default
    assert len(my_batch_1.data.dataframe.columns) == 18


def test_file_path_sparkdf_execution_engine_batch_list_from_batch_request_success_file_path_endswith_upcase_no_headers(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine,
    taxi_test_file_upcase,
    spark_session,
):
    batch_identifiers: Dict[str, int] = {
        "airflow_run_id": 1234567890,
    }
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_data_asset",
        "runtime_parameters": {
            "path": taxi_test_file_upcase,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    my_batch_1 = batch_list[0]
    assert my_batch_1.batch_spec is not None
    assert my_batch_1.batch_definition["data_asset_name"] == "my_data_asset"
    assert isinstance(my_batch_1.data, SparkDFBatchData)
    assert (
        my_batch_1.data.dataframe.count() == 10001
    )  # headers are not read-in by default
    assert len(my_batch_1.data.dataframe.columns) == 18


def test_file_path_sparkdf_execution_engine_batch_list_from_batch_request_success_directory_no_headers(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine,
    taxi_test_file_directory,
    spark_session,
):
    batch_identifiers: Dict[str, int] = {
        "airflow_run_id": 1234567890,
    }
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_data_asset",
        "runtime_parameters": {
            "path": taxi_test_file_directory,
        },
        "batch_identifiers": batch_identifiers,
        "batch_spec_passthrough": {
            "reader_method": "csv",
        },
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    my_batch_1 = batch_list[0]
    assert my_batch_1.batch_spec is not None
    assert my_batch_1.batch_definition["data_asset_name"] == "my_data_asset"
    assert isinstance(my_batch_1.data, SparkDFBatchData)
    assert my_batch_1.data.dataframe.count() == 30003  # 3 files read in as 1
    assert len(my_batch_1.data.dataframe.columns) == 18


def test_file_path_sparkdf_execution_engine_batch_list_from_batch_request_failed_wrong_file_path(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine,
):
    batch_identifiers: Dict[str, int] = {
        "airflow_run_id": 1234567890,
    }
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "my_data_asset",
        "runtime_parameters": {
            "path": "I_dont_exist",
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)

    # raised by guess_reader_method_from_path() in ExecutionEngine
    with pytest.raises(gx_exceptions.ExecutionEngineError):
        batch_list: List[
            Batch
        ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
            batch_request=batch_request
        )


def test_file_path_sparkedf_execution_engine_get_batch_list_with_named_asset(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, taxi_test_file
):
    batch_identifiers: Dict[str, int] = {"day": 1, "month": 12}
    # Verify that all keys in batch_identifiers are acceptable as batch_identifiers (using batch count).
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "asset_a",
        "runtime_parameters": {
            "path": taxi_test_file,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    my_batch_1 = batch_list[0]

    assert my_batch_1.batch_spec is not None
    assert my_batch_1.batch_definition["data_asset_name"] == "asset_a"
    assert isinstance(my_batch_1.data, SparkDFBatchData)
    assert my_batch_1.data.dataframe.count() == 10001
    assert len(my_batch_1.data.dataframe.columns) == 18
    assert my_batch_1.batch_definition.batch_identifiers == batch_identifiers


def test_file_path_sparkdf_execution_engine_get_batch_list_with_named_asset_two_batch_requests(
    datasource_with_runtime_data_connector_and_sparkdf_execution_engine, taxi_test_file
):
    batch_identifiers: Dict[str, int] = {"day": 1, "month": 12}
    # Verify that all keys in batch_identifiers are acceptable as batch_identifiers (using batch count).
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "asset_a",
        "runtime_parameters": {
            "path": taxi_test_file,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    # batches are a little bit more difficult to test because of batch_markers
    # they are ones that uniquely identify the data
    assert len(batch_list) == 1
    my_batch_1 = batch_list[0]

    assert my_batch_1.batch_spec is not None
    assert my_batch_1.batch_definition["data_asset_name"] == "asset_a"
    assert isinstance(my_batch_1.data, SparkDFBatchData)
    assert my_batch_1.data.dataframe.count() == 10001
    assert len(my_batch_1.data.dataframe.columns) == 18
    assert my_batch_1.batch_definition.batch_identifiers == batch_identifiers

    # second batch request
    batch_identifiers: Dict[str, int] = {"day": 2, "month": 12}
    # Verify that all keys in batch_identifiers are acceptable as batch_identifiers (using batch count).
    batch_request: Dict[str, Any] = {
        "datasource_name": datasource_with_runtime_data_connector_and_sparkdf_execution_engine.name,
        "data_connector_name": "test_runtime_data_connector",
        "data_asset_name": "asset_a",
        "runtime_parameters": {
            "path": taxi_test_file,
        },
        "batch_identifiers": batch_identifiers,
    }
    batch_request: RuntimeBatchRequest = RuntimeBatchRequest(**batch_request)
    batch_list: List[
        Batch
    ] = datasource_with_runtime_data_connector_and_sparkdf_execution_engine.get_batch_list_from_batch_request(
        batch_request=batch_request
    )
    assert len(batch_list) == 1
    my_batch_2 = batch_list[0]

    assert my_batch_2.batch_spec is not None
    assert my_batch_2.batch_definition["data_asset_name"] == "asset_a"
    assert isinstance(my_batch_2.data, SparkDFBatchData)
    assert my_batch_2.data.dataframe.count() == 10001
    assert len(my_batch_2.data.dataframe.columns) == 18
    assert my_batch_2.batch_definition.batch_identifiers == batch_identifiers
