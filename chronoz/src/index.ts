import {defaultState} from "./model/default-state"
import type {Finding} from "./types/finding"
import type {ImpactAssessment} from "./types/impact"
import { transmissionMap } from "./model/transmission-map" //dummy
import { assessImpact } from "./engine/impact-assessment"

const sampleFinding: Finding = {
    id: "finding-001",
    statement: "Bank lending standards tightened.",
    kind: "qualitative",
    sourceEvidenceIds: ["ev-001"],
    isFact: true,
    confidence: 0.8
}

const impact = assessImpact(sampleFinding)

const sampleImpact: ImpactAssessment = {
    findingId: sampleFinding.id,
    targetNode: "credit",
    direction: "negative",
    strength: "moderate",
    expectedLag: "medium",
    confidence: 0.7,
    reasoning:
    "Tighter lending standards may reduce credit availability."
}



console.log("CHronoZ Agent is running...")

console.log("\nCurrent State:")
console.log(defaultState)

console.log("\nNew Finding:")
console.log(sampleFinding)

console.log("\nTransmission Map:")
console.log(transmissionMap)

console.log("\nImpact Assessment:")
console.log(impact)