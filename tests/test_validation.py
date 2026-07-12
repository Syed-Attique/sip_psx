import pytest
from calculator import calculate_sip


def test_rejects_return_worse_than_negative_100_percent():
    with pytest.raises(ValueError, match="annual_return_pct"):
        calculate_sip(starting_amount=0, monthly_investment=10000, years=1,
                       annual_return_pct=-150, inflation_pct=10)


def test_rejects_inflation_of_negative_100_percent():
    with pytest.raises(ValueError, match="inflation_pct"):
        calculate_sip(starting_amount=0, monthly_investment=10000, years=1,
                       annual_return_pct=14, inflation_pct=-100)


def test_rejects_zero_years():
    with pytest.raises(ValueError, match="years"):
        calculate_sip(starting_amount=50000, monthly_investment=10000, years=0,
                       annual_return_pct=14, inflation_pct=10)


def test_rejects_negative_years():
    with pytest.raises(ValueError, match="years"):
        calculate_sip(starting_amount=0, monthly_investment=10000, years=-5,
                       annual_return_pct=14, inflation_pct=10)


def test_rejects_negative_starting_amount():
    with pytest.raises(ValueError, match="starting_amount"):
        calculate_sip(starting_amount=-1000, monthly_investment=10000, years=1,
                       annual_return_pct=14, inflation_pct=10)


def test_rejects_negative_monthly_investment():
    with pytest.raises(ValueError, match="monthly_investment"):
        calculate_sip(starting_amount=0, monthly_investment=-500, years=1,
                       annual_return_pct=14, inflation_pct=10)


def test_rejects_both_amounts_zero():
    with pytest.raises(ValueError, match="At least one"):
        calculate_sip(starting_amount=0, monthly_investment=0, years=1,
                       annual_return_pct=14, inflation_pct=10)


def test_rejects_negative_brokerage():
    with pytest.raises(ValueError, match="brokerage_pct"):
        calculate_sip(starting_amount=0, monthly_investment=10000, years=1,
                       annual_return_pct=14, inflation_pct=10, brokerage_pct=-1)


def test_rejects_cgt_rate_over_100_percent():
    with pytest.raises(ValueError, match="cgt_filer_pct"):
        calculate_sip(starting_amount=0, monthly_investment=10000, years=1,
                       annual_return_pct=14, inflation_pct=10, cgt_filer_pct=150)


def test_rejects_non_numeric_input():
    with pytest.raises(ValueError, match="must be a number"):
        calculate_sip(starting_amount=0, monthly_investment=10000, years="five",
                       annual_return_pct=14, inflation_pct=10)


def test_rejects_duration_shorter_than_one_month():
    with pytest.raises(ValueError, match="years"):
        calculate_sip(starting_amount=0, monthly_investment=10000, years=0.01,
                       annual_return_pct=14, inflation_pct=10)