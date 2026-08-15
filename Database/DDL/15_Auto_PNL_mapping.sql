INSERT INTO
    warehouse.dim_pnl_mapping (
        account_key,
        pnl_section,
        pnl_category,
        pnl_subcategory,
        display_order,
        is_revenue,
        is_operating_cost,
        is_financial_item,
        is_tax,
        is_ebitda_item
    )
SELECT
    a.account_key,
    CASE
        WHEN a.account_number IN ('601', '602', '604') THEN 'Revenue'
        WHEN a.account_number = '641' THEN 'Other Operating Income'
        WHEN a.account_number IN (
            '501',
            '502',
            '504',
            '511',
            '518',
            '521',
            '524',
            '548',
            '549',
            '582'
        ) THEN 'Operating Costs'
        WHEN a.account_number IN ('541') THEN 'Non-Core Operating Items'
        WHEN a.account_number IN ('551', '554', '558') THEN 'EBITDA Adjustments'
        WHEN a.account_number IN ('562', '563', '568') THEN 'Financial Result'
        WHEN a.account_number IN ('662', '663') THEN 'Financial Result'
        WHEN a.account_number IN ('591', '592') THEN 'Tax'
        ELSE 'Unmapped'
    END,
    CASE
        WHEN a.account_number IN ('601', '602', '604') THEN 'Sales Revenue'
        WHEN a.account_number = '641' THEN 'Fixed Asset Disposal'
        WHEN a.account_number = '501' THEN 'Materials'
        WHEN a.account_number = '502' THEN 'Energy'
        WHEN a.account_number = '504' THEN 'Cost of Goods Sold'
        WHEN a.account_number = '511' THEN 'Repairs & Maintenance'
        WHEN a.account_number = '518' THEN 'Services'
        WHEN a.account_number IN ('521', '524') THEN 'Personnel Costs'
        WHEN a.account_number = '541' THEN 'Fixed Asset Disposal Costs'
        WHEN a.account_number IN ('548', '549') THEN 'Other Operating Costs'
        WHEN a.account_number = '551' THEN 'Depreciation'
        WHEN a.account_number IN ('554', '558') THEN 'Provisions'
        WHEN a.account_number = '582' THEN 'Inventory Change'
        WHEN a.account_number = '662' THEN 'Interest Income'
        WHEN a.account_number = '663' THEN 'FX Gains'
        WHEN a.account_number = '562' THEN 'Interest Expense'
        WHEN a.account_number = '563' THEN 'FX Losses'
        WHEN a.account_number = '568' THEN 'Other Financial Expenses'
        WHEN a.account_number IN ('591', '592') THEN 'Income Tax'
        ELSE 'Unmapped'
    END,
    NULL,
    CASE
        WHEN a.account_number IN ('601', '602', '604') THEN 10
        WHEN a.account_number = '641' THEN 20
        WHEN a.account_number = '501' THEN 30
        WHEN a.account_number = '502' THEN 31
        WHEN a.account_number = '504' THEN 32
        WHEN a.account_number = '511' THEN 33
        WHEN a.account_number = '518' THEN 34
        WHEN a.account_number IN ('521', '524') THEN 35
        WHEN a.account_number IN ('548', '549') THEN 36
        WHEN a.account_number = '582' THEN 37
        WHEN a.account_number = '541' THEN 40
        WHEN a.account_number = '551' THEN 50
        WHEN a.account_number IN ('554', '558') THEN 51
        WHEN a.account_number IN ('662', '663') THEN 60
        WHEN a.account_number IN ('562', '563', '568') THEN 61
        WHEN a.account_number IN ('591', '592') THEN 70
        ELSE 999
    END,
    a.account_number IN ('601', '602', '604'),
    a.account_number IN (
        '501',
        '502',
        '504',
        '511',
        '518',
        '521',
        '524',
        '548',
        '549',
        '582'
    ),
    a.account_number IN ('562', '563', '568', '662', '663'),
    a.account_number IN ('591', '592'),
    a.account_number IN (
        '501',
        '502',
        '504',
        '511',
        '518',
        '521',
        '524',
        '548',
        '549',
        '582'
    )
FROM
    warehouse.dim_account a
WHERE
    a.account_number IN (
        '501',
        '502',
        '504',
        '511',
        '518',
        '521',
        '524',
        '541',
        '548',
        '549',
        '551',
        '554',
        '558',
        '582',
        '591',
        '592',
        '601',
        '602',
        '604',
        '641',
        '562',
        '563',
        '568',
        '662',
        '663'
    )
ON CONFLICT (account_key) DO UPDATE
SET
    pnl_section = EXCLUDED.pnl_section,
    pnl_category = EXCLUDED.pnl_category,
    pnl_subcategory = EXCLUDED.pnl_subcategory,
    display_order = EXCLUDED.display_order,
    is_revenue = EXCLUDED.is_revenue,
    is_operating_cost = EXCLUDED.is_operating_cost,
    is_financial_item = EXCLUDED.is_financial_item,
    is_tax = EXCLUDED.is_tax,
    is_ebitda_item = EXCLUDED.is_ebitda_item;