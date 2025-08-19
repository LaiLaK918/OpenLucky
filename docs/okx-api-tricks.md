# OKX API Best Practices and Tricks

Source: https://my.okx.com/docs-v5/trick_en/
Converted on: Sun Jul 13 12:21:03 CST 2025

---

# Instrument configuration

Users can get the exchange instruments configuration from [`GET /api/v5/public/instruments`](https://my.okx.com/docs-v5/en/#public-data-rest-api-get-instruments).

Subsequent instrument updates, such as tick size changes and new listings will be published from the websocket [`instruments`](https://my.okx.com/docs-v5/en/#public-data-websocket-instruments-channel) channel.

# Market data

Users can receive real time market data updates from websocket channels.

`bbo-tbt` and `books5` are depth snapshots that are published every 10ms and 100ms. New snapshots are not sent when there is no change in the orderbook.

`books`, `books-l2-tbt`, and `books50-l2-tbt` are incremental order book channels. `books` publishs the changes in the order book every 100ms. `books-l2-tbt` and `books50-l2-tbt` push changes every 10ms. In order to use `books-l2-tbt` and `books50-l2-tbt`, users must login before subscribing and are limited to VIP levels 5 and 4, respectively.

Order book data is created once every 10ms internally and relevant data is sent out depending on the subscribed channel. Users receive the same order book image from all websocket connections and channels.

No update is sent if the depth changes from A -> B -> A during the interval. If there are no updates to the depth for an extended period, the system resends the current depth for snapshot channels, a message with no depth updates for incremental channels, to inform users that the connection is still active.

# Configuring accounts and sub-accounts

After creating sub-accounts and their API Keys, users can configure the master account and sub-accounts via the API before trading.

## Account config

The account config of each account/sub-account can be retrieved via the REST API as follows:

[`GET /api/v5/account/config`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-account-configuration).

The API returns account mode, position mode, auto-borrow setting, and the Greeks type option, among additional account-related information.

## Account mode

In the Trading account trading system, 4 account modes are supported: Spot mode, Futures mode, Multi-currency margin mode, and Portfolio margin mode.

Users can only change these modes via the web or mobile app interface.

## Position

There are 2 position modes as detailed below.

`net` mode: Positions can be held on one side only. Exchange will open/close the position automatically depending on the position (positive/negative) specified.

`long` and `short` mode: Positions can be held on both sides at the same time.

To change the position mode, users can invoke the following REST API:

[`POST /api/v5/account/set-position-mode`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-set-position-mode)

Note: All positions must be closed with no pending orders to perform the switch.

## Auto-borrow

Auto-borrowing is only applicable in Multi-currency margin mode and Portfolio margin mode and can only be enabled or disabled via the web UI.

Exchange may automatically convert from the available balance in other currencies to repay the liability. The risk indicator can be found from the `twap` field in [`GET /api/v5/account/balance`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-balance) and WS [`account`](https://my.okx.com/docs-v5/en/#trading-account-websocket-account-channel) endpoints.

## Option Greeks type

Users can set the option Greeks type via the endpoint below:

[`POST /api/v5/account/set-greeks`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-set-greeks-pa-bs)

# Cross/Isolated margin mode

Users have the flexibility to have positions in isolated and cross-margin at the same time.

As a result, there is no API for setting margin mode per position. Instead, users should specify the margin mode (i.e. trade mode) using the field `tdMode` when placing an order.

## Getting leverage

Users can retrieve leverage information via the following REST API:

[`GET /api/v5/account/leverage-info`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-leverage)

Currently, there is no global leverage setting. The leverage can be set in different scopes.

For margin instrument type:

| Account Mode | Margin Mode | Scope |
| --- | --- | --- |
| **Spot mode** | Cross | Per instrument |
|  | Isolated | Per instrument |
| **Futures mode** | Cross | Per instrument |
|  | Isolated | Per instrument |
| **Multi-currency margin** | Cross | Per currency |
|  | Isolated | Per instrument |

For other instrument types:

| Position Mode | Instrument Type | Margin Mode | Scope |
| --- | --- | --- | --- |
| **Net** | Futures | Cross | Per Instrument Family |
|  |  | Isolated | Per Instrument Family |
|  | Swap | Cross | Per Instrument Family |
|  |  | Isolated | Per Instrument Family |
| **Long/Short** | Futures | Cross | Per Instrument Family |
|  |  | Isolated | Per Instrument Family per side |
|  | Swap | Cross | Per Instrument Family |
|  |  | Isolated | Per Instrument Family per side |

## Setting leverage

After getting the leverage info, users can set the leverage accordingly:

[`POST /api/v5/account/set-leverage`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-set-leverage)

With these 2 APIs, users can write a program to set the leverage of each instrument beforehand.

For example, consider the following scenario:

- Account mode: Multi-currency Margin
- Position mode: Net
- Instruments that users want to set leverage to 3.0:
  - BTC-USDT, EOS-USDT, LTC-BTC, LTC-USDT
  - BTC-USD-210319, BTC-USD-210326, BTC-USD-210625
  - BTC-USD-SWAP
- Interested in cross-margin mode only for above instruments

For spot/margin instruments, since the leverage is set per currency, users can extract the currency pair and set each currency accordingly, i.e. BTC, USDT, EOS, and LTC.

Sample request body of setting BTC leverage to 3.0 (applicable to selling BTC-USDT and buying LTC-BTC):

|  |
| --- |
| { "lever": "3.0", "mgnMode": "cross", "ccy": "BTC" } |

The request bodies for setting USDT, EOS, and LTC are similar.

If users want to set the leverage of `BTC-USD-210319`, `BTC-USD-210326`, and `BTC-USD-210625`, since they share the same instrument family, i.e. BTC-USD, leverage only needs to be set once with one of the instruments.

|  |
| --- |
| { "lever": "3.0", "mgnMode": "cross", "instId": "BTC-USD-210326" } |

If users want to set the leverage of BTC-USD-SWAP, leverage must be seperated between futures and swap despite having the same instrument family (BTC-USD) as the above futures.

To do so, users can invoke the API with the following request body:

|  |
| --- |
| { "lever": "3.0", "mgnMode": "cross", "instId": "BTC-USD-SWAP" } |

At this point, users should be set with the above 6 API calls for the 8 instruments.

Follow the above instructions to set up sub-accounts with the new API and configure accounts to suit trading preferences.

# Order management

## Trade mode

With the flexibility of placing orders with cross and isolated margin modes, users must specify the trade mode (`tdMode`).

The following table shows `tdMode` values that must be set:

| Account Mode | Instrument Type | Margin Mode | Trade Mode (tdMode) |
| --- | --- | --- | --- |
| **Spot mode** | Spot | (N/A) | cash |
|  | Option | (N/A) | cash |
| **Futures mode** | Spot | (N/A) | cash |
|  | Margin | Cross | cross |
|  |  | Isolated | isolated |
|  | Futures/Swap/Option | Cross | cross |
|  |  | Isolated | isolated |
| **Multi-currency Margin** | Spot/Margin | Cross | cross |
|  | Margin | Isolated | isolated |
|  | Futures/Swap/Option | Cross | cross |
|  |  | Isolated | isolated |

Let's say users want to place the following order as an example:

- Account mode: Multi-currency Margin
- Position mode: Net
- Instrument: BTC-USDT-SWAP
- Margin Mode: Cross
- Side: Buy (long)
- Type: Limit
- Price: 50,912.4 USDT
- Amount: 1 Cont

By looking at the trading mode table above, `tdMode` must be set to `cross`.

## Subscribing to the orders channel

Before placing an order, users must subscribe to the [`orders`](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-order-channel) channel with WebSocket to monitor the order state changes (e.g. `live`, `filled`) and take action if necessary (e.g. place a new order after execution).

There are several subscription granularities when subscribing to the orders channel.

To subscribe to the above-mentioned BTC-USDT-SWAP order updates, users can send any of the following requests after connecting and logging in to the private WebSocket:

| Subscription Method | Instrument Type | Instrument Type + Instrument Family (Derivatives only) | Instrument Type + Instrument ID |
| --- | --- | --- | --- |
| Request | { "op": "subscribe", "args": [ { "channel": "orders", "instType": "SWAP" } ] } | { "op": "subscribe", "args": [ { "channel": "orders", "instType": "SWAP", "instFamily": "BTC-USDT" } ] } | { "op": "subscribe", "args": [ { "channel": "orders", "instType": "SWAP", "instId": "BTC-USDT-SWAP" } ] } |
| Successful response | { "event": "subscribe", "arg": { "channel": "orders", "instType": "SWAP" } } | { "event": "subscribe", "args": [ { "channel": "orders", "instType": "SWAP", "instFamily": "BTC-USDT" } ] } | { "event": "subscribe", "args": [ { "channel": "orders", "instType": "SWAP", "instId": "BTC-USDT-SWAP" } ] } |

Optionally, users can pass `ANY` as `instType` to subscribe to all product types at once.

Note that the orders channel does not publish any initial snapshot of user orders before the subscription. It only publishes whenever the order state changes (e.g. from `live` to `canceled`).

If users want to obtain all the live order details before subscribing, users can invoke the following API:

[`GET /api/v5/trade/orders-pending`](https://my.okx.com/docs-v5/en/#order-book-trading-trade-get-order-list)

## Placing an order

To better identify the order in the system, it is recommended to provide a Client Order ID as assigned by the client (`clOrdId`) when placing the order. The Client Order ID as assigned by the client should be case-sensitive, and have a maximum of 32 alphanumeric characters.

`clOrdId` uniqueness check is only applied towards all pending orders. It is recommended to use a unique `clOrdId` at all times for troubleshooting etc.

In the following example, `clOrdId` is assigned as `testBTC0123`.

After subscribing to the orders channel, users can place the `BTC-USDT-SWAP` order.

Users can use REST or WebSocket to place orders.

### REST API

Users can invoke the following REST API and the server will acknowledge the request with an order ID (`ordId`):

|  |  |
| --- | --- |
| REST API | POST /api/v5/trade/order |
| Request body | { "instId": "BTC-USDT-SWAP", "tdMode": "cross", "clOrdId": "testBTC0123", "side": "buy", "ordType": "limit", "px": "50912.4", "sz": "1" } |
| Successful response | { "code": "0", "msg": "", "data": [ { "clOrdId": "testBTC0123", "ordId": "288981657420439575", "tag": "", "sCode": "0", "sMsg": "" } ] } |

Note that this only indicates that the exchange has received the request successfully with an order ID assigned. The order may not entered matching engine at this point in time. Users should check the order state.

### WebSocket

Users can place the order via WebSocket, which is, in theory, more efficient than using REST API with less overhead.

Since WebSocket operation is asynchronous, users will also need to provide the message ID (`id`) to identify the corresponding response.

After logging into the private WebSocket, users can send the following WebSocket message:

|  |
| --- |
| { "id": "NEWtestBTC0123", "op": "order", "args": [ { "instId": "BTC-USDT-SWAP", "tdMode": "cross", "clOrdId": "testBTC0123", "side": "buy", "ordType": "limit", "px": "50912.4", "sz": "1" } ] } |

The server will acknowledge the request with the following sample response with the same message ID (i.e.NEWtestBTC0123), along with an order ID (`ordId`) assigned by the exchange:

|  |
| --- |
| { "id": "NEWtestBTC0123", "op": "order", "data": [ { "clOrdId": "", "ordId": "288981657420439575", "tag": "", "sCode": "0", "sMsg": "" } ], "code": "0", "msg": "" } |

Note that this only indicates that the exchange has received the request successfully with an order ID assigned. The order may not entered matching engine at this point in time. Users should check the order state.

## Checking order state

After placing the order, if the order does not return any error (`"sCode": "0"`), OKX always sends out `"state": "live"` from websocket.

Sample message (subscribed to orders channel by instrument type + instrument family):

|  |
| --- |
| { "arg": { "channel": "orders", "instType": "SWAP", "instFamily": "BTC-USDT" }, "data": [ { "accFillSz": "0", "amendResult": "", "avgPx": "", "cTime": "1615170596148", "category": "normal", "ccy": "", "clOrdId": "testBTC0123", "code": "0", "fee": "0", "feeCcy": "USDT", "fillPx": "", "fillSz": "0", "fillTime": "", "instId": "BTC-USDT-SWAP", "instType": "SWAP", "lever": "3", "msg": "", "ordId": "288981657420439575", "ordType": "limit", "pnl": "0", "posSide": "net", "px": "50912.4", "rebate": "0", "rebateCcy": "USDT", "reqId": "", "side": "buy", "slOrdPx": "", "slTriggerPx": "", "state": "live", "sz": "1", "tag": "", "tdMode": "cross", "tpOrdPx": "", "tpTriggerPx": "", "tradeId": "", "uTime": "1615170596148" } ] } |

After the order is filled, the following sample message is pushed with the state changed to `filled`, along with other fill-related fields.

If the order is partially or fully filled, websocket returns `state` = `partially_filled` and `filled` respectively.

For immediate or cancel, fill or kill, and post only orders where orders may be rejected by the matching engine, users will see a `live` then `canceled` state.

User orders can be canceled by the system for various reasons, such as liquidation or self-trade prevention. Users can refer to   
`cancelSource` to see the reason for order cancellation.

The terminal state of an order is either `canceled` or `filled`.

A Trade ID (`tradeId`) will also be set for this fill and can be used for reconciliation with position as shown below.

|  |
| --- |
| { "arg": { "channel": "orders", "instType": "SWAP", "instFamily": "BTC-USDT" }, "data": [ { "accFillSz": "1", "amendResult": "", "avgPx": "50912.4", "cTime": "1615170596148", "category": "normal", "ccy": "", "clOrdId": "testBTC0123", "code": "0", "fee": "-0.1018248", "feeCcy": "USDT", "fillPx": "50912.4", "fillSz": "1", "fillTime": "1615170598021", "instId": "BTC-USDT-SWAP", "instType": "SWAP", "lever": "3", "msg": "", "ordId": "288981657420439575", "ordType": "limit", "pnl": "0", "posSide": "net", "px": "50912.4", "rebate": "0", "rebateCcy": "USDT", "reqId": "", "side": "buy", "slOrdPx": "", "slTriggerPx": "", "state": "filled", "sz": "1", "tag": "", "tdMode": "cross", "tpOrdPx": "", "tpTriggerPx": "", "tradeId": "60477021", "uTime": "1615170598022" } ] } |

Possible order states:

1. Rejected at entry, `sCode` is not 0, no updates from websocket orders channel
2. Placed an order and immediately fully filled: `live` -> `filled`
3. Placed an order and immediately filled by multiple trades: `live` -> `partially_filled` -> ... -> `filled`
4. Placed an order but immediately canceled by matching engine (such as IOC, FOK, post only): `live` -> `canceled` (cancel reason can be referred from cancelSource)
5. Placed an IOC, partially filled, then canceled by system because there is not enough depth in price defined: `live` -> `partially_filled` -> `canceled`

## Amending an order

Order amendment is supported for all instrument types, allowing price amendment (`newPx`) and/or amount (`newSz`) of the order. The cancel on fail (`cxlOnFail`) parameter is also available for order cancellation if the amendment fails.

REST:

[`POST /api/v5/trade/amend-order`](https://my.okx.com/docs-v5/en/#order-book-trading-trade-post-amend-order)

WebSocket operation (`op`) argument:

[`"op": "amend-order"`](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-amend-order)

Similar to placing orders, users should expect an acknowledgement after sending the amend request through REST or WebSocket. Users should refer to `amendResult` from Websocket `orders` channel to determine the outcome of the amendment request.

Note that the order cannot be amended once it is fully filled or canceled.

Successful response only means the request has been accepted by the exchange. Users should refer to websocket orders for the amendment result.

## Canceling an order

Similarly users can cancel the order using REST or WebSocket.

REST:

[`POST /api/v5/trade/cancel-order`](https://my.okx.com/docs-v5/en/#order-book-trading-trade-post-cancel-order)

WebSocket operation (`op`) argument:

[`"op": "cancel-order"`](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-cancel-order)

An acknowledgement will be received after sending the cancel request. The order is only canceled when users receive the order update from the WebSocket orders channel with `"state": "canceled"`.

Note that an order cannot be canceled when it is fully filled or is already canceled.

Successful response only means the request has been accepted by the exchange. Users should refer to websocket orders for cancellation confirmation.

## Batch operations

Batch operations are available for placing, amending, and canceling orders and supports a maximum of 20 orders per request. Orders in each batch request can be of different instrument types.

REST:

|  |  |
| --- | --- |
| Place | POST /api/v5/trade/batch-orders `POST /api/v5/trade/batch-orders` POST /api/v5/trade/batch-orders |
| Amend | POST /api/v5/trade/amend-batch-orders `POST /api/v5/trade/amend-batch-orders` POST /api/v5/trade/amend-batch-orders |
| Cancel | POST /api/v5/trade/cancel-batch-orders `POST /api/v5/trade/cancel-batch-orders` POST /api/v5/trade/cancel-batch-orders |

WebSocket operation (`op`) argument:

|  |  |
| --- | --- |
| Place | "op": "batch-orders" `"op": "batch-orders"` "op": "batch-orders" |
| Amend | "op": "batch-amend-orders" `"op": "batch-amend-orders"` "op": "batch-amend-orders" |
| Cancel | "op": "batch-cancel-orders" `"op": "batch-cancel-orders"` "op": "batch-cancel-orders" |

The batch operation is not all-or-nothing, i.e. it allows part of the order operations to be successful. Upon receiving the acknowledgment after sending a request, users should check the individual `sCode` and `sMsg` fields for each of the orders.

## Order timestamp

There are multiple timestamps within orders data for users to keep track of order states and latency measurements.

`cTime` is the order creation time after risk checks.

`uTime` is the last order updated time. It is updated after order amendment, trade fills, and order cancellation.

`fillTime` is the time when the order is matched. The `fillTime` is the same time as found in the market data trades data.

`inTime` is the time when the request is received at WebSocket / REST gateway. For REST, the time is recorded after authentication.

`outTime` is the time when the response is sent at WebSocket / REST gateway.

## Pagination

OKX offers a pagination function to facilitate users in accessing specific data from extensive datasets. The relevant request parameters are outlined below.

| Parameters | Types | Required | Description |
| --- | --- | --- | --- |
| before | String | No | Pagination of data to return records newer than the requested `ordId` ordId , `billId` billId , `tradeId` tradeId , `ts` ts etc. |
| after | String | No | Pagination of data to return records earlier than the requested `ordId` ordId , `billId` billId , `tradeId` tradeId , `ts` ts etc. |
| limit | String | No | Number of results per request. The maximum is 100. The default is 100. |

For better using this function, please refer to the tips below, assuming the original dataset is [10, 9, 8, 7, 6, 5, 4, 3, 2, 1].

| Tips | Examples |
| --- | --- |
| No matter how users are passing through request parameters, we always return the newest data to users. | We will always return the newly created records at the beginning, e.g. [10, 9, 8, 7, ...] |
| before and after are not included. | If before=6, after=10, the data returned will be [9, 8, 7]. |
| If the record amount between before and after is above the limit, we return the records that are closer to after. | If before=2, after=9, limit=3, the data returned will be [8, 7, 6]. |
| If only before is passed through without after, the data closed to before will be returned. | If before=6, limit=3, the data returned will be [9, 8, 7]. This feature is not applicable for position history, it will return [10, 9, 8]. |

To get data within a specific time range, we also offer timestamp filtering if before/after is used to do the pagination of IDs.

| Parameters | Types | Required | Description |
| --- | --- | --- | --- |
| begin | String | No | Filter with a begin timestamp. Unix timestamp format in milliseconds, e.g. 1597026383085 |
| end | String | No | Filter with an end timestamp. Unix timestamp format in milliseconds, e.g. 1597026383085 |
| limit | String | No | Number of results per request. The maximum is 100. The default is 100. |

The tips differ slightly when using begin/end.

| Tips | Examples |
| --- | --- |
| begin and end are included. | If begin=6, end=10, the data returned will be [10, 9, 8, 7, 6]. |
| If the record amount between begin and end is above the limit, we return the records that are closer to end. If only begin is passed through without after, the data closed to begin will be returned. | If begin=6, limit=3, the data returned will be [8, 7, 6]. This is not applicable to fills, it will return [10, 9, 8]. |

When both "begin/end" and "before/after" parameters are provided, we will first filter the timestamps based on "begin/end" criteria and then paginate the results according to "before/after".

The trading endpoints that have pagination function are listed below.

- [GET / Order List](https://my.okx.com/docs-v5/en/#order-book-trading-trade-get-order-list)
- [GET / Order history (last 7 days)](https://my.okx.com/docs-v5/en/#order-book-trading-trade-get-order-history-last-7-days)
- [GET / Order history (last 3 months)](https://my.okx.com/docs-v5/en/#order-book-trading-trade-get-order-history-last-3-months)
- [GET / Transaction details (last 3 days)](https://my.okx.com/docs-v5/en/#order-book-trading-trade-get-transaction-details-last-3-days)
- [GET / Transaction details (last 3 months)](https://my.okx.com/docs-v5/en/#order-book-trading-trade-get-transaction-details-last-3-months)
- [Get bills details (last 7 days)](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-bills-details-last-7-days)
- [Get bills details (last 3 months)](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-bills-details-last-3-months)
- [Get positions history](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-positions-history)

## Self trade prevention

The trading platform imposes mandatory self trade prevention at master account level, which means the accounts under the same master account, including master account itself and all its affiliated sub-accounts, will be prevented from self trade. The default STP mode is `Cancel Maker`. Users can also utilize the stpMode request parameter of the placing order endpoint to determine the stpMode of a certain order.

OKX supports the following 3 STP modes (`stpMode`): `cancel_maker`, `cancel_taker` and `cancel_both`.

Note that the mandatory STP feature is imposed to all users, all order types, and all order book trading products.

### STP Modes

For self-trade to occur, a user's taker order must be matched with their maker order which has been resting on the order book.

OKX offers 3 modes to define the behaviour to prevent self trade, based on the mode configured in the taker order.

**Cancel Maker**

This is the default STP mode. To prevent self-trading, the maker order will be canceled, then the taker order will continue to match with the next order in the price-time priority.

**Cancel Taker**

The taker order will be canceled to prevent self-trading. If the maker order is lower in the price-time priority, the taker order will be partially filled, then canceled. FOK orders are always honored and will be canceled if it would result in self-trading.

**Cancel Both**

Both taker and maker orders will be canceled to prevent self-trading. If the maker order is lower in the price-time priority, the taker order will be partially filled, then the remaining quantity of the taker and maker order are canceled. FOK orders are not supported in this mode. Only 1 maker order and 1 taker order are canceled.

# Trading account and positions information

## Account

### WebSocket subscription

It is recommended to subscribe to the [`account`](https://my.okx.com/docs-v5/en/#trading-account-websocket-account-channel) channel using WebSocket for receiving account updates. The account channel provides the optional parameter `ccy` to specify the currency of the account.

This endpoint returns equity value in USD and other parameters which are constantly updated due to mark price changes. OKX sends updated data to users regularly upon valuation changes.

Here is a sample request and response after connecting to and logging into the private WebSocket:

| Subscription Type | Account | Account with Specific Currency |
| --- | --- | --- |
| Request | { "op": "subscribe", "args": [ { "channel": "account" } ] } | { "op": "subscribe", "args": [ { "channel": "account", "ccy": "BTC" } ] } |
| Successful response | { "event": "subscribe", "arg": { "channel": "account" } } | { "event": "subscribe", "arg": { "channel": "account", "ccy": "BTC" } } |

### Initial snapshot

Unlike the orders channel, the [`account`](https://my.okx.com/docs-v5/en/#trading-account-websocket-account-channel) channel will publish an initial snapshot for the currencies with a non-zero balance, i.e. non-zero equity, available equity, or available balance.

If the user has too many currencies and the data is too large to be sent in a single push message, it will be split into multiple messages.

Consider an example account with a non-zero balance on BTC and USDT and the account is set to Multi-currency margin and Portfolio margin mode. Users should expect the following sample message from the account channel:

|  |  |
| --- | --- |
| Account Account | Account with Specific Currency Account with Specific Currency |
| { "arg": { "channel": "account" }, "data": [ { "adjEq": "30979.1086748182657014", "details": [ { "availBal": "", "availEq": "18962.59868274799", "ccy": "USDT", "crossLiab": "0", "disEq": "18978.5272656414983116", "eq": "18962.59868274799", "frozenBal": "0", "interest": "0", "isoEq": "0", "isoLiab": "0", "liab": "0", "mgnRatio": "", "ordFrozen": "0", "upl": "0" }, { "availBal": "", "availEq": "0", "ccy": "BTC", "crossLiab": "0.509575622217854", "disEq": "-25408.4180739947324516", "eq": "-0.5096053466363398", "frozenBal": "0", "interest": "0.0000297244184858", "isoEq": "0", "isoLiab": "0", "liab": "0.509575622217854", "mgnRatio": "", "ordFrozen": "0", "upl": "0" } ], "imr": "8469.4726913315758219", "isoEq": "0", "mgnRatio": "39.9556239578938079", "mmr": "762.252542219842", "totalEq": "44480.5383005753085878", "uTime": "1615190165641" } ] } | { "arg": { "channel": "account", "ccy": "BTC" }, "data": [ { "adjEq": "30979.1086748182657014", "details": [ { "availBal": "", "availEq": "0", "ccy": "BTC", "crossLiab": "0.509575622217854", "disEq": "-25408.4180739947324516", "eq": "-0.5096053466363398", "frozenBal": "0", "interest": "0.0000297244184858", "isoEq": "0", "isoLiab": "0", "liab": "0.509575622217854", "mgnRatio": "", "ordFrozen": "0", "upl": "0" } ], "imr": "8469.4726913315758219", "isoEq": "0", "mgnRatio": "39.9556239578938079", "mmr": "762.252542219842", "totalEq": "44480.5383005753085878", "uTime": "1615190165641" } ] } |

### Subsequent updates

Subsequently users will receive account updates driven by the following:

|  |  |
| --- | --- |
| Event-driven updates | Updates driven by events such as placing and canceling orders. Multiple events (e.g. multiple orders being executed at the same time) may be aggregated into one single account update. Only data of the affected currency will be published, including when the currency balance changes to zero. |
| Fixed time updates | Updates pushed at a regular interval (5 seconds as of writing). Similar to the initial snapshot, all currencies (or specified currencies with the ccy parameter) with non-zero balance will be pushed. |

### REST API

Alternatively, users can still invoke the REST API to get the balance for currencies with non-zero balance:

[`GET /api/v5/account/balance`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-balance)

Users can pass an optional parameter using `ccy` with a single currency (e.g. BTC) or multiple currencies (no more than 20) separated with commas (e.g. BTC,USDT,ETH). For example:

[`GET /api/v5/account/balance?ccy=BTC,USDT,ETH`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-balance)

Unlike the account channel in WebSocket, however, the currency balance, regardless of zero balance or not, will always be returned if it is specified using the `ccy` parameter in the REST API, as long as users have possessed that currency before.

## Maximum available tradable amount

With auto-borrow enabled in Multi-currency margin mode, users can buy/sell the instrument exceeding their available cash balance of that currency by borrowing.

In this case, it is useful to retrieve the max available tradable amount of the instrument including the available equity and loanable amount from the exchange.

To do this, poll the following REST API in regular interval:

[`GET /api/v5/account/max-avail-size`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-maximum-available-balance-equity)

See the following sample request and response for BTC-USDT with cross-margin mode under Multi-currency margin mode:

|  |  |
| --- | --- |
| Request | GET /api/v5/account/max-avail-size?instId=BTC-USDT&tdMode=cross |
| Successful Response | { "code": "0", "data": [ { "availBuy": "213800.4239369798722052", "availSell": "1.3539405224369181", "instId": "BTC-USDT" } ], "msg": "" } |

For Spot instruments, `availBuy` is in quote currency and `availSell` is in base currency.

The above response shows a maximum of 213,800.42 USDT is available to buy BTC-USDT, and a maximum of 1.35394052 BTC is available to sell BTC-USDT. This should be the same as the amount users see when trading on the web UI.

## Maximum withdrawal amount

In order to find out the maximum withdrawable amount from the trading account or one of their sub-accounts, users can fetch the amount from [`GET /api/v5/account/max-withdrawal`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-maximum-withdrawals).

The data returned from this endpoint factors in the outstanding loan and margin in use.

## Balance and position

Data will be pushed when triggered by events such as filled order and funding transfer.

The [`balance and position`](https://my.okx.com/docs-v5/en/#trading-account-websocket-balance-and-position-channel) channel applies to getting the account cash balance and the change of position asset.

If the user has too many currencies and the data is too large to be sent in a single push message, it will be split into multiple messages.

Upon changes in account balance or position, this channel with less fields provides the best latency data, compared to the accounts channel and positions channel, in order to push the changes to customers with the lowest latency.

## Positions

It is recommended to retrieve real-time positions data using WebSocket.

### WebSocket subscription

Similar to the orders channel, there are several subscription granularities when subscribing to the [`positions`](https://my.okx.com/docs-v5/en/#trading-account-websocket-positions-channel) channel.

This endpoint returns mark price and other parameters which are constantly updated. OKX regularly sends updated data to users.

To subscribe to the above BTC-USDT-SWAP position updates, users can send one of the following requests after connecting to and logging into the private WebSocket:

| Subscription Method | Instrument Type | Instrument Type + Instrument Family (Derivatives only) | Instrument Type + Instrument ID |
| --- | --- | --- | --- |
| Request | { "op": "subscribe", "args": [ { "channel": "positions", "instType": "SWAP" } ] } | { "op": "subscribe", "args": [ { "channel": "positions", "instType": "SWAP", "instFamily": "BTC-USDT" } ] } | { "op": "subscribe", "args": [ { "channel": "positions", "instType": "SWAP", "instId": "BTC-USDT-SWAP" } ] } |
| Successful response | { "event": "subscribe", "arg": { "channel": "positions", "instType": "SWAP" } } | { "event": "subscribe", "args": [ { "channel": "positions", "instType": "SWAP", "instFamily": "BTC-USDT" } ] } | { "event": "subscribe", "args": [ { "channel": "positions", "instType": "SWAP", "instId": "BTC-USDT-SWAP" } ] } |

Pass `ANY` as instType to subscribe to positions of all product types at once.

### Initial snapshot

The positions channel will publish an initial snapshot for the non-zero positions, i.e. pos > 0 or pos < 0.

In relation to the previous BTC-USDT-SWAP cross margin order (with position net mode) example, the following sample message is expected (subscribed by instrument type + instrument family):

|  |
| --- |
| { "arg": { "channel": "positions", "instType": "SWAP", "instFamily": "BTC-USDT" }, "data": [ { "adl": "2", "availPos": "", "avgPx": "50912.4", "cTime": "1615170596148", "ccy": "USDT", "imr": "165.15734103333082", "instId": "BTC-USDT-SWAP", "instType": "SWAP", "interest": "0", "last": "51000", "lever": "3", "liab": "", "liabCcy": "", "liqPx": "", "margin": "", "mgnMode": "cross", "mgnRatio": "0", "mmr": "1.98188809239997", "optVal": "", "pTime": "1615196199624", "pos": "1", "posCcy": "", "posId": "287999792370819074", "posSide": "net", "tradeId": "60477021", "uTime": "1615170598022", "upl": "0.4520230999924388", "uplRatio": "0.0027394232555804" } ] } |

### Subsequent updates

Similar to the account channel, subsequent users will receive positions updates driven by the following:

|  |  |
| --- | --- |
| Event-driven updates | Updates driven by events such as opening and closing positions. Multiple events (e.g. multiple orders being executed at the same time) may be aggregated into one single position update. Only affected position data will be published, including when the position is closed (i.e., changes to zero). |
| Fixed time updates | Updates pushed at a regular interval (5 seconds as of writing). All non-zero positions that matched the subscription granularity will be pushed. |

### Position ID

There is a Position ID (`posId`) field included in each set of position data that can be used as an optional query parameter when invoking the REST API as shown in the following section.

This field is uniquely generated by combining the below attributes of a position: `mgnMode`, `posSide`, `instId`, and `ccy` are included in the data to uniquely identify the position in the same account. It does not change after closing and reopening the position. A new position ID may be generated for positions that have been closed for a long period of time.

### REST API

Alternatively, users can still invoke the REST API for non-zero positions:

[`GET /api/v5/account/positions`](https://my.okx.com/docs-v5/en/#trading-account-rest-api-get-positions)

The following granularity is available:

| Granularity Granularity | Sample Request Sample Request |
| --- | --- |
| Instrument type | `GET /api/v5/account/positions?instType=SWAP` GET /api/v5/account/positions?instType=SWAP |
| Instrument ID | `GET /api/v5/account/positions?instId=BTC-USDT-SWAP` GET /api/v5/account/positions?instId=BTC-USDT-SWAP |
| Position ID (single) | `GET /api/v5/account/positions?posId=287999792370819074` GET /api/v5/account/positions?posId=287999792370819074 |
| Position ID (multiple, max 20) | `GET /api/v5/account/positions?posId=287999792370819074,289098391880081414` GET /api/v5/account/positions?posId=287999792370819074,289098391880081414 |

Unlike the positions channel in WebSocket, whether it is closed or not, position will always be returned if it is specified in the parameter posId in the REST API as long as the position has been opened before.

## Reconciliation between fill and positions

With the introduction of trade ID (`tradeId`) in the positions channel, it is possible to reconcile order fill (from orders channel) and positions. A possible use case is deriving the position from order fills.

Trade ID uniqueness is per `instId`.

A new order fill always comes with a newer trade ID, thus, users can make use of this to match the relevant position/order fill and compare the tradeID to determine which data is newer.

However, there are few pitfalls:

- Not every order update can be matched to a positions update as multiple position changes can be aggregated into one message — i.e., only last `tradeId` is received.
- Liquidation or ADL does not generate an order update (as the order is determined by the system).
- Positions update caused by liquidation or ADL does not update `tradeId`.

To reconcile between fill and positions properly, users must take into consideration the above pitfalls and compare the position (or make use of position updated timestamp (`uTime`)) apart from comparing `tradeId`.

For example, assume all sequences below are on the same instrument with the same margin mode and the position is in net mode.

| Seq. | Channel | Data | Reconciled Position |
| --- | --- | --- | --- |
| 1 | order | fillSz=20, side=buy, tradeId=150 | 20 |
| 2 | positions | pos=20, tradeId=150, uTime=1614859751636 | 20 |
| 3 | positions | pos=18, tradeId=151, uTime=1614859752637 | 18 |
| 4 | order | fillSz=2, side=sell, tradeId=151 | 18 |
| 5 | order | fillSz=3, side=sell, tradeId=156 | 15 |
| 6 | order | fillSz=1, side=sell, tradeId=158 | 14 |
| 7 | positions | pos=10, tradeId=163, uTime=1614859755037 | 10 |
| 8 | order | fillSz=1, side=sell, tradeId=159 | 10 |
| 9 | order | fillSz=3, side=sell, tradeId=163 | 10 |
| 10 | positions | pos=10, tradeId=163, uTime=1614859755037 | 10 |
| 11 | positions | pos=6, tradeId=163, uTime=1614866547430 | 6 |

Users can observe that:

- Single positions update #7 with `tradeId`=163 means order updates with `tradeId`<=163 can be ignored when reconciling the position — i.e., order update #8 and #9 are ignored in this case.
- Positions update #10 has the same `tradeId` and `pos` (as well as `uTime`) as #7, so it can be assumed #10 is from a fixed time update in a regular interval.
- Positions update #11 has the same `tradeId`=163, but a different position (and newer `uTime`), so it can be assumed that this is triggered by partial liquidation or ADL.

# Identifiers

| Identifier | Description |
| --- | --- |
| ordId | Order ID, globally unique |
| clOrdId | Client Order ID as assigned by the client, unique across all pending orders of all symbols |
| billId | Bill ID, globally unique |
| tradeId | Last trade ID, unique per symbol. For liquidation and ADL scenarios, the tradeId will be assigned a negative value to distinguish it from other matching transaction scenarios. |
| posId | Position ID. This is uniquely generated by combining the below attributes: `mgnMode` mgnMode , `posSide` posSide , `instId` instId , and `ccy` ccy . It does not change after closing and reopening the position. A new position ID may be generated for positions that have been closed for a long period of time; when switching account mode or position mode, the system will also generate a new position ID. |

# System status

Users can get the exchange status from [`GET /api/v5/system/status`](https://my.okx.com/docs-v5/en/#status-get-status).

Subsequent updates will be published from the websocket [`status`](https://my.okx.com/docs-v5/en/#status-ws-status-channel) channel.

Planned system maintenance that may result in short interruption (lasting less than 5 seconds) or websocket disconnection (users can immediately reconnect) will not be announced. The maintenance will only be performed during times of low market volatility.