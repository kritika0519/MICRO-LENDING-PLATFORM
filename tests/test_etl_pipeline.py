import pandas as pd
import pytest

from api.app import ApplicantInput, LoanInput
from src.database import load_tables_to_database, read_table_from_database
from src.run_business_queries import read_business_queries
from src.decision_engine import predict_default_probability
from src.etl_pipeline import build_default_flag, standardize_columns, build_customer_table, build_loan_table
from src.eda_analysis import build_eda_outputs
from src.features import build_fintech_features
from src.risk_score import probability_to_score, score_to_band
from src.eligibility import evaluate_eligibility
from src.decision_engine import make_decision


def test_build_default_flag_maps_statuses():
    df = pd.DataFrame({
        'loan_status': ['Charged Off', 'Fully Paid', 'Current', 'Late (31-120 days)', 'Default']
    })
    out = build_default_flag(df)
    assert out['default_flag'].tolist() == [1, 0, 0, 1, 1]


def test_standardize_columns_snake_case():
    df = pd.DataFrame({'loan Amnt': [1000], 'member-id': [10]})
    out = standardize_columns(df)
    assert 'loan_amnt' in out.columns
    assert 'member_id' in out.columns


def test_build_customer_and_loan_tables_include_required_ids():
    df = pd.DataFrame({
        'id': [1, 2],
        'member_id': [10, 11],
        'loan_amnt': [1000, 2000],
        'annual_inc': [50000, 60000],
        'term': ['36 months', '60 months'],
        'loan_status': ['Fully Paid', 'Charged Off'],
        'grade': ['A', 'B'],
        'home_ownership': ['RENT', 'MORTGAGE'],
        'addr_state': ['CA', 'NY'],
        'zip_code': ['900', '100']
    })

    customer = build_customer_table(df)
    loan = build_loan_table(df)

    assert 'member_id' in customer.columns
    assert 'customer_id' in customer.columns
    assert 'loan_id' in loan.columns
    assert 'member_id' in loan.columns
    assert len(customer) == 2
    assert len(loan) == 2


def test_predict_default_probability_returns_valid_probabilities():
    applicant = {
        'annual_inc': 70000,
        'emp_length': 3,
        'revol_util': 0.45,
        'delinq_2yrs': 0,
        'inq_last_6mths': 1,
        'fico_range_low': 680,
    }
    loan = {
        'loan_amnt': 20000,
        'dti': 18,
    }

    prob = predict_default_probability(applicant, loan)

    assert 0.0 <= prob <= 1.0


def test_missing_ids_are_backfilled_for_customer_and_loan_tables():
    df = pd.DataFrame({
        'loan_amnt': [1000, 2000],
        'annual_inc': [50000, 60000],
        'member_id': [None, None],
        'id': [None, None],
        'loan_status': ['Fully Paid', 'Charged Off'],
    })

    customer = build_customer_table(df)
    loan = build_loan_table(df)

    assert customer['member_id'].notna().all()
    assert loan['loan_id'].notna().all()
    assert len(customer) == 2
    assert len(loan) == 2


def test_processed_tables_can_be_loaded_and_read_from_sqlite(tmp_path):
    customers = pd.DataFrame({'customer_id': [1], 'member_id': [1], 'annual_inc': [50000]})
    loans = pd.DataFrame({'loan_id': [10], 'customer_id': [1], 'loan_amnt': [1000]})
    database_url = f'sqlite:///{tmp_path / "test.db"}'

    engine = load_tables_to_database(customers, loans, database_url)
    assert set(read_table_from_database('customers', database_url).columns) == set(customers.columns)
    assert len(read_table_from_database('loans', database_url)) == 1
    engine.dispose()


def test_eda_outputs_include_summary_and_charts(tmp_path):
    data = pd.DataFrame({
        'loan_amnt': [1000, 2000, 3000],
        'annual_inc': [40000, 50000, 60000],
        'dti': [10, 20, 30],
        'grade': ['A', 'B', 'A'],
        'default_flag': [0, 1, 0],
    })

    outputs = build_eda_outputs(data, tmp_path)
    assert all(path.exists() for path in outputs.values())
    assert 'default_rate' in pd.read_csv(outputs['summary'])['metric'].tolist()


def test_feature_engineering_includes_pdf_categories():
    data = pd.DataFrame({
        'loan_amnt': [10000], 'annual_inc': [60000], 'dti': [18], 'revol_util': [0.42],
        'delinq_2yrs': [0], 'inq_last_6mths': [1], 'earliest_cr_line': ['2010-01-01'],
        'issue_d': ['2018-12-01'], 'emp_length': [5],
    })
    features = build_fintech_features(data)
    assert {'income_category', 'loan_amount_category', 'credit_history_length'} <= set(features.columns)
    assert features.loc[0, 'credit_history_length'] == 8


def test_risk_eligibility_and_decision_contracts():
    assert probability_to_score(0.20) == 20
    assert score_to_band(80) == 'Very High Risk'
    applicant = {'annual_inc': 70000, 'emp_length': 5, 'revol_util': 0.3, 'fico_range_low': 700}
    loan = {'loan_amnt': 10000, 'dti': 15}
    eligibility = evaluate_eligibility(applicant, loan, risk_score=20, default_probability=0.2)
    decision = make_decision(applicant, loan, default_probability=0.2)
    assert eligibility['eligible'] is True
    assert decision['decision'] in {'APPROVE', 'REVIEW', 'REJECT'}
    assert decision['reasons']


def test_api_models_reject_invalid_ranges():
    with pytest.raises(ValueError):
        ApplicantInput(annual_inc=50000, emp_length=2, revol_util=1.2)
    with pytest.raises(ValueError):
        LoanInput(loan_amnt=0, dti=20)


def test_business_query_runner_contains_six_reports_without_use_statement():
    queries = read_business_queries()
    assert len(queries) == 6
    assert all('USE micro_lending' not in query.upper() for query in queries)
