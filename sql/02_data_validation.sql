-- ============================================================
-- Job Market Analytics Portfolio Project
-- 02_data_validation.sql
--
-- Purpose:
-- Validates row counts, IDs, missing values, relationships,
-- response outcomes, and analytical views before analysis.
-- ============================================================

USE job_market_analytics;


-- ------------------------------------------------------------
-- 1. APPLICATION DATASET VALIDATION
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_applications,
    COUNT(DISTINCT application_id) AS unique_application_ids,
    COUNT(DISTINCT job_id) AS unique_job_ids,
    SUM(application_date IS NULL) AS missing_application_dates,
    SUM(job_title IS NULL) AS missing_job_titles,
    SUM(job_reference_id IS NULL) AS missing_reference_ids,
    SUM(status = 'Rejected') AS rejected_applications,
    SUM(response_status = 'Responded') AS responded_applications
FROM application_analysis;


-- ------------------------------------------------------------
-- 2. JOB DATASET VALIDATION
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_jobs,
    COUNT(DISTINCT job_id) AS unique_job_ids,
    SUM(job_title IS NULL) AS missing_job_titles,
    SUM(job_title_clean IS NULL) AS missing_clean_titles,
    SUM(job_reference_id IS NULL) AS missing_reference_ids
FROM jobs;


-- ------------------------------------------------------------
-- 3. REFERENTIAL INTEGRITY
-- Every application should match a job.
-- Expected unmatched applications: 0
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS unmatched_applications
FROM application_analysis a
LEFT JOIN jobs j
    ON a.job_id = j.job_id
WHERE j.job_id IS NULL;


-- ------------------------------------------------------------
-- 4. MEASURABLE REJECTION TIMELINES
-- Rejections with both application and response dates.
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS measurable_rejections
FROM application_analysis
WHERE status = 'Rejected'
  AND application_date IS NOT NULL
  AND first_response_date IS NOT NULL;


-- ------------------------------------------------------------
-- 5. FINAL VALIDATION
--
-- Expected:
-- Applications:                459
-- Unique jobs:                 455
-- Observed rejections:          53
-- Observed responses:           53
-- Measurable rejection cases:   12
-- Dated applications:          418
-- ------------------------------------------------------------

SELECT
    CASE
        WHEN
            (SELECT COUNT(*)
             FROM application_analysis) = 459

        AND (SELECT COUNT(DISTINCT application_id)
             FROM application_analysis) = 459

        AND (SELECT COUNT(*)
             FROM jobs) = 455

        AND (SELECT COUNT(DISTINCT job_id)
             FROM jobs) = 455

        AND (SELECT SUM(status = 'Rejected')
             FROM application_analysis) = 53

        AND (SELECT SUM(response_status = 'Responded')
             FROM application_analysis) = 53

        AND (SELECT COUNT(*)
             FROM application_analysis
             WHERE status = 'Rejected'
               AND application_date IS NOT NULL
               AND first_response_date IS NOT NULL) = 12

        AND (SELECT COUNT(*)
             FROM application_analysis
             WHERE application_date IS NOT NULL) = 418

        THEN 'PASS'
        ELSE 'CHECK'
    END AS final_sql_validation;