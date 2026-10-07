-- ============================================================
-- Job Market Analytics Portfolio Project
-- 06_analytics_views.sql
--
-- Purpose:
-- Creates reusable analytical views for downstream SQL
-- analysis, reporting, and dashboard development.
-- ============================================================

USE job_market_analytics;


-- ------------------------------------------------------------
-- 1. APPLICATION DETAILS VIEW
-- Combines application and job information into one
-- analysis-ready dataset.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW vw_application_details AS

SELECT
    a.application_id,
    a.job_id,
    j.company_name,
    j.job_title,
    j.job_title_clean,
    j.role_category,
    j.career_level,
    a.application_date,
    a.status,
    a.response_status,
    a.first_response_date,
    a.email_count,

    CASE
        WHEN a.status = 'Rejected'
         AND a.application_date IS NOT NULL
         AND a.first_response_date IS NOT NULL
        THEN DATEDIFF(
            a.first_response_date,
            a.application_date
        )
        ELSE NULL
    END AS days_to_rejection

FROM application_analysis a

INNER JOIN jobs j
    ON a.job_id = j.job_id;


-- ------------------------------------------------------------
-- 2. MONTHLY APPLICATIONS VIEW
-- One row per application month.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW vw_monthly_applications AS

SELECT
    DATE_FORMAT(application_date, '%Y-%m') AS application_month,
    COUNT(*) AS applications

FROM application_analysis

WHERE application_date IS NOT NULL

GROUP BY DATE_FORMAT(application_date, '%Y-%m');


-- ------------------------------------------------------------
-- 3. ROLE PERFORMANCE VIEW
-- Summarizes application volume and observed response rate
-- for each role category.
--
-- Response rate should not be interpreted as interview or
-- offer success because observed responses currently
-- correspond to rejection outcomes in this dataset.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW vw_role_performance AS

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

GROUP BY j.role_category;