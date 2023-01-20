from __future__ import annotations

import copy
import itertools
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Type,
    cast,
)

import pydantic
from pydantic import dataclasses as pydantic_dc
from typing_extensions import ClassVar, Literal

from great_expectations.core.batch_spec import SqlAlchemyDatasourceBatchSpec
from great_expectations.experimental.datasources.interfaces import (
    Batch,
    BatchRequest,
    BatchRequestOptions,
    BatchSortersDefinition,
    DataAsset,
    Datasource,
)

if TYPE_CHECKING:
    import sqlalchemy

    from great_expectations.execution_engine import ExecutionEngine


class SQLDatasourceError(Exception):
    pass


@pydantic_dc.dataclass(frozen=True)
class ColumnSplitter:
    column_name: str
    method_name: str
    param_names: Sequence[str]

    def param_defaults(self, table_asset: TableAsset) -> Dict[str, List]:
        raise NotImplementedError

    @pydantic.validator("method_name")
    def _splitter_method_exists(cls, v: str):
        """Fail early if the `method_name` does not exist and would fail at runtime."""
        # NOTE (kilo59): this could be achieved by simply annotating the method_name field
        # as a `SplitterMethod` enum but we get cyclic imports.
        # This also adds the enums to the generated json schema.
        # https://docs.pydantic.dev/usage/types/#enums-and-choices
        # We could use `update_forward_refs()` but would have to change this to a BaseModel
        # https://docs.pydantic.dev/usage/postponed_annotations/
        from great_expectations.execution_engine.split_and_sample.data_splitter import (
            SplitterMethod,
        )

        method_members = set(SplitterMethod)
        if v not in method_members:
            permitted_values_str = "', '".join([m.value for m in method_members])
            raise ValueError(f"unexpected value; permitted: '{permitted_values_str}'")
        return v


class DatetimeRange(NamedTuple):
    min: datetime
    max: datetime


@pydantic_dc.dataclass(frozen=True)
class SqlYearMonthSplitter(ColumnSplitter):
    method_name: Literal["split_on_year_and_month"] = "split_on_year_and_month"
    param_names: List[Literal["year", "month"]] = pydantic.Field(
        default_factory=lambda: ["year", "month"]
    )

    def param_defaults(self, table_asset: TableAsset) -> Dict[str, List]:
        """Query sql database to get the years and months to split over.

        Args:
            table_asset: A TableAsset over which we want to split the data.
        """
        return _query_for_year_and_month(
            table_asset, self.column_name, _get_sql_datetime_range
        )


def _query_for_year_and_month(
    table_asset: TableAsset,
    column_name: str,
    query_datetime_range: Callable[
        [sqlalchemy.engine.base.Connection, str, str], DatetimeRange
    ],
) -> Dict[str, List]:
    # We should make an assertion about the execution_engine earlier. Right now it is assigned to
    # after construction. We may be able to use a hook in a property setter.
    from great_expectations.execution_engine import SqlAlchemyExecutionEngine

    assert isinstance(
        table_asset.datasource.execution_engine, SqlAlchemyExecutionEngine
    )

    with table_asset.datasource.execution_engine.engine.connect() as conn:
        datetimes: DatetimeRange = query_datetime_range(
            conn,
            table_asset.table_name,
            column_name,
        )
    year: List[int] = list(range(datetimes.min.year, datetimes.max.year + 1))
    month: List[int]
    if datetimes.min.year == datetimes.max.year:
        month = list(range(datetimes.min.month, datetimes.max.month + 1))
    else:
        month = list(range(1, 13))
    return {"year": year, "month": month}


def _get_sql_datetime_range(
    conn: sqlalchemy.engine.base.Connection, table_name: str, col_name: str
) -> DatetimeRange:
    q = f"select min({col_name}), max({col_name}) from {table_name}"
    min_max_dt = list(conn.execute(q))[0]
    return DatetimeRange(min=min_max_dt[0], max=min_max_dt[1])


class TableAsset(DataAsset):
    # Instance fields
    type: Literal["table"] = "table"
    table_name: str
    column_splitter: Optional[SqlYearMonthSplitter] = None
    name: str

    def batch_request_options_template(
        self,
    ) -> BatchRequestOptions:
        """A BatchRequestOptions template for get_batch_request.

        Returns:
            A BatchRequestOptions dictionary with the correct shape that get_batch_request
            will understand. All the option values are defaulted to None.
        """
        template: BatchRequestOptions = {}
        if not self.column_splitter:
            return template
        return {p: None for p in self.column_splitter.param_names}

    # This asset type will support a variety of splitters
    def add_year_and_month_splitter(
        self,
        column_name: str,
    ) -> TableAsset:
        """Associates a year month splitter with this DataAsset

        Args:
            column_name: A column name of the date column where year and month will be parsed out.

        Returns:
            This TableAsset so we can use this method fluently.
        """
        self.column_splitter = SqlYearMonthSplitter(
            column_name=column_name,
        )
        return self

    def _fully_specified_batch_requests(self, batch_request) -> List[BatchRequest]:
        """Populates a batch requests unspecified params producing a list of batch requests."""
        if self.column_splitter is None:
            # Currently batch_request.options is complete determined by the presence of a
            # column splitter. If column_splitter is None, then there are no specifiable options
            # so we return early.
            # In the future, if there are options that are not determined by the column splitter
            # this check will have to be generalized.
            return [batch_request]

        # Make a list of the specified and unspecified params in batch_request
        specified_options = []
        unspecified_options = []
        options_template = self.batch_request_options_template()
        for option_name in options_template.keys():
            if (
                option_name in batch_request.options
                and batch_request.options[option_name] is not None
            ):
                specified_options.append(option_name)
            else:
                unspecified_options.append(option_name)

        # Make a list of the all possible batch_request.options by expanding out the unspecified
        # options
        batch_requests: List[BatchRequest] = []

        if not unspecified_options:
            batch_requests.append(batch_request)
        else:
            # All options are defined by the splitter, so we look at its default values to fill
            # in the option values.
            default_option_values = []
            for option in unspecified_options:
                default_option_values.append(
                    self.column_splitter.param_defaults(self)[option]
                )
            for option_values in itertools.product(*default_option_values):
                # Add options from specified options
                options = {
                    name: batch_request.options[name] for name in specified_options
                }
                # Add options from unspecified options
                for i, option_value in enumerate(option_values):
                    options[unspecified_options[i]] = option_value
                batch_requests.append(
                    BatchRequest(
                        datasource_name=batch_request.datasource_name,
                        data_asset_name=batch_request.data_asset_name,
                        options=options,
                    )
                )
        return batch_requests

    def get_batch_list_from_batch_request(
        self, batch_request: BatchRequest
    ) -> List[Batch]:
        """A list of batches that match the BatchRequest.

        Args:
            batch_request: A batch request for this asset. Usually obtained by calling
                get_batch_request on the asset.

        Returns:
            A list of batches that match the options specified in the batch request.
        """
        self._validate_batch_request(batch_request)

        batch_list: List[Batch] = []
        column_splitter = self.column_splitter
        for request in self._fully_specified_batch_requests(batch_request):
            batch_metadata = copy.deepcopy(request.options)
            batch_spec_kwargs = {
                "type": "table",
                "data_asset_name": self.name,
                "table_name": self.table_name,
                "batch_identifiers": {},
            }
            if column_splitter:
                batch_spec_kwargs["splitter_method"] = column_splitter.method_name
                batch_spec_kwargs["splitter_kwargs"] = {
                    "column_name": column_splitter.column_name
                }
                # mypy infers that batch_spec_kwargs["batch_identifiers"] is a collection, but
                # it is hardcoded to a dict above, so we cast it here.
                cast(Dict, batch_spec_kwargs["batch_identifiers"]).update(
                    {column_splitter.column_name: request.options}
                )
            # Creating the batch_spec is our hook into the execution engine.
            batch_spec = SqlAlchemyDatasourceBatchSpec(**batch_spec_kwargs)
            data, markers = self.datasource.execution_engine.get_batch_data_and_markers(
                batch_spec=batch_spec
            )

            # batch_definition (along with batch_spec and markers) is only here to satisfy a
            # legacy constraint when computing usage statistics in a validator. We hope to remove
            # it in the future.
            # imports are done inline to prevent a circular dependency with core/batch.py
            from great_expectations.core import IDDict
            from great_expectations.core.batch import BatchDefinition

            batch_definition = BatchDefinition(
                datasource_name=self.datasource.name,
                data_connector_name="experimental",
                data_asset_name=self.name,
                batch_identifiers=IDDict(batch_spec["batch_identifiers"]),
                batch_spec_passthrough=None,
            )
            batch_list.append(
                Batch(
                    datasource=self.datasource,
                    data_asset=self,
                    batch_request=request,
                    data=data,
                    metadata=batch_metadata,
                    legacy_batch_markers=markers,
                    legacy_batch_spec=batch_spec,
                    legacy_batch_definition=batch_definition,
                )
            )
        self.sort_batches(batch_list)
        return batch_list


class SQLDatasource(Datasource):
    """Adds a generic SQL datasource to the data context.

    Args:
        name: The name of this datasource
        connection_string: The SQLAlchemy connection string used to connect to the database.
            For example: "postgresql+psycopg2://postgres:@localhost/test_database"
        assets: An optional dictionary whose keys are TableAsset names and whose values
            are TableAsset objects.
    """

    # class var definitions
    asset_types: ClassVar[List[Type[DataAsset]]] = [TableAsset]

    # right side of the operator determines the type name
    # left side enforces the names on instance creation
    type: Literal["sql"] = "sql"
    connection_string: str
    assets: Dict[str, TableAsset] = {}

    @property
    def execution_engine_type(self) -> Type[ExecutionEngine]:
        """Returns the default execution engine type."""
        from great_expectations.execution_engine import SqlAlchemyExecutionEngine

        return SqlAlchemyExecutionEngine

    def add_table_asset(
        self,
        name: str,
        table_name: str,
        order_by: Optional[BatchSortersDefinition] = None,
    ) -> TableAsset:
        """Adds a table asset to this datasource.

        Args:
            name: The name of this table asset.
            table_name: The table where the data resides.
            order_by: A list of BatchSorters or BatchSorter strings.

        Returns:
            The TableAsset that is added to the datasource.
        """
        asset = TableAsset(
            name=name,
            table_name=table_name,
            order_by=order_by or [],  # type: ignore[arg-type]  # coerce list[str]
            # see DataAsset._parse_order_by_sorter()
        )
        return self.add_asset(asset)
