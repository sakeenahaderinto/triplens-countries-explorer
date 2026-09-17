WITH source AS (
    SELECT 
        alpha_3_code,
        currencies
    FROM {{ ref('stg_countries') }}
),

flattened AS (
    SELECT
        source.alpha_3_code,
        f.value:code::string AS currency_code,
        f.value:name::string AS currency_name,
        f.value:symbol::string AS currency_symbol
    FROM source,
    LATERAL FLATTEN(input => source.currencies) f
    WHERE f.value:code::string IS NOT NULL
)

SELECT * FROM flattened