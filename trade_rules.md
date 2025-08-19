# Options in cross margin mode

In mode, you will be able to open long and short positions of options

## Position fields

| Term | Explanation | Parameter in Get position |
|------|-------------|---------------------------|
| Total | The total of long positions is a positive number, and the total of short positions is a negative number. | pos |
| Options value | If the unit for calculating the price is crypto, then options value = total positions * mark priceIf the unit for calculating the price is the number of contracts, then options value = total positions * mark price * multiplier | optVal |
| Floating PnL | Unrealized profit or loss of current position<br>Floating PnL = (mark price - avg. open price) * total positions * multiplier | upl |
| Floating PnL % | Floating PnL % = (mark price – avg. open price) / avg. open price<br>Floating PnL % = (avg. open price - mark price) / avg. open price | uplRatio |
| Initial margin | The initial margin for long positions is 0. Information on how to calculate the initial margin for short positions can be found here. | imr |
| Maintenance margin | The maintenance margin for long positions is 0. Information on how to calculate the maintenance margin for short positions can be found here. | mmr |

## Maintenance margin ratio risk levels
If your maintenance margin ratio falls to 300% or lower, you’ll receive a liquidation warning. You can add margin or reduce the position to decrease the risk level.

If your maintenance margin ratio falls to 100% or lower, order cancellation, forced position reduction, or liquidation may be triggered.

| Risk Level | Maintenance Margin Ratio |
|------------|--------------------------|
| Low-risk | > 500% |
| Medium-risk | 300% < ratio ≤ 500% |
| High-risk | 100% < ratio ≤ 300% |
| Liquidation | ≤ 100% |