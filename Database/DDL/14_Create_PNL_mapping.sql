CREATE TABLE IF NOT EXISTS warehouse.dim_pnl_mapping (
    account_key integer PRIMARY KEY,
    pnl_section varchar(50) NOT NULL,
    pnl_category varchar(100) NOT NULL,
    pnl_subcategory varchar(100),
    display_order integer NOT NULL,
    is_revenue boolean NOT NULL DEFAULT false,
    is_operating_cost boolean NOT NULL DEFAULT false,
    is_financial_item boolean NOT NULL DEFAULT false,
    is_tax boolean NOT NULL DEFAULT false,
    is_ebitda_item boolean NOT NULL DEFAULT false,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);