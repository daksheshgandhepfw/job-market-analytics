-- ============================================================
-- Job Market Analytics Portfolio Project
-- 03_application_analysis.sql
--
-- Purpose:
-- Analyzes application outcomes, application activity over
-- time, and rejection-response timing.
-- ============================================================

USE job_market_analytics;


-- ------------------------------------------------------------
-- 1. APPLICATION FUNNEL
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_applications,
    SUM(response_status = 'Responded') AS responded_applications,
    SUM(response_status <> 'Responded' OR response_status IS NULL)
        AS no_observed_response,
    SUM(status = 'Rejected') AS rejected_applications,

    ROUND(
        100.0 * SUM(response_status = 'Responded') / COUNT(*),
        2
    ) AS response_rate_pct

FROM application_analysis;


-- ------------------------------------------------------------
-- 2. MONTHLY APPLICATION VOLUME
-- Only applications with a known application date are included.
-- ------------------------------------------------------------

SELECT
    DATE_FORMAT(application_date, '%Y-%m') AS application_month,
    COUNT(*) AS applications

FROM application_analysis

WHERE application_date IS NOT NULL

GROUP BY DATE_FORMAT(application_date, '%Y-%m')

ORDER BY application_month;


-- ------------------------------------------------------------
-- 3. MONTHLY APPLICATION SHARE
-- Shows each month's share of all dated applications.
-- ------------------------------------------------------------

SELECT
    DATE_FORMAT(application_date, '%Y-%m') AS application_month,
    COUNT(*) AS applications,

    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS pct_of_dated_applications

FROM application_analysis

WHERE application_date IS NOT NULL

GROUP BY DATE_FORMAT(application_date, '%Y-%m')

ORDER BY applications DESC;


-- ------------------------------------------------------------
-- 4. REJECTION TIMING SUMMARY
-- Based only on rejected applications where both dates exist.
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS measurable_rejections,

    ROUND(
        AVG(DATEDIFF(first_response_date, application_date)),
        2
    ) AS avg_days_to_rejection,

    MIN(
        DATEDIFF(first_response_date, application_date)
    ) AS fastest_rejection_days,

    MAX(
        DATEDIFF(first_response_date, application_date)
    ) AS slowest_rejection_days

FROM application_analysis

WHERE status = 'Rejected'
  AND application_date IS NOT NULL
  AND first_response_date IS NOT NULL;


-- ------------------------------------------------------------
-- 5. REJECTION-TIME DISTRIBUTION
-- ------------------------------------------------------------

WITH rejection_times AS (
    SELECT
        DATEDIFF(
            first_response_date,
            application_date
        ) AS days_to_rejection

    FROM application_analysis

    WHERE status = 'Rejected'
      AND application_date IS NOT NULL
      AND first_response_date IS NOT NULL
),

bucketed AS (
    SELECT
        CASE
            WHEN days_to_rejection <= 3 THEN '0-3 days'
            WHEN days_to_rejection <= 7 THEN '4-7 days'
            WHEN days_to_rejection <= 14 THEN '8-14 days'
            ELSE '15+ days'
        END AS rejection_time_bucket

    FROM rejection_times
)

SELECT
    rejection_time_bucket,
    COUNT(*) AS rejections,

    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS pct_of_measurable_rejections

FROM bucketed

GROUP BY rejection_time_bucket

ORDER BY
    CASE rejection_time_bucket
        WHEN '0-3 days' THEN 1
        WHEN '4-7 days' THEN 2
        WHEN '8-14 days' THEN 3
        WHEN '15+ days' THEN 4
    END;
    