export type ImpactDirection = 
    | "positive"
    | "negative"
    | "neutral"

export type ImpactStrength = 
    | "low"
    | "moderate"
    | "high"

export type ImpactLag = 
    | "short"
    | "medium"
    | "long"

export type ImpactAssessment = {
    findingId: string

    targetNode: string

    direction: ImpactDirection
    strength: ImpactStrength
    expectedLag: ImpactLag

    confidence: number

    reasoning: string
}