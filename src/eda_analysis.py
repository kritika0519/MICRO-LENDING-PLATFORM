from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT_DIR / 'data' / 'processed' / 'loans.csv'
DEFAULT_CUSTOMERS_INPUT = ROOT_DIR / 'data' / 'processed' / 'customers.csv'
DEFAULT_OUTPUT = ROOT_DIR / 'data' / 'eda'


def ensure_processed_data() -> None:
    """Generate processed CSVs if the raw dataset is present but the processed outputs are missing."""
    if DEFAULT_INPUT.exists() and DEFAULT_CUSTOMERS_INPUT.exists():
        return

    from src.etl_pipeline import clean_raw_dataset

    clean_raw_dataset()


def load_eda_data(input_path: Path = DEFAULT_INPUT, sample_size: int = 100000) -> pd.DataFrame:
    """Load a bounded loan sample and join customer attributes for analysis."""
    columns = [
        'customer_id', 'loan_amnt', 'dti', 'int_rate', 'grade', 'purpose',
        'loan_status', 'default_flag', 'issue_d', 'term', 'addr_state'
    ]
    loan_data = pd.read_csv(input_path, usecols=lambda column: column in columns, nrows=sample_size)
    customer_data = pd.read_csv(DEFAULT_CUSTOMERS_INPUT, usecols=['customer_id', 'annual_inc', 'addr_state'])
    return loan_data.merge(customer_data, on='customer_id', how='left')


def build_eda_outputs(data: pd.DataFrame, output_dir: Path = DEFAULT_OUTPUT) -> dict[str, Path]:
    """Create business summaries and charts used in the project demonstration."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = data.copy()
    for column in ['annual_inc', 'loan_amnt', 'dti', 'int_rate']:
        if column not in data.columns:
            data[column] = pd.NA
        data[column] = pd.to_numeric(data[column], errors='coerce')
    for column in ['grade', 'addr_state']:
        if column not in data.columns:
            data[column] = 'unknown'
    if 'default_flag' not in data.columns:
        data['default_flag'] = 0
    data['default_flag'] = pd.to_numeric(data['default_flag'], errors='coerce').fillna(0).astype(int)
    if 'issue_d' in data.columns:
        data['issue_d'] = pd.to_datetime(data['issue_d'], errors='coerce')
        data['issue_year'] = data['issue_d'].dt.year
    else:
        data['issue_year'] = pd.NA
    data['income_category'] = pd.cut(
        data['annual_inc'].fillna(0),
        bins=[-0.01, 30000, 60000, 100000, float('inf')],
        labels=['low', 'moderate', 'high', 'very_high'],
        right=False,
    )

    summary = pd.DataFrame({
        'metric': ['rows', 'default_rate', 'median_loan_amount', 'median_annual_income', 'median_dti'],
        'value': [len(data), data['default_flag'].mean(), data['loan_amnt'].median(), data['annual_inc'].median(), data['dti'].median()],
    })
    summary_path = output_dir / 'eda_summary.csv'
    summary.to_csv(summary_path, index=False)

    grade_summary = data.groupby('grade', dropna=False)['default_flag'].agg(['count', 'mean']).reset_index()
    grade_summary = grade_summary.rename(columns={'mean': 'default_rate'})
    grade_path = output_dir / 'default_rate_by_grade.csv'
    grade_summary.to_csv(grade_path, index=False)

    income_summary = data.groupby('income_category', observed=False)['default_flag'].agg(['count', 'mean']).reset_index()
    income_summary = income_summary.rename(columns={'mean': 'default_rate'})
    income_path = output_dir / 'default_rate_by_income_category.csv'
    income_summary.to_csv(income_path, index=False)

    region_summary = data.groupby('addr_state', dropna=False)['default_flag'].agg(['count', 'mean']).reset_index()
    region_summary = region_summary.rename(columns={'mean': 'default_rate'})
    region_path = output_dir / 'default_rate_by_region.csv'
    region_summary.to_csv(region_path, index=False)

    year_summary = data.groupby('issue_year', dropna=False)['default_flag'].agg(['count', 'mean']).reset_index()
    year_summary = year_summary.rename(columns={'mean': 'default_rate'})
    year_path = output_dir / 'default_rate_by_year.csv'
    year_summary.to_csv(year_path, index=False)

    sns.set_theme(style='whitegrid')
    chart_paths: dict[str, Path] = {}

    grade_chart = output_dir / 'default_rate_by_grade.png'
    sns.barplot(data=grade_summary.sort_values('default_rate'), x='grade', y='default_rate', color='#176b87')
    plt.title('Default Rate by Loan Grade')
    plt.ylabel('Default rate')
    plt.xlabel('Grade')
    plt.tight_layout()
    plt.savefig(grade_chart, dpi=140)
    plt.close()
    chart_paths['grade_chart'] = grade_chart

    income_chart = output_dir / 'default_rate_by_income_category.png'
    sns.barplot(data=income_summary, x='income_category', y='default_rate', color='#d77a61')
    plt.title('Default Rate by Income Category')
    plt.ylabel('Default rate')
    plt.xlabel('Income category')
    plt.tight_layout()
    plt.savefig(income_chart, dpi=140)
    plt.close()
    chart_paths['income_chart'] = income_chart

    region_chart = output_dir / 'loans_by_region.png'
    region_plot = region_summary.sort_values('count', ascending=False).head(15)
    sns.barplot(data=region_plot, x='count', y='addr_state', color='#4c956c')
    plt.title('Top Regions by Loan Volume')
    plt.xlabel('Loan count')
    plt.ylabel('State')
    plt.tight_layout()
    plt.savefig(region_chart, dpi=140)
    plt.close()
    chart_paths['region_chart'] = region_chart

    dti_chart = output_dir / 'loan_amount_vs_dti.png'
    sample = data[['loan_amnt', 'dti', 'default_flag']].dropna().head(5000)
    sns.scatterplot(data=sample, x='dti', y='loan_amnt', hue='default_flag', alpha=0.45, palette='Set1')
    plt.title('Loan Amount vs Debt-to-Income Ratio')
    plt.tight_layout()
    plt.savefig(dti_chart, dpi=140)
    plt.close()
    chart_paths['dti_chart'] = dti_chart

    return {
        'summary': summary_path,
        'grade_summary': grade_path,
        'income_summary': income_path,
        'region_summary': region_path,
        'year_summary': year_path,
        **chart_paths,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate EDA summaries and charts for the lending dataset.')
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--sample-size', type=int, default=100000)
    args = parser.parse_args()

    ensure_processed_data()
    outputs = build_eda_outputs(load_eda_data(args.input, args.sample_size), args.output)
    for name, path in outputs.items():
        print(f'{name}: {path}')


if __name__ == '__main__':
    main()
