import type { TransmissionEdge } from "../types/transmission"

/*
  DEVELOPMENT PLACEHOLDER ONLY

  This transmission map is currently a simplified
  theory-based representation for testing CHronoZ.

  Future implementation should be calibrated using:
  - historical macroeconomic data
  - statistical analysis
  - estimated transmission lags
  - state-dependent effects
  - predictive / regime modelling
*/

export const transmissionMap: TransmissionEdge[] = [
  {
    from: "policy",
    to: "credit",
    sign: "negative",
    strength: "moderate",
    lag: "medium",
    mechanism:
      "More restrictive policy can reduce credit availability and demand."
  },

  {
    from: "credit",
    to: "investment",
    sign: "positive",
    strength: "moderate",
    lag: "medium",
    mechanism:
      "Credit availability supports financing for investment."
  },

  {
    from: "investment",
    to: "growth",
    sign: "positive",
    strength: "moderate",
    lag: "medium",
    mechanism:
      "Higher investment contributes to aggregate economic activity."
  },

  {
    from: "growth",
    to: "labor",
    sign: "positive",
    strength: "moderate",
    lag: "medium",
    mechanism:
      "Stronger economic activity generally supports labor demand."
  },

  {
    from: "labor",
    to: "inflation",
    sign: "positive",
    strength: "weak",
    lag: "long",
    mechanism:
      "Tighter labor conditions may increase wage and price pressures."
  }
]