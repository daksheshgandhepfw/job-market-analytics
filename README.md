# Job Application & Job Market Analytics

## Project Overview

This project analyzes my job application activity and the characteristics of the jobs I applied to using an end-to-end data analytics workflow.

The project transforms raw job-application data into structured analytical datasets, validates data quality, performs SQL and Python analysis, and produces business-style insights and visualizations.

The goal was to build a realistic portfolio project demonstrating practical **data analytics skills across data cleaning, SQL, Python, exploratory analysis, KPI development, and dashboarding**.

## Project Highlights

- Analyzed **459 job applications**
- Identified **455 unique jobs**
- Recorded **53 observed rejections**
- Built reusable Python data-processing and validation scripts
- Created analytical datasets for SQL, Python, and BI analysis
- Performed SQL analysis using reusable analytical queries and views
- Conducted exploratory data analysis with Python and Pandas
- Built a Tableau dashboard for job-market and application analysis
- Added validation checks for duplicate records, missing values, response outcomes, and date consistency
- Sanitized published datasets to remove private email and application identifiers

## Business Questions

The analysis focuses on questions such as:

- How many applications have been submitted?
- What proportion of applications received an observed response?
- How are applications distributed across job categories?
- Which career levels appear most frequently?
- Which companies and role categories dominate the application dataset?
- How quickly do observed rejections occur?
- How does application activity change over time?
- What patterns can be identified across role category, career level, and application outcomes?

## Dataset

The repository contains three sanitized analytical datasets:

### `applications.csv`

Application-level information used to analyze application activity and outcomes.

### `jobs_final.csv`

Job-level information containing cleaned job attributes such as company, title, role category, and career level.

### `application_analysis.csv`

Combined analytical dataset used for application-level analysis across job and response characteristics.

Private Gmail identifiers and internal matching identifiers are excluded from the published datasets.

## Data Pipeline

The project follows an end-to-end analytics workflow:

```text
Raw Job Application Data
        ↓
Data Extraction
        ↓
Data Cleaning & Standardization
        ↓
Job/Application Matching
        ↓
Data Quality Validation
        ↓
Final Analytical Datasets
        ↓
SQL Analysis
        ↓
Python / Pandas EDA
        ↓
Tableau Dashboard
        ↓
Business Insights
```

## Repository Structure

```text
job-market-analytics/
│
├── data/
│   ├── raw/                       # Private raw source data (not published)
│   └── processed/
│       ├── applications.csv
│       ├── jobs_final.csv
│       └── application_analysis.csv
│
├── notebooks/
│   └── 01_exploratory_analysis.ipynb
│
├── sql/
│   ├── 01_setup.sql
│   ├── 02_data_validation.sql
│   ├── 03_application_analysis.sql
│   ├── 04_job_market_analysis.sql
│   ├── 05_advanced_analysis.sql
│   └── 06_analytics_views.sql
│
├── src/                           # Python processing and validation scripts
├── dashboard/                     # Dashboard-related project assets
├── images/                        # Portfolio images and screenshots
├── .gitignore
└── README.md
```

## SQL Analysis

The SQL portion of the project includes:

- Dataset setup and schema creation
- Data-quality validation
- Application KPI analysis
- Job-market analysis
- Advanced analytical queries
- Reusable analytical views

Examples of metrics analyzed include:

- Total applications
- Observed rejection count
- Application distribution by role category
- Application distribution by career level
- Company-level application activity
- Response and outcome patterns
- Time-to-rejection metrics

## Python & Pandas Analysis

Python and Pandas were used for:

- Loading and validating analytical datasets
- Inspecting missing and duplicate values
- Exploring categorical distributions
- Analyzing application outcomes
- Calculating summary statistics
- Comparing role and career-level segments
- Creating exploratory visualizations
- Cross-checking SQL-derived KPIs

The exploratory analysis is available in:

```text
notebooks/01_exploratory_analysis.ipynb
```

## Dashboard

A Tableau dashboard was developed to present the most important job-application and job-market metrics interactively.

The dashboard includes analysis of:

- Application volume
- Application outcomes
- Role categories
- Career levels
- Job-title patterns
- Company distribution
- Application trends
- Rejection activity

The Tableau workbook itself is kept outside the public repository because its embedded extracts originated from private application data. The analytical datasets published in this repository are sanitized.

## Data Quality & Privacy

Because the source data originated from personal job-application activity, privacy and data quality were treated as part of the analytics workflow.

Validation checks include:

- Duplicate application IDs
- Missing job IDs
- Missing application dates
- Missing job titles
- Response dates occurring before application dates
- Rejection-status consistency
- Application/job matching consistency

The public repository excludes:

- Gmail message identifiers
- Authentication credentials
- Raw email data
- Private Tableau extracts
- Internal job-reference identifiers

## Tools & Technologies

**Languages & Analysis**

- Python
- Pandas
- SQL

**Visualization**

- Matplotlib
- Tableau

**Development**

- Jupyter Notebook
- Git
- GitHub

## Skills Demonstrated

This project demonstrates practical experience with:

- Data cleaning
- Data validation
- Exploratory data analysis
- SQL querying
- KPI development
- Data transformation
- Analytical dataset design
- Python automation
- Dashboard development
- Data privacy and publication workflows
- Git version control

## Key Takeaway

This project demonstrates how raw operational data can be transformed into a structured analytics workflow that supports data-quality validation, SQL analysis, exploratory analysis, KPI reporting, and business intelligence visualization.
