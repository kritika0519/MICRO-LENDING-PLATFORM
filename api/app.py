from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.decision_engine import make_decision, predict_default_probability
from src.eligibility import evaluate_eligibility
from src.risk_score import risk_summary

app = FastAPI(title='Micro Lending Risk API', version='1.0.0')


class ApplicantInput(BaseModel):
    annual_inc: float = Field(..., ge=0)
    emp_length: float = Field(..., ge=0)
    revol_util: float = Field(default=0.0, ge=0.0, le=1.0)
    delinq_2yrs: int = Field(default=0, ge=0)
    inq_last_6mths: int = Field(default=0, ge=0)
    fico_range_low: float = Field(default=0.0, ge=0.0, le=850.0)


class LoanInput(BaseModel):
    loan_amnt: float = Field(..., gt=0)
    dti: float = Field(..., ge=0, le=100)
    term: int = Field(default=36)
    purpose: str = Field(default='debt_consolidation')


class PredictionRequest(BaseModel):
    applicant: ApplicantInput
    loan: LoanInput


@app.get('/')
def root():
    return {'message': 'Micro Lending Risk API is running'}


@app.post('/risk-score')
def risk_score_api(payload: PredictionRequest):
    applicant = payload.applicant.model_dump()
    loan = payload.loan.model_dump()
    probability = predict_default_probability(applicant, loan)
    result = risk_summary(probability)
    return result


@app.post('/eligibility')
def eligibility_api(payload: PredictionRequest):
    applicant = payload.applicant.model_dump()
    loan = payload.loan.model_dump()
    probability = predict_default_probability(applicant, loan)
    result = evaluate_eligibility(
        applicant=applicant,
        loan=loan,
        risk_score=risk_summary(probability)['risk_score'],
        default_probability=probability,
    )
    return result


@app.post('/loan-decision')
def loan_decision_api(payload: PredictionRequest):
    applicant = payload.applicant.model_dump()
    loan = payload.loan.model_dump()
    default_probability = predict_default_probability(applicant, loan)
    return make_decision(applicant, loan, default_probability)
