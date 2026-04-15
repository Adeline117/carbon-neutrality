# BCT Depositor Data: Dune Analytics Instructions

## Step 1: Run the query

Go to: https://dune.com/queries/new

Paste the SQL below and click "Run":

```sql
WITH bct_deposits AS (
    SELECT
        evt_block_number AS block_number,
        evt_block_time AS block_time,
        evt_tx_hash AS tx_hash,
        sender AS depositor,
        erc20 AS tco2_address,
        CAST(amount AS DOUBLE) / 1e18 AS amount_tonnes
    FROM toucan_protocol_polygon.Pool_evt_Deposited
    WHERE contract_address = 0x2F800Db0fdb5223b3C3f354886d907A671414A7F
      AND evt_block_time >= TIMESTAMP '2021-10-01'
      AND evt_block_time <= TIMESTAMP '2023-06-30'
),

tco2_metadata AS (
    SELECT DISTINCT
        d.tco2_address,
        t.name AS tco2_name,
        t.symbol AS tco2_symbol
    FROM bct_deposits d
    LEFT JOIN tokens_polygon.erc20 t ON t.contract_address = d.tco2_address
)

SELECT
    d.block_number,
    d.block_time,
    d.tx_hash,
    d.depositor,
    d.tco2_address,
    d.amount_tonnes,
    m.tco2_name,
    m.tco2_symbol
FROM bct_deposits d
LEFT JOIN tco2_metadata m ON d.tco2_address = m.tco2_address
ORDER BY d.block_number
```

## Step 2: Export CSV

1. Wait for query to complete (~30 seconds)
2. Click "Download CSV" button (top-right of results table)
3. Save as `bct_deposits.csv` in this directory:
   `data/depositor-analysis/bct_deposits.csv`

## Step 3: Run the depositor portfolio query

Run a second query for depositor TCO2 balances:

```sql
WITH bct_depositors AS (
    SELECT DISTINCT sender AS depositor
    FROM toucan_protocol_polygon.Pool_evt_Deposited
    WHERE contract_address = 0x2F800Db0fdb5223b3C3f354886d907A671414A7F
      AND evt_block_time >= TIMESTAMP '2021-10-01'
      AND evt_block_time <= TIMESTAMP '2023-06-30'
),

-- All TCO2 transfers involving BCT depositors
tco2_transfers AS (
    SELECT
        t."from" AS from_addr,
        t."to" AS to_addr,
        t.contract_address AS tco2_address,
        CAST(t.value AS DOUBLE) / 1e18 AS amount,
        t.evt_block_time AS block_time
    FROM erc20_polygon.evt_Transfer t
    INNER JOIN bct_depositors d ON (t."from" = d.depositor OR t."to" = d.depositor)
    WHERE t.contract_address IN (
        SELECT DISTINCT erc20
        FROM toucan_protocol_polygon.Pool_evt_Deposited
    )
    AND t.evt_block_time <= TIMESTAMP '2023-06-30'
)

SELECT
    to_addr AS holder,
    tco2_address,
    SUM(CASE WHEN to_addr = holder THEN amount ELSE 0 END)
      - SUM(CASE WHEN from_addr = holder THEN amount ELSE 0 END) AS net_balance,
    COUNT(*) AS n_transfers
FROM tco2_transfers
GROUP BY 1, 2
HAVING net_balance > 0
ORDER BY holder, net_balance DESC
```

Save as `depositor_portfolios.csv`.

## Step 4: Run analysis

```bash
cd data/depositor-analysis
python3 analyze_adverse_selection.py \
  --deposits bct_deposits.csv \
  --portfolios depositor_portfolios.csv
```

This will output:
- `results.md` — full analysis with statistics
- `adverse_selection_results.json` — machine-readable results
- Key numbers for the Nat Comms paper (Delta, Cohen's d, selection rate, p-value)

## Expected timeline

- Query 1: ~30 seconds
- Query 2: ~2-5 minutes (larger dataset)
- Analysis: ~10 seconds
- Total: ~10 minutes
