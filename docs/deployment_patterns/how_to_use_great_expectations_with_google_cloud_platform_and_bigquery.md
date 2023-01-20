---
title: How to Use Great Expectations with Google Cloud Platform and BigQuery
---
import Prerequisites from './components/deployment_pattern_prerequisites.jsx'
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import Congratulations from '../guides/connecting_to_your_data/components/congratulations.md'
import TechnicalTag from '@site/docs/term_tags/_tag.mdx';

This guide will help you integrate Great Expectations (GX) with [Google Cloud Platform](https://cloud.google.com/gcp) (GCP) using our recommended workflow.

<Prerequisites>

- Have a working local installation of Great Expectations that is at least version 0.13.49.
- Have read through the documentation and are familiar with the Google Cloud Platform features that are used in this guide.
- Have completed the set-up of a GCP project with a running Google Cloud Storage container that is accessible from your region, and read/write access to a BigQuery database if this is where you are loading your data.
- Access to a GCP [Service Account](https://cloud.google.com/iam/docs/service-accounts) with permission to access and read objects in Google Cloud Storage, and read/write access to a BigQuery database if this is where you are loading your data.

</Prerequisites>


:::caution Note on Installing Great Expectations in Google Cloud Composer

  Currently, Great Expectations will only install in Composer 1 and Composer 2 environments with the following packages pinned. 

  `[tornado]==6.2`
  `[nbconvert]==6.4.5`
  `[mistune]==0.8.4`

  We are currently investigating ways to provide a smoother deployment experience in Google Composer, and will have more updates soon. 

:::

We recommend that you use Great Expectations in GCP by using the following services:
  - [Google Cloud Composer](https://cloud.google.com/composer) (GCC) for managing workflow orchestration including validating your data. GCC is built on [Apache Airflow](https://airflow.apache.org/).
  - [BigQuery](https://cloud.google.com/bigquery) or files in [Google Cloud Storage](https://cloud.google.com/storage) (GCS) as your <TechnicalTag tag="datasource" text="Datasource"/>
  - [GCS](https://cloud.google.com/storage) for storing metadata (<TechnicalTag tag="expectation_suite" text="Expectation Suites"/>, <TechnicalTag tag="validation_result" text="Validation Results"/>, <TechnicalTag tag="data_docs" text="Data Docs"/>)
  - [Google App Engine](https://cloud.google.com/appengine) (GAE) for hosting and controlling access to <TechnicalTag tag="data_docs" text="Data Docs"/>.

We also recommend that you deploy Great Expectations to GCP in two steps:
1. [Developing a local configuration for GX that uses GCP services to connect to your data, store Great Expectations metadata, and run a Checkpoint.](#part-1-local-configuration-of-great-expectations-that-connects-to-google-cloud-platform)
2. [Migrating the local configuration to Cloud Composer so that the workflow can be orchestrated automatically on GCP.](#part-2-migrating-our-local-configuration-to-cloud-composer)

The following diagram shows the recommended components for a Great Expectations deployment in GCP:

![Screenshot of Data Docs](../deployment_patterns/images/ge_and_gcp_diagram.png)

Relevant documentation for the components can also be found here:

- [How to configure an Expectation store to use GCS](../guides/setup/configuring_metadata_stores/how_to_configure_an_expectation_store_in_gcs.md)
- [How to configure a Validation Result store in GCS](../guides/setup/configuring_metadata_stores/how_to_configure_a_validation_result_store_in_gcs.md)
- [How to host and share Data Docs on GCS](../guides/setup/configuring_data_docs/how_to_host_and_share_data_docs_on_gcs.md)
- Optionally, you can also use a [Secret Manager for GCP Credentials](../guides/setup/configuring_data_contexts/how_to_configure_credentials.md)

:::note Note on V3 Expectations for BigQuery

  A small number of V3 Expectations have not been migrated to BigQuery, and will be very soon. These include:

  - `expect_column_quantile_values_to_be_between`
  - `expect_column_kl_divergence_to_be_less_than`

:::

## Part 1: Local Configuration of Great Expectations that connects to Google Cloud Platform

### 1. If necessary, upgrade your Great Expectations version

The current guide was developed and tested using Great Expectations 0.13.49. Please ensure that your current version is equal or newer than this.

A local installation of Great Expectations can be upgraded using a simple `pip install` command with the `--upgrade` flag.

```bash
pip install great-expectations --upgrade
```

### 2. Connect to Metadata Stores on GCP

The following sections describe how you can take a basic local configuration of Great Expectations and connect it to Metadata stores on GCP.

The full configuration used in this guide can be found in the [`great-expectations` repository](https://github.com/great-expectations/great_expectations/tree/develop/tests/integration/fixtures/gcp_deployment/) and is also linked at the bottom of this document.

:::note Note on Trailing Slashes in Metadata Store prefixes

  When specifying `prefix` values for Metadata Stores in GCS, please ensure that a trailing slash `/` is not included (ie `prefix: my_prefix/` ). Currently this creates an additional folder with the name `/` and stores metadata in the `/` folder instead of `my_prefix`.

:::

#### Add Expectations Store
By default, newly profiled Expectations are stored in JSON format in the `expectations/` subdirectory of your `great_expectations/` folder. A new Expectations Store can be configured by adding the following lines into your `great_expectations.yml` file, replacing the `project`, `bucket` and `prefix` with your information.

```YAML file=../../tests/integration/fixtures/gcp_deployment/great_expectations/great_expectations.yml#L38-L44
```

Great Expectations can then be configured to use this new Expectations Store, `expectations_GCS_store`, by setting the `expectations_store_name` value in the `great_expectations.yml` file.

```YAML file=../../tests/integration/fixtures/gcp_deployment/great_expectations/great_expectations.yml#L72
```

For additional details and example configurations, please refer to [How to configure an Expectation store to use GCS](../guides/setup/configuring_metadata_stores/how_to_configure_an_expectation_store_in_gcs.md).

#### Add Validations Store
By default, Validations are stored in JSON format in the `uncommitted/validations/` subdirectory of your `great_expectations/` folder. A new Validations Store can be configured by adding the following lines into your `great_expectations.yml` file, replacing the `project`, `bucket` and `prefix` with your information.

```YAML file=../../tests/integration/fixtures/gcp_deployment/great_expectations/great_expectations.yml#L52-L58
```

Great Expectations can then be configured to use this new Validations Store, `validations_GCS_store`, by setting the `validations_store_name` value in the `great_expectations.yml` file.

```YAML file=../../tests/integration/fixtures/gcp_deployment/great_expectations/great_expectations.yml#L73
```

For additional details and example configurations, please refer to  [How to configure an Validation Result store to use GCS](../guides/setup/configuring_metadata_stores/how_to_configure_a_validation_result_store_in_gcs.md).

#### Add Data Docs Store
To host and share Datadocs on GCS, we recommend using the [following guide](../guides/setup/configuring_data_docs/how_to_host_and_share_data_docs_on_gcs.md), which will explain how to host and share Data Docs on Google Cloud Storage using IP-based access.

Afterwards, your `great-expectations.yml` will contain the following configuration under `data_docs_sites`,  with `project`, and `bucket` being replaced with your information.

```YAML file=../../tests/integration/fixtures/gcp_deployment/great_expectations/great_expectations.yml#L91-L98
```


You should also be able to view the deployed DataDocs site by running the following CLI command:

```bash
gcloud app browse
```

If successful, the `gcloud` CLI will provide the URL to your app and launch it in a new browser window, and you should be able to view the index page of your Data Docs site.

### 3. Connect to your Data

The remaining sections in Part 1 contain a simplified description of [how to connect to your data in GCS](https://docs.greatexpectations.io/docs/guides/connecting_to_your_data/cloud/gcs/pandas) or [BigQuery](https://docs.greatexpectations.io/docs/guides/connecting_to_your_data/database/bigquery) and eventually build a <TechnicalTag tag="checkpoint" text="Checkpoint"/> that will be migrated to Cloud Composer. The following code can be run either in an interactive Python session or Jupyter Notebook that is in your `great_expectations/` folder.
More details can be found in the corresponding How to Guides, which have been linked.

<Tabs
  groupId="connect-to-data-gcs-bigquery"
  defaultValue='gcs'
  values={[
  {label: 'Data in GCS', value:'gcs'},
  {label: 'Data in BigQuery', value:'bigquery'},
  ]}>
<TabItem value="gcs">

To connect to your data in GCS, first instantiate your project's DataContext by importing the necessary packages and modules.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py imports"
```

Then, load your DataContext into memory using the `get_context()` method.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py get_context"
```

Next, load the following Datasource configuration that will connect to data in GCS,

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py datasource_yaml"
```

Save the configuration into your DataContext by using the `add_datasource()` function.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py add_datasource"
```

For more details on how to configure the Datasource, and additional information on authentication, please refer to [How to connect to data on GCS using Pandas
](../guides/connecting_to_your_data/cloud/gcs/pandas.md)

</TabItem>
<TabItem value="bigquery">

To connect to your data in BigQuery, first instantiate your project's DataContext by importing the necessary packages and modules.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py imports"
```

Then, load your DataContext into memory using the `get_context()` method.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py get_context"
```

Next, load the following Datasource configuration that will connect to data in BigQuery,

:::note

In order to support tables that are created as the result of queries in BigQuery, Great Expectations previously asked users to define a named permanent table to be used as a "temporary" table that could later be deleted, or set to expire by the database. This is no longer the case, and Great Expectations will automatically set tables that are created as the result of queries to expire after 1 day.

:::

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py datasource_yaml"
```

Save the configuration into your DataContext by using the `add_datasource()` function.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py add_datasource"
```

For more details on how to configure the BigQuery Datasource, please refer to [How to connect to a BigQuery database](../guides/connecting_to_your_data/database/bigquery.md)

</TabItem>
</Tabs>

### 4. Get Batch and Create ExpectationSuite

<Tabs
  groupId="connect-to-data-gcs-bigquery"
  defaultValue='gcs'
  values={[
  {label: 'Data in GCS', value:'gcs'},
  {label: 'Data in BigQuery', value:'bigquery'},
  ]}>
<TabItem value="gcs">

For our example, we will be creating an ExpectationSuite with [instant feedback from a sample Batch of data](../guides/expectations/how_to_create_and_edit_expectations_with_instant_feedback_from_a_sample_batch_of_data.md), which we will describe in our `BatchRequest`. For additional examples on how to create ExpectationSuites, either through [domain knowledge](../guides/expectations/how_to_create_and_edit_expectations_based_on_domain_knowledge_without_inspecting_data_directly.md) or using the [User Configurable Profiler](../guides/expectations/how_to_create_and_edit_expectations_with_a_profiler.md), please refer to the documentation under `How to Guides` -> `Creating and editing Expectations for your data` -> `Core skills`.

First, load a batch of data by specifying a `data_asset_name` in a `BatchRequest`.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py batch_request"
```

Next, create an ExpectationSuite (`test_gcs_suite` in our example), and use it to get a `Validator`.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py create_expectation_suite"
```

Next, use the `Validator` to run expectations on the batch and automatically add them to the ExpectationSuite. For our example, we will add `expect_column_values_to_not_be_null` and `expect_column_values_to_be_between` (`passenger_count` and `congestion_surcharge` are columns in our test data, and they can be replaced with columns in your data).

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py validator_calls"
```

Lastly, save the ExpectationSuite, which now contains our two Expectations.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py save_expectation_suite"
```

For more details on how to configure the RuntimeBatchRequest, as well as an example of how you can load data by specifying a GCS path to a single CSV, please refer to [How to connect to data on GCS using Pandas](../guides/connecting_to_your_data/cloud/gcs/pandas.md)

</TabItem>
<TabItem value="bigquery">

For our example, we will be creating our ExpectationSuite with [instant feedback from a sample Batch of data](../guides/expectations/how_to_create_and_edit_expectations_with_instant_feedback_from_a_sample_batch_of_data.md), which we will describe in our `RuntimeBatchRequest`. For additional examples on how to create ExpectationSuites, either through [domain knowledge](../guides/expectations/how_to_create_and_edit_expectations_based_on_domain_knowledge_without_inspecting_data_directly.md) or using the [User Configurable Profiler](../guides/expectations/how_to_create_and_edit_expectations_with_a_profiler.md), please refer to the documentation under `How to Guides` -> `Creating and editing Expectations for your data` -> `Core skills`.

First, load a batch of data by specifying an SQL query in a `RuntimeBatchRequest` (`SELECT * from demo.taxi_data LIMIT 10` is an example query for our test data and can be replaced with any query you would like).

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py batch_request"
```

Next, create an ExpectationSuite (`test_bigquery_suite` in our example), and use it to get a `Validator`.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py create_expectation_suite"
```

Next, use the `Validator` to run expectations on the batch and automatically add them to the ExpectationSuite. For our example, we will add `expect_column_values_to_not_be_null` and `expect_column_values_to_be_between` (`passenger_count` and `congestion_surcharge` are columns in our test data, and they can be replaced with columns in your data).

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py validator_calls"
```

Lastly, save the ExpectationSuite, which now contains our two Expectations.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py save_expectation_suite"
```

For more details on how to configure the BatchRequest, as well as an example of how you can load data by specifying a table name, please refer to [How to connect to a BigQuery database](../guides/connecting_to_your_data/database/bigquery.md)

</TabItem>
</Tabs>

### 5. Build and Run a Checkpoint

For our example, we will create a basic Checkpoint configuration using the `SimpleCheckpoint` class. For [additional examples](../guides/validation/checkpoints/how_to_create_a_new_checkpoint.md), information on [how to add validations, data, or suites to existing checkpoints](../guides/validation/checkpoints/how_to_add_validations_data_or_suites_to_a_checkpoint.md), and [more complex configurations](../guides/validation/checkpoints/how_to_configure_a_new_checkpoint_using_test_yaml_config.md) please refer to the documentation under `How to Guides` -> `Validating your data` -> `Checkpoints`.

<Tabs
  groupId="connect-to-data-gcs-bigquery"
  defaultValue='gcs'
  values={[
  {label: 'Data in GCS', value:'gcs'},
  {label: 'Data in BigQuery', value:'bigquery'},
  ]}>
<TabItem value="gcs">

Add the following Checkpoint `gcs_checkpoint` to the DataContext.  Here we are using the same `BatchRequest` and `ExpectationSuite` name that we used to create our Validator above, translated into a YAML configuration.

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py checkpoint_config"
```
```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py add_checkpoint"
```

Next, you can either run the Checkpoint directly in-code,

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py run_checkpoint"
```

or through the following CLI command.

```bash
great_expectations --v3-api checkpoint run gcs_checkpoint
```

At this point, if you have successfully configured the local prototype, you will have the following:

1. An ExpectationSuite in the GCS bucket configured in `expectations_GCS_store` (ExpectationSuite is named `test_gcs_suite` in our example).
2. A new Validation Result in the GCS bucket configured in `validation_GCS_store`.
3. Data Docs in the GCS bucket configured in `gs_site` that is accessible by running `gcloud app browse`.

Now you are ready to migrate the local configuration to Cloud Composer.

</TabItem>
<TabItem value="bigquery">

Add the following Checkpoint `bigquery_checkpoint` to the DataContext.  Here we are using the same `RuntimeBatchRequest` and `ExpectationSuite` name that we used to create our Validator above, translated into a YAML configuration.


```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py checkpoint_config"
```
```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py add_checkpoint"
```

Next, you can either run the Checkpoint directly in-code,

```python name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py run_checkpoint"
```

or through the following CLI command.

```bash
great_expectations --v3-api checkpoint run bigquery_checkpoint
```

At this point, if you have successfully configured the local prototype, you will have the following:

1. An ExpectationSuite in the GCS bucket configured in `expectations_GCS_store` (ExpectationSuite is named `test_bigquery_suite` in our example).
2. A new Validation Result in the GCS bucket configured in `validation_GCS_store`.
3. Data Docs in the GCS bucket configured in `gs_site` that is accessible by running `gcloud app browse`.

Now you are ready to migrate the local configuration to Cloud Composer.

</TabItem>
</Tabs>


## Part 2: Migrating our Local Configuration to Cloud Composer

We will now take the local GX configuration from [Part 1](#part-1-local-configuration-of-great-expectations-that-connects-to-google-cloud-platform) and migrate it to a Cloud Composer environment so that we can automate the workflow.

There are a number of ways that Great Expectations can be run in Cloud Composer or Airflow.

1. [Running a Checkpoint in Airflow using a `bash operator`](./how_to_use_great_expectations_with_airflow.md#option-1-running-a-checkpoint-with-a-bashoperator)
2. [Running a Checkpoint in Airflow using a `python operator`](./how_to_use_great_expectations_with_airflow.md#option-2-running-the-checkpoint-script-output-with-a-pythonoperator)
3. [Running a Checkpoint in Airflow using a `Airflow operator`](https://github.com/great-expectations/airflow-provider-great-expectations)

For our example, we are going to use the `bash operator` to run the Checkpoint. This portion of the guide can also be found in the following [Walkthrough Video](https://drive.google.com/file/d/1YhEMqSRkp5JDIQA_7fleiKTTlEmYx2K8/view?usp=sharing).

### 1. Create and Configure a Service Account

Create and configure a Service Account on GCS with the appropriate privileges needed to run Cloud Composer. Please follow the steps described in the [official Google Cloud documentation](https://cloud.google.com/iam/docs/service-accounts) to create a Service Account on GCP.

In order to run Great Expectations in a Cloud Composer environment, your Service Account will need the following privileges:

- `Composer Worker`
- `Logs Viewer`
- `Logs Writer`
- `Storage Object Creator`
- `Storage Object Viewer`

If you are accessing data in BigQuery, please ensure your Service account also has privileges for:

- `BigQuery Data Editor`
- `BigQuery Job User`
- `BigQuery Read Session User`

### 2. Create Cloud Composer environment

Create a Cloud Composer environment in the project you will be running Great Expectations. Please follow the steps described in the [official Google Cloud documentation](https://cloud.google.com/composer/docs/composer-2/create-environments) to create an environment that is suited for your needs.

:::info Note on Versions.
The current Deployment Guide was developed and tested in Great Expectations 0.13.49, Composer 1.17.7 and Airflow 2.0.2. Please ensure your Environment is equivalent or newer than this configuration.
:::

### 3. Install Great Expectations in Cloud Composer

Installing Python dependencies in Cloud Composer can be done through the Composer web Console (recommended), `gcloud` or through a REST query.  Please follow the steps described in [Installing Python dependencies in Google Cloud](https://cloud.google.com/composer/docs/how-to/using/installing-python-dependencies#install-package) to install `great-expectations` in Cloud Composer. If you are connecting to data in BigQuery, please ensure `sqlalchemy-bigquery` is also installed in your Cloud Composer environment.

:::info Troubleshooting Installation
If you run into trouble while installing Great Expectations in Cloud Composer, the [official Google Cloud documentation offers the following guide on troubleshooting PyPI package installations.](https://cloud.google.com/composer/docs/troubleshooting-package-installation)
:::

### 4. Move local configuration to Cloud Composer

Cloud Composer uses Cloud Storage to store Apache Airflow DAGs (also known as workflows), with each Environment having an associated Cloud Storage bucket (typically the name of the bucket will follow the pattern `[region]-[composer environment name]-[UUID]-bucket`).

The simplest way to perform the migration is to move the entire local `great_expectations/` folder from [Part 1](#part-1-local-configuration-of-great-expectations-that-connects-to-google-cloud-platform) to the Cloud Storage bucket where Composer can access the configuration.

First open the Environments page in the Cloud Console, then click on the name of the environment to open the Environment details page. In the Configuration tab, the name of the Cloud Storage bucket can be found to the right of the DAGs folder.

This will take you to the folder where DAGs are stored, which can be accessed from the Airflow worker nodes at: `/home/airflow/gcsfuse/dags`. The location we want to uploads `great_expectations/` is **one level above the `/dags` folder**.

Upload the local `great_expectations/` folder either dragging and dropping it into the window, using [`gsutil cp`](https://cloud.google.com/storage/docs/gsutil/commands/cp), or by clicking the `Upload Folder` button.

Once the `great_expectations/` folder is uploaded to the Cloud Storage bucket, it will be mapped to the Airflow instances in your Cloud Composer and be accessible from the Airflow Worker nodes at the location: `/home/airflow/gcsfuse/great_expectations`.

### 5. Write DAG and Add to Cloud Composer
<Tabs
  groupId="connect-to-data-gcs-bigquery"
  defaultValue='gcs'
  values={[
  {label: 'Data in GCS', value:'gcs'},
  {label: 'Data in BigQuery', value:'bigquery'},
  ]}>
<TabItem value="gcs">

We will create a simple DAG with a single node (`t1`) that runs a `BashOperator`, which we will store in a file named: [`ge_checkpoint_gcs.py`](https://github.com/great-expectations/great_expectations/blob/develop/tests/integration/fixtures/gcp_deployment/ge_checkpoint_gcs.py).

```python file=../../tests/integration/fixtures/gcp_deployment/ge_checkpoint_gcs.py
```

The `BashOperator` will first change directories to `/home/airflow/gcsfuse/great_expectations`, where we have uploaded our local configuration.
Then we will run the Checkpoint using same CLI command we used to run the Checkpoint locally:

```bash
great_expectations --v3-api checkpoint run gcs_checkpoint
````

To add the DAG to Cloud Composer, move `ge_checkpoint_gcs.py` to the environment's DAGs folder in Cloud Storage. First, open the Environments page in the Cloud Console, then click on the name of the environment to open the Environment details page.

On the Configuration tab, click on the name of the Cloud Storage bucket that is found to the right of the DAGs folder. Upload the local copy of the DAG you want to upload.

For more details, please consult the [official documentation for Cloud Composer](https://cloud.google.com/composer/docs/how-to/using/managing-dags#adding)

</TabItem>
<TabItem value="bigquery">

We will create a simple DAG with a single node (`t1`) that runs a `BashOperator`, which we will store in a file named:  [`ge_checkpoint_bigquery.py`](https://github.com/great-expectations/great_expectations/blob/develop/tests/integration/fixtures/gcp_deployment/ge_checkpoint_bigquery.py).

```python file=../../tests/integration/fixtures/gcp_deployment/ge_checkpoint_bigquery.py
```

The `BashOperator` will first change directories to `/home/airflow/gcsfuse/great_expectations`, where we have uploaded our local configuration.
Then we will run the Checkpoint using same CLI command we used to run the Checkpoint locally:


```bash
great_expectations --v3-api checkpoint run bigquery_checkpoint
```

To add the DAG to Cloud Composer, move `ge_checkpoint_bigquery.py` to the environment's DAGs folder in Cloud Storage. First, open the Environments page in the Cloud Console, then click on the name of the environment to open the Environment details page.

On the Configuration tab, click on the name of the Cloud Storage bucket that is found to the right of the DAGs folder. Upload the local copy of the DAG you want to upload.

For more details, please consult the [official documentation for Cloud Composer](https://cloud.google.com/composer/docs/how-to/using/managing-dags#adding)
</TabItem>
</Tabs>


### 6. Run DAG / Checkpoint

Now that the DAG has been uploaded, we can [trigger the DAG](https://cloud.google.com/composer/docs/triggering-dags) using the following methods:

1. [Trigger the DAG manually.](https://cloud.google.com/composer/docs/triggering-dags#manually)
2. [Trigger the DAG on a schedule, which we have set to be once-per-day in our DAG](https://cloud.google.com/composer/docs/triggering-dags#schedule)
3. [Trigger the DAG in response to events.](http://airflow.apache.org/docs/apache-airflow/stable/concepts/sensors.html)

In order to trigger the DAG manually, first open the Environments page in the Cloud Console, then click on the name of the environment to open the Environment details page. In the Airflow webserver column, follow the Airflow link for your environment. This will open the Airflow web interface for your Cloud Composer environment. In the interface, click on the Trigger Dag button on the DAGs page to run your DAG configuration.

### 7. Check that DAG / Checkpoint has run successfully

If the DAG run was successful, we should see the `Success` status appear on the DAGs page of the Airflow Web UI. We can also check so check that new Data Docs have been generated by accessing the URL to our `gcloud` app.

### 8. Congratulations!

You've successfully migrated your Great Expectations configuration to Cloud Composer!

There are many ways to iterate and improve this initial version, which used a `bash operator` for simplicity. For information on more sophisticated ways of triggering Checkpoints, building our DAGs, and dividing our Data Assets into Batches using DataConnectors, please refer to the following documentation:

- [How to run a Checkpoint in Airflow using a `python operator`](./how_to_use_great_expectations_with_airflow.md#option-2-running-the-checkpoint-script-output-with-a-pythonoperator).
- [How to run a Checkpoint in Airflow using a `Great Expectations Airflow operator`](https://github.com/great-expectations/airflow-provider-great-expectations)(recommended).
- [How to trigger the DAG on a schedule](https://cloud.google.com/composer/docs/triggering-dags#schedule).
- [How to trigger the DAG on a schedule](https://cloud.google.com/composer/docs/triggering-dags#schedule).
- [How to trigger the DAG in response to events](http://airflow.apache.org/docs/apache-airflow/stable/concepts/sensors.html).
- [How to use the Google Kubernetes Engine (GKE) to deploy, manage and scale your application](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/kubernetes_engine.html).
- [How to configure a DataConnector to introspect and partition tables in SQL](../guides/connecting_to_your_data/how_to_configure_a_dataconnector_to_introspect_and_partition_tables_in_sql.md).
- [How to configure a DataConnector to introspect and partition a file system or blob store](../guides/connecting_to_your_data/how_to_configure_a_dataconnector_to_introspect_and_partition_a_file_system_or_blob_store.md).

Also, the following scripts and configurations can be found here:

- Local GX configuration used in this guide can be found in the [`great-expectations` GIT repository](https://github.com/great-expectations/great_expectations/tree/develop/tests/integration/fixtures/gcp_deployment/).
- [Script to test BigQuery configuration](https://github.com/great-expectations/great_expectations/blob/develop/tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_bigquery_yaml_configs.py).
- [Script to test GCS configuration](https://github.com/great-expectations/great_expectations/blob/develop/tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs_yaml_configs.py).
