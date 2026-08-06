def assert_trial_balance_balanced(tb):

    assert tb.total_debit == tb.total_credit

def assert_balance_sheet_balanced(bs):

    assert (
        bs.assets
        ==
        bs.liabilities
        +
        bs.equity
    )

def assert_variances_exist(report):

    assert len(report.variances) > 0