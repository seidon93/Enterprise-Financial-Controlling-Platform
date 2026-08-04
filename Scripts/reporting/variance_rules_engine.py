"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : variance_rules_engine.py
Object Type     : Variance Rules Engine
Layer           : Reporting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Evaluates whether a variance is favorable or unfavorable.
===============================================================================
"""

from __future__ import annotations

from decimal import Decimal

from Scripts.domain.variance_rule import VarianceRule


class VarianceRulesEngine:

    @staticmethod
    def is_favorable(
        rule: VarianceRule,
        variance: Decimal,
    ) -> bool:

        if rule.favorable_if_higher:
            return variance >= Decimal("0")

        return variance <= Decimal("0")