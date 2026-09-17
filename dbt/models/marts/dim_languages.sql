WITH source AS (
    SELECT 
        alpha_3_code,
        languages
    FROM {{ ref('stg_countries') }}
),

flattened AS (
    SELECT
        source.alpha_3_code,
        f.value:iso639_1::string AS language_code,
        f.value:name::string AS language_name,
        f.value:native_name::string AS language_native_name
    FROM source,
    LATERAL FLATTEN(input => source.languages) f
    WHERE f.value:name::string IS NOT NULL
)

SELECT * FROM flattened