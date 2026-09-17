WITH source AS (
    SELECT 
        alpha_3_code,
        timezones
    FROM {{ ref('stg_countries') }}
),

flattened AS (
    SELECT
        source.alpha_3_code,
        f.value::string AS timezone
    FROM source,
    LATERAL FLATTEN(input => source.timezones) f
    WHERE f.value::string IS NOT NULL
)

SELECT * FROM flattened