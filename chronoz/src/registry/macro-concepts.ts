/**
 * CHronoZ Canonical Macro Concept Registry
 *
 * Version: v0.1
 *
 * Purpose:
 * - Provide a controlled economic vocabulary for semantic encoding.
 * - Prevent the LLM from inventing arbitrary macro concepts.
 * - Keep semantic concepts separate from measurement series.
 *
 * IMPORTANT:
 * This is an experimental taxonomy.
 *
 * It does NOT define:
 * - FRED/BPS/BI series
 * - transformations
 * - benchmark methodology
 * - statistical state
 * - causal relationships
 * - market signals
 */

export const CANONICAL_MACRO_CONCEPTS = {

    // ============================================================
    // GROWTH & ECONOMIC ACTIVITY
    // ============================================================

    real_activity: {
        channel: "growth",
        horizon: "cyclical",
        description:
            "Broad real economic activity or aggregate output conditions.",
        examples: [
            "economic activity",
            "real economic activity",
            "aggregate output"
        ]
    },

    industrial_activity: {
        channel: "growth",
        horizon: "cyclical",
        description:
            "Industrial production and broad industrial-sector activity.",
        examples: [
            "industrial production",
            "factory output",
            "industrial activity"
        ]
    },

    manufacturing_activity: {
        channel: "growth",
        horizon: "cyclical",
        description:
            "Activity specifically associated with manufacturing production.",
        examples: [
            "manufacturing output",
            "factory activity",
            "manufacturing PMI"
        ]
    },

    services_activity: {
        channel: "growth",
        horizon: "cyclical",
        description:
            "Economic activity in services-producing sectors.",
        examples: [
            "services activity",
            "service-sector output",
            "services PMI"
        ]
    },

    consumer_activity: {
        channel: "growth",
        horizon: "cyclical",
        description:
            "Household consumption and consumer spending activity.",
        examples: [
            "consumer spending",
            "retail activity",
            "household consumption"
        ]
    },

    investment_activity: {
        channel: "growth",
        horizon: "cyclical",
        description:
            "Business and economy-wide investment or capital expenditure activity.",
        examples: [
            "business investment",
            "capital expenditure",
            "capex"
        ]
    },

    housing_activity: {
        channel: "growth",
        horizon: "cyclical",
        description:
            "Residential construction, housing transactions, and housing-market activity.",
        examples: [
            "housing starts",
            "home sales",
            "residential construction"
        ]
    },


    // ============================================================
    // INFLATION & PRICES
    // ============================================================

    headline_inflation: {
        channel: "inflation",
        horizon: "cyclical",
        description:
            "Broad consumer price inflation.",
        examples: [
            "headline CPI",
            "consumer price inflation",
            "headline inflation"
        ]
    },

    core_inflation: {
        channel: "inflation",
        horizon: "cyclical",
        description:
            "Underlying consumer price inflation excluding specified volatile components.",
        examples: [
            "core CPI",
            "core inflation"
        ]
    },

    goods_inflation: {
        channel: "inflation",
        horizon: "cyclical",
        description:
            "Inflation in goods prices.",
        examples: [
            "goods inflation",
            "goods prices"
        ]
    },

    services_inflation: {
        channel: "inflation",
        horizon: "cyclical",
        description:
            "Inflation in services prices.",
        examples: [
            "services inflation",
            "service prices"
        ]
    },

    wage_inflation: {
        channel: "inflation",
        horizon: "cyclical",
        description:
            "Growth in wages or labor compensation relevant to inflation pressure.",
        examples: [
            "wage inflation",
            "wage pressure",
            "compensation growth"
        ]
    },

    inflation_expectations: {
        channel: "inflation",
        horizon: "cyclical",
        description:
            "Expectations regarding future inflation.",
        examples: [
            "inflation expectations",
            "expected inflation"
        ]
    },

    producer_prices: {
        channel: "inflation",
        horizon: "cyclical",
        description:
            "Prices received by producers or upstream input-price conditions.",
        examples: [
            "PPI",
            "producer prices",
            "input prices"
        ]
    },


    // ============================================================
    // LABOR & INCOME
    // ============================================================

    employment: {
        channel: "labor",
        horizon: "cyclical",
        description:
            "Employment levels or employment growth.",
        examples: [
            "employment",
            "payrolls",
            "jobs"
        ]
    },

    unemployment: {
        channel: "labor",
        horizon: "cyclical",
        description:
            "Unemployment conditions in the labor market.",
        examples: [
            "unemployment",
            "joblessness",
            "unemployment rate"
        ]
    },

    labor_demand: {
        channel: "labor",
        horizon: "cyclical",
        description:
            "Employer demand for labor and hiring intensity.",
        examples: [
            "labor demand",
            "job openings",
            "hiring demand"
        ]
    },

    labor_supply: {
        channel: "labor",
        horizon: "structural",
        description:
            "Availability and participation of workers in the labor market.",
        examples: [
            "labor force participation",
            "worker availability",
            "labor supply"
        ]
    },

    wage_growth: {
        channel: "labor",
        horizon: "cyclical",
        description:
            "Growth in wages or labor compensation.",
        examples: [
            "wage growth",
            "earnings growth",
            "pay growth"
        ]
    },

    household_income: {
        channel: "labor",
        horizon: "cyclical",
        description:
            "Household income and purchasing-power conditions.",
        examples: [
            "household income",
            "disposable income",
            "real income"
        ]
    },


    // ============================================================
    // CREDIT & FINANCIAL CONDITIONS
    // ============================================================

    credit_growth: {
        channel: "credit",
        horizon: "cyclical",
        description:
            "Growth or contraction in credit outstanding.",
        examples: [
            "credit growth",
            "loan growth",
            "bank lending growth"
        ]
    },

    lending_conditions: {
        channel: "credit",
        horizon: "cyclical",
        description:
            "Overall conditions under which borrowers can obtain financing.",
        examples: [
            "lending conditions",
            "borrowing conditions",
            "financing conditions"
        ]
    },

    lending_standards: {
        channel: "credit",
        horizon: "cyclical",
        description:
            "Standards or restrictions applied by lenders when extending credit.",
        examples: [
            "lending standards",
            "bank lending standards",
            "credit standards"
        ]
    },

    credit_demand: {
        channel: "credit",
        horizon: "cyclical",
        description:
            "Demand by households or businesses for credit.",
        examples: [
            "loan demand",
            "credit demand",
            "borrowing demand"
        ]
    },

    corporate_credit: {
        channel: "credit",
        horizon: "cyclical",
        description:
            "Credit conditions specifically affecting non-financial corporations.",
        examples: [
            "corporate borrowing",
            "corporate credit",
            "business lending"
        ]
    },

    household_credit: {
        channel: "credit",
        horizon: "cyclical",
        description:
            "Credit conditions specifically affecting households.",
        examples: [
            "consumer credit",
            "household borrowing",
            "mortgage credit"
        ]
    },

    credit_spreads: {
        channel: "credit",
        horizon: "cyclical",
        description:
            "Market compensation for credit risk relative to a reference rate.",
        examples: [
            "credit spread",
            "corporate bond spread",
            "risk spread"
        ]
    },

    default_conditions: {
        channel: "credit",
        horizon: "cyclical",
        description:
            "Observed or developing conditions related to borrower defaults and credit losses.",
        examples: [
            "defaults",
            "default rates",
            "credit losses"
        ]
    },

    financial_conditions: {
        channel: "financial_conditions",
        horizon: "cyclical",
        description:
            "Broad conditions governing the availability and cost of financial funding.",
        examples: [
            "financial conditions",
            "financial conditions index",
            "overall funding conditions"
        ]
    },


    // ============================================================
    // MONETARY POLICY & LIQUIDITY
    // ============================================================

    policy_rate: {
        channel: "policy_liquidity",
        horizon: "cyclical",
        description:
            "Central-bank policy interest rate.",
        examples: [
            "policy rate",
            "central bank rate",
            "benchmark interest rate"
        ]
    },

    policy_expectations: {
        channel: "policy_liquidity",
        horizon: "cyclical",
        description:
            "Expectations regarding future monetary-policy decisions.",
        examples: [
            "rate expectations",
            "policy expectations",
            "expected rate cuts"
        ]
    },

    real_policy_rate: {
        channel: "policy_liquidity",
        horizon: "cyclical",
        description:
            "Policy interest rate adjusted for inflation conditions.",
        examples: [
            "real policy rate",
            "real interest rate"
        ]
    },

    yield_curve: {
        channel: "policy_liquidity",
        horizon: "cyclical",
        description:
            "Relative structure of interest rates across maturities.",
        examples: [
            "yield curve",
            "curve steepening",
            "curve inversion"
        ]
    },

    central_bank_liquidity: {
        channel: "policy_liquidity",
        horizon: "cyclical",
        description:
            "Liquidity supplied or withdrawn by the central bank or monetary authority.",
        examples: [
            "central bank liquidity",
            "balance sheet expansion",
            "liquidity injection"
        ]
    },

    money_supply: {
        channel: "policy_liquidity",
        horizon: "cyclical",
        description:
            "Broad monetary aggregates and money creation conditions.",
        examples: [
            "money supply",
            "monetary aggregate",
            "broad money"
        ]
    },


    // ============================================================
    // FISCAL & GOVERNMENT
    // ============================================================

    government_spending: {
        channel: "fiscal",
        horizon: "cyclical",
        description:
            "Government expenditure and public-sector demand.",
        examples: [
            "government spending",
            "public expenditure"
        ]
    },

    fiscal_balance: {
        channel: "fiscal",
        horizon: "cyclical",
        description:
            "Government fiscal surplus or deficit.",
        examples: [
            "fiscal deficit",
            "budget balance",
            "fiscal surplus"
        ]
    },

    government_debt: {
        channel: "fiscal",
        horizon: "structural",
        description:
            "Outstanding government debt and sovereign leverage.",
        examples: [
            "government debt",
            "public debt",
            "sovereign debt"
        ]
    },

    fiscal_impulse: {
        channel: "fiscal",
        horizon: "cyclical",
        description:
            "Change in the fiscal stance and its contribution to aggregate demand.",
        examples: [
            "fiscal impulse",
            "fiscal stance"
        ]
    },

    government_investment: {
        channel: "fiscal",
        horizon: "structural",
        description:
            "Public investment in infrastructure and productive capacity.",
        examples: [
            "public investment",
            "government infrastructure spending"
        ]
    },


    // ============================================================
    // EXTERNAL SECTOR & FX
    // ============================================================

    exchange_rate: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Domestic currency value relative to foreign currencies.",
        examples: [
            "exchange rate",
            "currency",
            "currency depreciation"
        ]
    },

    trade_activity: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Aggregate import and export activity.",
        examples: [
            "trade activity",
            "trade volumes",
            "trade growth"
        ]
    },

    export_demand: {
        channel: "external",
        horizon: "cyclical",
        description:
            "External demand for a country's goods and services.",
        examples: [
            "export demand",
            "foreign demand"
        ]
    },

    import_demand: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Domestic demand for imported goods and services.",
        examples: [
            "import demand",
            "import volumes"
        ]
    },

    capital_flows: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Cross-border financial capital flows.",
        examples: [
            "capital flows",
            "portfolio flows",
            "foreign investment flows"
        ]
    },

    external_financing: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Availability and cost of financing from external or international sources.",
        examples: [
            "external financing",
            "foreign funding conditions"
        ]
    },

    global_dollar_conditions: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Global financial conditions associated with the US dollar and dollar funding.",
        examples: [
            "dollar strength",
            "global dollar liquidity",
            "dollar funding conditions"
        ]
    },


    // ============================================================
    // COMMODITIES & REAL-ECONOMY INPUTS
    // ============================================================

    energy_prices: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Broad energy price conditions affecting producers and consumers.",
        examples: [
            "energy prices",
            "energy costs"
        ]
    },

    oil_market: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Oil prices and oil-market supply-demand conditions.",
        examples: [
            "oil prices",
            "crude oil",
            "oil market"
        ]
    },

    gas_market: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Natural-gas prices and gas-market supply-demand conditions.",
        examples: [
            "natural gas",
            "gas prices",
            "gas market"
        ]
    },

    electricity_prices: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Electricity pricing and power-market price conditions.",
        examples: [
            "electricity prices",
            "power prices",
            "electricity tariffs"
        ]
    },

    metals_prices: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Prices and market conditions for industrial or precious metals.",
        examples: [
            "metal prices",
            "copper prices",
            "nickel prices"
        ]
    },

    agricultural_prices: {
        channel: "external",
        horizon: "cyclical",
        description:
            "Prices of agricultural commodities and food-related raw materials.",
        examples: [
            "agricultural prices",
            "food commodity prices"
        ]
    },


    // ============================================================
    // STRUCTURAL / POTENTIAL GROWTH
    // ============================================================

    productivity: {
        channel: "structural",
        horizon: "structural",
        description:
            "Efficiency of production and output generated from economic inputs.",
        examples: [
            "productivity",
            "labor productivity",
            "total factor productivity"
        ]
    },

    potential_growth: {
        channel: "structural",
        horizon: "structural",
        description:
            "Long-run sustainable growth capacity of the economy.",
        examples: [
            "potential growth",
            "trend growth",
            "long-run growth capacity"
        ]
    },

    demographics: {
        channel: "structural",
        horizon: "structural",
        description:
            "Population and demographic structure affecting economic capacity.",
        examples: [
            "demographics",
            "population growth",
            "aging population"
        ]
    },

    supply_capacity: {
        channel: "structural",
        horizon: "structural",
        description:
            "Physical or productive capacity available to supply goods and services.",
        examples: [
            "productive capacity",
            "supply capacity",
            "capacity constraints"
        ]
    }

} as const;

export type CanonicalMacroConcept =
    keyof typeof CANONICAL_MACRO_CONCEPTS;