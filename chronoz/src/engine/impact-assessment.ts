import type { Finding } from "../types/finding"
import type { ImpactAssessment } from "../types/impact"

/*
  DEVELOPMENT PLACEHOLDER ONLY

  This function uses simple hard-coded rules
  to test CHronoZ's impact-assessment pipeline.

  Future implementation should use:
  - calibrated economic state
  - statistical evidence
  - transmission map
  - state-dependent effects
  - predictive / regime modelling
*/

export function assessImpact(
  finding: Finding
): ImpactAssessment {

  if (
    finding.statement
      .toLowerCase()
      .includes("lending standards tightened")
  ) {
    return {
      findingId: finding.id,
      targetNode: "credit",
      direction: "negative",
      strength: "moderate",
      expectedLag: "medium",
      confidence: 0.7,
      reasoning:
        "Tighter lending standards may reduce credit availability."
    }
  }

  return {
    findingId: finding.id,
    targetNode: "unknown",
    direction: "neutral",
    strength: "low",
    expectedLag: "short",
    confidence: 0.2,
    reasoning:
      "No matching placeholder rule was found."
  }
}