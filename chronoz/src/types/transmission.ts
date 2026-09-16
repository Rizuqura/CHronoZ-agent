export type TransmissionSign = 
    | "positive"
    | "negative"
    | "mixed"

export type TransmissionStrength = 
    | "weak"
    | "moderate"
    | "strong"
    
export type TransmissionLag =
    | "short"
    | "medium"
    | "long"

export type TransmissionEdge = {
    from : string
    to : string

    sign : TransmissionSign
    strength : TransmissionStrength
    lag : TransmissionLag

    mechanism : string
}