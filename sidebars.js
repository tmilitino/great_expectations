module.exports = {
  docs: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started (A Tutorial)',
      link: { type: 'doc', id: 'tutorials/getting_started/tutorial_overview' },
      items: [
        { type: 'doc', id: 'tutorials/getting_started/tutorial_setup', label: '1. Setup' },
        { type: 'doc', id: 'tutorials/getting_started/tutorial_connect_to_data', label: '2. Connect to Data' },
        { type: 'doc', id: 'tutorials/getting_started/tutorial_create_expectations', label: '3. Create Expectations' },
        { type: 'doc', id: 'tutorials/getting_started/tutorial_validate_data', label: '4. Validate Data' },
        { type: 'doc', id: 'tutorials/getting_started/tutorial_review', label: 'Review and next steps' }
      ]
    },
    {
      type: 'category',
      label: 'Step 1: Setup',
      link: { type: 'doc', id: 'guides/setup/setup_overview' },
      items: [
        {
          type: 'category',
          label: 'Installation',
          items: [
            'guides/setup/installation/local',
            'guides/setup/installation/hosted_environment'
          ]
        },
        {
          type: 'category',
          label: 'Data Contexts',
          items: [
            'guides/setup/configuring_data_contexts/how_to_configure_a_new_data_context_with_the_cli',
            'guides/setup/configuring_data_contexts/how_to_configure_datacontext_components_using_test_yaml_config',
            'guides/setup/configuring_data_contexts/how_to_configure_credentials',
            'guides/setup/configuring_data_contexts/how_to_instantiate_a_data_context_without_a_yml_file'
          ]
        },
        {
          type: 'category',
          label: 'Metadata Stores',
          items: [
            {
              type: 'category',
              label: 'Expectation Stores',
              items: [
                'guides/setup/configuring_metadata_stores/how_to_configure_an_expectation_store_in_amazon_s3',
                'guides/setup/configuring_metadata_stores/how_to_configure_an_expectation_store_in_azure_blob_storage',
                'guides/setup/configuring_metadata_stores/how_to_configure_an_expectation_store_in_gcs',
                'guides/setup/configuring_metadata_stores/how_to_configure_an_expectation_store_on_a_filesystem',
                'guides/setup/configuring_metadata_stores/how_to_configure_an_expectation_store_to_postgresql'
              ]
            },
            {
              type: 'category',
              label: 'Validation Result Stores',
              items: [
                'guides/setup/configuring_metadata_stores/how_to_configure_a_validation_result_store_in_amazon_s3',
                'guides/setup/configuring_metadata_stores/how_to_configure_a_validation_result_store_in_azure_blob_storage',
                'guides/setup/configuring_metadata_stores/how_to_configure_a_validation_result_store_in_gcs',
                'guides/setup/configuring_metadata_stores/how_to_configure_a_validation_result_store_on_a_filesystem',
                'guides/setup/configuring_metadata_stores/how_to_configure_a_validation_result_store_to_postgresql'
              ]
            },
            {
              type: 'category',
              label: 'Metric Stores',
              items: [
                'guides/setup/configuring_metadata_stores/how_to_configure_a_metricsstore'
              ]
            }
          ]
        },
        {
          type: 'category',
          label: 'Data Docs',
          items: [
            'guides/setup/configuring_data_docs/how_to_host_and_share_data_docs_on_a_filesystem',
            'guides/setup/configuring_data_docs/how_to_host_and_share_data_docs_on_azure_blob_storage',
            'guides/setup/configuring_data_docs/how_to_host_and_share_data_docs_on_gcs',
            'guides/setup/configuring_data_docs/how_to_host_and_share_data_docs_on_amazon_s3'
          ]
        },
        { type: 'doc', id: 'guides/setup/index', label: 'Index' }
      ]
    },
    {
      type: 'category',
      label: 'Step 2: Connect to data',
      link: { type: 'doc', id: 'guides/connecting_to_your_data/connect_to_data_overview' },
      items: [
        {
          type: 'category',
          label: 'Core skills',
          items: [
            'guides/connecting_to_your_data/how_to_choose_which_dataconnector_to_use',
            'guides/connecting_to_your_data/how_to_choose_between_working_with_a_single_or_multiple_batches_of_data',
            'guides/connecting_to_your_data/datasource_configuration/how_to_configure_a_pandas_datasource',
            'guides/connecting_to_your_data/datasource_configuration/how_to_configure_a_spark_datasource',
            'guides/connecting_to_your_data/datasource_configuration/how_to_configure_a_sql_datasource',
            'guides/connecting_to_your_data/how_to_configure_an_inferredassetdataconnector',
            'guides/connecting_to_your_data/how_to_configure_a_configuredassetdataconnector',
            'guides/connecting_to_your_data/how_to_configure_a_runtimedataconnector',
            'guides/connecting_to_your_data/how_to_configure_a_dataconnector_to_introspect_and_partition_a_file_system_or_blob_store',
            'guides/connecting_to_your_data/how_to_configure_a_dataconnector_to_introspect_and_partition_tables_in_sql',
            'guides/connecting_to_your_data/how_to_create_a_batch_of_data_from_an_in_memory_spark_or_pandas_dataframe',
            'guides/connecting_to_your_data/how_to_get_one_or_more_batches_of_data_from_a_configured_datasource'
          ]
        },
        {
          type: 'category',
          label: 'In memory',
          items: [
            'guides/connecting_to_your_data/in_memory/pandas',
            'guides/connecting_to_your_data/in_memory/spark'
          ]
        },
        {
          type: 'category',
          label: 'Database',
          items: [
            'guides/connecting_to_your_data/database/athena',
            'guides/connecting_to_your_data/database/bigquery',
            'guides/connecting_to_your_data/database/mssql',
            'guides/connecting_to_your_data/database/mysql',
            'guides/connecting_to_your_data/database/postgres',
            'guides/connecting_to_your_data/database/redshift',
            'guides/connecting_to_your_data/database/snowflake',
            'guides/connecting_to_your_data/database/sqlite',
            'guides/connecting_to_your_data/database/trino'
          ]
        },
        {
          type: 'category',
          label: 'Filesystem',
          items: [
            'guides/connecting_to_your_data/filesystem/pandas',
            'guides/connecting_to_your_data/filesystem/spark'
          ]
        },
        {
          type: 'category',
          label: 'Cloud',
          items: [
            'guides/connecting_to_your_data/cloud/s3/pandas',
            'guides/connecting_to_your_data/cloud/s3/spark',
            'guides/connecting_to_your_data/cloud/gcs/pandas',
            'guides/connecting_to_your_data/cloud/gcs/spark',
            'guides/connecting_to_your_data/cloud/azure/pandas',
            'guides/connecting_to_your_data/cloud/azure/spark'
          ]
        },
        {
          type: 'category',
          label: 'Advanced',
          items: [
            'guides/connecting_to_your_data/advanced/how_to_configure_a_dataconnector_for_splitting_and_sampling_a_file_system_or_blob_store',
            'guides/connecting_to_your_data/advanced/how_to_configure_a_dataconnector_for_splitting_and_sampling_tables_in_sql'
          ]
        },
        { type: 'doc', id: 'guides/connecting_to_your_data/index', label: 'Index' }
      ]
    },
    {
      type: 'category',
      label: 'Step 3: Create Expectations',
      link: { type: 'doc', id: 'guides/expectations/create_expectations_overview' },
      items: [
        {
          type: 'category',
          label: 'Core skills',
          items: [
            'guides/expectations/how_to_create_and_edit_expectations_based_on_domain_knowledge_without_inspecting_data_directly',
            'guides/expectations/how_to_create_and_edit_expectations_with_a_profiler',
            'guides/expectations/how_to_create_and_edit_expectations_with_instant_feedback_from_a_sample_batch_of_data',
            { type: 'doc', id: 'guides/miscellaneous/how_to_configure_notebooks_generated_by_suite_edit' }
          ]
        },
        {
          type: 'category',
          label: 'Profilers and Data Assistants',
          items: [
            'guides/expectations/data_assistants/how_to_create_an_expectation_suite_with_the_onboarding_data_assistant',
            'guides/expectations/advanced/how_to_create_a_new_expectation_suite_using_rule_based_profilers',
            'guides/expectations/advanced/how_to_create_a_new_expectation_suite_by_profiling_from_a_jsonschema_file'
          ]
        },
        {
          type: 'category',
          label: 'Advanced skills',
          items: [
            'guides/expectations/advanced/how_to_create_expectations_that_span_multiple_batches_using_evaluation_parameters',
            'guides/expectations/advanced/how_to_dynamically_load_evaluation_parameters_from_a_database',
            'guides/expectations/advanced/how_to_compare_two_tables_with_the_user_configurable_profiler'
          ]
        },
        {
          type: 'category',
          label: 'Creating Custom Expectations',
          items: [
            'guides/expectations/creating_custom_expectations/overview',
            'guides/expectations/creating_custom_expectations/how_to_create_custom_column_aggregate_expectations',
            'guides/expectations/creating_custom_expectations/how_to_create_custom_column_map_expectations',
            'guides/expectations/creating_custom_expectations/how_to_create_custom_table_expectations',
            'guides/expectations/creating_custom_expectations/how_to_create_custom_column_pair_map_expectations',
            'guides/expectations/creating_custom_expectations/how_to_create_custom_multicolumn_map_expectations',
            'guides/expectations/creating_custom_expectations/how_to_create_custom_regex_based_column_map_expectations',
            'guides/expectations/creating_custom_expectations/how_to_create_custom_set_based_column_map_expectations',
            'guides/expectations/creating_custom_expectations/how_to_create_custom_query_expectations',
            'guides/expectations/creating_custom_expectations/how_to_create_custom_parameterized_expectations',
            'guides/expectations/creating_custom_expectations/how_to_use_custom_expectations',
            {
              type: 'category',
              label: 'Adding Features to Custom Expectations',
              items: [
                'guides/expectations/advanced/how_to_add_comments_to_expectations_and_display_them_in_data_docs',
                'guides/expectations/features_custom_expectations/how_to_add_example_cases_for_an_expectation',
                'guides/expectations/features_custom_expectations/how_to_add_input_validation_for_an_expectation',
                'guides/expectations/features_custom_expectations/how_to_add_spark_support_for_an_expectation',
                'guides/expectations/features_custom_expectations/how_to_add_sqlalchemy_support_for_an_expectation'
              ]
            }
          ]
        },
        { type: 'doc', id: 'guides/expectations/index', label: 'Index' }
      ]
    },
    {
      type: 'category',
      label: 'Step 4: Validate data',
      link: { type: 'doc', id: 'guides/validation/validate_data_overview' },
      items: [
        {
          type: 'category',
          label: 'Core skills',
          items: [
            'guides/validation/how_to_validate_data_by_running_a_checkpoint'
          ]
        },
        {
          type: 'category',
          label: 'Checkpoints',
          items: [
            'guides/validation/checkpoints/how_to_add_validations_data_or_suites_to_a_checkpoint',
            'guides/validation/checkpoints/how_to_create_a_new_checkpoint',
            'guides/validation/checkpoints/how_to_configure_a_new_checkpoint_using_test_yaml_config',
            'guides/validation/checkpoints/how_to_pass_an_in_memory_dataframe_to_a_checkpoint'
          ]
        },
        {
          type: 'category',
          label: 'Actions',
          items: [
            'guides/validation/validation_actions/how_to_trigger_email_as_a_validation_action',
            'guides/validation/validation_actions/how_to_collect_openlineage_metadata_using_a_validation_action',
            'guides/validation/validation_actions/how_to_trigger_opsgenie_notifications_as_a_validation_action',
            'guides/validation/validation_actions/how_to_trigger_slack_notifications_as_a_validation_action',
            'guides/validation/validation_actions/how_to_update_data_docs_as_a_validation_action'
          ]
        },
        {
          type: 'category',
          label: 'Advanced',
          items: [
            'guides/validation/advanced/how_to_deploy_a_scheduled_checkpoint_with_cron',
            'guides/validation/advanced/how_to_get_data_docs_urls_for_custom_validation_actions',
            'guides/validation/advanced/how_to_validate_data_without_a_checkpoint',
            'guides/validation/advanced/how_to_validate_data_with_an_in_memory_checkpoint'
          ]
        },
        { type: 'doc', id: 'guides/validation/index', label: 'Index' }
      ]
    },
    {
      type: 'category',
      label: 'Integration guides',
      link: { type: 'doc', id: 'deployment_patterns/integrations_and_howtos_overview' },
      items: [
        {
          type: 'category',
          label: 'Using Great Expectations with AWS',
          items: [
            'deployment_patterns/how_to_use_great_expectations_in_aws_glue',
            { label: 'How to use Great Expectations with AWS using S3 and Pandas', type: 'doc', id: 'deployment_patterns/how_to_use_gx_with_aws/how_to_use_gx_with_aws_using_cloud_storage_and_pandas' }
          ]
        },
        'deployment_patterns/how_to_instantiate_a_data_context_hosted_environments',
        'deployment_patterns/how_to_instantiate_a_data_context_on_an_emr_spark_cluster',
        'deployment_patterns/how_to_use_great_expectations_with_airflow',
        'deployment_patterns/how_to_use_great_expectations_in_databricks',
        { type: 'doc', id: 'integrations/integration_datahub' },
        'deployment_patterns/how_to_use_great_expectations_in_deepnote',
        'deployment_patterns/how_to_use_great_expectations_in_flyte',
        'deployment_patterns/how_to_use_great_expectations_with_google_cloud_platform_and_bigquery',
        'deployment_patterns/how_to_use_great_expectations_with_meltano',
        'deployment_patterns/how_to_use_great_expectations_with_prefect',
        'deployment_patterns/how_to_use_great_expectations_with_ydata_synthetic',
        'deployment_patterns/how_to_use_great_expectations_in_emr_serverless',
        { type: 'doc', id: 'integrations/integration_zenml' },
        { type: 'doc', id: 'deployment_patterns/index', label: 'Index' }
      ]
    },
    {
      type: 'category',
      label: 'Contributing',
      link: { type: 'doc', id: 'contributing/contributing' },
      items: [
        {
          type: 'category',
          label: 'Contributing basics',
          items: [
            { type: 'doc', id: 'contributing/contributing_setup' },
            { type: 'doc', id: 'contributing/contributing_checklist' },
            { type: 'doc', id: 'contributing/contributing_github' },
            { type: 'doc', id: 'contributing/contributing_test' },
            { type: 'doc', id: 'contributing/contributing_maturity' },
            { type: 'doc', id: 'contributing/contributing_misc' }
          ]
        },
        {
          type: 'category',
          label: 'Contributing specifics',
          items: [
            {
              type: 'category',
              label: 'How to contribute how-to guides',
              items: [
                { type: 'doc', id: 'guides/miscellaneous/how_to_write_a_how_to_guide' },
                { type: 'doc', id: 'guides/miscellaneous/how_to_template' }
              ]
            },
            {
              type: 'category',
              label: 'How to contribute integration documentation',
              items: [
                'integrations/contributing_integration',
                { type: 'doc', id: 'integrations/integration_template', label: 'TEMPLATE Integration Document' }
              ]
            },
            { type: 'doc', id: 'guides/expectations/contributing/how_to_contribute_a_custom_expectation_to_great_expectations' },
            { type: 'doc', id: 'contributing/contributing_package' }
          ]
        },
        {
          type: 'category',
          label: 'Style guides',
          items: [
            { type: 'doc', id: 'contributing/style_guides/docs_style' },
            { type: 'doc', id: 'contributing/style_guides/code_style' },
            { type: 'doc', id: 'contributing/style_guides/cli_and_notebooks_style' }
          ]
        },
        'contributing/index'
      ]
    },
    {
      type: 'category',
      label: 'Reference',
      link: { type: 'doc', id: 'reference/reference_overview' },
      items: [
        {
          type: 'category',
          label: 'Supplemental documentation',
          link: { type: 'doc', id: 'reference/supplemental_documentation' },
          items: [
            { type: 'doc', id: 'guides/miscellaneous/how_to_use_the_great_expectations_cli' },
            { type: 'doc', id: 'guides/miscellaneous/how_to_use_the_project_check_config_command' },
            { type: 'doc', id: 'reference/customize_your_deployment' },
            { type: 'doc', id: 'reference/anonymous_usage_statistics' }
          ]
        },
        {
          type: 'category',
          label: 'API documentation',
          link: { type: 'doc', id: 'reference/api_reference' },
          items: [
            {
              type: 'autogenerated',
              dirName: 'reference/api'
            }
          ]
        },
        {
          type: 'category',
          label: 'Glossary of Terms',
          link: { type: 'doc', id: 'glossary' },
          items: [
            'terms/action',
            'terms/batch',
            'terms/batch_request',
            'terms/custom_expectation',
            'terms/checkpoint',
            'terms/cli',
            'terms/datasource',
            'terms/data_context',
            'terms/data_asset',
            'terms/data_assistant',
            'terms/data_connector',
            'terms/data_docs',
            'terms/evaluation_parameter',
            'terms/execution_engine',
            {
              type: 'category',
              label: 'Expectations',
              link: { type: 'doc', id: 'terms/expectation' },
              collapsed: true,
              items: [
                { type: 'doc', id: 'reference/expectations/conditional_expectations' },
                { type: 'doc', id: 'reference/expectations/distributional_expectations' },
                { type: 'doc', id: 'reference/expectations/implemented_expectations' },
                { type: 'doc', id: 'reference/expectation_suite_operations' },
                { type: 'doc', id: 'reference/expectations/result_format' },
                { type: 'doc', id: 'reference/expectations/standard_arguments' }
              ]
            },
            'terms/expectation_suite',
            'terms/metric',
            'terms/plugin',
            'terms/profiler',
            {
              type: 'category',
              label: 'Stores',
              link: { type: 'doc', id: 'terms/store' },
              items: [
                'terms/checkpoint_store',
                'terms/data_docs_store',
                'terms/evaluation_parameter_store',
                'terms/expectation_store',
                'terms/metric_store',
                'terms/validation_result_store'
              ]
            },
            'terms/renderer',
            'terms/supporting_resource',
            'terms/validator',
            'terms/validation_result'
          ]
        }
      ]
    },
    { type: 'doc', id: 'changelog' },
    { type: 'doc', id: 'guides/miscellaneous/migration_guide' }
  ]
}
