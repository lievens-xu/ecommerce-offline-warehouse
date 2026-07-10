{% macro generate_schema_name(custom_schema_name, node) -%}
    {#
        Custom schema name macro for the e-commerce data warehouse.

        This macro ensures that when a model uses `{{ config(schema='dwd') }}`,
        the output schema is exactly `dwd`, not `target_schema_dwd`.

        此宏确保当模型使用 `{{ config(schema='dwd') }}` 时，
        输出 schema 正好是 `dwd`，而不是 `target_schema_dwd`。

        - If custom_schema_name is provided (e.g., dwd, dws, ads), use it directly.
        - Otherwise, fall back to the target schema (e.g., dbt_dev).
    -#}
    {{ custom_schema_name | default(target.schema) }}
{%- endmacro %}