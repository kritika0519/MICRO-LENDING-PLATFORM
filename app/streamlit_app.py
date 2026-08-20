from __future__ import annotations

import streamlit as st

from src.decision_engine import make_decision, predict_default_probability

st.set_page_config(page_title='Micro Lending Platform', layout='wide')

st.title('Micro-Lending Risk Decision Platform')

with st.form('loan_form'):
    col1, col2 = st.columns(2)
    with col1:
        annual_inc = st.number_input('Annual Income', min_value=0.0, value=70000.0)
        emp_length = st.number_input('Employment Length (years)', min_value=0.0, value=3.0)
        revol_util = st.number_input('Revolving Utilization', min_value=0.0, max_value=1.0, value=0.45)
        delinq_2yrs = st.number_input('Delinquent Events in 2 Years', min_value=0, value=0)
        inq_last_6mths = st.number_input('Inquiries in Last 6 Months', min_value=0, value=1)

    with col2:
        loan_amnt = st.number_input('Requested Loan Amount', min_value=0.0, value=20000.0)
        dti = st.number_input('DTI', min_value=0.0, max_value=100.0, value=18.0)
        fico_range_low = st.number_input('FICO Low', min_value=0.0, value=680.0)

    submitted = st.form_submit_button('Evaluate Loan')

if submitted:
    applicant = {
        'annual_inc': annual_inc,
        'emp_length': emp_length,
        'revol_util': revol_util,
        'delinq_2yrs': delinq_2yrs,
        'inq_last_6mths': inq_last_6mths,
        'fico_range_low': fico_range_low,
    }
    loan = {
        'loan_amnt': loan_amnt,
        'dti': dti,
    }
    default_probability = predict_default_probability(applicant, loan)
    result = make_decision(applicant, loan, default_probability)

    st.subheader('Decision Output')
    st.metric('Decision', result['decision'])
    st.metric('Risk Score', result['risk_score'])
    st.metric('Risk Band', result['risk_band'])
    st.metric('Eligibility', 'Eligible' if result['eligible'] else 'Not Eligible')

    st.write('Reasons:')
    for reason in result['reasons']:
        st.write('-', reason) 
