# Micro-Lending Risk Decision Platform

A full-stack, end-to-end lending risk assessment project built around historical Lending Club loan data. The platform estimates default risk, applies lending policy checks, and produces a loan decision with explainable reasons.

## Overview

This project is designed to help a lender answer four key questions:

1. Who is the borrower?
2. How risky is the borrower?
3. What is the probability of default?
4. Should the loan be approved, reviewed, or rejected?

It combines:

- ETL and data cleaning
- SQL-based portfolio analysis
- exploratory data analysis and charts
- feature engineering
- machine learning for default prediction
- eligibility screening rules
- a decision engine
- a FastAPI backend
- a Streamlit front-end

## Problem Statement

Digital lenders need a consistent and explainable decision-support system to evaluate loan applications. Manual review alone is slow and inconsistent, while pure model output without policy checks can miss important business constraints.

This project solves that by combining:

- a predictive model for default likelihood
- human-interpretable risk scoring
- business-rule validation for eligibility
- final decision outputs with clear reasons

## Dataset Used

The project uses the Lending Club loan dataset, which contains borrower and loan characteristics such as:

- annual income
- employment length
- revolving utilization
- debt-to-income ratio
- FICO range
- delinquency history
- inquiry history
- loan amount
- loan status

Official dataset source:

- Kaggle: https://www.kaggle.com/datasets/adarshsng/lending-club-loan-data-csv

The raw dataset is intended to be stored locally as:

```text
lendingLoan zip/loan.csv
```

In this workspace, the local working copy is also available under:

```text
data/processed/loan.csv
```

> The raw source file is intentionally not committed to GitHub due to its large size.

## What We Built

The project creates a complete lending-risk workflow:

- data cleaning and feature preparation
- processed customer and loan data tables
- SQL queries for business analysis
- default prediction model
- configurable risk scoring and risk band mapping
- policy-based eligibility rules
- final approval/review/rejection decision logic
- API and UI to interact with the model

## End-to-End Workflow

![Project workflow](docs/assets/decision_pipeline.png)

```text
Raw lending data
  -> ETL and data validation
  -> processed customer and loan tables
  -> SQL business analysis
  -> feature engineering
  -> default prediction model
  -> risk score and risk band
  -> eligibility rules
  -> approval / review / rejection decision
  -> API and Streamlit UI
```

## Risk Logic and Formulas

### 1. Loan-to-income ratio

The project calculates loan-to-income as:

$$
\text{Loan-to-Income} = \frac{\text{Loan Amount}}{\text{Annual Income}}
$$

This is used to check whether the borrower is taking on too much debt relative to income.

### 2. Default probability to risk score

The default probability is converted to a 0-100 score using:

$$
\text{Risk Score} = \text{round}(\text{Default Probability} \times 100)
$$

Example:

- default probability = 0.55
- risk score = round(0.55 × 100) = 55

### 3. Risk bands

The risk score is mapped into business-friendly bands:

- < 25 = Low Risk
- < 50 = Medium Risk
- < 75 = High Risk
- > = 75 = Very High Risk

### 4. Eligibility checks

Eligibility is not based on the model alone. Borrowers are also rejected if they violate practical lending rules such as:

- income below minimum threshold
- loan-to-income too high
- DTI too high
- credit utilization too high
- employment length too low
- FICO below threshold
- delinquency history too severe
- too many recent inquiries
- model probability too high


## Decision Outputs

The project distinguishes between approval, review, and rejection states based on risk score, business rules, and eligibility checks.

### Input form example

![Loan form example](docs/assets/Output%20pic1.png)

### Decision result example

![Decision result example](docs/assets/Output%20pic2.png)

## Repository Structure

```text
.
├── api/
│   └── app.py
├── app/
│   └── streamlit_app.py
├── data/
│   ├── processed/
│   │   ├── loan.csv
│   │   ├── customers.csv
│   │   └── loans.csv
│   └── eda/
├── docs/
│   ├── assets/
│   ├── business_problem.md
│   ├── dataset_dictionary.md
│   ├── er_diagram.md
│   ├── feature_catalog.md
│   ├── final_project_report.md
│   ├── project_documentation.md
│   ├── project_roadmap.md
│   ├── requirement_classification.md
│   └── system_architecture.md
├── models/
│   └── default_model.joblib
├── scripts/
│   └── generate_visual_assets.py
├── sql/
│   ├── business_queries.sql
│   └── schema.sql
├── src/
│   ├── decision_engine.py
│   ├── eda_analysis.py
│   ├── eligibility.py
│   ├── etl_pipeline.py
│   ├── features.py
│   ├── risk_score.py
│   ├── train_model.py
│   └── ...
├── tests/
├── .gitignore
├── PROJECT_GUIDE.md
├── README.md
├── requirements.txt
├── pytest.ini
└── .git/
```

## How to Run the Project

### 1. Install dependencies

```powershell
pip install -r requirements.txt
```

### 2. Start the FastAPI backend

```powershell
python -m uvicorn api.app:app --host 127.0.0.1 --port 8000
```

Open the API docs here:

- http://127.0.0.1:8000/docs

### 3. Start the Streamlit app

```powershell
python -m streamlit run app/streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

Open:

- http://127.0.0.1:8501

### 4. Run the automated tests

```powershell
python -m pytest -q
```

### 5. Regenerate ETL outputs and analytics

```powershell
python -m src.etl_pipeline
python -m src.eda_analysis --sample-size 50000
```

### 6. Retrain the model when needed

```powershell
python -m src.train_model
```

## Example Input and Output

Example applicant values:

- annual income: 120000
- employment length: 8 years
- revolving utilization: 0.20
- delinquencies: 0
- inquiries: 0
- FICO low: 760
- requested loan: 10000
- DTI: 10

This type of borrower is usually a strong credit candidate and can be approved if policy checks also pass.

## Documentation

Additional project documentation is available in:

- [docs/business_problem.md](docs/business_problem.md)
- [docs/project_documentation.md](docs/project_documentation.md)
- [PROJECT_GUIDE.md](PROJECT_GUIDE.md)

## Notes

This project is intended as a capstone-style, practical lending-risk system and is a good learning framework for:

- financial analytics
- risk modeling
- explainable AI in lending
- backend/frontend integration
- end-to-end ML application design

It is not a production credit decision system without additional compliance review, policy validation, and model governance.

## License

This project is for educational and demonstration purposes.

## Current status

The project code is ready for the capstone demonstration. MySQL Workbench is the official database environment, the six SQL reports have been verified there, and the Python API and Streamlit decision form are ready for demonstration.

The remaining production recommendations are a dependency vulnerability scan and, if desired, replacing the supplied null-ID dataset with a source export containing real Lending Club identifiers.
