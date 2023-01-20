from typing import Any, Dict, List

import pandas as pd
import pytest
from _pytest import monkeypatch

from great_expectations.data_context.util import file_relative_path
from great_expectations.exceptions import MetricResolutionError

try:
    import sqlalchemy as sa
    from sqlalchemy import Column, Integer, String, select
    from sqlalchemy.orm import declarative_base
except ImportError:
    sa = None
    Column = None
    Integer = None
    String = None
    select = None
    declarative_base = None


from great_expectations.execution_engine import SqlAlchemyExecutionEngine
from great_expectations.expectations.metrics.util import (
    get_unexpected_indices_for_multiple_pandas_named_indices,
    get_unexpected_indices_for_single_pandas_named_index,
    sql_statement_with_post_compile_to_string,
)
from tests.test_utils import (
    get_awsathena_connection_url,
    get_bigquery_connection_url,
    get_default_mssql_url,
    get_default_mysql_url,
    get_default_postgres_url,
    get_default_trino_url,
    get_redshift_connection_url,
    get_snowflake_connection_url,
)

# The following class allows for declarative instantiation of base class for SqlAlchemy. Adopted from
# https://docs.sqlalchemy.org/en/14/faq/sqlexpressions.html#rendering-postcompile-parameters-as-bound-parameters

Base = declarative_base()


class A(Base):
    __tablename__ = "a"
    id = Column(Integer, primary_key=True)
    data = Column(String)


def select_with_post_compile_statements() -> "sqlalchemy.sql.Select":
    test_id: str = "00000000"
    return select(A).where(A.data == test_id)


def _compare_select_statement_with_converted_string(engine) -> None:
    """
    Helper method used to do the call to sql_statement_with_post_compile_to_string() and compare with expected val
    Args:
        engine (ExecutionEngine): SqlAlchemyExecutionEngine with connection to backend under test
    """
    select_statement: "sqlalchemy.sql.Select" = select_with_post_compile_statements()
    returned_string = sql_statement_with_post_compile_to_string(
        engine=engine, select_statement=select_statement
    )
    assert returned_string == (
        "SELECT a.id, a.data \n" "FROM a \n" "WHERE a.data = '00000000';"
    )


@pytest.fixture
def unexpected_index_list_one_index_column():
    return [
        {"animals": "cat", "pk_1": 0},
        {"animals": "fish", "pk_1": 1},
        {"animals": "dog", "pk_1": 2},
        {"animals": "giraffe", "pk_1": 3},
        {"animals": "lion", "pk_1": 4},
        {"animals": "zebra", "pk_1": 5},
    ]


@pytest.fixture
def unexpected_index_list_two_index_columns():
    return [
        {"animals": "cat", "pk_1": 0, "pk_2": "zero"},
        {"animals": "fish", "pk_1": 1, "pk_2": "one"},
        {"animals": "dog", "pk_1": 2, "pk_2": "two"},
        {"animals": "giraffe", "pk_1": 3, "pk_2": "three"},
        {"animals": "lion", "pk_1": 4, "pk_2": "four"},
        {"animals": "zebra", "pk_1": 5, "pk_2": "five"},
    ]


@pytest.mark.unit
@pytest.mark.parametrize(
    "backend_name,connection_string",
    [
        (
            "sqlite",
            f"sqlite:///{file_relative_path(__file__, '../../test_sets/metrics_test.db')}",
        ),
        ("postgresql", get_default_postgres_url()),
        ("mysql", get_default_mysql_url()),
        ("mssql", get_default_mssql_url()),
        ("trino", get_default_trino_url()),
        ("redshift", get_redshift_connection_url()),
        ("snowflake", get_snowflake_connection_url()),
    ],
)
def test_sql_statement_conversion_to_string_for_backends(
    backend_name: str, connection_string: str, test_backends: List[str]
):

    if backend_name in test_backends:
        engine = SqlAlchemyExecutionEngine(connection_string=connection_string)
        _compare_select_statement_with_converted_string(engine=engine)
    else:
        pytest.skip(f"skipping sql statement conversion test for : {backend_name}")


@pytest.mark.unit
def test_sql_statement_conversion_to_string_awsathena(test_backends):
    if "awsathena" in test_backends:
        monkeypatch.setenv("ATHENA_STAGING_S3", "s3://test-staging/")
        monkeypatch.setenv("ATHENA_DB_NAME", "test_db_name")
        monkeypatch.setenv("ATHENA_TEN_TRIPS_DB_NAME", "test_ten_trips_db_name")
        connection_string = get_awsathena_connection_url()
        engine = SqlAlchemyExecutionEngine(connection_string=connection_string)
        _compare_select_statement_with_converted_string(engine=engine)
    else:
        pytest.skip(f"skipping sql statement conversion test for : awsathena")


@pytest.mark.unit
def test_sql_statement_conversion_to_string_bigquery(test_backends):
    """
    Bigquery backend returns a slightly different query
    """
    if "bigquery" in test_backends:
        monkeypatch.setenv("GE_TEST_GCP_PROJECT", "ge-oss")
        connection_string = get_bigquery_connection_url()
        engine = SqlAlchemyExecutionEngine(connection_string=connection_string)
        select_statement: "sqlalchemy.sql.Select" = (
            select_with_post_compile_statements()
        )
        returned_string = sql_statement_with_post_compile_to_string(
            engine=engine, select_statement=select_statement
        )
        assert returned_string == (
            "SELECT `a`.`id`, `a`.`data` \n"
            "FROM `a` \n"
            "WHERE `a`.`data` = '00000000';"
        )
    else:
        pytest.skip(f"skipping sql statement conversion test for : bigquery")


@pytest.mark.unit
def test_get_unexpected_indices_for_single_pandas_named_index_named_unexpected_index_columns(
    pandas_animals_dataframe_for_unexpected_rows_and_index,
    unexpected_index_list_one_index_column,
):
    dataframe: pd.DataFrame = pandas_animals_dataframe_for_unexpected_rows_and_index
    updated_dataframe: pd.DataFrame = dataframe.set_index(["pk_1"])
    expectation_domain_column_name: str = "animals"
    unexpected_index_column_names: List[str] = ["pk_1"]

    unexpected_index_list = get_unexpected_indices_for_single_pandas_named_index(
        domain_records_df=updated_dataframe,
        expectation_domain_column_name=expectation_domain_column_name,
        unexpected_index_column_names=unexpected_index_column_names,
    )
    assert unexpected_index_list == unexpected_index_list_one_index_column


@pytest.mark.unit
def test_get_unexpected_indices_for_single_pandas_named_index(
    pandas_animals_dataframe_for_unexpected_rows_and_index,
    unexpected_index_list_one_index_column,
):
    dataframe: pd.DataFrame = pandas_animals_dataframe_for_unexpected_rows_and_index
    updated_dataframe: pd.DataFrame = dataframe.set_index(["pk_1"])
    expectation_domain_column_name = "animals"
    unexpected_index_column_names = [updated_dataframe.index.name]

    unexpected_index_list = get_unexpected_indices_for_single_pandas_named_index(
        domain_records_df=updated_dataframe,
        expectation_domain_column_name=expectation_domain_column_name,
        unexpected_index_column_names=unexpected_index_column_names,
    )
    assert unexpected_index_list == unexpected_index_list_one_index_column


@pytest.mark.unit
def test_get_unexpected_indices_for_multiple_pandas_named_indices(
    pandas_animals_dataframe_for_unexpected_rows_and_index,
    unexpected_index_list_two_index_columns,
):
    dataframe: pd.DataFrame = pandas_animals_dataframe_for_unexpected_rows_and_index
    updated_dataframe: pd.DataFrame = dataframe.set_index(["pk_1", "pk_2"])
    expectation_domain_column_name = "animals"
    unexpected_index_column_names = list(updated_dataframe.index.names)

    unexpected_index_list = get_unexpected_indices_for_multiple_pandas_named_indices(
        domain_records_df=updated_dataframe,
        expectation_domain_column_name=expectation_domain_column_name,
        unexpected_index_column_names=unexpected_index_column_names,
    )
    assert unexpected_index_list == unexpected_index_list_two_index_columns


@pytest.mark.unit
def test_get_unexpected_indices_for_multiple_pandas_named_indices_named_unexpected_index_columns(
    pandas_animals_dataframe_for_unexpected_rows_and_index,
    unexpected_index_list_two_index_columns,
):
    dataframe: pd.DataFrame = pandas_animals_dataframe_for_unexpected_rows_and_index
    updated_dataframe: pd.DataFrame = dataframe.set_index(["pk_1", "pk_2"])
    expectation_domain_column_name = "animals"
    unexpected_index_column_names = ["pk_1", "pk_2"]

    unexpected_index_list = get_unexpected_indices_for_multiple_pandas_named_indices(
        domain_records_df=updated_dataframe,
        expectation_domain_column_name=expectation_domain_column_name,
        unexpected_index_column_names=unexpected_index_column_names,
    )
    assert unexpected_index_list == unexpected_index_list_two_index_columns


@pytest.mark.unit
def test_get_unexpected_indices_for_multiple_pandas_named_indices_named_unexpected_index_columns_one_column(
    pandas_animals_dataframe_for_unexpected_rows_and_index,
    unexpected_index_list_one_index_column,
):
    dataframe: pd.DataFrame = pandas_animals_dataframe_for_unexpected_rows_and_index
    updated_dataframe: pd.DataFrame = dataframe.set_index(["pk_1", "pk_2"])
    expectation_domain_column_name = "animals"
    unexpected_index_column_names = ["pk_1"]

    unexpected_index_list = get_unexpected_indices_for_multiple_pandas_named_indices(
        domain_records_df=updated_dataframe,
        expectation_domain_column_name=expectation_domain_column_name,
        unexpected_index_column_names=unexpected_index_column_names,
    )
    assert unexpected_index_list == unexpected_index_list_one_index_column


@pytest.mark.unit
def test_get_unexpected_indices_for_multiple_pandas_named_indices_named_unexpected_index_columns_wrong_column(
    pandas_animals_dataframe_for_unexpected_rows_and_index,
):
    dataframe: pd.DataFrame = pandas_animals_dataframe_for_unexpected_rows_and_index
    updated_dataframe: pd.DataFrame = dataframe.set_index(["pk_1", "pk_2"])
    expectation_domain_column_name = "animals"
    unexpected_index_column_names = ["i_dont_exist"]
    with pytest.raises(MetricResolutionError) as e:
        get_unexpected_indices_for_multiple_pandas_named_indices(
            domain_records_df=updated_dataframe,
            expectation_domain_column_name=expectation_domain_column_name,
            unexpected_index_column_names=unexpected_index_column_names,
        )
    assert e.value.message == (
        "Error: The column i_dont_exist does not exist in the named indices. Please "
        "check your configuration"
    )


@pytest.mark.unit
def test_get_unexpected_indices_for_multiple_pandas_named_indices_named_unexpected_index_wrong_domain(
    pandas_animals_dataframe_for_unexpected_rows_and_index,
):
    dataframe: pd.DataFrame = pandas_animals_dataframe_for_unexpected_rows_and_index
    updated_dataframe: pd.DataFrame = dataframe.set_index(["pk_1", "pk_2"])
    expectation_domain_column_name = None
    unexpected_index_column_names = ["pk_1"]
    with pytest.raises(MetricResolutionError) as e:
        get_unexpected_indices_for_multiple_pandas_named_indices(
            domain_records_df=updated_dataframe,
            expectation_domain_column_name=expectation_domain_column_name,
            unexpected_index_column_names=unexpected_index_column_names,
        )
    assert e.value.message == (
        "Error: The domain column is currently set to None. Please check your "
        "configuration."
    )
