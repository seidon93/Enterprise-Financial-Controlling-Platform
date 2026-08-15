CREATE TABLE IF NOT EXISTS mart.dim_pnl_management_mapping (
    account_number integer PRIMARY KEY,
    management_line varchar(100) NOT NULL,
    management_group varchar(100) NOT NULL,
    management_sign integer NOT NULL DEFAULT 1,
    ebitda_included boolean NOT NULL DEFAULT false,
    sort_order integer NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO
    mart.dim_pnl_management_mapping (
        account_number,
        management_line,
        management_group,
        management_sign,
        ebitda_included,
        sort_order
    )
VALUES
    -- =========================================================
    -- REVENUE
    -- =========================================================
    (601, 'Sales Revenue', 'Revenue', 1, true, 10),
    (602, 'Sales Revenue', 'Revenue', 1, true, 10),
    (604, 'Sales Revenue', 'Revenue', 1, true, 10),
    -- =========================================================
    -- OTHER OPERATING INCOME
    -- =========================================================
    (
        641,
        'Other Operating Income',
        'Other Operating Income',
        1,
        true,
        20
    ),
    -- =========================================================
    -- OPERATING COSTS
    -- =========================================================
    (
        501,
        'Material Consumption',
        'Operating Costs',
        -1,
        true,
        30
    ),
    (
        502,
        'Energy Consumption',
        'Operating Costs',
        -1,
        true,
        31
    ),
    (
        504,
        'Cost of Goods Sold',
        'Operating Costs',
        -1,
        true,
        32
    ),
    (
        511,
        'Repairs & Maintenance',
        'Operating Costs',
        -1,
        true,
        33
    ),
    (
        518,
        'Other Services',
        'Operating Costs',
        -1,
        true,
        34
    ),
    (
        521,
        'Payroll Costs',
        'Operating Costs',
        -1,
        true,
        35
    ),
    (
        524,
        'Social & Health Insurance',
        'Operating Costs',
        -1,
        true,
        35
    ),
    (
        548,
        'Other Operating Costs',
        'Operating Costs',
        -1,
        true,
        36
    ),
    (
        549,
        'Shortages & Damages',
        'Operating Costs',
        -1,
        true,
        36
    ),
    (
        582,
        'Inventory Change',
        'Operating Costs',
        -1,
        true,
        37
    ),
    -- =========================================================
    -- NON-CORE OPERATING ITEMS
    -- =========================================================
    (
        541,
        'Fixed Asset Disposal Costs',
        'Non-Core Operating Items',
        -1,
        true,
        40
    ),
    -- =========================================================
    -- EBITDA ADJUSTMENTS
    -- =========================================================
    (
        551,
        'Depreciation',
        'EBITDA Adjustments',
        -1,
        false,
        50
    ),
    (
        554,
        'Provisions',
        'EBITDA Adjustments',
        -1,
        false,
        51
    ),
    (
        558,
        'Provisions',
        'EBITDA Adjustments',
        -1,
        false,
        51
    ),
    -- =========================================================
    -- FINANCIAL RESULT
    -- =========================================================
    (
        562,
        'Interest Expense',
        'Financial Result',
        -1,
        false,
        61
    ),
    (
        563,
        'FX Losses',
        'Financial Result',
        -1,
        false,
        61
    ),
    (
        568,
        'Other Financial Expenses',
        'Financial Result',
        -1,
        false,
        61
    ),
    (
        662,
        'Interest Income',
        'Financial Result',
        1,
        false,
        60
    ),
    (663, 'FX Gains', 'Financial Result', 1, false, 60),
    -- =========================================================
    -- TAX
    -- =========================================================
    (591, 'Income Tax', 'Tax', -1, false, 70),
    (592, 'Income Tax', 'Tax', -1, false, 70),
    -- =========================================================
    -- CLOSING / TECHNICAL ACCOUNTS
    -- =========================================================
    (
        701,
        'Opening Balance Sheet Account',
        'Closing Accounts',
        1,
        false,
        90
    ),
    (
        702,
        'Closing Balance Sheet Account',
        'Closing Accounts',
        1,
        false,
        90
    ),
    (
        710,
        'Profit and Loss Account',
        'Closing Accounts',
        1,
        false,
        90
    )
ON CONFLICT (account_number) DO UPDATE
SET
    management_line = EXCLUDED.management_line,
    management_group = EXCLUDED.management_group,
    management_sign = EXCLUDED.management_sign,
    ebitda_included = EXCLUDED.ebitda_included,
    sort_order = EXCLUDED.sort_order,
    is_active = EXCLUDED.is_active;