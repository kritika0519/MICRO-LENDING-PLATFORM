from __future__ import annotations

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / 'docs' / 'assets'
ASSET_DIR.mkdir(parents=True, exist_ok=True)


def save_pipeline_diagram(path: Path):
    fig, ax = plt.subplots(figsize=(14, 6), facecolor='#0a1018')
    ax.set_facecolor('#0a1018')
    ax.axis('off')

    boxes = [
        ('Raw Loan Data', (0.04, 0.70), (0.18, 0.22)),
        ('ETL & Cleaning', (0.24, 0.70), (0.18, 0.22)),
        ('Feature Engineering', (0.44, 0.70), (0.18, 0.22)),
        ('ML Default Model', (0.64, 0.70), (0.18, 0.22)),
        ('Risk + Eligibility', (0.84, 0.70), (0.18, 0.22)),
        ('Decision Output', (0.46, 0.18), (0.20, 0.22)),
    ]

    for label, (x, y), (w, h) in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor='#111b29', edgecolor='#4a5d75', linewidth=1.5))
        ax.text(x + w / 2, y + h / 2, label, ha='center', va='center', color='white', fontsize=12, family='DejaVu Sans')

    arrows = [
        ((0.22, 0.81), (0.24, 0.81)),
        ((0.42, 0.81), (0.44, 0.81)),
        ((0.62, 0.81), (0.64, 0.81)),
        ((0.82, 0.81), (0.84, 0.81)),
        ((0.54, 0.70), (0.54, 0.40)),
        ((0.54, 0.18), (0.54, 0.08)),
    ]

    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start, arrowprops=dict(arrowstyle='->', color='#8cc7ff', lw=2))

    ax.text(0.50, 0.02, 'End-to-End Micro-Lending Platform Workflow', ha='center', va='bottom', color='#dfe9f5', fontsize=16, fontweight='bold')
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def save_risk_distribution(path: Path):
    labels = ['Low', 'Medium', 'High', 'Very High']
    values = [42, 30, 20, 8]
    fig, ax = plt.subplots(figsize=(8, 5), facecolor='#0a1018')
    ax.set_facecolor('#0a1018')
    bars = ax.bar(labels, values, color=['#4ade80', '#fbbf24', '#fb7185', '#a78bfa'], edgecolor='white', linewidth=0.8)
    ax.set_title('Example Risk Band Distribution', color='white', fontsize=14, pad=16)
    ax.set_ylabel('Applicants', color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    for spine in ax.spines.values():
        spine.set_color('#2d3748')
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1, str(h), ha='center', va='bottom', color='white', fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def save_probability_chart(path: Path):
    scores = np.array([8, 25, 34, 55, 72, 87])
    probs = scores / 100

    fig, ax = plt.subplots(figsize=(8, 5), facecolor='#0a1018')
    ax.set_facecolor('#0a1018')
    ax.plot(scores, probs, marker='o', color='#67e8f9', linewidth=2.5, markersize=6)
    ax.fill_between(scores, probs, 0, alpha=0.18, color='#67e8f9')
    ax.set_title('Risk Score vs Default Probability', color='white', fontsize=14)
    ax.set_xlabel('Risk Score (0-100)', color='white')
    ax.set_ylabel('Default Probability', color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    for spine in ax.spines.values():
        spine.set_color('#2d3748')
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def draw_streamlit_card(path: Path, decision: str, risk_score: int, risk_band: str, eligible: bool, reasons: list[str], title: str):
    fig, ax = plt.subplots(figsize=(14, 9), facecolor='#050b13')
    ax.set_facecolor('#050b13')
    ax.axis('off')

    # outer panel
    panel = plt.Rectangle((0.03, 0.04), 0.94, 0.92, facecolor='#0d1724', edgecolor='#303d4d', linewidth=2)
    ax.add_patch(panel)

    # title
    ax.text(0.06, 0.86, 'Micro-Lending Risk Decision Platform', fontsize=18, fontweight='bold', color='white', ha='left')

    # form box rows
    form_y = 0.72
    fields = [
        ('Annual Income', '$70,000'),
        ('Employment Length', '3 years'),
        ('Revolving Utilization', '0.45'),
        ('Delinquent Events', '0'),
        ('Inquiries (6m)', '1'),
        ('Requested Loan', '$20,000'),
        ('DTI', '18.0'),
        ('FICO Low', '680'),
    ]

    for i, (label, value) in enumerate(fields):
        y = form_y - i * 0.05
        ax.add_patch(plt.Rectangle((0.06, y), 0.34, 0.04, facecolor='#1b2430', edgecolor='#3b4758'))
        ax.add_patch(plt.Rectangle((0.45, y), 0.34, 0.04, facecolor='#1b2430', edgecolor='#3b4758'))
        ax.text(0.07, y + 0.018, label, fontsize=9, color='#d8e1eb', ha='left', va='center')
        ax.text(0.46, y + 0.018, value, fontsize=9, color='white', ha='left', va='center')

    button = plt.Rectangle((0.06, 0.25), 0.16, 0.05, facecolor='#1d1f22', edgecolor='#3d4652', linewidth=1)
    ax.add_patch(button)
    ax.text(0.14, 0.275, 'Evaluate Loan', ha='center', va='center', fontsize=9, color='white')

    # decision panel
    decision_box = plt.Rectangle((0.55, 0.12), 0.38, 0.60, facecolor='#090d12', edgecolor='#243041', linewidth=1.5)
    ax.add_patch(decision_box)
    ax.text(0.58, 0.63, 'Decision Output', fontsize=17, color='white', fontweight='bold', ha='left')
    ax.text(0.58, 0.56, 'Decision', fontsize=11, color='#dfeaf9', ha='left')
    ax.text(0.58, 0.49, decision.upper(), fontsize=23, color='white', fontweight='bold', ha='left')
    ax.text(0.58, 0.40, f'Risk Score', fontsize=11, color='#dfeaf9', ha='left')
    ax.text(0.58, 0.34, str(risk_score), fontsize=32, color='white', fontweight='bold', ha='left')
    ax.text(0.58, 0.24, 'Risk Band', fontsize=11, color='#dfeaf9', ha='left')
    ax.text(0.58, 0.18, risk_band, fontsize=22, color='white', fontweight='bold', ha='left')
    ax.text(0.58, 0.10, 'Eligibility', fontsize=11, color='#dfeaf9', ha='left')
    ax.text(0.58, 0.06, 'Eligible' if eligible else 'Not Eligible', fontsize=18, color='white', fontweight='bold', ha='left')

    # small reason list on right side only for reject? no, keep compact
    # use same for all examples
    ax.text(0.05, 0.18, title, fontsize=12, color='#92bdf2', fontweight='bold', ha='left')
    for idx, reason in enumerate(reasons[:3]):
        y = 0.14 - idx * 0.04
        ax.text(0.06, y, f'- {reason}', fontsize=9, color='white', ha='left', va='center')

    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def main():
    save_pipeline_diagram(ASSET_DIR / 'decision_pipeline.png')
    save_risk_distribution(ASSET_DIR / 'risk_band_distribution.png')
    save_probability_chart(ASSET_DIR / 'risk_probability_curve.png')

    # Example streamlit UI images based on project logic
    draw_streamlit_card(
        ASSET_DIR / 'streamlit_decision_approve.png',
        'APPROVE',
        8,
        'Low Risk',
        True,
        ['Default probability is low', 'Strong income and credit profile', 'Meets eligibility rules'],
        'Low-risk applicant example',
    )
    draw_streamlit_card(
        ASSET_DIR / 'streamlit_decision_review.png',
        'REVIEW',
        34,
        'Medium Risk',
        True,
        ['Income is acceptable', 'Debt burden is elevated', 'Risk score is moderate'],
        'Medium-risk applicant example',
    )
    draw_streamlit_card(
        ASSET_DIR / 'streamlit_decision_reject.png',
        'REJECT',
        55,
        'High Risk',
        False,
        ['Default probability exceeds lending tolerance', 'Risk band: High Risk', 'DTI and utilization are too high'],
        'High-risk applicant example',
    )

    print(f'Generated visual assets in: {ASSET_DIR}')


if __name__ == '__main__':
    main()
