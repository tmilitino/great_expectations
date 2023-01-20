---
title: How to connect to a BigQuery database
---
import Prerequisites from '../components/prerequisites.jsx'
import WhereToRunCode from '../components/where_to_run_code.md'
import NextSteps from '../components/next_steps.md'
import Congratulations from '../components/congratulations.md'
import DatabaseCredentials from '../components/adding_database_credentials.md'
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import TechnicalTag from '@site/docs/term_tags/_tag.mdx';

This guide will help you connect to data in a BigQuery database.
This will allow you to <TechnicalTag tag="validation" text="Validate" /> and explore your data.

<Prerequisites>

- Have access to data in a BigQuery database
- Followed the [Google Cloud Library guide](https://googleapis.dev/python/google-api-core/latest/auth.html) for authentication

</Prerequisites>

## Steps

### 1. Choose how to run the code in this guide

<WhereToRunCode />

### 2. Install required dependencies

First, install the necessary dependencies for Great Expectations to connect to your BigQuery database by running the following in your terminal:

```console
pip install sqlalchemy-bigquery
```

### 3. Add credentials

<DatabaseCredentials />

For this guide we will use a `connection_string` like this:

```
bigquery://<GCP_PROJECT>/<BIGQUERY_DATASET>
```

### 4. Instantiate your project's DataContext

Import these necessary packages and modules.

```python name="tests/integration/docusaurus/connecting_to_your_data/database/bigquery_yaml_example.py imports"
```

Load your DataContext into memory using the `get_context()` method.

```python name="tests/integration/docusaurus/connecting_to_your_data/database/bigquery_yaml_example.py get_context"
```

### 5. Configure your Datasource

<Tabs
  groupId="yaml-or-python"
  defaultValue='yaml'
  values={[
  {label: 'YAML', value:'yaml'},
  {label: 'Python', value:'python'},
  ]}>

<TabItem value="yaml">

Put your connection string in this template:

```python name="tests/integration/docusaurus/connecting_to_your_data/database/bigquery_yaml_example.py datasource_yaml"
```

Run this code to test your configuration.

```python name="tests/integration/docusaurus/connecting_to_your_data/database/bigquery_yaml_example.py test_yaml_config"
```

</TabItem>

<TabItem value="python">

Put your connection string in this template:

```python name="tests/integration/docusaurus/connecting_to_your_data/database/bigquery_python_example.py datasource_config"
```

Run this code to test your configuration.

```python name="tests/integration/docusaurus/connecting_to_your_data/database/bigquery_python_example.py test_yaml_config"
```

</TabItem>

</Tabs>

You will see your database tables listed as `Available data_asset_names` in the output of `test_yaml_config()`.

Feel free to adjust your configuration and re-run `test_yaml_config` as needed.

### 6. Save the Datasource configuration to your DataContext

Save the configuration into your `DataContext` by using the `add_datasource()` function.

:::note

In order to support tables that are created as the result of queries in BigQuery, Great Expectations previously asked users to define a named permanent table to be used as a "temporary" table that could later be deleted, or set to expire by the database. This is no longer the case, and Great Expectations will automatically set tables that are created as the result of queries to expire after 1 day.

:::

<Tabs
  groupId="yaml-or-python"
  defaultValue='yaml'
  values={[
  {label: 'YAML', value:'yaml'},
  {label: 'Python', value:'python'},
  ]}>

<TabItem value="yaml">

```python name="tests/integration/docusaurus/connecting_to_your_data/database/bigquery_yaml_example.py add_datasource"
```

</TabItem>

<TabItem value="python">

```python name="tests/integration/docusaurus/connecting_to_your_data/database/bigquery_python_example.py add_datasource"
```

</TabItem>

</Tabs>

### 7. Test your new Datasource

Verify your new <TechnicalTag tag="datasource" text="Datasource" /> by loading data from it into a <TechnicalTag tag="validator" text="Validator" /> using a `BatchRequest`.

<Tabs
  defaultValue='runtime_batch_request'
  values={[
  {label: 'Using a SQL query', value:'runtime_batch_request'},
  {label: 'Using a table name', value:'batch_request'},
  ]}>

<TabItem value="runtime_batch_request">

Here is an example of loading data by specifying a SQL query.

```python name="tests/integration/docusaurus/connecting_to_your_data/database/bigquery_yaml_example.py runtime_batch_request"
```

</TabItem>

<TabItem value="batch_request">

Here is an example of loading data by specifying an existing table name.

```python name="tests/integration/docusaurus/connecting_to_your_data/database/bigquery_python_example.py batch_request"
```

</TabItem>

</Tabs>

<Congratulations />

## Additional Notes

To view the full scripts used in this page, see them on GitHub:

- [bigquery_yaml_example.py](https://github.com/great-expectations/great_expectations/blob/develop/tests/integration/docusaurus/connecting_to_your_data/database/bigquery_yaml_example.py)
- [bigquery_python_example.py](https://github.com/great-expectations/great_expectations/blob/develop/tests/integration/docusaurus/connecting_to_your_data/database/bigquery_python_example.py)

## Next Steps

<NextSteps />
