export type Direction = 
    | "up" 
    | "down" 
    | "flat"

export type Momentum = 
    | "accelerating" 
    | "stable"
    | "decelerating" 

export type EconomicNode = {
    id: string
    name: string

    level: string
    direction: Direction
    momentum: Momentum

    confidence: number
    lastUpdated: string
}

