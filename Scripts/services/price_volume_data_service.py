"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : price_volume_data_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
Description     : Extracts sales price and volume data from the General Ledger.
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal

from accounting.general_ledger_engine import GeneralLedgerEngine


class PriceVolumeDataService:
    """
    Extracts sales price and volume information from General Ledger entries.

    The service uses sales revenue journal lines as the source of truth.

    Required journal-line attributes:
        - account_number
        - material_code
        - quantity
        - unit_price
        - credit_amount
        - posting date through JournalEntry.document
    """

    REVENUE_ACCOUNT = "602"

    @staticmethod
    def _is_sales_line(line) -> bool:
        """
        Return True when the journal line represents sales revenue.
        """

        return (
            line.account_number
            == PriceVolumeDataService.REVENUE_ACCOUNT
            and line.credit_amount > Decimal("0")
            and line.material_code is not None
            and line.quantity is not None
            and line.unit_price is not None
        )

    @staticmethod
    def _period_key(posting_date: date) -> int:
        """
        Return fiscal year used for period comparison.
        """

        return posting_date.year

    @staticmethod
    def extract(
        general_ledger: GeneralLedgerEngine,
    ) -> dict[int, dict[str, dict[str, Decimal]]]:
        """
        Extract sales data grouped by year and material.

        Result structure:

        {
            year: {
                material_code: {
                    "quantity": Decimal(...),
                    "revenue": Decimal(...),
                    "weighted_price": Decimal(...),
                }
            }
        }
        """

        aggregated: dict[
            int,
            dict[str, dict[str, Decimal]]
        ] = defaultdict(
            lambda: defaultdict(
                lambda: {
                    "quantity": Decimal("0"),
                    "revenue": Decimal("0"),
                    "weighted_price": Decimal("0"),
                }
            )
        )

        for entry in general_ledger.entries:

            posting_date = entry.document.posting_date
            year = PriceVolumeDataService._period_key(
                posting_date
            )

            for line in entry.lines:

                if not PriceVolumeDataService._is_sales_line(
                    line
                ):
                    continue

                material_code = line.material_code

                if material_code is None:
                    continue

                quantity = line.quantity
                unit_price = line.unit_price

                if quantity is None or unit_price is None:
                    continue

                revenue = (
                    quantity * unit_price
                )

                aggregated[year][material_code][
                    "quantity"
                ] += quantity

                aggregated[year][material_code][
                    "revenue"
                ] += revenue

        for year_data in aggregated.values():

            for material_data in year_data.values():

                quantity = material_data["quantity"]
                revenue = material_data["revenue"]

                if quantity != Decimal("0"):
                    material_data["weighted_price"] = (
                        revenue / quantity
                    )

        return dict(aggregated)

    @staticmethod
    def get_available_years(
        general_ledger: GeneralLedgerEngine,
    ) -> list[int]:
        """
        Return sorted fiscal years containing sales data.
        """

        data = PriceVolumeDataService.extract(
            general_ledger
        )

        return sorted(data.keys())

    @staticmethod
    def get_comparison_periods(
        general_ledger: GeneralLedgerEngine,
    ) -> tuple[int, int]:
        """
        Return previous and current available sales years.

        The latest available year is treated as the current
        period and the immediately preceding available year
        as the comparison period.
        """

        years = PriceVolumeDataService.get_available_years(
            general_ledger
        )

        if len(years) < 2:
            raise ValueError(
                "At least two fiscal years of sales data "
                "are required for Price × Volume analysis."
            )

        previous_year = years[-2]
        current_year = years[-1]

        return previous_year, current_year

    @staticmethod
    def prepare_comparison_data(
        general_ledger: GeneralLedgerEngine,
    ) -> list[dict[str, Decimal | str | int]]:
        """
        Prepare material-level data for Price × Volume analysis.

        Only materials existing in both comparison periods
        are included.
        """

        data = PriceVolumeDataService.extract(
            general_ledger
        )

        previous_year, current_year = (
            PriceVolumeDataService.get_comparison_periods(
                general_ledger
            )
        )

        previous_data = data[previous_year]
        current_data = data[current_year]

        materials = sorted(
            set(previous_data)
            & set(current_data)
        )

        result = []

        for material_code in materials:

            previous = previous_data[material_code]
            current = current_data[material_code]

            result.append(
                {
                    "previous_year": previous_year,
                    "current_year": current_year,
                    "material_code": material_code,

                    "previous_price": previous[
                        "weighted_price"
                    ],

                    "current_price": current[
                        "weighted_price"
                    ],

                    "previous_volume": previous[
                        "quantity"
                    ],

                    "current_volume": current[
                        "quantity"
                    ],
                }
            )

        return result