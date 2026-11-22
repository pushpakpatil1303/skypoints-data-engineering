
-- Refresh staging with cleaned member profiles
INSERT OVERWRITE INTO SKYPOINTS_DB.STAGING.MEMBER_PROFILE (
    MEMBER_NAME,
    MEMBER_ID,
    ENROLLMENT_DATE,
    LAST_FLIGHT_DATE,
    TIER_CODE,
    AGENT_NAME,
    STATE,
    COUNTRY,
    POST_CODE,
    DOB,
    IS_ACTIVE,
    AGE,
    STALE_MEMBER,
    SOURCE_FILE,
    LOAD_TIMESTAMP
)

WITH standardized AS (
    SELECT
        MEMBER_NAME,
        MEMBER_ID,
        TIER_CODE,
        AGENT_NAME,
        STATE,
        COUNTRY,
        POST_CODE,
        IS_ACTIVE,
        SOURCE_FILE,
        LOAD_TIMESTAMP,

        -- Convert enrollment dates based on country
        CASE
            WHEN COUNTRY = 'USA'
                 AND LENGTH(TRIM(ENROLLMENT_DATE)) = 7
            THEN TRY_TO_DATE(
                '0' || TRIM(ENROLLMENT_DATE),
                'MMDDYYYY'
            )

            WHEN COUNTRY = 'USA'
                 AND LENGTH(TRIM(ENROLLMENT_DATE)) = 8
            THEN TRY_TO_DATE(
                TRIM(ENROLLMENT_DATE),
                'MMDDYYYY'
            )

            ELSE TRY_TO_DATE(
                LEFT(ENROLLMENT_DATE, 10),
                'YYYY-MM-DD'
            )
        END AS ENROLLMENT_DT,

        -- Convert last flight dates
        CASE
            WHEN COUNTRY = 'USA'
                 AND LENGTH(TRIM(LAST_FLIGHT_DATE)) = 7
            THEN TRY_TO_DATE(
                '0' || TRIM(LAST_FLIGHT_DATE),
                'MMDDYYYY'
            )

            WHEN COUNTRY = 'USA'
                 AND LENGTH(TRIM(LAST_FLIGHT_DATE)) = 8
            THEN TRY_TO_DATE(
                TRIM(LAST_FLIGHT_DATE),
                'MMDDYYYY'
            )

            ELSE TRY_TO_DATE(
                LEFT(LAST_FLIGHT_DATE, 10),
                'YYYY-MM-DD'
            )
        END AS FLIGHT_DT,

        -- Convert date of birth
        TRY_TO_DATE(
            LEFT(DOB, 10),
            'YYYY-MM-DD'
        ) AS DOB_DT

    FROM SKYPOINTS_DB.RAW.MEMBER_PROFILE
),

transformed AS (
    SELECT
        *,

        -- Calculate completed years of age
        CASE
            WHEN DOB_DT IS NULL THEN NULL
            ELSE DATEDIFF(YEAR, DOB_DT, CURRENT_DATE())
                 - IFF(
                     DATEADD(
                         YEAR,
                         DATEDIFF(YEAR, DOB_DT, CURRENT_DATE()),
                         DOB_DT
                     ) > CURRENT_DATE(),
                     1, 0
                 )
        END AS CALCULATED_AGE,

        -- Flag members whose last flight was over 90 days ago
        CASE
            WHEN FLIGHT_DT IS NULL THEN NULL
            WHEN FLIGHT_DT < DATEADD(
                DAY, -90, CURRENT_DATE()
            ) THEN TRUE
            ELSE FALSE
        END AS IS_STALE

    FROM standardized
)

-- Load transformed records into staging
SELECT
    MEMBER_NAME,
    MEMBER_ID,
    ENROLLMENT_DT,
    FLIGHT_DT,
    TIER_CODE,
    AGENT_NAME,
    STATE,
    COUNTRY,
    POST_CODE,
    DOB_DT,
    IS_ACTIVE,
    CALCULATED_AGE,
    IS_STALE,
    SOURCE_FILE,
    LOAD_TIMESTAMP
FROM transformed;
