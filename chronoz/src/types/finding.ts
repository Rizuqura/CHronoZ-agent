export type MacroRelevance =
    | "none"
    | "indirect"
    | "direct";

export type ClaimEntityType =
    | "company"
    | "country"
    | "sector"
    | "industry"
    | "government"
    | "institution"
    | "market"
    | "unknown";

export type ClaimDirection =
    | "increase"
    | "decrease"
    | "stable"
    | "accelerate"
    | "decelerate"
    | "delay"
    | "advance"
    | "tighten"
    | "ease"
    | "mixed"
    | "unknown";

export type TimeHorizon =
    | "historical"
    | "current"
    | "near_term"
    | "medium_term"
    | "long_term"
    | "unknown";

export interface AtomicClaim {
    id: string;

    statement: string;

    sourceSpan: string;

    entity: {
        type: ClaimEntityType;
        name: string;
    };

    variable: {
        name: string;
        direction: ClaimDirection;
    };

    timeHorizon: TimeHorizon;

    macroRelevance: MacroRelevance;

    macroChannel:
        | "growth"
        | "inflation"
        | "labor"
        | "credit"
        | "policy_liquidity"
        | "financial_conditions"
        | "external"
        | "fiscal"
        | "structural"
        | null;

    conceptKey: string | null;
}

export interface ResearchEncoding {
    id: string;
    cardId: string;
    claims: AtomicClaim[];
}