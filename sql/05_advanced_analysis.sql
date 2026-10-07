-- ============================================================
-- Job Market Analytics Portfolio Project
-- 05_advanced_analysis.sql
--
-- Purpose:
-- Demonstrates advanced analytical SQL using CTEs, window
-- functions, ranking, running totals, median calculations,
-- and comparative metrics.
-- ============================================================

USE job_market_analytics;


-- ------------------------------------------------------------
-- 1. MONTH-OVER-MONTH APPLICATION CHANGE
-- ------------------------------------------------------------

WITH monthly_applications AS (
    SELECT
        DATE_FORMAT(application_date, '%Y-%m') AS application_month,
        COUNT(*) AS applications

    FROM application_analysis

    WHERE application_date IS NOT NULL

    GROUP BY DATE_FORMAT(application_date, '%Y-%m')
),

monthly_comparison AS (
    SELECT
        application_month,
        applications,

        LAG(applications) OVER (
            ORDER BY application_month
        ) AS previous_month_applications

    FROM monthly_applications
)

SELECT
    application_month,
    applications,
    previous_month_applications,

    ROUND(
        100.0 * (applications - previous_month_applications)
        / NULLIF(previous_month_applications, 0),
        2
    ) AS mom_change_pct

FROM monthly_comparison

ORDER BY application_month;


-- ------------------------------------------------------------
-- 2. CUMULATIVE APPLICATIONS
-- ------------------------------------------------------------

WITH monthly_applications AS (
    SELECT
        DATE_FORMAT(application_date, '%Y-%m') AS application_month,
        COUNT(*) AS applications

    FROM application_analysis

    WHERE application_date IS NOT NULL

    GROUP BY DATE_FORMAT(application_date, '%Y-%m')
)

SELECT
    application_month,
    applications,

    SUM(applications) OVER (
        ORDER BY application_month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_applications

FROM monthly_applications

ORDER BY application_month;


-- ------------------------------------------------------------
-- 3. MEDIAN DAYS TO REJECTION
--
-- MySQL does not provide a direct MEDIAN aggregate, so the
-- middle observation(s) are identified using window functions.
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

ranked_rejections AS (
    SELECT
        days_to_rejection,

        ROW_NUMBER() OVER (
            ORDER BY days_to_rejection
        ) AS row_num,

        COUNT(*) OVER () AS total_rows

    FROM rejection_times
)

SELECT
    AVG(days_to_rejection) AS median_days_to_rejection

FROM ranked_rejections

WHERE row_num IN (
    FLOOR((total_rows + 1) / 2),
    FLOOR((total_rows + 2) / 2)
);


-- ------------------------------------------------------------
-- 4. APPLICATION SHARE VS RESPONSE SHARE
-- ------------------------------------------------------------

SELECT
    j.role_category,

    COUNT(*) AS applications,

    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (),
        2
    ) AS application_share_pct,

    SUM(a.response_status = 'Responded') AS responses,

    ROUND(
        100.0 * SUM(a.response_status = 'Responded')
        / SUM(SUM(a.response_status = 'Responded')) OVER (),
        2
    ) AS response_share_pct

FROM application_analysis a

INNER JOIN jobs j
    ON a.job_id = j.job_id

GROUP BY j.role_category

ORDER BY applications DESC;


-- ------------------------------------------------------------
-- 5. RESPONSE REPRESENTATION INDEX
--
-- Index =
--     share of observed responses
--     ---------------------------
--     share of applications
--
-- > 1 : category contributes a disproportionately large
--       share of observed responses.
--
-- < 1 : category contributes a disproportionately small
--       share of observed responses.
--
-- This is NOT a success index because observed responses
-- currently correspond to rejection outcomes in this dataset.
-- ------------------------------------------------------------

WITH role_metrics AS (
    SELECT
        j.role_category,

        COUNT(*) AS applications,

        SUM(
            a.response_status = 'Responded'
        ) AS responses,

        100.0 * COUNT(*)
            / SUM(COUNT(*)) OVER ()
            AS application_share_pct,

        100.0 * SUM(
            a.response_status = 'Responded'
        )
            / SUM(
                SUM(a.response_status = 'Responded')
            ) OVER ()
            AS response_share_pct

    FROM application_analysis a

    INNER JOIN jobs j
        ON a.job_id = j.job_id

    GROUP BY j.role_category
)

SELECT
    role_category,
    applications,
    responses,

    ROUND(
        application_share_pct,
        2
    ) AS application_share_pct,

    ROUND(
        response_share_pct,
        2
    ) AS response_share_pct,

    ROUND(
        response_share_pct
        / NULLIF(application_share_pct, 0),
        2
    ) AS response_representation_index

FROM role_metrics

ORDER BY response_representation_index DESC;