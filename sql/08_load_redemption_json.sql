
INSERT INTO SKYPOINTS_DB.RAW.REDEMPTION_JSON (
    RAW_DATA,
    SOURCE_FILE
)
SELECT
    PARSE_JSON('{
        "member_id": "223457",
        "feed_date": "20240115",
        "redemptions": [
            {
                "txn_id": "RX10091",
                "txn_date": "20240110",
                "partner": "AeroLink",
                "miles_redeemed": 12000,
                "status": "COMPLETED"
            },
            {
                "txn_id": "RX10092",
                "txn_date": "20240113",
                "partner": "SkyPoints",
                "miles_redeemed": 5000,
                "status": "PENDING"
            }
        ]
    }'),
    'partner_redemptions.json'
WHERE NOT EXISTS (
    SELECT 1
    FROM SKYPOINTS_DB.RAW.REDEMPTION_JSON
    WHERE SOURCE_FILE = 'partner_redemptions.json'
);


SELECT
    SOURCE_FILE,
    RAW_DATA:member_id::VARCHAR AS MEMBER_ID,
    RAW_DATA:feed_date::VARCHAR AS FEED_DATE,
    ARRAY_SIZE(RAW_DATA:redemptions) AS REDEMPTION_COUNT
FROM SKYPOINTS_DB.RAW.REDEMPTION_JSON
WHERE SOURCE_FILE = 'partner_redemptions.json';
