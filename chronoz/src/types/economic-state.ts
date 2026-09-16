import type { EconomicStateNode } from "./economic-node"

export type CurrentEconomicState = {
    growth: EconomicStateNode
    inflation: EconomicStateNode
    labor: EconomicStateNode
    credit: EconomicStateNode
    policy: EconomicStateNode
    liquidity: EconomicStateNode

}