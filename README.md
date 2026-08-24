# Micro-Lending Risk Decision Platform

A capstone-style lending risk assessment system built on historical Lending Club data. The project combines data cleaning, feature engineering, machine learning, business-rule eligibility checks, and a Streamlit-based decision interface to estimate default risk and support loan decisions.

## Project Highlights

- End-to-end loan default risk assessment
- Default probability prediction using a trained ML model
- Risk score and risk-band generation
- Rule-based eligibility checks for lending policy
- Explainable approve / review / reject decision flow
- FastAPI backend for model and decision endpoints
- Streamlit interface for analyst input and output
- SQL-based business analysis and reporting
- Automated tests for ETL, feature engineering, eligibility, and decision logic

## Problem Statement

Digital lenders need a consistent, explainable way to evaluate credit applicants. A model alone can estimate risk, but a robust lending process also needs business rules, applicant-level checks, and decision reasoning.

This project addresses that gap by combining:

- ML-based default prediction
- risk scoring and risk-band categorization
- borrower eligibility rules
- final decision logic with human-readable reasons

The end result is a decision-support workflow rather than a black-box model output.

## What the System Does

The project follows a practical lending pipeline:

1. Applicant enters loan and borrower information
2. Data is validated and transformed for model use
3. Relevant financial features are engineered
4. The model estimates default probability
5. Probability is converted into a 0–100 risk score and risk band
6. Eligibility checks are applied
7. Final decision is generated as APPROVE, REVIEW, or REJECT
8. Reasons are shown for transparency

```text
Applicant Input
  -> Feature Engineering
  -> Default Risk Prediction
  -> Risk Score / Risk Band
  -> Eligibility Rules
  -> Decision Engine
  -> Approve / Review / Reject
```

## Live Application / Output

These are real application screenshots from the repository.

### 1. Loan Evaluation Interface

![Loan evaluation form](docs/assets/Output%20pic1.png)

The Streamlit interface allows a lending analyst to enter inputs such as:

- Annual Income
- Requested Loan Amount
- Employment Length
- DTI
- Revolving Utilization
- FICO Low
- Delinquent Events in 2 Years
- Inquiries in Last 6 Months

After entering the values, the user clicks Evaluate Loan to generate a decision.

### 2. Risk Decision Output

![Decision result](docs/assets/Output%20pic2.png)

The output screen shows the final decision with:

- Decision
- Risk Score
- Risk Band
- Eligibility status
- Explanation reasons

This is the main user-facing result produced by the project.

## How Risk Assessment Works

The actual implementation is split across the model, score conversion, eligibility checks, and final decision engine.

### Default prediction

The model predicts the probability that a loan will default. The training workflow compares multiple estimators and saves the best-performing model.

The logic is implemented in:

- [src/train_model.py](src/train_model.py)
- [src/decision_engine.py](src/decision_engine.py)
- [src/features.py](src/features.py)

### Risk score

The project converts a default probability into a 0–100 risk score using the implementation in [src/risk_score.py](src/risk_score.py):

```python
risk_score = round(default_probability * 100)
```

### Risk band thresholds

The actual logic in [src/risk_score.py](src/risk_score.py) is:

- score < 25 → Low Risk
- score < 50 → Medium Risk
- score < 75 → High Risk
- score >= 75 → Very High Risk

### Eligibility checks

Eligibility is evaluated separately from the ML model in [src/eligibility.py](src/eligibility.py). The system rejects applicants when key business thresholds are violated, including:

- annual income below minimum threshold
- loan-to-income ratio above recommended limit
- DTI above permissible limit
- credit utilization too high
- employment length below minimum threshold
- FICO below threshold
- delinquency history too severe
- recent inquiry intensity too high
- default probability above tolerance
- risk score above approval threshold

### Final decision

The final decision logic in [src/decision_engine.py](src/decision_engine.py) is:

- if not eligible → REJECT
- else if risk band is Low Risk → APPROVE
- else if risk band is Medium Risk or High Risk → REVIEW
- else → REJECT

This combines both ML-driven risk and policy-driven eligibility.

## Machine Learning

The repository includes a training workflow for a default-risk model using historical Lending Club data.

### What is being predicted

The target is a default flag derived from loan status categories, as implemented in [src/etl_pipeline.py](src/etl_pipeline.py).

### What features are used

The feature engineering step in [src/features.py](src/features.py) creates a set of borrower and loan features such as:

- loan-to-income ratio
- average FICO
- credit history length
- delinquency flag
- inquiry intensity
- utilization category
- debt burden category
- employment stability
- income category
- loan amount category

### Model training

The training process in [src/train_model.py](src/train_model.py):

- samples the dataset
- builds engineered features
- splits into train/test data
- tests multiple models
- compares metrics
- saves the selected model to `models/default_model.joblib`

The repository explicitly compares:

- Logistic Regression
- Random Forest
- Gradient Boosting

The model is then loaded during prediction inside [src/decision_engine.py](src/decision_engine.py).

> No fabricated performance numbers are claimed here; the repository includes the training/evaluation code and the saved model artifact used during prediction.

## End-to-End Architecture

![Project pipeline](docs/assets/decision_pipeline.png)

The implemented flow is:

```text
Raw Lending Club dataset
  -> ETL and data cleaning
  -> Processed customer and loan tables
  -> SQL analysis and reporting
  -> Feature engineering
  -> Model training and prediction
  -> Risk score and risk band
  -> Eligibility rules
  -> Final decision engine
  -> FastAPI backend
  -> Streamlit dashboard
```

## Data & SQL Analytics

The project uses the Lending Club dataset from Kaggle:

[https://www.kaggle.com/datasets/adarshsng/lending-club-loan-data-csv](https://www.kaggle.com/datasets/adarshsng/lending-club-loan-data-csv)

The raw dataset is intentionally not committed to GitHub because it is large and is excluded via the repository `.gitignore` file.

The repository includes SQL analysis assets under [sql](sql):

- [sql/schema.sql](sql/schema.sql)
- [sql/business_queries.sql](sql/business_queries.sql)

These support the business reporting side of the project and are aligned with the ETL and lending analysis workflow.

## Tech Stack

| Category        | Technologies                |
| --------------- | --------------------------- |
| Language        | Python                      |
| ML / Data       | pandas, NumPy, scikit-learn |
| Backend         | FastAPI                     |
| Frontend        | Streamlit                   |
| Database / SQL  | MySQL, SQL, SQLAlchemy      |
| Visualization   | Matplotlib, Seaborn         |
| Testing         | Pytest                      |
| Version Control | Git, GitHub                 |

## Project Structure

```text
.
├── api/
│   └── app.py
├── app/
│   └── streamlit_app.py
├── data/
│   └── processed/
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

> The raw dataset and generated analysis files are intentionally excluded from GitHub via `.gitignore` and are expected to be downloaded or generated locally.

## How to Run

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "MICRO-LENDING PLATFORM - End-to-End FinTech Capstone Project"
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the dataset locally

Download the Lending Club dataset from the Kaggle source mentioned above and place it in the repository as:

```text
lendingLoan zip/loan.csv
```

### 5. Run the ETL pipeline

```bash
python -m src.etl_pipeline
```

### 6. Generate EDA charts

```bash
python -m src.eda_analysis --sample-size 50000
```

### 7. Start the FastAPI backend

```bash
python -m uvicorn api.app:app --host 127.0.0.1 --port 8000
```

### 8. Start the Streamlit app

```bash
python -m streamlit run app/streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

### 9. Run tests

```bash
python -m pytest -q
```

## Testing

The repository includes automated tests for the main project flow, including:

- ETL behavior
- feature engineering
- risk scoring
- eligibility logic
- decision engine behavior
- API validation

The project is configured to run with:

```bash
python -m pytest -q
```

## Documentation

Additional project documents are available in the [docs](docs) folder:

- [docs/business_problem.md](docs/business_problem.md)
- [docs/project_documentation.md](docs/project_documentation.md)
- [PROJECT_GUIDE.md](PROJECT_GUIDE.md)

## Limitations

This project is a strong educational and portfolio implementation, but it is not a production credit underwriting system. In a real financial environment, additional governance, model validation, compliance review, explainability audits, and monitoring would be required before deployment.

## Why This Project Matters

This project demonstrates a complete end-to-end ML pipeline in a business context:

- data engineering
- model training and inference
- structured risk logic
- API integration
- analyst-facing UI
- explainable decision support

It brings together software engineering, data analysis, and machine learning in a practical lending use case.

---

Built as a micro-lending risk decision system for loan evaluation and decision support.
