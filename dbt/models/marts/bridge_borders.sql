WITH source AS (
    SELECT 
        alpha_3_code,
        borders
    FROM {{ ref('stg_countries') }}
),

flattened AS (
    SELECT
        source.alpha_3_code,
        f.value::string AS border_country_code
    FROM source,
    LATERAL FLATTEN(input => source.borders) f
    WHERE f.value::string IS NOT NULL
)

SELECT * FROM flattened