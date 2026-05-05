"
-- Bridge-level decomposition: ALL Toucan-bridged TCO2 tokens
-- Run at: https://dune.com/queries/new?category=decoded_projects&namespace=toucan_protocol

WITH all_bridged AS (
    SELECT
        evt_block_number AS block_number,
        evt_block_time AS created_time,
        tokenAddress AS tco2_address
    FROM toucan_protocol_polygon.ToucanCarbonOffsetsFactory_evt_TokenCreated
    WHERE evt_block_time <= '2023-01-01'  -- same window as BCT analysis
),

bct_deposited AS (
    SELECT DISTINCT "erc20" AS tco2_address
    FROM toucan_protocol_polygon.Pool_evt_Deposited
    WHERE contract_address = 0x2F800Db0fdb5223b3C3f354886d907A671414A7F
),

nct_deposited AS (
    SELECT DISTINCT "erc20" AS tco2_address
    FROM toucan_protocol_polygon.Pool_evt_Deposited
    WHERE contract_address = 0xD838290e877E0188a4A44700463419ED96c16107
),

classified AS (
    SELECT
        a.tco2_address,
        a.created_time,
        t.name AS tco2_name,
        t.symbol,
        CASE
            WHEN b.tco2_address IS NOT NULL THEN 'BCT'
            WHEN n.tco2_address IS NOT NULL THEN 'NCT_only'
            ELSE 'never_deposited'
        END AS pool_status
    FROM all_bridged a
    LEFT JOIN bct_deposited b ON b.tco2_address = a.tco2_address
    LEFT JOIN nct_deposited n ON n.tco2_address = a.tco2_address
    LEFT JOIN tokens.erc20 t ON t.contract_address = a.tco2_address
        AND t.blockchain = 'polygon'
)

SELECT
    pool_status,
    COUNT(*) AS n_tokens,
    COUNT(DISTINCT tco2_address) AS n_unique
FROM classified
GROUP BY pool_status
ORDER BY n_tokens DESC;

-- ============================================================
-- QUERY 2: Full token names + VCS project IDs for classification
-- Run this to get the data needed for methodology classification
-- ============================================================
/*
SELECT
    tco2_address,
    tco2_name,
    pool_status,
    -- Parse VCS project ID from name "TCO2-VCS-1234-2015"
    CASE
        WHEN tco2_name LIKE 'TCO2-VCS-%' THEN split_part(tco2_name, '-', 3)
        ELSE NULL
    END AS vcs_project_id,
    CASE
        WHEN tco2_name LIKE 'TCO2-VCS-%' THEN split_part(tco2_name, '-', 4)
        ELSE NULL
    END AS vintage
FROM classified
ORDER BY created_time;
*/

-- ============================================================
-- QUERY 3: Quick composition summary by pool status
-- Groups by whether renewable keyword appears in token name
-- (Approximate — full classification needs Verra registry cross-ref)
-- ============================================================
/*
SELECT
    pool_status,
    COUNT(*) AS n_tokens,
    COUNT(DISTINCT tco2_address) AS n_unique,
    -- Rough renewable detection from common project patterns
    SUM(CASE
        WHEN tco2_name LIKE '%Wind%' OR tco2_name LIKE '%Solar%'
             OR tco2_name LIKE '%Hydro%' OR tco2_name LIKE '%Renewable%'
        THEN 1 ELSE 0
    END) AS likely_renewable_count
FROM classified
WHERE tco2_name IS NOT NULL
GROUP BY pool_status;
*/
