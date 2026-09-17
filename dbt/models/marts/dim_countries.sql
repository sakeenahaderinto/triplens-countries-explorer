WITH source AS (
    SELECT * FROM {{ ref('stg_countries') }}
),

renamed AS (
    SELECT
        alpha_3_code,
        alpha_2_code,
        country_name,
        official_name,
        region,
        subregion,
        population,
        is_landlocked,
        flag_emoji
    FROM source
)

SELECT * FROM renamed