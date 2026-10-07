-- ============================================================
-- Job Market Analytics Portfolio Project
-- 01_setup.sql
--
-- Purpose:
-- Creates the MySQL database schema used for the analysis.
-- The jobs table stores one row per unique job, while
-- application_analysis stores one row per application.
-- ============================================================


-- ------------------------------------------------------------
-- 1. DATABASE
-- ------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS job_market_analytics;

USE job_market_analytics;


-- ------------------------------------------------------------
-- 2. JOBS TABLE
-- Grain: One row per unique job
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(20) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(500),
    job_title_clean VARCHAR(500),
    role_category VARCHAR(100) NOT NULL,
    career_level VARCHAR(100) NOT NULL,
    job_reference_id VARCHAR(255)
);


-- ------------------------------------------------------------
-- 3. APPLICATION ANALYSIS TABLE
-- Grain: One row per application
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS application_analysis (
    application_id VARCHAR(20) PRIMARY KEY,
    job_id VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    job_title VARCHAR(500),
    job_title_clean VARCHAR(500),
    role_category VARCHAR(100),
    career_level VARCHAR(100),
    job_reference_id VARCHAR(255),
    application_date DATE,
    status VARCHAR(50),
    response_status VARCHAR(50),
    first_response_date DATE,
    email_count INT,
    email_ids TEXT
);


-- ------------------------------------------------------------
-- 4. RELATIONSHIP
-- application_analysis.job_id -> jobs.job_id
-- ------------------------------------------------------------

ALTER TABLE application_analysis
ADD CONSTRAINT fk_application_job
FOREIGN KEY (job_id)
REFERENCES jobs(job_id);