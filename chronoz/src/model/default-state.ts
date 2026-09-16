import type { CurrentEconomicState } from "../types/economic-state"

/*
  DEVELOPMENT PLACEHOLDER ONLY

  This default economic state is currently hard-coded
  for testing CHronoZ architecture and data flow.

  It DOES NOT represent a real macroeconomic assessment.

  Future implementation:
  - historical data ingestion
  - statistical calibration
  - z-score / percentile normalization
  - composite economic node scoring
  - regime modelling
  - machine-learning / predictive model integration

  Eventually this file should act only as a fallback
  when no calibrated economic state is available.
*/

export const defaultState: CurrentEconomicState = {
    growth: {
        id: "growth",
        name: "Growth",
        level: "neutral",
        direction: "flat",
        momentum: "stable",
        confidence: 0.5,
        lastUpdated: new Date().toISOString()
    },
    inflation: {
        id: "inflation",
        name: "Inflation",
        level: "neutral",
        direction: "flat",
        momentum: "stable",
        confidence: 0.5,
        lastUpdated: new Date().toISOString()
    },
    labor: {
        id: "labor",
        name: "Labor",
        level: "neutral",
        direction: "flat",
        momentum: "stable",
        confidence: 0.5,
        lastUpdated: new Date().toISOString()
    },
    credit: {
        id: "credit",
        name: "Credit",
        level: "neutral",
        direction: "flat",
        momentum: "stable",
        confidence: 0.5,
        lastUpdated: new Date().toISOString()
    },
    policy: {
        id: "policy",
        name: "Policy",
        level: "neutral",
        direction: "flat",
        momentum: "stable",
        confidence: 0.5,
        lastUpdated: new Date().toISOString()
    },
    liquidity: {
    id: "liquidity",
    name: "Liquidity",
    level: "moderate",
    direction: "up",
    momentum: "stable",
    confidence: 0.5,
    lastUpdated: new Date().toISOString()
  }
}