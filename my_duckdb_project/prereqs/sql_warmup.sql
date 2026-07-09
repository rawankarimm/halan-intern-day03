-- ============================================================================
-- Load the first 10,000 rows of the local PaySim CSV into DuckDB
-- ============================================================================

-- Create a table and populate it with the first 10,000 rows of your local file
CREATE OR REPLACE TABLE paysim AS 
SELECT * FROM read_csv_auto('paysim_sample.csv')
LIMIT 10000; --first 10,000 rows

-- ============================================================================
-- QUERIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Question 1: Total transaction volume (sum of amount) per transaction type (What are the most common ways money moves around in this system,
-- and where is the bulk of the cash flowing?)
-- Analytical Value: This establishes our baseline. Before we can spot "weird" behavior,
-- we need to know what "normal" looks like. For instance, if CASH_OUT or TRANSFER make up 90%
-- of the total volume, we know where to focus our engineering optimization or fraud monitoring efforts.
-- ----------------------------------------------------------------------------
SELECT 
    type,
    SUM(amount) AS total_volume,
FROM paysim
GROUP BY type
ORDER BY total_volume DESC;


-- ----------------------------------------------------------------------------
-- Question 2: 90th percentile transaction amount per type (What is the upper boundary for a "normal" transaction
-- size for each type?)
-- Analytical Value: Identifying the 90th percentile allows us to understand the 
-- "heavy-tail" behavior of transactions without being distorted by extreme 
-- outliers. It defines what constitutes a "normally high" transaction for each type.
-- ----------------------------------------------------------------------------
SELECT 
    type,
    QUANTILE_CONT(amount, 0.90) AS t90th_percentile_amount
FROM paysim
GROUP BY type
ORDER BY t90th_percentile_amount DESC;


-- ----------------------------------------------------------------------------
-- Question 3: Sender accounts appearing in > 3 transactions (Which individual accounts are highly active
-- or moving money frequently within this small sample?)
-- Analytical Value: High-frequency senders within a short window can be indicative 
-- of automated scripts, structuring (breaking large transfers into small ones to 
-- avoid detection), or highly active "mule" accounts.
-- ----------------------------------------------------------------------------
SELECT 
    nameOrig AS sender_account,
    COUNT(*) AS transaction_count
FROM paysim
GROUP BY nameOrig
HAVING COUNT(*) > 3
ORDER BY transaction_count DESC;

----------------
--no sender accounts appear in more than 3 transactions in the first 10,000 rows of the sample data


-- ----------------------------------------------------------------------------
-- Question 4: Running cumulative total of TRANSFER transactions per step (How does the velocity or momentum of
-- money transfers build up over time (tracked by steps)?)
-- Analytical Value: Steps represent units of time (hours). A running cumulative 
-- total allows analysts to spot sudden acceleration or surges in risk-heavy 
-- TRANSFER operations over time, which can signal a coordinated attack or platform-wide anomaly.
-- ----------------------------------------------------------------------------
SELECT 
    step,
    type,
    amount,
    SUM(amount) OVER (
        PARTITION BY type 
        ORDER BY step
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_transfer_total
FROM paysim
WHERE type = 'TRANSFER'
ORDER BY step;

--another way
SELECT 
    step,
    type,
    amount,
    COALESCE(
    LAG(amount) OVER (
        PARTITION BY type 
        ORDER BY step
    )  + amount,amount ) AS previous_transfer_amount,
FROM paysim
WHERE type = 'TRANSFER'
ORDER BY step;


-- ----------------------------------------------------------------------------
-- Question 5: Fraud percentage among "full drain" transactions (When an account is completely wiped out
-- to exactly zero dollars, how likely is it to be an actual instance of fraud?)
-- Analytical Value: Fraudsters frequently aim to empty a victim's account 
-- completely to maximize their illicit yield before the account is frozen. 
-- Measuring the conversion rate of this specific user behavior to an actual 
-- 'isFraud' flag tests the predictive strength of "full drain" as a heuristic rule.
-- ----------------------------------------------------------------------------
WITH full_drain AS (
    SELECT 
        isFraud
    FROM paysim
    WHERE newbalanceOrig = 0 AND oldbalanceOrg > 0
)
SELECT 
    COUNT(*) AS full_drain_transactions,
    SUM(isFraud) AS fraud_count,
    (SUM(isFraud)::DOUBLE / NULLIF(COUNT(*), 0)) * 100 AS fraud_percentage
FROM full_drain;


SELECT nameOrig as Name, COUNT(*) as transaction_count FROM paysim
GROUP BY nameOrig
HAVING COUNT(*) > 1;