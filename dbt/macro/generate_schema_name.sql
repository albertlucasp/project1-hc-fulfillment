{#
    Override dbt's built-in generate_schema_name macro.

    Default dbt behavior concatenates a model's custom +schema config onto
    the profile's target schema (e.g. "staging" + "intermediate" ->
    "staging_intermediate") - that exists to give each developer on a shared
    warehouse their own isolated sandbox schema. This is a single-developer
    project on a personal SQL Server instance, so that isolation isn't
    needed; instead we want +schema to be used exactly as configured, so
    staging/intermediate/marts models land in schemas of those exact names,
    mirroring the raw/audit split ingestion already uses.
#}

{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}

        {{ default_schema }}

    {%- else -%}

        {{ custom_schema_name | trim }}

    {%- endif -%}

{%- endmacro %}