"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : scenario_router.py
Object Type     : Scenario Router
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Routes business events to accounting scenarios.
===============================================================================
"""


from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from domain.business_event import BusinessEvent
from domain.business_event_type import BusinessEventType

from decimal import Decimal

from scenarios.sales_invoice import (
    SalesInvoiceRequest,
    SalesInvoiceScenario,
)

from scenarios.purchase_invoice import (
    PurchaseInvoiceRequest,
    PurchaseInvoiceScenario,
)

from scenarios.customer_payment import (
    CustomerPaymentRequest,
    CustomerPaymentScenario,
)

from scenarios.supplier_payment import (
    SupplierPaymentRequest,
    SupplierPaymentScenario,
)

from scenarios.assets.asset_acquisition import (
    AssetAcquisitionRequest,
    AssetAcquisitionScenario,
)

from scenarios.assets.asset_capitalization import (
    AssetCapitalizationRequest,
    AssetCapitalizationScenario,
)

from scenarios.assets.asset_depreciation import (
    AssetDepreciationRequest,
    AssetDepreciationScenario,
)

from scenarios.assets.asset_impairment import (
    AssetImpairmentRequest,
    AssetImpairmentScenario,
)

from scenarios.assets.asset_disposal import (
    AssetDisposalRequest,
    AssetDisposalScenario,
)

from scenarios.assets.asset_sale import (
    AssetSaleRequest,
    AssetSaleScenario,
)

from scenarios.assets.asset_transfer import (
    AssetTransferRequest,
    AssetTransferScenario,
)

from scenarios.inventory.inventory_receipt import (
    InventoryReceiptRequest,
    InventoryReceiptScenario,
)

from scenarios.inventory.inventory_issue import (
    InventoryIssueRequest,
    InventoryIssueScenario,
)

from scenarios.inventory.inventory_transfer import (
    InventoryTransferRequest,
    InventoryTransferScenario,
)

from scenarios.inventory.inventory_adjustment import (
    InventoryAdjustmentRequest,
    InventoryAdjustmentScenario,
)

from scenarios.payroll.payroll_expense import PayrollExpenseScenario
from scenarios.payroll.employer_contribution import EmployerContributionScenario
from scenarios.payroll.payroll_tax import PayrollTaxScenario
from scenarios.payroll.payroll_payment import PayrollPaymentScenario

from scenarios.payroll.payroll_expense import (
    PayrollExpenseRequest,
)

from scenarios.payroll.employer_contribution import (
    EmployerContributionRequest,
)

from scenarios.payroll.payroll_tax import (
    PayrollTaxRequest,
)

from scenarios.payroll.payroll_payment import (
    PayrollPaymentRequest,
)
from scenarios.banking.bank_fee import BankFeeScenario
from scenarios.banking.interest_income import InterestIncomeScenario
from scenarios.banking.interest_expense import InterestExpenseScenario
from scenarios.banking.fx_gain import FXGainScenario
from scenarios.banking.fx_loss import FXLossScenario
from scenarios.banking.loan_drawdown import LoanDrawdownScenario
from scenarios.banking.loan_repayment import LoanRepaymentScenario
from scenarios.banking.cash_deposit import CashDepositScenario
from scenarios.banking.cash_withdrawal import CashWithdrawalScenario
from scenarios.banking.internal_transfer import InternalTransferScenario
from scenarios.banking.bank_fee import BankFeeRequest
from scenarios.banking.interest_income import InterestIncomeRequest
from scenarios.banking.interest_expense import InterestExpenseRequest
from scenarios.banking.fx_gain import FXGainRequest
from scenarios.banking.fx_loss import FXLossRequest
from scenarios.banking.loan_drawdown import LoanDrawdownRequest
from scenarios.banking.loan_repayment import LoanRepaymentRequest
from scenarios.banking.cash_deposit import CashDepositRequest
from scenarios.banking.cash_withdrawal import CashWithdrawalRequest
from scenarios.banking.internal_transfer import InternalTransferRequest



class ScenarioRouter:
    """
    Converts BusinessEvents into JournalEntries.
    """

    def __init__(
        self,
        sales_scenario: SalesInvoiceScenario,
        purchase_scenario: PurchaseInvoiceScenario,
        customer_payment_scenario: CustomerPaymentScenario,
        supplier_payment_scenario: SupplierPaymentScenario,
        asset_acquisition_scenario: AssetAcquisitionScenario,
        asset_capitalization_scenario: AssetCapitalizationScenario,
        asset_depreciation_scenario: AssetDepreciationScenario,
        asset_impairment_scenario: AssetImpairmentScenario,
        asset_disposal_scenario: AssetDisposalScenario,
        asset_sale_scenario: AssetSaleScenario,
        asset_transfer_scenario: AssetTransferScenario,
        inventory_receipt_scenario: InventoryReceiptScenario,
        inventory_issue_scenario: InventoryIssueScenario,
        inventory_transfer_scenario: InventoryTransferScenario,
        inventory_adjustment_scenario: InventoryAdjustmentScenario,
        payroll_expense_scenario: PayrollExpenseScenario,
        employer_contribution_scenario: EmployerContributionScenario,
        payroll_tax_scenario: PayrollTaxScenario,
        payroll_payment_scenario: PayrollPaymentScenario,
        bank_fee_scenario: BankFeeScenario,
        interest_income_scenario: InterestIncomeScenario,
        interest_expense_scenario: InterestExpenseScenario,
        fx_gain_scenario: FXGainScenario,
        fx_loss_scenario: FXLossScenario,
        loan_drawdown_scenario: LoanDrawdownScenario,
        loan_repayment_scenario: LoanRepaymentScenario,
        cash_deposit_scenario: CashDepositScenario,
        cash_withdrawal_scenario: CashWithdrawalScenario,
        internal_transfer_scenario: InternalTransferScenario,

    ) -> None:

        self.sales_scenario = sales_scenario
        self.purchase_scenario = purchase_scenario
        self.customer_payment_scenario = customer_payment_scenario
        self.supplier_payment_scenario = supplier_payment_scenario
        self.asset_acquisition_scenario = asset_acquisition_scenario
        self.asset_capitalization_scenario = asset_capitalization_scenario
        self.asset_depreciation_scenario = asset_depreciation_scenario
        self.asset_impairment_scenario = asset_impairment_scenario
        self.asset_disposal_scenario = asset_disposal_scenario
        self.asset_sale_scenario = asset_sale_scenario
        self.asset_transfer_scenario = asset_transfer_scenario
        self.inventory_receipt_scenario = inventory_receipt_scenario
        self.inventory_issue_scenario = inventory_issue_scenario
        self.inventory_transfer_scenario = inventory_transfer_scenario
        self.inventory_adjustment_scenario = inventory_adjustment_scenario
        self.payroll_expense_scenario = payroll_expense_scenario
        self.employer_contribution_scenario = employer_contribution_scenario
        self.payroll_tax_scenario = payroll_tax_scenario
        self.payroll_payment_scenario = payroll_payment_scenario

        self.bank_fee_scenario = bank_fee_scenario
        self.interest_income_scenario = interest_income_scenario
        self.interest_expense_scenario = interest_expense_scenario
        self.fx_gain_scenario = fx_gain_scenario
        self.fx_loss_scenario = fx_loss_scenario
        self.loan_drawdown_scenario = loan_drawdown_scenario
        self.loan_repayment_scenario = loan_repayment_scenario
        self.cash_deposit_scenario = cash_deposit_scenario
        self.cash_withdrawal_scenario = cash_withdrawal_scenario
        self.internal_transfer_scenario = internal_transfer_scenario

    def process(
        self,
        event: BusinessEvent,
    ):

        match event.event_type:

            case BusinessEventType.SALES_INVOICE:

                request = SalesInvoiceRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    invoice_date=event.event_date,
                    due_date=event.due_date,
                    net_amount=event.amount,
                    vat_rate=event.vat_rate,
                    description=event.description,
                    customer_code=event.customer_code,
                )

                return self.sales_scenario.create(request)

            case BusinessEventType.PURCHASE_INVOICE:
                request = PurchaseInvoiceRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    invoice_date=event.event_date,
                    due_date=event.due_date,
                    net_amount=event.amount,
                    vat_rate=event.vat_rate,
                    description=event.description,
                    supplier_code=event.supplier_code,
                )
                return self.purchase_scenario.create(request)

            case BusinessEventType.CUSTOMER_PAYMENT:

                request = CustomerPaymentRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    payment_date=event.event_date,
                    payment_amount=event.amount,
                    description=event.description,
                    customer_code=event.customer_code,
                )

                return self.customer_payment_scenario.create(request)

            case BusinessEventType.SUPPLIER_PAYMENT:
                request = SupplierPaymentRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    supplier_code=event.supplier_code,
                    payment_date=event.event_date,
                    payment_amount=event.amount,
                    description=event.description,
                )

                return self.supplier_payment_scenario.create(request)

            case BusinessEventType.ASSET_ACQUISITION:

                request = AssetAcquisitionRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.asset_acquisition_scenario.create(request)

            case BusinessEventType.ASSET_CAPITALIZATION:

                request = AssetCapitalizationRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.asset_capitalization_scenario.create(request)

            case BusinessEventType.ASSET_DEPRECIATION:

                request = AssetDepreciationRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    depreciation_date=event.event_date,
                    depreciation_amount=event.amount,
                )

                return self.asset_depreciation_scenario.create(request)

            case BusinessEventType.ASSET_IMPAIRMENT:

                request = AssetImpairmentRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    impairment_date=event.event_date,
                    impairment_amount=event.amount,
                )

                return self.asset_impairment_scenario.create(request)

            case BusinessEventType.ASSET_DISPOSAL:

                request = AssetDisposalRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    disposal_date=event.event_date,
                    net_book_value=event.amount,
                )

                return self.asset_disposal_scenario.create(request)

            case BusinessEventType.ASSET_SALE:

                request = AssetSaleRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    sale_date=event.event_date,
                    sale_amount=event.amount,
                    customer_code=event.customer_code,
                )

                return self.asset_sale_scenario.create(request)

            case BusinessEventType.ASSET_TRANSFER:

                request = AssetTransferRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    transfer_date=event.event_date,
                    asset_value=event.amount,
                    from_cost_center_code=event.cost_center_code,
                    from_department_code=event.department_code,
                    to_cost_center_code=event.cost_center_code,
                    to_department_code=event.department_code,
                )

                return self.asset_transfer_scenario.create(request)

            
            case BusinessEventType.INVENTORY_RECEIPT:

                request = InventoryReceiptRequest(
                company_code=event.company_code,
                cost_center_code=event.cost_center_code,
                department_code=event.department_code,
                currency_code=event.currency_code,

                material_code=event.material_code,
                material_name=event.material_name,

                warehouse_code=event.warehouse_code,
                storage_location=event.storage_location,

                receipt_date=event.event_date,

                quantity=event.quantity,
                unit_price=event.unit_price,
                total_amount=event.amount,

                supplier_code=event.supplier_code,
                description=event.description,
            )

                return self.inventory_receipt_scenario.create(request)


            case BusinessEventType.INVENTORY_ISSUE:

                request = InventoryIssueRequest(
                    company_code=event.company_code,
                    inventory_code=event.inventory_code,
                    material_code=event.material_code,
                    material_name=event.material_name,
                    event_date=event.event_date,
                    quantity=event.quantity,
                    unit_cost=event.unit_cost,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    description=event.description,
                )

                return self.inventory_issue_scenario.create(request)

            case BusinessEventType.INVENTORY_TRANSFER:

                request = InventoryTransferRequest(
                    company_code=event.company_code,
                    inventory_code=event.inventory_code,
                    material_code=event.material_code,
                    material_name=event.material_name,
                    event_date=event.event_date,
                    quantity=event.quantity,
                    unit_cost=event.unit_cost,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    from_cost_center_code=event.from_cost_center_code,
                    from_department_code=event.from_department_code,
                    to_cost_center_code=event.to_cost_center_code,
                    to_department_code=event.to_department_code,
                    description=event.description,
                )

                return self.inventory_transfer_scenario.create(request)

            case BusinessEventType.INVENTORY_ADJUSTMENT:

                request = InventoryAdjustmentRequest(
                    company_code=event.company_code,
                    inventory_code=event.inventory_code,
                    material_code=event.material_code,
                    material_name=event.material_name,
                    event_date=event.event_date,
                    quantity=event.quantity,
                    unit_cost=event.unit_cost,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    description=event.description,
                )

                return self.inventory_adjustment_scenario.create(request)


            case BusinessEventType.PAYROLL_EXPENSE:

                return self.payroll_expense_scenario.create(
                    PayrollExpenseRequest(
                        company_code=event.company_code,
                        employee_code=event.employee_code,
                        payroll_date=event.payroll_date or event.event_date,
                        gross_salary=event.gross_salary,
                        currency_code=event.currency_code,
                        cost_center_code=event.cost_center_code,
                        department_code=event.department_code,
                    )
                )


            case BusinessEventType.EMPLOYER_CONTRIBUTION:

                return self.employer_contribution_scenario.create(
                    EmployerContributionRequest(
                        company_code=event.company_code,
                        employee_code=event.employee_code,
                        payroll_date=event.payroll_date or event.event_date,
                        contribution_amount=event.employer_contribution,
                        currency_code=event.currency_code,
                        cost_center_code=event.cost_center_code,
                        department_code=event.department_code,
                    )
                )


            case BusinessEventType.PAYROLL_TAX:

                return self.payroll_tax_scenario.create(
                    PayrollTaxRequest(
                        company_code=event.company_code,
                        employee_code=event.employee_code,
                        payroll_date=event.payroll_date or event.event_date,
                        tax_amount=event.employee_tax,
                        currency_code=event.currency_code,
                        cost_center_code=event.cost_center_code,
                        department_code=event.department_code,
                    )
                )


            case BusinessEventType.PAYROLL_PAYMENT:

                    request = PayrollPaymentRequest(
                        company_code=event.company_code,
                        employee_code=event.employee_code,
                        payment_date=event.event_date,

                        payment_amount=(
                            event.gross_salary
                            - event.employee_tax
                            + event.bonus_amount
                            + event.overtime_amount
                        ),

                        currency_code=event.currency_code,
                        cost_center_code=event.cost_center_code,
                        department_code=event.department_code,
                    )

                    return self.payroll_payment_scenario.create(request)

            case BusinessEventType.BANK_FEE:

                request = BankFeeRequest(
                    company_code=event.company_code,
                    bank_account=event.bank_account,
                    transaction_date=event.event_date,
                    amount=event.amount,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.bank_fee_scenario.create(request)


            case BusinessEventType.INTEREST_INCOME:

                request = InterestIncomeRequest(
                    company_code=event.company_code,
                    bank_account=event.bank_account,
                    transaction_date=event.event_date,
                    amount=event.amount,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.interest_income_scenario.create(request)


            case BusinessEventType.INTEREST_EXPENSE:

                request = InterestExpenseRequest(
                    company_code=event.company_code,
                    bank_account=event.bank_account,
                    transaction_date=event.event_date,
                    amount=event.amount,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.interest_expense_scenario.create(request)


            case BusinessEventType.FX_GAIN:

                request = FXGainRequest(
                    company_code=event.company_code,
                    bank_account=event.bank_account,
                    transaction_date=event.event_date,
                    amount=event.amount,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.fx_gain_scenario.create(request)


            case BusinessEventType.FX_LOSS:

                request = FXLossRequest(
                    company_code=event.company_code,
                    bank_account=event.bank_account,
                    transaction_date=event.event_date,
                    amount=event.amount,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.fx_loss_scenario.create(request)

            case BusinessEventType.LOAN_DRAWDOWN:

                request = LoanDrawdownRequest(
                    company_code=event.company_code,
                    bank_account=event.bank_account,
                    transaction_date=event.event_date,
                    amount=event.amount,
                    loan_term=event.loan_term,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.loan_drawdown_scenario.create(request)


            case BusinessEventType.LOAN_REPAYMENT:

                request = LoanRepaymentRequest(
                    company_code=event.company_code,
                    bank_account=event.bank_account,
                    transaction_date=event.event_date,
                    amount=event.amount,
                    loan_term=event.loan_term,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.loan_repayment_scenario.create(request)


            case BusinessEventType.CASH_DEPOSIT:

                request = CashDepositRequest(
                    company_code=event.company_code,
                    bank_account=event.bank_account,
                    transaction_date=event.event_date,
                    amount=event.amount,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.cash_deposit_scenario.create(request)


            case BusinessEventType.CASH_WITHDRAWAL:

                request = CashWithdrawalRequest(
                    company_code=event.company_code,
                    bank_account=event.bank_account,
                    transaction_date=event.event_date,
                    amount=event.amount,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.cash_withdrawal_scenario.create(request)


            case BusinessEventType.INTERNAL_TRANSFER:

                request = InternalTransferRequest(
                    company_code=event.company_code,
                    source_bank_account=event.source_bank_account,
                    target_bank_account=event.target_bank_account,
                    transaction_date=event.event_date,
                    amount=event.amount,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.internal_transfer_scenario.create(request)


            case _:

                raise NotImplementedError(
                    f"Unsupported event: {event.event_type}"
                )
    