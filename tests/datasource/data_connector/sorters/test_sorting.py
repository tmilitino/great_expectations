from typing import Iterator

import pytest

import great_expectations.exceptions.exceptions as gx_exceptions
from great_expectations.core.batch import BatchDefinition, IDDict
from great_expectations.datasource.data_connector.sorter import (
    CustomListSorter,
    DateTimeSorter,
    DictionarySorter,
    LexicographicSorter,
    NumericSorter,
    Sorter,
)


@pytest.fixture()
def example_batch_def_list():
    a = BatchDefinition(
        datasource_name="A",
        data_connector_name="a",
        data_asset_name="james_20200810_1003",
        batch_identifiers=IDDict(
            {"name": "james", "timestamp": "20200810", "price": "1003"}
        ),
    )
    b = BatchDefinition(
        datasource_name="A",
        data_connector_name="b",
        data_asset_name="abe_20200809_1040",
        batch_identifiers=IDDict(
            {"name": "abe", "timestamp": "20200809", "price": "1040"}
        ),
    )
    c = BatchDefinition(
        datasource_name="A",
        data_connector_name="c",
        data_asset_name="eugene_20200809_1500",
        batch_identifiers=IDDict(
            {"name": "eugene", "timestamp": "20200809", "price": "1500"}
        ),
    )
    d = BatchDefinition(
        datasource_name="A",
        data_connector_name="d",
        data_asset_name="alex_20200819_1300",
        batch_identifiers=IDDict(
            {"name": "alex", "timestamp": "20200819", "price": "1300"}
        ),
    )
    e = BatchDefinition(
        datasource_name="A",
        data_connector_name="e",
        data_asset_name="alex_20200809_1000",
        batch_identifiers=IDDict(
            {"name": "alex", "timestamp": "20200809", "price": "1000"}
        ),
    )
    f = BatchDefinition(
        datasource_name="A",
        data_connector_name="f",
        data_asset_name="will_20200810_1001",
        batch_identifiers=IDDict(
            {"name": "will", "timestamp": "20200810", "price": "1001"}
        ),
    )
    g = BatchDefinition(
        datasource_name="A",
        data_connector_name="g",
        data_asset_name="eugene_20201129_1900",
        batch_identifiers=IDDict(
            {"name": "eugene", "timestamp": "20201129", "price": "1900"}
        ),
    )
    h = BatchDefinition(
        datasource_name="A",
        data_connector_name="h",
        data_asset_name="will_20200809_1002",
        batch_identifiers=IDDict(
            {"name": "will", "timestamp": "20200809", "price": "1002"}
        ),
    )
    i = BatchDefinition(
        datasource_name="A",
        data_connector_name="i",
        data_asset_name="james_20200811_1009",
        batch_identifiers=IDDict(
            {"name": "james", "timestamp": "20200811", "price": "1009"}
        ),
    )
    j = BatchDefinition(
        datasource_name="A",
        data_connector_name="j",
        data_asset_name="james_20200713_1567",
        batch_identifiers=IDDict(
            {"name": "james", "timestamp": "20200713", "price": "1567"}
        ),
    )
    return [a, b, c, d, e, f, g, h, i, j]


@pytest.fixture()
def example_hierarchical_batch_def_list():
    a = BatchDefinition(
        datasource_name="A",
        data_connector_name="a",
        data_asset_name="alex_20220913_1000",
        batch_identifiers=IDDict({"date": {"month": 1, "year": 2022}}),
    )
    b = BatchDefinition(
        datasource_name="A",
        data_connector_name="b",
        data_asset_name="will_20220913_1002",
        batch_identifiers=IDDict({"date": {"year": 2022, "month": 4}}),
    )
    c = BatchDefinition(
        datasource_name="A",
        data_connector_name="c",
        data_asset_name="anthony_20220913_1003",
        batch_identifiers=IDDict({"date": {"month": 1, "year": 2021}}),
    )
    d = BatchDefinition(
        datasource_name="A",
        data_connector_name="d",
        data_asset_name="chetan_20220913_1567",
        batch_identifiers=IDDict({"date": {"month": 6, "year": 2022}}),
    )
    e = BatchDefinition(
        datasource_name="A",
        data_connector_name="e",
        data_asset_name="nathan_20220913_1500",
        batch_identifiers=IDDict({"date": {"year": 2021, "month": 3}}),
    )
    f = BatchDefinition(
        datasource_name="A",
        data_connector_name="f",
        data_asset_name="gabriel_20220913_1040",
        batch_identifiers=IDDict({"date": {"month": 2, "year": 2021}}),
    )
    g = BatchDefinition(
        datasource_name="A",
        data_connector_name="g",
        data_asset_name="bill_20220913_1300",
        batch_identifiers=IDDict({"date": {"year": 2021, "month": 4}}),
    )
    h = BatchDefinition(
        datasource_name="A",
        data_connector_name="h",
        data_asset_name="tal_20220913_1009",
        batch_identifiers=IDDict({"date": {"month": 5, "year": 2022}}),
    )
    i = BatchDefinition(
        datasource_name="A",
        data_connector_name="i",
        data_asset_name="don_20220913_1900",
        batch_identifiers=IDDict({"date": {"year": 2022, "month": 3}}),
    )
    j = BatchDefinition(
        datasource_name="A",
        data_connector_name="j",
        data_asset_name="ken_20220913_1001",
        batch_identifiers=IDDict({"date": {"month": 2, "year": 2022}}),
    )
    return [a, b, c, d, e, f, g, h, i, j]


@pytest.mark.integration
def test_create_three_batch_definitions_sort_lexicographically():
    a = BatchDefinition(
        datasource_name="A",
        data_connector_name="a",
        data_asset_name="aaa",
        batch_identifiers=IDDict({"id": "A"}),
    )
    b = BatchDefinition(
        datasource_name="B",
        data_connector_name="b",
        data_asset_name="bbb",
        batch_identifiers=IDDict({"id": "B"}),
    )
    c = BatchDefinition(
        datasource_name="C",
        data_connector_name="c",
        data_asset_name="ccc",
        batch_identifiers=IDDict({"id": "C"}),
    )

    batch_list = [a, b, c]

    # sorting by "id" reverse alphabetically (descending)
    my_sorter = LexicographicSorter(name="id", orderby="desc")
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(
        batch_list,
    )
    assert sorted_batch_list == [c, b, a]

    # sorting by "id" reverse alphabetically (ascending)
    my_sorter = LexicographicSorter(name="id", orderby="asc")
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(
        batch_list,
    )
    assert sorted_batch_list == [a, b, c]


@pytest.mark.integration
def test_create_three_batch_definitions_sort_numerically():
    one = BatchDefinition(
        datasource_name="A",
        data_connector_name="a",
        data_asset_name="aaa",
        batch_identifiers=IDDict({"id": 1}),
    )
    two = BatchDefinition(
        datasource_name="B",
        data_connector_name="b",
        data_asset_name="bbb",
        batch_identifiers=IDDict({"id": 2}),
    )
    three = BatchDefinition(
        datasource_name="C",
        data_connector_name="c",
        data_asset_name="ccc",
        batch_identifiers=IDDict({"id": 3}),
    )

    batch_list = [one, two, three]
    my_sorter = NumericSorter(name="id", orderby="desc")
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [three, two, one]

    my_sorter = NumericSorter(name="id", orderby="asc")
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [one, two, three]

    # testing a non-numeric, which should throw an error
    i_should_not_work = BatchDefinition(
        datasource_name="C",
        data_connector_name="c",
        data_asset_name="ccc",
        batch_identifiers=IDDict({"id": "aaa"}),
    )

    batch_list = [one, two, three, i_should_not_work]
    with pytest.raises(gx_exceptions.SorterError):
        sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)


@pytest.mark.integration
def test_date_time():
    first = BatchDefinition(
        datasource_name="A",
        data_connector_name="a",
        data_asset_name="aaa",
        batch_identifiers=IDDict({"date": "20210101"}),
    )
    second = BatchDefinition(
        datasource_name="B",
        data_connector_name="b",
        data_asset_name="bbb",
        batch_identifiers=IDDict({"date": "20210102"}),
    )
    third = BatchDefinition(
        datasource_name="C",
        data_connector_name="c",
        data_asset_name="ccc",
        batch_identifiers=IDDict({"date": "20210103"}),
    )

    batch_list = [first, second, third]
    my_sorter = DateTimeSorter(name="date", datetime_format="%Y%m%d", orderby="desc")
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [third, second, first]

    my_sorter = DateTimeSorter(name="date", datetime_format="%Y%m%d", orderby="asc")
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [first, second, third]

    with pytest.raises(gx_exceptions.SorterError):
        # numeric date_time_format
        i_dont_work = DateTimeSorter(name="date", datetime_format=12345, orderby="desc")

    my_date_is_not_a_string = BatchDefinition(
        datasource_name="C",
        data_connector_name="c",
        data_asset_name="ccc",
        batch_identifiers=IDDict({"date": 20210103}),
    )

    batch_list = [first, second, third, my_date_is_not_a_string]
    my_sorter = DateTimeSorter(name="date", datetime_format="%Y%m%d", orderby="desc")

    with pytest.raises(gx_exceptions.SorterError):
        sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)


@pytest.mark.integration
def test_custom_list(periodic_table_of_elements):
    Hydrogen = BatchDefinition(
        datasource_name="A",
        data_connector_name="a",
        data_asset_name="aaa",
        batch_identifiers=IDDict({"element": "Hydrogen"}),
    )
    Helium = BatchDefinition(
        datasource_name="B",
        data_connector_name="b",
        data_asset_name="bbb",
        batch_identifiers=IDDict({"element": "Helium"}),
    )
    Lithium = BatchDefinition(
        datasource_name="C",
        data_connector_name="c",
        data_asset_name="ccc",
        batch_identifiers=IDDict({"element": "Lithium"}),
    )

    batch_list = [Hydrogen, Helium, Lithium]
    my_sorter = CustomListSorter(
        name="element", orderby="desc", reference_list=periodic_table_of_elements
    )
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [Lithium, Helium, Hydrogen]

    my_sorter = CustomListSorter(
        name="element", orderby="asc", reference_list=periodic_table_of_elements
    )
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [Hydrogen, Helium, Lithium]


@pytest.mark.integration
def test_dictionary(example_hierarchical_batch_def_list):
    [a, b, c, d, e, f, g, h, i, j] = example_hierarchical_batch_def_list
    batch_list = [a, b, c, d, e, f, g, h, i, j]
    my_sorter = DictionarySorter(
        name="date", orderby="desc", key_reference_list=["year", "month"]
    )
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [d, h, b, i, j, a, g, e, f, c]

    my_sorter = DictionarySorter(
        name="date", orderby="asc", key_reference_list=["year", "month"]
    )
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [c, f, e, g, a, j, i, b, h, d]

    my_sorter = DictionarySorter(
        name="date",
        orderby="desc",
        order_keys_by="desc",
    )
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [d, h, b, i, j, a, g, e, f, c]

    my_sorter = DictionarySorter(
        name="date",
        orderby="asc",
        order_keys_by="desc",
    )
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [c, f, e, g, a, j, i, b, h, d]

    my_sorter = DictionarySorter(
        name="date", orderby="desc", key_reference_list=["month"]
    )
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [d, h, b, g, e, i, f, j, a, c]

    my_sorter = DictionarySorter(
        name="date", orderby="asc", key_reference_list=["month"]
    )
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [a, c, f, j, e, i, b, g, h, d]

    my_sorter = DictionarySorter(
        name="date",
        orderby="desc",
    )
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [d, h, b, g, i, e, j, f, a, c]

    my_sorter = DictionarySorter(
        name="date",
        orderby="asc",
    )
    sorted_batch_list = my_sorter.get_sorted_batch_definitions(batch_list)
    assert sorted_batch_list == [c, a, f, j, e, i, g, b, h, d]


@pytest.mark.integration
def test_example_file_list_sorters(example_batch_def_list):
    [a, b, c, d, e, f, g, h, i, j] = example_batch_def_list
    batch_list = [a, b, c, d, e, f, g, h, i, j]

    name_sorter = LexicographicSorter(name="name", orderby="desc")
    timestamp_sorter = DateTimeSorter(
        name="timestamp", datetime_format="%Y%m%d", orderby="desc"
    )
    price_sorter = NumericSorter(name="price", orderby="desc")

    # 1. sorting just by name
    sorters_list = [name_sorter]
    sorters: Iterator[Sorter] = reversed(sorters_list)
    for sorter in sorters:
        sorted_batch_list = sorter.get_sorted_batch_definitions(
            batch_definitions=batch_list
        )
    assert sorted_batch_list == [f, h, a, i, j, c, g, d, e, b]

    # 2. sorting by timestamp + name
    sorters_list = [timestamp_sorter, name_sorter]
    sorters: Iterator[Sorter] = reversed(sorters_list)
    for sorter in sorters:
        sorted_batch_list = sorter.get_sorted_batch_definitions(
            batch_definitions=batch_list
        )
    assert sorted_batch_list == [g, d, i, a, f, b, c, e, h, j]

    # 3. sorting just by price + timestamp + name
    sorters_list = [price_sorter, timestamp_sorter, name_sorter]
    sorters: Iterator[Sorter] = reversed(sorters_list)
    for sorter in sorters:
        sorted_batch_list = sorter.get_sorted_batch_definitions(
            batch_definitions=batch_list
        )
    assert sorted_batch_list == [g, j, c, d, b, i, a, h, f, e]
