import pytest
from calculator import calculate_sip


def test_worked_example_from_planning_doc():
    """
    Same inputs/outputs as planning doc section 5:
    Rs 100,000 starting amount + Rs 20,000/month, 1 year, 14% return, 10% inflation.
    """
    result = calculate_sip(
        starting_amount=100000,
        monthly_investment=20000,
        years=1,
        annual_return_pct=14,
        inflation_pct=10,
    )

    assert result["total_contributed"] == pytest.approx(340000.00, abs=0.01)
    assert result["total_purchase_fees"] == pytest.approx(644.30, abs=0.01)
    assert result["cost_basis"] == pytest.approx(339355.70, abs=0.01)
    assert result["gross_value"] == pytest.approx(370431.14, abs=0.01)
    assert result["gain"] == pytest.approx(31075.44, abs=0.01)
    assert result["cgt_filer"] == pytest.approx(4661.32, abs=0.01)
    assert result["cgt_nonfiler"] == pytest.approx(9322.63, abs=0.01)
    assert result["net_value_filer"] == pytest.approx(365769.83, abs=0.01)
    assert result["net_value_nonfiler"] == pytest.approx(361108.51, abs=0.01)
    assert result["real_value_filer"] == pytest.approx(332518.03, abs=0.01)


def test_zero_return_zero_fees_equals_contributions():
    """
    Sanity check: if nothing grows and nothing is charged, the gross value
    at the end should be exactly what was put in - no compounding, no fees,
    nothing to calculate wrong.
    """
    result = calculate_sip(
        starting_amount=50000,
        monthly_investment=10000,
        years=2,
        annual_return_pct=0,
        inflation_pct=0,
        brokerage_pct=0,
        sst_pct_of_brokerage=0,
        cdc_pct=0,
        annual_flat_fee=0,
        cgt_filer_pct=15,
        cgt_nonfiler_pct=30,
    )

    expected_total = 50000 + 10000 * 24  # starting amount + 24 months of SIP
    assert result["total_contributed"] == pytest.approx(expected_total, abs=0.01)
    assert result["gross_value"] == pytest.approx(expected_total, abs=0.01)
    # No growth at all means no gain, so no tax either
    assert result["gain"] == pytest.approx(0, abs=0.01)
    assert result["cgt_filer"] == pytest.approx(0, abs=0.01)


def test_no_tax_on_a_loss():
    """
    If the investment loses money (negative assumed return), there should be
    no capital gains tax charged - you don't get taxed on a loss.
    """
    result = calculate_sip(
        starting_amount=0,
        monthly_investment=10000,
        years=1,
        annual_return_pct=-20,   # a bad year, on purpose
        inflation_pct=10,
    )

    assert result["gross_value"] < result["total_contributed"]
    assert result["gain"] == 0
    assert result["cgt_filer"] == 0
    assert result["cgt_nonfiler"] == 0
    # with no tax owed, net value should just equal gross value
    assert result["net_value_filer"] == pytest.approx(result["gross_value"], abs=0.01)