import pytest

from great_expectations.data_context.data_context.file_data_context import (
    FileDataContext,
)
from great_expectations.util import get_context

"""
This module specifically tests for combinations of paths for datasource new.

Tests are named according to the matrix of possible states is as follows:

run from                    data path
-------------------------------------
within the ge dir           absolute
within the ge dir           relative
adjacent to the ge dir      absolute
adjacent to the ge dir      relative
misc + --config             absolute
misc + --config             relative

Please note that all tests have the same expected result, hence the consolidation.
"""

import os
from unittest import mock

import nbformat
from click.testing import CliRunner
from nbconvert.preprocessors import ExecutePreprocessor

from great_expectations.cli import cli


def _run_notebook(context: FileDataContext) -> None:
    uncommitted_dir = os.path.join(context.root_directory, context.GX_UNCOMMITTED_DIR)
    expected_notebook = os.path.join(uncommitted_dir, "datasource_new.ipynb")
    with open(expected_notebook) as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=60, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": uncommitted_dir}})


def _run_cli_datasource_new_path_test(
    context: FileDataContext, args: str, invocation_input: str, base_path: str
) -> None:
    root_dir = context.root_directory
    runner = CliRunner(mix_stderr=True)
    result = runner.invoke(
        cli,
        args=args,
        input=invocation_input,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    _run_notebook(context)

    # Renew a context since we executed a notebook in a different process
    del context
    context = get_context(context_root_dir=root_dir)
    assert context.list_datasources() == [
        {
            "name": "my_datasource",
            "class_name": "Datasource",
            "module_name": "great_expectations.datasource",
            "execution_engine": {
                "module_name": "great_expectations.execution_engine",
                "class_name": "PandasExecutionEngine",
            },
            "data_connectors": {
                "default_inferred_data_connector_name": {
                    "default_regex": {
                        "group_names": ["data_asset_name"],
                        "pattern": "(.*)",
                    },
                    "module_name": "great_expectations.datasource.data_connector",
                    "base_directory": f"../../{base_path}",
                    "class_name": "InferredAssetFilesystemDataConnector",
                },
                "default_runtime_data_connector_name": {
                    "assets": {
                        "my_runtime_asset_name": {
                            "batch_identifiers": ["runtime_batch_identifier_name"],
                            "class_name": "Asset",
                            "module_name": "great_expectations.datasource.data_connector.asset",
                        }
                    },
                    "class_name": "RuntimeDataConnector",
                    "module_name": "great_expectations.datasource.data_connector",
                },
            },
        }
    ]


@mock.patch("subprocess.call", return_value=True, side_effect=None)
@pytest.mark.slow  # 5.17s
def test_cli_datasource_new_run_from_ge_dir_absolute_data_path(
    mock_subprocess, monkeypatch, empty_data_context, filesystem_csv_2
):
    context = empty_data_context
    files_directory = os.path.basename(filesystem_csv_2)
    monkeypatch.chdir(context.root_directory)
    invocation = "--v3-api datasource new"
    invocation_input = f"1\n1\n{filesystem_csv_2}\n"
    _run_cli_datasource_new_path_test(
        context, invocation, invocation_input, files_directory
    )


@mock.patch("subprocess.call", return_value=True, side_effect=None)
@pytest.mark.slow  # 5.13s
def test_cli_datasource_new_run_from_ge_dir_relative_data_path(
    mock_subprocess, monkeypatch, empty_data_context, filesystem_csv_2
):
    context = empty_data_context
    files_directory = os.path.basename(filesystem_csv_2)
    monkeypatch.chdir(context.root_directory)
    invocation = "--v3-api datasource new"
    invocation_input = f"1\n1\n../../{files_directory}\n"
    _run_cli_datasource_new_path_test(
        context, invocation, invocation_input, files_directory
    )


@mock.patch("subprocess.call", return_value=True, side_effect=None)
@pytest.mark.slow  # 5.32s
def test_cli_datasource_new_run_from_adjacent_dir_absolute_data_path(
    mock_subprocess, monkeypatch, empty_data_context, filesystem_csv_2
):
    context = empty_data_context
    adjacent_dir = os.path.dirname(context.root_directory)
    files_directory = os.path.basename(filesystem_csv_2)
    monkeypatch.chdir(adjacent_dir)
    invocation = "--v3-api datasource new"
    invocation_input = f"1\n1\n{filesystem_csv_2}\n"
    _run_cli_datasource_new_path_test(
        context, invocation, invocation_input, files_directory
    )


@mock.patch("subprocess.call", return_value=True, side_effect=None)
@pytest.mark.slow  # 5.28s
def test_cli_datasource_new_run_from_adjacent_dir_relative_data_path(
    mock_subprocess, monkeypatch, empty_data_context, filesystem_csv_2
):
    context = empty_data_context
    adjacent_dir = os.path.dirname(context.root_directory)
    files_directory = os.path.basename(filesystem_csv_2)
    monkeypatch.chdir(adjacent_dir)
    invocation = "--v3-api datasource new"
    invocation_input = f"1\n1\n../{files_directory}\n"
    _run_cli_datasource_new_path_test(
        context, invocation, invocation_input, files_directory
    )


@mock.patch("subprocess.call", return_value=True, side_effect=None)
@pytest.mark.slow  # 5.22s
def test_cli_datasource_new_run_from_misc_dir_using_config_flag_absolute_data_path(
    mock_subprocess, monkeypatch, empty_data_context, filesystem_csv_2, misc_directory
):
    context = empty_data_context
    files_directory = os.path.basename(filesystem_csv_2)
    monkeypatch.chdir(misc_directory)
    invocation = f"--config {context.root_directory} --v3-api datasource new"
    invocation_input = f"1\n1\n{filesystem_csv_2}\n"
    _run_cli_datasource_new_path_test(
        context, invocation, invocation_input, files_directory
    )


@mock.patch("subprocess.call", return_value=True, side_effect=None)
@pytest.mark.slow  # 5.36s
def test_cli_datasource_new_run_from_misc_dir_using_config_flag_relative_data_path(
    mock_subprocess, monkeypatch, empty_data_context, filesystem_csv_2, misc_directory
):
    context = empty_data_context
    files_directory = os.path.basename(filesystem_csv_2)
    monkeypatch.chdir(misc_directory)
    invocation = f"--config {context.root_directory} --v3-api datasource new"
    invocation_input = f"1\n1\n../{files_directory}\n"
    _run_cli_datasource_new_path_test(
        context, invocation, invocation_input, files_directory
    )
