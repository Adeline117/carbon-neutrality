-- NFTX Cross-Domain Validation: Quantitative evidence of the transparency trap in NFT markets
-- Run at: https://dune.com/queries/new
-- Purpose: Show that NFTX vaults exhibit the same adverse selection pattern as BCT
-- Expected: 3 queries, run separately. Save results to data/nftx_validation_results.json

-- ============================================================================
-- Query 1: Top NFTX vaults by mint/redeem volume (overview)
-- ============================================================================
SELECT
    m.contract_address AS vault_address,
    t.name AS vault_name,
    t.symbol,
    COUNT(DISTINCT m.evt_tx_hash) AS total_mints,
    r.total_redeems,
    r.total_redeems - COUNT(DISTINCT m.evt_tx_hash) AS net_outflow,
    CASE
        WHEN COUNT(DISTINCT m.evt_tx_hash) > 0
        THEN CAST(r.total_redeems AS double) / COUNT(DISTINCT m.evt_tx_hash)
        ELSE NULL
    END AS redeem_mint_ratio
FROM nftx_v2_ethereum.NFTXVaultUpgradeable_evt_Minted m
LEFT JOIN (
    SELECT contract_address, COUNT(DISTINCT evt_tx_hash) AS total_redeems
    FROM nftx_v2_ethereum.NFTXVaultUpgradeable_evt_Redeemed
    GROUP BY 1
) r ON m.contract_address = r.contract_address
LEFT JOIN tokens.erc20 t
    ON t.contract_address = m.contract_address
    AND t.blockchain = 'ethereum'
GROUP BY 1, 2, 3, r.total_redeems
HAVING COUNT(DISTINCT m.evt_tx_hash) >= 50  -- Only vaults with meaningful activity
ORDER BY total_mints DESC
LIMIT 20

-- ============================================================================
-- Query 2: Per-vault mint vs redeem counts with net flow direction
-- Focus on the top 4 vaults (CryptoPunks, BAYC, Sandbox, Milady)
-- Shows whether redeems exceed mints (net outflow = selective exit)
-- ============================================================================
WITH vault_events AS (
    SELECT
        contract_address,
        'mint' AS event_type,
        evt_block_number,
        evt_block_time,
        evt_tx_hash
    FROM nftx_v2_ethereum.NFTXVaultUpgradeable_evt_Minted
    UNION ALL
    SELECT
        contract_address,
        'redeem' AS event_type,
        evt_block_number,
        evt_block_time,
        evt_tx_hash
    FROM nftx_v2_ethereum.NFTXVaultUpgradeable_evt_Redeemed
),
vault_summary AS (
    SELECT
        v.contract_address,
        t.name AS vault_name,
        COUNT(CASE WHEN v.event_type = 'mint' THEN 1 END) AS mints,
        COUNT(CASE WHEN v.event_type = 'redeem' THEN 1 END) AS redeems,
        COUNT(*) AS total_events,
        MIN(v.evt_block_time) AS first_event,
        MAX(v.evt_block_time) AS last_event
    FROM vault_events v
    LEFT JOIN tokens.erc20 t
        ON t.contract_address = v.contract_address
        AND t.blockchain = 'ethereum'
    GROUP BY 1, 2
    HAVING COUNT(*) >= 100  -- Meaningful activity threshold
)
SELECT
    vault_name,
    contract_address,
    mints,
    redeems,
    total_events,
    redeems - mints AS net_outflow,
    ROUND(CAST(redeems AS double) / NULLIF(mints, 0), 3) AS redeem_mint_ratio,
    CASE WHEN redeems > mints THEN 'NET_EXIT' ELSE 'NET_ENTRY' END AS flow_direction,
    first_event,
    last_event
FROM vault_summary
ORDER BY total_events DESC

-- ============================================================================
-- Query 3: Temporal pattern — monthly mint vs redeem for top vaults
-- Shows whether exit-acceleration pattern exists (redeems increase relative
-- to mints over time, analogous to BCT's temporal quality ordering)
-- ============================================================================
WITH monthly AS (
    SELECT
        contract_address,
        DATE_TRUNC('month', evt_block_time) AS month,
        'mint' AS event_type,
        COUNT(*) AS event_count
    FROM nftx_v2_ethereum.NFTXVaultUpgradeable_evt_Minted
    GROUP BY 1, 2, 3
    UNION ALL
    SELECT
        contract_address,
        DATE_TRUNC('month', evt_block_time) AS month,
        'redeem' AS event_type,
        COUNT(*) AS event_count
    FROM nftx_v2_ethereum.NFTXVaultUpgradeable_evt_Redeemed
    GROUP BY 1, 2, 3
)
SELECT
    t.name AS vault_name,
    m.month,
    SUM(CASE WHEN m.event_type = 'mint' THEN m.event_count ELSE 0 END) AS monthly_mints,
    SUM(CASE WHEN m.event_type = 'redeem' THEN m.event_count ELSE 0 END) AS monthly_redeems,
    SUM(CASE WHEN m.event_type = 'redeem' THEN m.event_count ELSE 0 END)
      - SUM(CASE WHEN m.event_type = 'mint' THEN m.event_count ELSE 0 END) AS monthly_net_outflow
FROM monthly m
LEFT JOIN tokens.erc20 t
    ON t.contract_address = m.contract_address
    AND t.blockchain = 'ethereum'
-- Filter to top vaults by total volume
WHERE m.contract_address IN (
    SELECT contract_address
    FROM nftx_v2_ethereum.NFTXVaultUpgradeable_evt_Minted
    GROUP BY 1
    HAVING COUNT(*) >= 200
)
GROUP BY 1, 2
ORDER BY vault_name, month
