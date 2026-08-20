# Micro-Lending Platform

This GitHub repository contains the runnable application code for the capstone. Large Lending Club data files are intentionally kept out of GitHub because the raw dataset is over 1 GB and normal GitHub files have a 100 MB limit. Download the dataset locally before running ETL or retraining the model.

## What this project does

This project is an end-to-end loan risk assessment system built with Lending Club data.

A lending analyst can enter a borrower profile and a loan request. The system then:

1. estimates the probability of default
2. converts that probability into a risk score and risk band
3. checks the borrower against lending rules
4. returns `APPROVE`, `REVIEW`, or `REJECT`
5. explains the reasons behind the result

The project also includes the database, SQL analysis, ETL pipeline, machine-learning model, FastAPI service, and Streamlit form required for the capstone.

## Project flow

```text
loan.csv
  -> Python and Pandas cleaning
  -> customers.csv and loans.csv
  -> MySQL tables: customers and loans
  -> SQL business analysis
  -> feature engineering
  -> default prediction
  -> risk score
  -> eligibility checks
  -> final decision
  -> FastAPI and Streamlit
```

## Folder guide

- `lendingLoan zip/loan.csv` - original Lending Club dataset, downloaded locally and ignored by Git
- `data/processed/` - cleaned customer and loan CSV files generated locally by ETL
- `data/eda/` - EDA summaries and charts generated locally
- `data/model_evaluation/` - model comparison and evaluation results generated locally
- `src/etl_pipeline.py` - reads and cleans the raw CSV
- `src/features.py` - creates lending-risk features
- `src/train_model.py` - trains and evaluates the model
- `src/database.py` - loads processed data into MySQL or local SQLite
- `src/run_business_queries.py` - runs the six SQL reports
- `src/risk_score.py` - converts probability to score and risk band
- `src/eligibility.py` - applies lending eligibility rules
- `src/decision_engine.py` - produces the final decision
- `api/app.py` - FastAPI endpoints
- `app/streamlit_app.py` - Streamlit user interface
- `sql/schema.sql` - official MySQL schema
- `sql/business_queries.sql` - six business analysis queries
- `notebooks/` - EDA and feature-engineering notebooks
- `tests/` - automated tests

## Get the dataset locally

Download the Lending Club CSV from the dataset link in the project assignment and place it here:

```text
lendingLoan zip/loan.csv
```

This folder is intentionally ignored in GitHub because the file is too large for normal GitHub storage.

## Database: MySQL

MySQL is the official database for this project. SQLite is kept only as a local fallback for testing when MySQL is not available.

The database contains:

- `customers` - one record for each customer identifier
- `loans` - loan applications linked to customers through `customer_id`

The schema supports one customer having many loans. In the supplied CSV, the original `id` and `member_id` values are empty, so the ETL creates surrogate IDs. As a result, this particular file currently has one generated customer ID per loan.

### 1. Create the database tables

Open MySQL Workbench and run:

```sql
SOURCE D:/Documents/Fintech/MICRO-LENDING PLATFORM - End-to-End FinTech Capstone Project/sql/schema.sql;
```

Or run from a MySQL terminal:

```bash
mysql -u your_user -p < sql/schema.sql
```

### 2. Configure the Python connection

Set the connection string in your terminal. Do not place the password in source code or commit it to the project.

PowerShell example:

```powershell
$env:MICRO_LENDING_MYSQL_URL = 'mysql+pymysql://your_user:your_password@localhost:3306/micro_lending'
```

The password is not stored anywhere in this repository.

### 3. Load the processed data

The processed CSV files already exist. To load them into MySQL:

```powershell
python -c "from src.database import load_processed_tables_to_database, MYSQL_DATABASE_URL; load_processed_tables_to_database(MYSQL_DATABASE_URL)"
```

The loader checks existing MySQL row counts before inserting. It will not blindly append the same full dataset again.

## Testing MySQL in Workbench

Run these checks in MySQL Workbench:

```sql
USE micro_lending;

SELECT COUNT(*) AS customers FROM customers;
SELECT COUNT(*) AS loans FROM loans;
SELECT COUNT(DISTINCT customer_id) AS distinct_loan_customers FROM loans;

SELECT COUNT(*) AS duplicate_customers
FROM (
    SELECT customer_id
    FROM customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) AS duplicates;

SELECT COUNT(*) AS orphan_loans
FROM loans l
LEFT JOIN customers c ON c.customer_id = l.customer_id
WHERE c.customer_id IS NULL;

SHOW INDEX FROM customers;
SHOW INDEX FROM loans;
```

Expected current data checks:

- customers: `2,260,668`
- loans: `2,260,668`
- distinct loan customers: `2,260,668`
- duplicate customers: `0`
- orphan loans: `0`

Then run the six reports from [sql/business_queries.sql](sql/business_queries.sql). They are:

1. Default rate by grade
2. High-risk borrowers
3. Approval readiness by state
4. Customer debt burden
5. High-risk loans for manual review
6. Default risk by loan purpose

The detailed reports intentionally use `LIMIT 1000` so Workbench and future dashboards do not try to display millions of rows.

## Testing the Python project

From the project root:

```powershell
python -m pytest -q
python -m compileall -q src api app
```

The test suite checks ETL, ID handling, feature engineering, database fallback loading, EDA output creation, risk scoring, eligibility, decision logic, API validation, and the six-query contract.

## Testing the API

Start the API in one terminal:

```powershell
python -m uvicorn api.app:app --host 127.0.0.1 --port 8000
```

Open the API documentation in a browser:

- http://127.0.0.1:8000/docs

Or test from a second PowerShell terminal:

```powershell
$headers = @{ 'Content-Type' = 'application/json' }
$body = '{"applicant":{"annual_inc":120000,"emp_length":8,"revol_util":0.2,"delinq_2yrs":0,"inq_last_6mths":0,"fico_range_low":760},"loan":{"loan_amnt":10000,"dti":10}}'

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/' -Method Get
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/risk-score' -Method Post -Headers $headers -Body $body
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/eligibility' -Method Post -Headers $headers -Body $body
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/loan-decision' -Method Post -Headers $headers -Body $body
```

The final response should include the default probability, risk score, risk band, eligibility, decision, and reasons.

Stop the API with `Ctrl+C` in the terminal running Uvicorn.

## Testing the Streamlit form

Start Streamlit in another terminal:

```powershell
python -m streamlit run app/streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

Open:

- http://127.0.0.1:8501

Enter values such as:

- Annual income: `120000`
- Employment length: `8`
- Revolving utilization: `0.20`
- Delinquencies: `0`
- Recent inquiries: `0`
- FICO low: `760`
- Loan amount: `10000`
- DTI: `10`

Click **Evaluate Loan**. The form displays the model result, risk score, risk band, eligibility result, final decision, and reasons.

Stop Streamlit with `Ctrl+C` in its terminal.

## Rebuilding generated outputs

Run ETL only when you intentionally want to regenerate the processed CSVs:

```powershell
python -m src.etl_pipeline
```

Generate EDA files:

```powershell
python -m src.eda_analysis --sample-size 50000
```

Run the local SQLite fallback and six reports:

```powershell
python -m src.database
python -m src.run_business_queries
```

Retrain the model only when you intentionally want a new model artifact:

```powershell
python -m src.train_model
```

## Main project decisions

- Default statuses: `Charged Off`, `Default`, `Late (31-120 days)`, and `Late (16-30 days)`.
- Non-default statuses include `Fully Paid`, `Current`, and `In Grace Period`.
- Risk score is the model default probability expressed on a 0-100 scale.
- Eligibility and risk are separate: a borrower can have a low model score but still fail a business rule.
- The model uses application-time information and does not use repayment or recovery outcomes as prediction features.

## Current status

The project code is ready for the capstone demonstration. MySQL Workbench is the official database environment, the six SQL reports have been verified there, and the Python API and Streamlit decision form are ready for demonstration.

The remaining production recommendations are a dependency vulnerability scan and, if desired, replacing the supplied null-ID dataset with a source export containing real Lending Club identifiers.
