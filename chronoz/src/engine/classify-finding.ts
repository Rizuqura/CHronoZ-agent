import type {
    ResearchEncoding
} from "../types/finding";

import type {
    ResearchCard
} from "./extract-evidence";

import {
    llmClient,
    llmModel
} from "../llm/llm-client";

import {
    CANONICAL_MACRO_CONCEPTS
} from "../registry/macro-concepts";


export async function encodeResearchCard(
    card: ResearchCard
): Promise<ResearchEncoding> {

    const canonicalConceptKeys =
        Object.keys(CANONICAL_MACRO_CONCEPTS);


    const response =
        await llmClient.responses.create({

            model: llmModel,

            instructions: `

                --------------------------------------------------
                ATOMIC CLAIM RULE
                --------------------------------------------------

                Split the Research Card when it contains different factual
                or inferential statements.

                Each claim must represent one independently understandable
                economic observation or statement.

                Do not merge multiple variables into one claim merely because
                they appear in the same sentence.

                For example:

                "Credit standards tightened while loan demand weakened."

                This contains two independent observations:

                Claim A:
                Credit standards tightened.

                Claim B:
                Loan demand weakened.

                These should be represented as separate claims.

                The purpose of splitting is to preserve the individual
                variables so that deterministic downstream systems can later
                compare each variable against its own benchmark.

                --------------------------------------------------
                VARIABLE MODEL
                --------------------------------------------------

                The variable field represents WHAT changed.

                Think in terms of an economic state variable rather than
                the entity performing the action.

                Examples of variable classes:

                Growth:
                - real_activity
                - industrial_activity
                - manufacturing_activity
                - services_activity
                - consumer_activity
                - investment_activity
                - housing_activity

                Inflation:
                - headline_inflation
                - core_inflation
                - goods_inflation
                - services_inflation
                - wage_inflation
                - inflation_expectations
                - producer_prices

                Labor:
                - employment
                - unemployment
                - labor_demand
                - labor_supply
                - wage_growth
                - household_income

                Credit:
                - credit_growth
                - lending_conditions
                - lending_standards
                - credit_demand
                - corporate_credit
                - household_credit
                - credit_spreads
                - default_conditions

                Policy / Liquidity:
                - policy_rate
                - policy_expectations
                - real_policy_rate
                - yield_curve
                - central_bank_liquidity
                - money_supply

                Fiscal:
                - government_spending
                - fiscal_balance
                - government_debt
                - fiscal_impulse
                - government_investment

                External:
                - exchange_rate
                - trade_activity
                - export_demand
                - import_demand
                - capital_flows
                - external_financing
                - global_dollar_conditions

                Structural:
                - productivity
                - potential_growth
                - demographics
                - supply_capacity

                Only use a variable that is supported by the source.

                Do not infer a more specific variable than the source supports.

                --------------------------------------------------
                VARIABLE RELATIONSHIP MODEL
                --------------------------------------------------

                Economic observations may contain relationships between
                variables.

                However, the encoder must preserve the relationship without
                turning it into a causal conclusion.

                Example:

                "Higher interest rates reduced credit demand."

                The claim contains:

                source variable:
                interest_rate

                target variable:
                credit_demand

                observed relationship:
                higher interest rates
                → lower credit demand

                This is different from simply observing:

                "Credit demand declined."

                The first statement contains a relationship between variables.

                The second contains only a state observation.

                When the source explicitly states a relationship, preserve it
                as part of the claim.

                When the source does NOT explicitly state the relationship,
                do not invent one.

                --------------------------------------------------
                RELATIONSHIP TYPES
                --------------------------------------------------

                When a claim explicitly contains multiple variables, identify
                the logical relationship represented by the source.

                Possible relationship structures:

                1. STATE

                A single variable changed.

                Example:

                "Industrial production declined."

                Model:

                industrial_activity
                ↓


                2. COMPARISON

                One variable differs relative to another variable or reference.

                Example:

                "Real wage growth exceeded consumer price inflation."

                Model:

                wage_growth
                >
                headline_inflation


                3. ASSOCIATION

                The source explicitly states that two variables moved together
                or were associated.

                Example:

                "Credit growth weakened alongside slower investment."

                Model:

                credit_growth
                ↓
                investment_activity
                ↓

                Do NOT convert this into causality.


                4. CAUSAL CLAIM

                The source explicitly attributes one variable's change to
                another variable.

                Example:

                "Higher borrowing costs reduced investment."

                Model:

                borrowing_cost
                ↑
                →
                investment_activity
                ↓

                Preserve the stated relationship.

                Do not independently verify or endorse the causal claim.


                5. CONDITIONAL RELATIONSHIP

                The source states that the effect depends on another condition.

                Example:

                "Higher interest rates may reduce housing activity when
                mortgage availability is constrained."

                Model:

                policy_rate
                ↑
                +
                mortgage_availability
                constrained
                →
                housing_activity
                ↓

                Preserve the condition.

                Do not generalize it beyond the source.


                6. EXPECTATION

                The source describes an expected future relationship rather
                than an observed current relationship.

                Example:

                "Lower interest rates are expected to support housing activity."

                Model:

                policy_rate
                ↓
                → expected
                housing_activity
                ↑

                Do not encode the expected outcome as an observed fact.

                --------------------------------------------------
                ECONOMIC LOGIC MODEL
                --------------------------------------------------

                The encoder should think in terms of:

                VARIABLE
                ↓
                OBSERVED CHANGE
                ↓
                OPTIONAL EXPLICIT RELATIONSHIP
                ↓
                MACRO CONCEPT

                Do NOT think in terms of:

                ENTITY
                ↓
                STOCK PRICE
                ↓
                INVESTMENT CONCLUSION

                The entity provides context.

                The variable provides the economic object.

                The direction provides the observed or stated movement.

                The relationship describes how variables are connected when
                that relationship is explicitly present.

                The conceptKey provides the canonical semantic mapping.

                --------------------------------------------------
                MODEL LOGIC EXAMPLES
                --------------------------------------------------

                Example A — single-variable observation

                Input:

                "Industrial production declined."

                Model:

                variable:
                industrial_activity

                direction:
                decrease

                macroRelevance:
                direct

                macroChannel:
                growth

                conceptKey:
                industrial_activity

                There is no need to invent another variable or relationship.


                Example B — labor observation

                Input:

                "Employment growth accelerated."

                Model:

                variable:
                employment

                direction:
                accelerate

                macroRelevance:
                direct

                macroChannel:
                labor

                conceptKey:
                employment


                Example C — credit observation

                Input:

                "Bank lending standards tightened."

                Model:

                variable:
                lending_standards

                direction:
                tighten

                macroRelevance:
                direct

                macroChannel:
                credit

                conceptKey:
                lending_standards


                Example D — two independent variables

                Input:

                "Credit standards tightened while loan demand weakened."

                Split into:

                Claim A:

                variable:
                lending_standards

                direction:
                tighten

                conceptKey:
                lending_standards


                Claim B:

                variable:
                credit_demand

                direction:
                decrease

                conceptKey:
                credit_demand

                Do not combine these into one variable.


                Example E — explicit relationship

                Input:

                "Higher interest rates reduced housing activity."

                Model:

                source variable:
                policy_rate

                direction:
                increase

                target variable:
                housing_activity

                direction:
                decrease

                relationship:
                policy_rate
                ↑
                →
                housing_activity
                ↓

                The relationship is preserved because the source explicitly
                states causality.

                Do not independently transform this into a statistical claim.


                Example F — association without causality

                Input:

                "Credit growth weakened alongside business investment."

                Model:

                credit_growth
                ↓

                investment_activity
                ↓

                relationship:
                association

                Do NOT encode:

                credit_growth
                ↓
                →
                investment_activity
                ↓

                because the source only states that they moved together.


                Example G — comparison

                Input:

                "Real wage growth exceeded consumer price inflation."

                Model:

                wage_growth
                >
                headline_inflation

                This is a comparative relationship.

                Do not convert it into:

                wage_growth causes inflation.


                Example H — expectation

                Input:

                "Markets expect lower policy rates to support economic activity."

                Model:

                policy_rate
                ↓
                → expected
                real_activity
                ↑

                This is an expectation.

                It is NOT an observed economic outcome.

                Do not encode:

                real_activity
                ↑

                unless the source separately states that economic activity
                actually increased.


                Example I — conditional relationship

                Input:

                "Lower borrowing costs are likely to support housing activity
                when mortgage availability remains stable."

                Model:

                borrowing_cost
                ↓
                +
                mortgage_availability
                stable
                →
                housing_activity
                ↑

                Preserve the condition.

                Do not remove the condition and generalize the relationship.


                Example J — indirect observation

                Input:

                "Businesses postponed capital expenditure because financing
                conditions became more restrictive."

                This contains:

                capital_expenditure
                ↓ / delayed

                financing_conditions
                tighten

                and an explicit relationship:

                financing_conditions
                tighten
                →
                investment_activity
                ↓

                If the canonical registry contains:

                financial_conditions

                but does not contain a specific capital-expenditure concept,
                do not invent one.

                Map only the variables that have a valid canonical concept.

                --------------------------------------------------
                FACT VS RELATIONSHIP
                --------------------------------------------------

                A claim may contain both:

                1. observable state information
                2. a relationship asserted by the source

                Keep these conceptually separate.

                For example:

                "Higher borrowing costs reduced investment."

                Observed/state information:

                borrowing_cost ↑
                investment_activity ↓

                Source-stated relationship:

                borrowing_cost ↑
                →
                investment_activity ↓

                The encoder must not add additional relationships such as:

                investment_activity ↓
                →
                employment ↓

                unless the source explicitly states that relationship.

                --------------------------------------------------
                CAUSALITY DISCIPLINE
                --------------------------------------------------

                The presence of a relationship in the source does NOT mean
                CHronoZ has independently established causality.

                If the source says:

                "Higher rates reduced investment."

                preserve:

                relationship.type = "causal_claim"

                But do NOT treat it as:

                causal_relationship_verified = true

                The encoder only records what the source claims.

                Causal validation belongs to downstream research and
                econometric analysis.

                --------------------------------------------------
                MACRO MAPPING LOGIC
                --------------------------------------------------

                Use the following decision hierarchy:

                STEP 1

                Does the claim explicitly describe a variable that exists
                in the canonical macro registry?

                If YES:

                macroRelevance = direct

                conceptKey = matching canonical concept


                STEP 2

                Does the claim concern an economic variable that is not
                directly represented in the canonical registry, but has an
                explicitly stated macroeconomic relationship or transmission
                relevance?

                If YES:

                macroRelevance = indirect

                conceptKey = null

                unless another explicitly stated variable has a valid
                canonical mapping.


                STEP 3

                Is the claim primarily firm-specific, operational, descriptive,
                or otherwise not meaningfully represented by the macro registry?

                If YES:

                macroRelevance = none

                conceptKey = null


                --------------------------------------------------
                CANONICAL CONCEPT MAPPING
                --------------------------------------------------

                You may ONLY use a conceptKey from this canonical registry:

                ${JSON.stringify(canonicalConceptKeys)}

                You MUST NOT create a new concept key.

                If no supplied canonical concept clearly matches the variable:

                conceptKey = null

                Do not approximate a concept merely because it sounds
                economically related.

                The mapping must be semantically defensible.

                --------------------------------------------------
                IMPORTANT DISTINCTION
                --------------------------------------------------

                conceptKey is a semantic mapping.

                It does NOT mean:

                - the variable has been measured
                - the variable has been benchmarked
                - the variable has been normalized
                - the variable has a z-score
                - the variable has been statistically validated
                - the relationship has been causally validated
                - the variable currently deviates from its historical norm

                The encoder stops at semantic representation.

                Downstream deterministic systems perform:

                conceptKey
                ↓
                measurement registry
                ↓
                data series
                ↓
                transformation
                ↓
                historical benchmark
                ↓
                normalized state
                `,

            input: `
Research Card ID:
${card.id}

Highlight:
${card.highlight}

Context:
${card.context}
`,

            text: {
                format: {
                    type: "json_schema",

                    name: "chronoz_research_encoding",

                    strict: true,

                    schema: {

                        type: "object",

                        properties: {

                            id: {
                                type: "string"
                            },

                            cardId: {
                                type: "string"
                            },

                            claims: {

                                type: "array",

                                items: {

                                    type: "object",

                                    properties: {

                                        id: {
                                            type: "string"
                                        },

                                        statement: {
                                            type: "string"
                                        },

                                        sourceSpan: {
                                            type: "string"
                                        },

                                        entity: {

                                            type: "object",

                                            properties: {

                                                type: {
                                                    type: "string",

                                                    enum: [
                                                        "company",
                                                        "country",
                                                        "sector",
                                                        "industry",
                                                        "government",
                                                        "institution",
                                                        "market",
                                                        "unknown"
                                                    ]
                                                },

                                                name: {
                                                    type: "string"
                                                }

                                            },

                                            required: [
                                                "type",
                                                "name"
                                            ],

                                            additionalProperties: false
                                        },

                                        variable: {

                                            type: "object",

                                            properties: {

                                                name: {
                                                    type: "string"
                                                },

                                                direction: {
                                                    type: "string",

                                                    enum: [
                                                        "increase",
                                                        "decrease",
                                                        "stable",
                                                        "accelerate",
                                                        "decelerate",
                                                        "delay",
                                                        "advance",
                                                        "tighten",
                                                        "ease",
                                                        "mixed",
                                                        "unknown"
                                                    ]
                                                }

                                            },

                                            required: [
                                                "name",
                                                "direction"
                                            ],

                                            additionalProperties: false
                                        },

                                        timeHorizon: {

                                            type: "string",

                                            enum: [
                                                "historical",
                                                "current",
                                                "near_term",
                                                "medium_term",
                                                "long_term",
                                                "unknown"
                                            ]
                                        },

                                        macroRelevance: {

                                            type: "string",

                                            enum: [
                                                "none",
                                                "indirect",
                                                "direct"
                                            ]
                                        },

                                        macroChannel: {

                                            anyOf: [
                                                {
                                                    type: "string",

                                                    enum: [
                                                        "growth",
                                                        "inflation",
                                                        "labor",
                                                        "credit",
                                                        "policy_liquidity",
                                                        "financial_conditions",
                                                        "external",
                                                        "fiscal",
                                                        "structural"
                                                    ]
                                                },
                                                {
                                                    type: "null"
                                                }
                                            ]
                                        },

                                        conceptKey: {

                                            anyOf: [
                                                {
                                                    type: "string",

                                                    enum:
                                                        canonicalConceptKeys
                                                },
                                                {
                                                    type: "null"
                                                }
                                            ]
                                        }

                                    },

                                    required: [
                                        "id",
                                        "statement",
                                        "sourceSpan",
                                        "entity",
                                        "variable",
                                        "timeHorizon",
                                        "macroRelevance",
                                        "macroChannel",
                                        "conceptKey"
                                    ],

                                    additionalProperties: false
                                }
                            }

                        },

                        required: [
                            "id",
                            "cardId",
                            "claims"
                        ],

                        additionalProperties: false
                    }
                }
            }
        });


    const encoding =
        JSON.parse(
            response.output_text
        ) as ResearchEncoding;


    return encoding;
}