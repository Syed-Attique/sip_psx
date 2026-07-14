def _validate_inputs(
    starting_amount, monthly_investment, step_up_pct, years, annual_return_pct, inflation_pct,
    brokerage_pct, sst_pct_of_brokerage, cdc_pct, annual_flat_fee,
    cgt_filer_pct, cgt_nonfiler_pct,
):
    numeric_fields = {
        "starting_amount": starting_amount,
        "monthly_investment": monthly_investment,
        "step_up_pct": step_up_pct,
        "years": years,
        "annual_return_pct": annual_return_pct,
        "inflation_pct": inflation_pct,
        "brokerage_pct": brokerage_pct,
        "sst_pct_of_brokerage": sst_pct_of_brokerage,
        "cdc_pct": cdc_pct,
        "annual_flat_fee": annual_flat_fee,
        "cgt_filer_pct": cgt_filer_pct,
        "cgt_nonfiler_pct": cgt_nonfiler_pct,
    }

    # 1. Every input must actually be a real number - not text, None, a list,
    #    or a boolean (bool is secretly a subclass of int in Python, so
    #    True/False would otherwise sneak past a plain int/float check).
    for name, value in numeric_fields.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number, got {type(value).__name__}: {value!r}")

    # 2. Money amounts can't be negative, and at least one of them must be
    #    positive - otherwise there's nothing to actually calculate.
    if starting_amount < 0 or starting_amount > 100_000_000_000:
        raise ValueError(f"starting_amount must be between 0 and 100 Billion, got {starting_amount}")
    if monthly_investment < 0 or monthly_investment > 100_000_000_000:
        raise ValueError(f"monthly_investment must be between 0 and 100 Billion, got {monthly_investment}")
    if starting_amount == 0 and monthly_investment == 0:
        raise ValueError(
            "At least one of starting_amount or monthly_investment must be "
            "greater than 0 - there's nothing to calculate otherwise"
        )

    if step_up_pct < 0 or step_up_pct > 5000:
        raise ValueError(f"step_up_pct must be between 0 and 5000, got {step_up_pct}")

    # 3. Duration must be positive and long enough to cover at least 1 month.
    #    We also cap it at 100 years to prevent Serverless loop exhaustion (DoS).
    if years <= 0 or years > 100:
        raise ValueError(f"years must be between > 0 and 100, got {years}")
    if round(years * 12) < 1:
        raise ValueError(f"years={years} is too short to produce even a single month of investment")

    # 4. Return and inflation can't imply losing more than 100% of value.
    #    We also cap it at 5000% to prevent Math Overflow errors.
    if annual_return_pct <= -100 or annual_return_pct > 5000:
        raise ValueError(
            f"annual_return_pct must be between -99 and 5000, got {annual_return_pct}"
        )
    if inflation_pct <= -100 or inflation_pct > 5000:
        raise ValueError(
            f"inflation_pct must be between -99 and 5000, got {inflation_pct}"
        )

    # 5. Fees and charges can't be negative.
    for name, value in [
        ("brokerage_pct", brokerage_pct),
        ("sst_pct_of_brokerage", sst_pct_of_brokerage),
        ("cdc_pct", cdc_pct),
        ("annual_flat_fee", annual_flat_fee),
    ]:
        if value < 0:
            raise ValueError(f"{name} cannot be negative, got {value}")

    # 6. Tax rates must be sensible percentages.
    for name, value in [
        ("cgt_filer_pct", cgt_filer_pct),
        ("cgt_nonfiler_pct", cgt_nonfiler_pct),
    ]:
        if value < 0 or value > 100:
            raise ValueError(f"{name} must be between 0 and 100, got {value}")


def _calculate_yearly_breakdown(
    starting_amount, monthly_investment, step_up_pct, years, annual_return_pct, inflation_pct,
    brokerage_pct, sst_pct_of_brokerage, cdc_pct, annual_flat_fee,
    cgt_filer_pct, cgt_nonfiler_pct
):
    yearly_breakdown = []
    
    months = round(years * 12)
    monthly_rate = (1 + annual_return_pct / 100) ** (1 / 12) - 1

    balance = 0.0
    total_contributed = 0.0
    cost_basis = 0.0
    current_monthly_investment = monthly_investment

    for month in range(1, months + 1):
        contribution = current_monthly_investment
        if month == 1:
            contribution += starting_amount

        brokerage_fee = contribution * (brokerage_pct / 100)
        sst_fee = brokerage_fee * (sst_pct_of_brokerage / 100)
        cdc_fee = contribution * (cdc_pct / 100)
        total_fee = brokerage_fee + sst_fee + cdc_fee
        net_invested = contribution - total_fee

        balance = (balance + net_invested) * (1 + monthly_rate)

        if month % 12 == 0:
            balance -= annual_flat_fee
            current_monthly_investment *= (1 + step_up_pct / 100)

        total_contributed += contribution
        cost_basis += net_invested

        if month % 12 == 0:
            current_year = month // 12
            gross_value = balance
            gain = max(0.0, gross_value - cost_basis)
            
            cgt = gain * (cgt_filer_pct / 100)
            net_value = gross_value - cgt
            
            inflation_factor = (1 + inflation_pct / 100) ** current_year
            real_value = net_value / inflation_factor
            
            yearly_breakdown.append({
                "year": current_year,
                "invested": total_contributed,
                "real_value": real_value
            })

    return yearly_breakdown


def calculate_sip(
    starting_amount,        # lump sum invested in month 1, alongside the SIP amount
    monthly_investment,     # rupees invested every month
    step_up_pct,            # annual percentage increase in monthly investment
    years,                  # how long the SIP runs
    annual_return_pct,      # your assumed KSE-100 annual return, e.g. 14 for 14%
    inflation_pct,          # your assumed annual inflation, e.g. 10 for 10%
    brokerage_pct=0.15,     # % fee per purchase
    sst_pct_of_brokerage=13.0,   # Sindh Sales Tax, charged on the brokerage fee itself
    cdc_pct=0.02,           # CDC handling fee, % of purchase amount
    annual_flat_fee=700.0,  # NCCPL + CDC account-keeping fee, once a year
    cgt_filer_pct=15.0,     # capital gains tax rate if you're a filer
    cgt_nonfiler_pct=30.0,  # capital gains tax rate if you're a non-filer
):
    _validate_inputs(
        starting_amount, monthly_investment, step_up_pct, years, annual_return_pct, inflation_pct,
        brokerage_pct, sst_pct_of_brokerage, cdc_pct, annual_flat_fee,
        cgt_filer_pct, cgt_nonfiler_pct,
    )

    months = round(years * 12)

    # Step A — annual rate to monthly rate (compounding-safe, not annual/12)
    monthly_rate = (1 + annual_return_pct / 100) ** (1 / 12) - 1

    balance = 0.0
    total_contributed = 0.0
    total_purchase_fees = 0.0
    cost_basis = 0.0
    current_monthly_investment = monthly_investment

    for month in range(1, months + 1):
        # Step B — this month's contribution, fees, net invested
        contribution = current_monthly_investment
        if month == 1:
            contribution += starting_amount

        brokerage_fee = contribution * (brokerage_pct / 100)
        sst_fee = brokerage_fee * (sst_pct_of_brokerage / 100)
        cdc_fee = contribution * (cdc_pct / 100)
        total_fee = brokerage_fee + sst_fee + cdc_fee
        net_invested = contribution - total_fee

        # Step C — add money in, then grow the whole balance together
        balance = (balance + net_invested) * (1 + monthly_rate)

        # Step D — once a year, subtract the flat account fee
        if month % 12 == 0:
            balance -= annual_flat_fee
            current_monthly_investment *= (1 + step_up_pct / 100)

        total_contributed += contribution
        total_purchase_fees += total_fee
        cost_basis += net_invested

    # Section 3 — exit calculations
    gross_value = balance
    gain = max(0.0, gross_value - cost_basis)

    cgt_filer = gain * (cgt_filer_pct / 100)
    cgt_nonfiler = gain * (cgt_nonfiler_pct / 100)

    net_value_filer = gross_value - cgt_filer
    net_value_nonfiler = gross_value - cgt_nonfiler

    inflation_factor = (1 + inflation_pct / 100) ** years
    real_value_filer = net_value_filer / inflation_factor
    real_value_nonfiler = net_value_nonfiler / inflation_factor

    yearly_breakdown = _calculate_yearly_breakdown(
        starting_amount, monthly_investment, step_up_pct, years, annual_return_pct, inflation_pct,
        brokerage_pct, sst_pct_of_brokerage, cdc_pct, annual_flat_fee,
        cgt_filer_pct, cgt_nonfiler_pct
    )

    return {
        "total_contributed": total_contributed,
        "total_purchase_fees": total_purchase_fees,
        "annual_fees_paid": annual_flat_fee * (months // 12),
        "cost_basis": cost_basis,
        "gross_value": gross_value,
        "gain": gain,
        "cgt_filer": cgt_filer,
        "cgt_nonfiler": cgt_nonfiler,
        "net_value_filer": net_value_filer,
        "net_value_nonfiler": net_value_nonfiler,
        "real_value_filer": real_value_filer,
        "real_value_nonfiler": real_value_nonfiler,
        "yearly_breakdown": yearly_breakdown,
    }


if __name__ == "__main__":
    # Worked example from planning doc section 5:
    # Rs 100,000 starting amount + Rs 20,000/month, 1 year, 14% return, 10% inflation
    result = calculate_sip(
        starting_amount=100000,
        monthly_investment=20000,
        step_up_pct=10.0,
        years=1,
        annual_return_pct=14,
        inflation_pct=10,
    )
    for key, value in result.items():
        if key == "yearly_breakdown":
            print(f"yearly_breakdown       = {len(value)} years calculated")
        else:
            print(f"{key:22s} = {value:,.2f}")

