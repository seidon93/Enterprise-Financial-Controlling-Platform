from Scripts.budget.budget_version import BudgetVersion


def test_budget_versions():

    assert BudgetVersion.ORIGINAL.value == "Original Budget"

    assert BudgetVersion.ACTUAL.value == "Actual"