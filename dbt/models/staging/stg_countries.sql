WITH source AS (
    SELECT * FROM {{ source('raw', 'countries_raw') }}
),

renamed AS (
    SELECT
        -- Primary & Identifiers
        payload:codes.alpha_3::string AS alpha_3_code,
        payload:codes.alpha_2::string AS alpha_2_code,
        payload:names.common::string AS country_name,
        payload:names.official::string AS official_name,

        -- Geographic & Demographic Attributes
        payload:region::string AS region,
        payload:subregion::string AS subregion,
        payload:population::number AS population,
        payload:landlocked::boolean AS is_landlocked,
        payload:flag.emoji::string AS flag_emoji,

        -- Semi-structured fields (keep as VARIANT for downstream unnesting)
        payload:capitals AS capitals,
        payload:languages AS languages,
        payload:currencies AS currencies,
        payload:timezones AS timezones,
        payload:borders AS borders,
        payload:calling_codes AS calling_codes,

        -- Metadata
        loaded_at

    FROM source
)

SELECT * FROM renamed
WHERE NULLIF(alpha_3_code, '') IS NOT NULL