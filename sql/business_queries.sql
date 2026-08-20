-- ============================================================
-- MICRO-LENDING PLATFORM
-- BUSINESS ANALYTICS QUERIES
-- MySQL 8+
-- ============================================================

USE micro_lending;


-- ============================================================
-- 1. RISK OVERVIEW: DEFAULT RATE BY LOAN GRADE
-- ============================================================

SELECT
    grade,
    COUNT(*) AS loan_count,
    ROUND(AVG(default_flag) * 100, 2) AS default_rate_pct
FROM loans
GROUP BY grade
ORDER BY default_rate_pct DESC;


-- ============================================================
-- 2. HIGH-RISK BORROWERS BY ANNUAL INCOME AND DTI
-- ============================================================

SELECT
    c.member_id,
    c.annual_inc,
    l.loan_amnt,
    l.dti,
    l.grade,
    l.loan_status,

    CASE
        WHEN l.loan_status IN (
            'Charged Off',
            'Default',
            'Late (31-120 days)',
            'Late (16-30 days)'
        )
        THEN 'High Risk'

        WHEN l.loan_status IN (
            'Current',
            'In Grace Period'
        )
        THEN 'Monitoring'

        ELSE 'Low Risk'
    END AS risk_band

FROM loans l

JOIN customers c
    ON c.customer_id = l.customer_id

WHERE l.dti > 30
   OR c.annual_inc < 50000

ORDER BY
    l.dti DESC,
    c.annual_inc ASC

LIMIT 1000;


-- ============================================================
-- 3. LOAN APPROVAL READINESS BY STATE
-- ============================================================

SELECT
    c.addr_state,

    COUNT(*) AS loans,

    ROUND(
        AVG(
            CASE
                WHEN l.loan_status IN (
                    'Fully Paid',
                    'Current',
                    'In Grace Period'
                )
                THEN 1
                ELSE 0
            END
        ) * 100,
        2
    ) AS healthy_pct,

    ROUND(
        AVG(
            CASE
                WHEN l.loan_status IN (
                    'Charged Off',
                    'Default',
                    'Late (31-120 days)',
                    'Late (16-30 days)'
                )
                THEN 1
                ELSE 0
            END
        ) * 100,
        2
    ) AS default_pct

FROM loans l

JOIN customers c
    ON c.customer_id = l.customer_id

GROUP BY c.addr_state

ORDER BY default_pct DESC;


-- ============================================================
-- 4. CUSTOMER-LEVEL DEBT BURDEN SUMMARY
--
-- IMPORTANT:
-- Current dataset was verified:
--
-- COUNT(*) = 2,260,668
-- COUNT(DISTINCT customer_id) = 2,260,668
--
-- Therefore current dataset has one loan per customer.
-- The heavy GROUP BY/SUM/COUNT version was timing out.
-- This optimized version is used for the current dataset.
-- ============================================================

SELECT
    c.member_id,
    c.annual_inc,
    c.revol_util,
    c.delinq_2yrs,
    c.inq_last_6mths,

    l.loan_amnt AS total_requested_amount,

    1 AS total_loans

FROM customers c

JOIN loans l
    ON l.customer_id = c.customer_id

ORDER BY l.loan_amnt DESC

LIMIT 1000;


-- ============================================================
-- 5. CANDIDATE HIGH-RISK LOANS FOR MANUAL REVIEW
-- ============================================================

SELECT
    l.loan_id,
    l.member_id,
    l.loan_amnt,
    l.dti,
    l.grade,
    l.sub_grade,
    l.int_rate,
    l.loan_status,

    c.annual_inc,
    c.fico_range_low,
    c.delinq_2yrs,
    c.revol_util

FROM loans l

JOIN customers c
    ON c.customer_id = l.customer_id

WHERE l.dti > 35
   OR c.delinq_2yrs >= 2
   OR c.revol_util > 0.75

ORDER BY l.dti DESC

LIMIT 1000;


-- ============================================================
-- 6. DEFAULT RISK BY LOAN PURPOSE
-- ============================================================

SELECT
    purpose,
    COUNT(*) AS total_loans,
    ROUND(AVG(default_flag) * 100, 2) AS default_rate_pct

FROM loans

GROUP BY purpose

ORDER BY
    default_rate_pct DESC,
    total_loans DESC;


-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Verify database row counts

SELECT
    (SELECT COUNT(*) FROM customers) AS total_customers,
    (SELECT COUNT(*) FROM loans) AS total_loans;


-- Verify one-loan-per-customer assumption

SELECT
    COUNT(*) AS total_loans,
    COUNT(DISTINCT customer_id) AS unique_customers

FROM loans;


-- Sample customers

SELECT *
FROM customers
LIMIT 5;


-- Sample loans

SELECT *
FROM loans
LIMIT 5;