"""
FD Saathi 2.0 — Pydantic Request & Response Models
"""

from pydantic import BaseModel, Field


# ── Request Models ────────────────────────────────────────────────────────

class FDAnalyzeRequest(BaseModel):
    fd_amount: float = Field(..., gt=0, description="FD principal amount in ₹")
    fd_rate: float = Field(..., gt=0, le=20, description="FD interest rate (%)")
    days_left: int = Field(..., gt=0, le=3650, description="Days remaining to maturity")
    loan_rate: float = Field(..., gt=0, le=30, description="Loan interest rate (%)")

    class Config:
        json_schema_extra = {
            "example": {
                "fd_amount": 500000,
                "fd_rate": 7.5,
                "days_left": 180,
                "loan_rate": 11.0
            }
        }


class LoanApplyRequest(BaseModel):
    fd_amount: float = Field(..., gt=0, description="FD principal used as collateral")
    loan_rate: float = Field(..., gt=0, le=30, description="Loan interest rate (%)")
    tenure_months: int = Field(default=12, ge=1, le=60, description="Loan tenure in months")

    class Config:
        json_schema_extra = {
            "example": {
                "fd_amount": 500000,
                "loan_rate": 11.0,
                "tenure_months": 12
            }
        }


# ── Response Models ───────────────────────────────────────────────────────

class FDAnalyzeResponse(BaseModel):
    recommendation: str
    fd_penalty: float
    loan_interest: float
    net_savings: float
    penalty_ratio: float
    confidence: int
    risk: str
    reasoning: str


class LoanApprovalResponse(BaseModel):
    status: str
    approved_amount: float
    monthly_emi: float
    interest_rate: float
    tenure_months: int
    processing_fee: float
    disbursement: str
    ltv_percent: float
    fd_status: str


class AIDecisionResponse(BaseModel):
    recommendation: str
    confidence: int
    risk: str
    reasoning: str
    simple_explanation: str
  """
FD Saathi 2.0 — Pydantic Request & Response Models
"""

from pydantic import BaseModel, Field


# ── Request Models ────────────────────────────────────────────────────────

class FDAnalyzeRequest(BaseModel):
    fd_amount: float = Field(..., gt=0, description="FD principal amount in ₹")
    fd_rate: float = Field(..., gt=0, le=20, description="FD interest rate (%)")
    days_left: int = Field(..., gt=0, le=3650, description="Days remaining to maturity")
    loan_rate: float = Field(..., gt=0, le=30, description="Loan interest rate (%)")

    class Config:
        json_schema_extra = {
            "example": {
                "fd_amount": 500000,
                "fd_rate": 7.5,
                "days_left": 180,
                "loan_rate": 11.0
            }
        }


class LoanApplyRequest(BaseModel):
    fd_amount: float = Field(..., gt=0, description="FD principal used as collateral")
    loan_rate: float = Field(..., gt=0, le=30, description="Loan interest rate (%)")
    tenure_months: int = Field(default=12, ge=1, le=60, description="Loan tenure in months")

    class Config:
        json_schema_extra = {
            "example": {
                "fd_amount": 500000,
                "loan_rate": 11.0,
                "tenure_months": 12
            }
        }


# ── Response Models ───────────────────────────────────────────────────────

class FDAnalyzeResponse(BaseModel):
    recommendation: str
    fd_penalty: float
    loan_interest: float
    net_savings: float
    penalty_ratio: float
    confidence: int
    risk: str
    reasoning: str


class LoanApprovalResponse(BaseModel):
    status: str
    approved_amount: float
    monthly_emi: float
    interest_rate: float
    tenure_months: int
    processing_fee: float
    disbursement: str
    ltv_percent: float
    fd_status: str


class AIDecisionResponse(BaseModel):
    recommendation: str
    confidence: int
    risk: str
    reasoning: str
    simple_explanation: str
  """
FD Saathi 2.0 — Core Decision Engine (Python)

Formula:
    penalty   = fd_amount × 0.5%  +  fd_amount × fd_rate × days/365 × 10%
    loan_cost = fd_amount × loan_rate × days/365
    savings   = penalty − loan_cost

    if savings > 0  →  RECOMMEND: loan
    else            →  RECOMMEND: break_fd

Confidence:
    93% if |Δ| > 2% of amount
    78% if |Δ| > 0.5% of amount
    62% otherwise

Risk:
    High   — loan_rate > 13% OR amount > 10L
    Medium — loan_rate > 10.5% OR savings < 5000
    Low    — otherwise
"""

from dataclasses import dataclass


@dataclass
class FDResult:
    fd_penalty: float
    loan_interest: float
    net_savings: float
    penalty_ratio: float
    recommendation: str   # 'loan' | 'break_fd'
    confidence: int       # 62 | 78 | 93
    risk: str             # 'Low' | 'Medium' | 'High'


def calculate(
    fd_amount: float,
    fd_rate: float,
    days_left: int,
    loan_rate: float
) -> FDResult:
    """
    Core FD vs Loan decision engine.

    Args:
        fd_amount: FD principal in ₹
        fd_rate:   FD interest rate (%)
        days_left: Days remaining to FD maturity
        loan_rate: Loan interest rate (%)

    Returns:
        FDResult with recommendation and confidence
    """
    # Penalty = flat fee + proportional interest forfeiture
    penalty = (fd_amount * 0.005) + (fd_amount * (fd_rate / 100) * (days_left / 365) * 0.1)

    # Loan interest for the same period
    loan_interest = fd_amount * (loan_rate / 100) * (days_left / 365)

    # Net savings by taking loan vs breaking FD
    net_savings = penalty - loan_interest

    # Penalty-to-loan ratio
    penalty_ratio = round(penalty / max(loan_interest, 1), 2)

    # Recommendation
    recommendation = "loan" if net_savings > 0 else "break_fd"

    # Confidence scoring
    abs_savings = abs(net_savings)
    if abs_savings > fd_amount * 0.02:
        confidence = 93
    elif abs_savings > fd_amount * 0.005:
        confidence = 78
    else:
        confidence = 62

    # Risk assessment
    if loan_rate > 13 or fd_amount > 1_000_000:
        risk = "High"
    elif loan_rate > 10.5 or net_savings < 5000:
        risk = "Medium"
    else:
        risk = "Low"

    return FDResult(
        fd_penalty=round(penalty, 2),
        loan_interest=round(loan_interest, 2),
        net_savings=round(net_savings, 2),
        penalty_ratio=penalty_ratio,
        recommendation=recommendation,
        confidence=confidence,
        risk=risk,
    )
  """
FD Saathi 2.0 — /fd/analyze endpoint
"""

from fastapi import APIRouter
from models import FDAnalyzeResponse
from fd_engine import calculate

router = APIRouter()


@router.get("/analyze", response_model=FDAnalyzeResponse)
def analyze_fd(
    fd_amount: float,
    fd_rate: float,
    days_left: int,
    loan_rate: float
):
    """
    Analyze whether breaking an FD or taking a Loan Against FD is cheaper.

    - **fd_amount**: FD principal in ₹
    - **fd_rate**: FD interest rate (%)
    - **days_left**: Days remaining to maturity
    - **loan_rate**: Loan interest rate (%)
    """
    r = calculate(fd_amount, fd_rate, days_left, loan_rate)

    is_loan = r.recommendation == "loan"
    reasoning = (
        f"FD Penalty (₹{r.fd_penalty:,.0f}) is {r.penalty_ratio}× higher than "
        f"loan interest (₹{r.loan_interest:,.0f}). Taking a loan saves ₹{r.net_savings:,.0f}."
        if is_loan else
        f"Loan interest (₹{r.loan_interest:,.0f}) exceeds the FD break penalty "
        f"(₹{r.fd_penalty:,.0f}). Breaking FD saves ₹{abs(r.net_savings):,.0f}."
    )

    return FDAnalyzeResponse(
        recommendation=r.recommendation,
        fd_penalty=r.fd_penalty,
        loan_interest=r.loan_interest,
        net_savings=r.net_savings,
        penalty_ratio=r.penalty_ratio,
        confidence=r.confidence,
        risk=r.risk,
        reasoning=reasoning,
    )
