-- ============================================================
-- Job Market Analytics Portfolio Project
-- 04_job_market_analysis.sql
--
-- Purpose:
-- Analyzes the composition of the job market represented in
-- the dataset and compares observed responses across job
-- categories and career levels.
-- ============================================================

USE job_market_analytics;


-- ------------------------------------------------------------
-- 1. ROLE CATEGORY DISTRIBUTION
-- Grain: unique jobs
-- ------------------------------------------------------------

SELECT
    role_category,
    COUNT(*) AS job_count,

    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS pct_of_jobs

FROM jobs

GROUP BY role_category

ORDER BY job_count DESC;


-- ------------------------------------------------------------
-- 2. CAREER LEVEL DISTRIBUTION
-- Grain: unique jobs
-- ------------------------------------------------------------

SELECT
    career_level,
    COUNT(*) AS job_count,

    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS pct_of_jobs

FROM jobs

GROUP BY career_level

ORDER BY job_count DESC;


-- ------------------------------------------------------------
-- 3. DATA-FOCUSED ROLES BY CAREER LEVEL
-- ------------------------------------------------------------

SELECT
    role_category,
    career_level,
    COUNT(*) AS job_count

FROM jobs

WHERE role_category IN (
    'Data Engineering',
    'Data / Analytics Analyst',
    'Data Science'
)

GROUP BY
    role_category,
    career_level

ORDER BY
    role_category,
    job_count DESC;


-- ------------------------------------------------------------
-- 4. OBSERVED RESPONSE RATE BY ROLE CATEGORY
--
-- Note:
-- "Responded" currently represents an observed employer
-- response in the collected data and should not be interpreted
-- as a positive outcome.
-- ------------------------------------------------------------

SELECT
    j.role_category,
    COUNT(*) AS applications,
    SUM(a.response_status = 'Responded') AS responses,

    ROUND(
        100.0 * SUM(a.response_status = 'Responded')
        / COUNT(*),
        2
    ) AS response_rate_pct

FROM application_analysis a

INNER JOIN jobs j
    ON a.job_id = j.job_id

GROUP BY j.role_category

ORDER BY response_rate_pct DESC;


-- ------------------------------------------------------------
-- 5. OBSERVED RESPONSE RATE BY CAREER LEVEL
-- ------------------------------------------------------------

SELECT
    j.career_level,
    COUNT(*) AS applications,
    SUM(a.response_status = 'Responded') AS responses,

    ROUND(
        100.0 * SUM(a.response_status = 'Responded')
        / COUNT(*),
        2
    ) AS response_rate_pct

FROM application_analysis a

INNER JOIN jobs j
    ON a.job_id = j.job_id

GROUP BY j.career_level

ORDER BY response_rate_pct DESC;


-- ------------------------------------------------------------
-- 6. ROLE + CAREER LEVEL RESPONSE ANALYSIS
--
-- Minimum of five applications is required to reduce the
-- influence of very small groups.
-- ------------------------------------------------------------

SELECT
    j.role_category,
    j.career_level,
    COUNT(*) AS applications,
    SUM(a.response_status = 'Responded') AS responses,

    ROUND(
        100.0 * SUM(a.response_status = 'Responded')
        / COUNT(*),
        2
    ) AS response_rate_pct

FROM application_analysis a

INNER JOIN jobs j
    ON a.job_id = j.job_id

GROUP BY
    j.role_category,
    j.career_level

HAVING COUNT(*) >= 5

ORDER BY
    response_rate_pct DESC,
    applications DESC;