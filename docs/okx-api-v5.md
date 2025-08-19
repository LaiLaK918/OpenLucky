# OKX API Documentation v5

Source: https://my.okx.com/docs-v5/en/
Converted on: Sun Jul 13 11:49:14 CST 2025

---

# Overview

Welcome to our API documentation. OKX provides REST and WebSocket APIs to suit your trading needs.

## API Resources and Support

### Tutorials

- Learn how to trade with API: [Best practice to OKX’s API](https://my.okx.com/docs-v5/trick_en/#instrument-configuration)
- Learn python spot trading step by step: [Python Spot Trading Tutorial](https://my.okx.com/help/how-can-i-do-spot-trading-with-the-jupyter-notebook)
- Learn python derivatives trading step by step: [Python Derivatives Trading Tutorial](https://my.okx.com/help/how-can-i-do-derivatives-trading-with-the-jupyter-notebook)

### Python libraries

- Use Python SDK for easier integration: [Python SDK](https://pypi.org/project/python-okx/)
- Get access to our market maker python sample code [Python market maker sample](https://github.com/okxapi/okx-sample-market-maker)

### Customer service

- Please take 1 minute to help us improve: [API Satisfaction Survey](https://forms.gle/Ehou2xFv5GE1xUGr9)
- If you have any questions, please consult online customer service

## API key Creation

Please refer to [my api page](https://my.okx.com/account/my-api) regarding API Key creation.

### Generating an API key

Create an API key on the website before signing any requests. After creating an API key, keep the following information safe:

- API key
- Secret key
- Passphrase

The system returns randomly-generated API keys and SecretKeys. You will need to provide the Passphrase to access the API. We store the salted hash of your Passphrase for authentication. We cannot recover the Passphrase if you have lost it. You will need to create a new set of API key.

### API key permissions

There are three permissions below that can be associated with an API key. One or more permission can be assigned to any key.

- `Read` : Can request and view account info such as bills and order history which need read permission
- `Trade` : Can place and cancel orders, funding transfer, make settings which need write permission
- `Withdraw` : Can make withdrawals

### API key security

To improve security, we strongly recommend clients linked the API key to IP addresses  

- Each API key can bind up to 20 IP addresses, which support IPv4/IPv6 and network segment formats.

API keys that are not linked to an IP address and have `trade` or `withdraw` permissions will expire after 14 days of inactivity. (The API key of demo trading will not expire)   

- Only when the user calls an API that requires API key authentication will it be considered as the API key is used.
- Calling an API that does not require API key authentication will not be considered used even if API key information is passed in.
- For websocket, only operation of logging in will be considered to have used the API key. Any operation though the connection after logging in (such as subscribing/placing an order) will not be considered to have used the API key. Please pay attention.

Users can get the usage records of the API key with `trade` or `withdraw` permissions but unlinked to any IP address though [Security Center](https://my.okx.com/account/security).

## REST Authentication

### Making Requests

All private REST requests must contain the following headers:

- `OK-ACCESS-KEY` The API key as a String.
- `OK-ACCESS-SIGN` The Base64-encoded signature (see Signing Messages subsection for details).
- `OK-ACCESS-TIMESTAMP` The UTC timestamp of your request .e.g : 2020-12-08T09:08:57.715Z
- `OK-ACCESS-PASSPHRASE` The passphrase you specified when creating the API key.

Request bodies should have content type `application/json` and be in valid JSON format.

### Signature

> Signing Messages

The `OK-ACCESS-SIGN` header is generated as follows:

- Create a pre-hash string of timestamp + method + requestPath + body (where + represents String concatenation).
- Prepare the SecretKey.
- Sign the pre-hash string with the SecretKey using the HMAC SHA256.
- Encode the signature in the Base64 format.

Example: `sign=CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(timestamp + 'GET' + '/api/v5/account/balance?ccy=BTC', SecretKey))`

The `timestamp` value is the same as the `OK-ACCESS-TIMESTAMP` header with millisecond ISO format, e.g. `2020-12-08T09:08:57.715Z`.

The request method should be in UPPERCASE: e.g. `GET` and `POST`.

The `requestPath` is the path of requesting an endpoint.

Example: `/api/v5/account/balance`

The `body` refers to the String of the request body. It can be omitted if there is no request body (frequently the case for `GET` requests).

Example: `{"instId":"BTC-USDT","lever":"5","mgnMode":"isolated"}`

`GET` request parameters are counted as requestpath, not body

The SecretKey is generated when you create an API key.

Example: `22582BD0CFF14C41EDBF1AB98506286D`

## WebSocket

### Overview

WebSocket is a new HTML5 protocol that achieves full-duplex data transmission between the client and server, allowing data to be transferred effectively in both directions. A connection between the client and server can be established with just one handshake. The server will then be able to push data to the client according to preset rules. Its advantages include:

- The WebSocket request header size for data transmission between client and server is only 2 bytes.
- Either the client or server can initiate data transmission.
- There's no need to repeatedly create and delete TCP connections, saving resources on bandwidth and server.

We recommend developers use WebSocket API to retrieve market data and order book depth.

### Connect

**Connection limit**: 3 requests per second (based on IP)

When subscribing to a public channel, use the address of the public service. When subscribing to a private channel, use the address of the private service

**Request limit**:

The total number of 'subscribe'/'unsubscribe'/'login' requests per connection is limited to 480 times per hour.

If there’s a network problem, the system will automatically disable the connection.

The connection will break automatically if the subscription is not established or data has not been pushed for more than 30 seconds.

To keep the connection stable:

1. Set a timer of N seconds whenever a response message is received, where N is less than 30.

2. If the timer is triggered, which means that no new message is received within N seconds, send the String 'ping'.

3. Expect a 'pong' as a response. If the response message is not received within N seconds, please raise an error or reconnect.

### Connection count limit

The limit will be set at 30 WebSocket connections per specific WebSocket channel per sub-account. Each WebSocket connection is identified by the unique `connId`.

The WebSocket channels subject to this limitation are as follows:

1. [Orders channel](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-order-channel)
2. [Account channel](https://my.okx.com/docs-v5/en/#trading-account-websocket-account-channel)
3. [Positions channel](https://my.okx.com/docs-v5/en/#trading-account-websocket-positions-channel)
4. [Balance and positions channel](https://my.okx.com/docs-v5/en/#trading-account-websocket-balance-and-position-channel)
5. [Position risk warning channel](https://my.okx.com/docs-v5/en/#trading-account-websocket-position-risk-warning)
6. [Account greeks channel](https://my.okx.com/docs-v5/en/#trading-account-websocket-account-greeks-channel)

If users subscribe to the same channel through the same WebSocket connection through multiple arguments, for example, by using `{"channel": "orders", "instType": "ANY"}` and `{"channel": "orders", "instType": "SWAP"}`, it will be counted once only. If users subscribe to the listed channels (such as orders and accounts) using either the same or different connections, it will not affect the counting, as these are considered as two different channels. The system calculates the number of WebSocket connections per channel.

The platform will send the number of active connections to clients through the `channel-conn-count` event message **to new channel subscriptions**.

> Connection count update

```highlight
{
    "event":"channel-conn-count",
    "channel":"orders",
    "connCount": "2",
    "connId":"abcd1234"
}

```

When the limit is breached, generally the latest connection that sends the subscription request will be rejected. Client will receive the usual subscription acknowledgement followed by the `channel-conn-count-error` from the connection that the subscription has been terminated. In exceptional circumstances the platform may unsubscribe existing connections.

> Connection limit error

```highlight
{
    "event": "channel-conn-count-error",
    "channel": "orders",
    "connCount": "20",
    "connId":"a4d3ae55"
}

```

Order operations through WebSocket, including place, amend and cancel orders, are not impacted through this change.

### Login

> Request Example

```highlight
{
  "op": "login",
  "args": [
    {
      "apiKey": "******",
      "passphrase": "******",
      "timestamp": "1538054050",
      "sign": "7L+zFQ+CEgGu5rzCj4+BdV2/uUHGqddA9pI6ztsRRPs="
    }
  ]
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| op | String | Yes | Operation `login` login |
| args | Array of objects | Yes | List of account to login |
| > apiKey | String | Yes | API Key |
| > passphrase | String | Yes | API Key password |
| > timestamp | String | Yes | Unix Epoch time, the unit is seconds |
| > sign | String | Yes | Signature string |

> Successful Response Example

```highlight
{
  "event": "login",
  "code": "0",
  "msg": "",
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "event": "error",
  "code": "60009",
  "msg": "Login failed.",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| event | String | Yes | Operation `login` login `error` error |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

**apiKey**: Unique identification for invoking API. Requires user to apply one manually.

**passphrase**: API Key password

**timestamp**: the Unix Epoch time, the unit is seconds, e.g. 1704876947

**sign**: signature string, the signature algorithm is as follows:

First concatenate `timestamp`, `method`, `requestPath`, strings, then use HMAC SHA256 method to encrypt the concatenated string with SecretKey, and then perform Base64 encoding.

**secretKey**: The security key generated when the user applies for API key, e.g. `22582BD0CFF14C41EDBF1AB98506286D`

**Example of timestamp**: const timestamp = '' + Date.now() / 1,000

**Among sign example**: sign=CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(timestamp +'GET'+'/users/self/verify', secretKey))

**method**: always 'GET'.

**requestPath** : always '/users/self/verify'

The request will expire 30 seconds after the timestamp. If your server time differs from the API server time, we recommended using the REST API to query the API server time and then set the timestamp.

### Subscribe

**Subscription Instructions**

> Request format description

```highlight
{
  "op": "subscribe",
  "args": ["<SubscriptionTopic>"]
}

```

WebSocket channels are divided into two categories: `public` and `private` channels.

`Public channels` -- No authentication is required, include tickers channel, K-Line channel, limit price channel, order book channel, and mark price channel etc.

`Private channels` -- including account channel, order channel, and position channel, etc -- require log in.

Users can choose to subscribe to one or more channels, and the total length of multiple channels cannot exceed 64 KB.

Below is an example of subscription parameters. The requirement of subscription parameters for each channel is different. For details please refer to the specification of each channels.

> Request Example

```highlight
{
    "op":"subscribe",
    "args":[
        {
            "channel":"tickers",
            "instId":"BTC-USDT"
        }
    ]
}

```

**Request parameters**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| op | String | Yes | Operation `subscribe` subscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name |
| > instType | String | No | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION `ANY` ANY |
| > instFamily | String | No | Instrument family Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| > instId | String | No | Instrument ID |

> Response Example

```highlight
{
    "event": "subscribe",
    "arg": {
        "channel": "tickers",
        "instId": "BTC-USDT"
    },
    "connId": "accb8e21"
}

```

**Return parameters**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| event | String | Yes | Event `subscribe` subscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name |
| > instType | String | No | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION `ANY` ANY |
| > instFamily | String | No | Instrument family Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| > instId | String | No | Instrument ID |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

### Unsubscribe

Unsubscribe from one or more channels.

> Request format description

```highlight
{
  "op": "unsubscribe",
  "args": ["< SubscriptionTopic> "]
}

```

> Request Example

```highlight
{
  "op": "unsubscribe",
  "args": [
    {
      "channel": "tickers",
      "instId": "BTC-USDT"
    }
  ]
}

```

**Request parameters**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| op | String | Yes | Operation `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of channels to unsubscribe from |
| > channel | String | Yes | Channel name |
| > instType | String | No | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION `ANY` ANY |
| > instFamily | String | No | Instrument family Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| > instId | String | No | Instrument ID |

> Response Example

```highlight
{
    "event": "unsubscribe",
    "arg": {
        "channel": "tickers",
        "instId": "BTC-USDT"
    },
    "connId": "d0b44253"
}

```

**Response parameters**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| event | String | Yes | Event `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Unsubscribed channel |
| > channel | String | Yes | Channel name |
| > instType | String | No | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION |
| > instFamily | String | No | Instrument family Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| > instId | String | No | Instrument ID |
| code | String | No | Error code |
| msg | String | No | Error message |

### Notification

WebSocket has introduced a new message type (event = `notice`).

Client will receive the information in the following scenarios:

- Websocket disconnect for service upgrade

60 seconds prior to the upgrade of the WebSocket service, the notification message will be sent to users indicating that the connection will soon be disconnected.
Users are encouraged to establish a new connection to prevent any disruptions caused by disconnection.

> Response Example

```highlight
{
    "event": "notice",
    "code": "64008",
    "msg": "The connection will soon be closed for a service upgrade. Please reconnect.",
    "connId": "a4d3ae55"
}

```

The feature is supported by WebSocket Public (/ws/v5/public) and Private (/ws/v5/private) for now.

## Production Trading Services

The Production Trading URL:
- REST: `https://eea.okx.com`
- Public WebSocket: `wss://wseea.okx.com:8443/ws/v5/public`
- Private WebSocket: `wss://wseea.okx.com:8443/ws/v5/private`
- Business WebSocket: `wss://wseea.okx.com:8443/ws/v5/business`

## Demo Trading Services

Currently, the API works for Demo Trading, but some functions are not supported, such as `withdraw`, `deposit`, `purchase/redemption`, etc.

The Demo Trading URL:
- REST: `https://eea.okx.com`
- Public WebSocket: `wss://wseeapap.okx.com:8443/ws/v5/public`
- Private WebSocket: `wss://wseeapap.okx.com:8443/ws/v5/private`
- Business WebSocket: `wss://wseeapap.okx.com:8443/ws/v5/business`

OKX account can be used for login on Demo Trading. If you already have an OKX account, you can log in directly.

Start API Demo Trading by the following steps:  
Login OKX —> Trade —> Demo Trading —> Personal Center —> Demo Trading API -> Create Demo Trading API Key —> Start your Demo Trading

> **Note:** `x-simulated-trading: 1` needs to be added to the header of the Demo Trading request.

> Http Header Example

```highlight
Content-Type: application/json
OK-ACCESS-KEY: 37c541a1-****-****-****-10fe7a038418
OK-ACCESS-SIGN: leaVRETrtaoEQ3yI9qEtI1CZ82ikZ4xSG5Kj8gnl3uw=
OK-ACCESS-PASSPHRASE: 1****6
OK-ACCESS-TIMESTAMP: 2020-03-28T12:21:41.274Z
x-simulated-trading: 1
```

## Account mode

To facilitate your trading experience, please set the appropriate account mode before starting trading.

In the trading account trading system, 4 account modes are supported: `Spot mode`, `Futures mode`, `Multi-currency margin mode`, and `Portfolio margin mode`.

You need to set on the Web/App for the first set of every account mode.

## Production Trading Services

The Production Trading URL:

- REST: `https://eea.okx.com`
- Public WebSocket: `wss://wseea.okx.com:8443/ws/v5/public`
- Private WebSocket: `wss://wseea.okx.com:8443/ws/v5/private`
- Business WebSocket: `wss://wseea.okx.com:8443/ws/v5/business`

## Demo Trading Services

Currently, the API works for Demo Trading, but some functions are not supported, such as `withdraw`,`deposit`,`purchase/redemption`, etc.

The Demo Trading URL:

- REST: `https://eea.okx.com`
- Public WebSocket: `wss://wseeapap.okx.com:8443/ws/v5/public`
- Private WebSocket: `wss://wseeapap.okx.com:8443/ws/v5/private`
- Business WebSocket: `wss://wseeapap.okx.com:8443/ws/v5/business`

OKX account can be used for login on Demo Trading. If you already have an OKX account, you can log in directly.

Start API Demo Trading by the following steps:  
Login OKX —> Trade —> Demo Trading —> Personal Center —> Demo Trading API -> Create Demo Trading API Key —> Start your Demo Trading

Note: `x-simulated-trading: 1` needs to be added to the header of the Demo Trading request.
> Http Header Example

```highlight
Content-Type: application/json

OK-ACCESS-KEY: 37c541a1-****-****-****-10fe7a038418

OK-ACCESS-SIGN: leaVRETrtaoEQ3yI9qEtI1CZ82ikZ4xSG5Kj8gnl3uw=

OK-ACCESS-PASSPHRASE: 1****6

OK-ACCESS-TIMESTAMP: 2020-03-28T12:21:41.274Z

x-simulated-trading: 1

```

## Transaction Timeouts

Orders may not be processed in time due to network delay or busy OKX servers. You can configure the expiry time of the request using `expTime` if you want the order request to be discarded after a specific time.

If `expTime` is specified in the requests for Place (multiple) orders or Amend (multiple) orders, the request will not be processed if the current system time of the server is after the `expTime`.

### REST API

Set the following parameters in the request header

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| expTime | String | No | Request effective deadline. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

The following endpoints are supported:

- [Place order](https://my.okx.com/docs-v5/en/#order-book-trading-trade-post-place-order)
- [Place multiple orders](https://my.okx.com/docs-v5/en/#order-book-trading-trade-post-place-multiple-orders)
- [Amend order](https://my.okx.com/docs-v5/en/#order-book-trading-trade-post-amend-order)
- [Amend multiple orders](https://my.okx.com/docs-v5/en/#order-book-trading-trade-post-amend-multiple-orders)

> Request Example

```highlight
curl -X 'POST' \
  'https://www.okx.com/api/v5/trade/order' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'OK-ACCESS-KEY: *****' \
  -H 'OK-ACCESS-SIGN: *****'' \
  -H 'OK-ACCESS-TIMESTAMP: *****'' \
  -H 'OK-ACCESS-PASSPHRASE: *****'' \
  -H 'expTime: 1597026383085' \   // request effective deadline
  -d '{
  "instId": "BTC-USDT",
  "tdMode": "cash",
  "side": "buy",
  "ordType": "limit",
  "px": "1000",
  "sz": "0.01"
}'

```

### WebSocket

The following parameters are set in the request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| expTime | String | No | Request effective deadline. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

The following endpoints are supported:

- [Place order](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-place-order)
- [Place multiple orders](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-place-multiple-orders)
- [Amend order](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-amend-order)
- [Amend multiple orders](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-amend-multiple-orders)

> Request Example

```highlight
{
    "id": "1512",
    "op": "order",
    "expTime":"1597026383085",  // request effective deadline
    "args": [{
        "side": "buy",
        "instId": "BTC-USDT",
        "tdMode": "isolated",
        "ordType": "market",
        "sz": "100"
    }]
}

```

## Rate Limits

Our REST and WebSocket APIs use rate limits to protect our APIs against malicious usage so our trading platform can operate reliably and fairly.  
When a request is rejected by our system due to rate limits, the system returns error code 50011 (Rate limit reached. Please refer to API documentation and throttle requests accordingly).  
The rate limit is different for each endpoint. You can find the limit for each endpoint from the endpoint details. Rate limit definitions are detailed below:

- WebSocket login and subscription rate limits are based on connection.
- Public unauthenticated REST rate limits are based on IP address.
- Private REST rate limits are based on User ID (sub-accounts have individual User IDs).
- WebSocket order management rate limits are based on User ID (sub-accounts have individual User IDs).

### Trading-related APIs

For Trading-related APIs (place order, cancel order, and amend order) the following conditions apply:

- Rate limits are shared across the REST and WebSocket channels.
- Rate limits for placing orders, amending orders, and cancelling orders are independent from each other.
- Rate limits are defined on the Instrument ID level (except Options)
- Rate limits for Options are defined based on the Instrument Family level. Refer to the [Get instruments](https://my.okx.com/docs-v5/en/#public-data-rest-api-get-instruments) endpoint to view Instrument Family information.
- Rate limits for a multiple order endpoint and a single order endpoint are also independent, with the exception being when there is only one order sent to a multiple order endpoint, the order will be counted as a single order and adopt the single order rate limit.

### Sub-account rate limit

At the sub-account level, we allow a maximum of 1000 order requests per 2 seconds. Only new order requests and amendment order requests will be counted towards this limit. The limit encompasses all requests from the endpoints below. For batch order requests consisting of multiple orders, each order will be counted individually. Error code 50061 is returned when the sub-account rate limit is exceeded. The existing rate limit rule per instrument ID remains unchanged and the existing rate limit and sub-account rate limit will operate in parallel. If clients require a higher rate limit, clients can trade via multiple sub-accounts.

- [POST / Place order](https://my.okx.com/docs-v5/en/#order-book-trading-trade-post-place-order)
- [POST / Place multiple orders](https://my.okx.com/docs-v5/en/#order-book-trading-trade-post-place-multiple-orders)
- [POST / Amend order](https://my.okx.com/docs-v5/en/#order-book-trading-trade-post-amend-order)
- [POST / Amend multiple orders](https://my.okx.com/docs-v5/en/#order-book-trading-trade-post-amend-multiple-orders)
- [WS / Place order](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-place-order)
- [WS / Place multiple orders](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-place-multiple-orders)
- [WS / Amend order](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-amend-order)
- [WS / Amend multiple orders](https://my.okx.com/docs-v5/en/#order-book-trading-trade-ws-amend-multiple-orders)

### Fill ratio based sub-account rate limit

This is only applicable to >= VIP5 customers.
  
As an incentive for more efficient trading, the exchange will offer a higher sub-account rate limit to clients with a high trade fill ratio.
  
  
The exchange calculates two ratios based on the transaction data from the past 7 days at 00:00 UTC.

1. Sub-account fill ratio: This ratio is determined by dividing (the trade volume in USDT of the sub-account) by (sum of (new and amendment request count per symbol \* symbol multiplier) of the sub-account). Note that the master trading account itself is also considered as a sub-account in this context.
2. Master account aggregated fill ratio: This ratio is calculated by dividing (the trade volume in USDT on the master account level) by (the sum (new and amendment count per symbol \* symbol multiplier] of all sub-accounts).

The symbol multiplier allows for fine-tuning the weight of each symbol. A smaller symbol multiplier (<1) is used for smaller pairs that require more updates per trading volume. All instruments have a default symbol multiplier, and some instruments will have overridden symbol multipliers.

| InstType | Override rule | Overridden symbol multiplier | Default symbol multiplier |
| --- | --- | --- | --- |
| Perpetual Futures | Per instrument ID | 1 <br/>Instrument ID: BTC-USDT-SWAP, BTC-USD-SWAP, ETH-USDT-SWAP, ETH-USD-SWAP | 0.2 |
| Expiry Futures | Per instrument Family | 0.3 <br/>Instrument Family: BTC-USDT, BTC-USD, ETH-USDT, ETH-USD | 0.1 |
| Spot | Per instrument ID | 0.5 <br/>Instrument ID: BTC-USDT, ETH-USDT | 0.1 |
| Options | Per instrument Family | - | 0.1 |

The fill ratio computation excludes block trading, spread trading, MMP and fiat orders for order count; and excludes block trading, spread trading for trade volume. Only successful order requests (sCode=0) are considered.

At 08:00 UTC, the system will use the maximum value between the sub-account fill ratio and the master account aggregated fill ratio based on the data snapshot at 00:00 UTC to determine the sub-account rate limit based on the table below. For broker (non-disclosed) clients, the system considers the sub-account fill ratio only.

| Tier | Fill ratio[x<=ratio<y) | Sub-account rate limit per 2 seconds(new and amendment) |
| --- | --- | --- |
| Tier 1 | [0,1) | 1,000 |
| Tier 2 | [1,2) | 1,250 |
| Tier 3 | [2,3) | 1,500 |
| Tier 4 | [3,5) | 1,750 |
| Tier 5 | [5,10) | 2,000 |
| Tier 6 | [10,20) | 2,500 |
| Tier 7 | [20,50) | 3,000 |
| Tier 8 | >= 50 | 10,000 |

If there is an improvement in the fill ratio and rate limit to be uplifted, the uplift will take effect immediately at 08:00 UTC. However, if the fill ratio decreases and the rate limit needs to be lowered, a one-day grace period will be granted, and the lowered rate limit will only be implemented on T+1 at 08:00 UTC. On T+1, if the fill ratio improves, the higher rate limit will be applied accordingly. In the event of client demotion to VIP4, their rate limit will be downgraded to Tier 1, accompanied by a one-day grace period.

If the 7-day trading volume of a sub-account is less than 1,000,000 USDT, the fill ratio of the master account will be applied to it.

For newly created sub-accounts, the Tier 1 rate limit will be applied at creation until T+1 8am UTC, at which the normal rules will be applied.

Block trading, spread trading, MMP and spot/margin orders are exempted from the sub-account rate limit.

The exchange offers [GET / Account rate limit](https://my.okx.com/docs-v5/en/#order-book-trading-trade-get-account-rate-limit) endpoint that provides ratio and rate limit data, which will be updated daily at 8am UTC. It will return the sub-account fill ratio, the master account aggregated fill ratio, current sub-account rate limit and sub-account rate limit on T+1 (applicable if the rate limit is going to be demoted).
  
  
The fill ratio and rate limit calculation example is shown below. Client has 3 accounts, symbol multiplier for BTC-USDT-SWAP = 1 and XRP-USDT = 0.1.

1. Account A (master account):
   1. BTC-USDT-SWAP trade volume = 100 USDT, order count = 10;
   2. XRP-USDT trade volume = 20 USDT, order count = 15;
   3. Sub-account ratio = (100+20) / (10 \* 1 + 15 \* 0.1) = 10.4
2. Account B (sub-account):
   1. BTC-USDT-SWAP trade volume = 200 USDT, order count = 100;
   2. XRP-USDT trade volume = 20 USDT, order count = 30;
   3. Sub-account ratio = (200+20) / (100 \* 1 + 30 \* 0.1) = 2.13
3. Account C (sub-account):
   1. BTC-USDT-SWAP trade volume = 300 USDT, order count = 1000;
   2. XRP-USDT trade volume = 20 USDT, order count = 45;
   3. Sub-account ratio = (300+20) / (100 \* 1 + 45 \* 0.1) = 3.06
4. Master account aggregated fill ratio = (100+20+200+20+300+20) / (10 \* 1 + 15 \* 0.1 + 100 \* 1 + 30 \* 0.1 + 100 \* 1 + 45 \* 0.1) = 3.01
5. Rate limit of accounts
   1. Account A = max(10.4, 3.01) = 10.4 -> 2500 order requests/2s
   2. Account B = max(2.13, 3.01) = 3.01 -> 1750 order requests/2s
   3. Account C = max(3.06, 3.01) = 3.06 -> 1750 order requests/2s

### Best practices

If you require a higher request rate than our rate limit, you can set up different sub-accounts to batch request rate limits. We recommend this method for throttling or spacing out requests in order to maximize each accounts' rate limit and avoid disconnections or rejections.

# Trading Account

The API endpoints of `Account` require authentication.

## REST API

### Get instruments

Retrieve available instruments info of current account.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: User ID + Instrument Type

#### Permission: Read

#### HTTP Request

`GET /api/v5/account/instruments`

> Request Example

```highlight
GET /api/v5/account/instruments?instType=SPOT

```

```highlight
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1" # Production trading: 0, Demo trading: 1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

result = accountAPI.get_instruments(instType="SPOT")
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | Yes | Instrument type `SPOT` SPOT : Spot `MARGIN` MARGIN : Margin `SWAP` SWAP : Perpetual Futures `FUTURES` FUTURES : Expiry Futures `OPTION` OPTION : Option |
| uly | String | Conditional | Underlying Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION .If instType is `OPTION` OPTION , either `uly` uly or `instFamily` instFamily is required. |
| instFamily | String | Conditional | Instrument family Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION . If instType is `OPTION` OPTION , either `uly` uly or `instFamily` instFamily is required. |
| instId | String | No | Instrument ID |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "auctionEndTime": "",
            "baseCcy": "BTC",
            "ctMult": "",
            "ctType": "",
            "ctVal": "",
            "ctValCcy": "",
            "contTdSwTime": "1704876947000",
            "expTime": "",
            "futureSettlement": false,
            "instFamily": "",
            "instId": "BTC-EUR",
            "instType": "SPOT",
            "lever": "",
            "listTime": "1704876947000",
            "lotSz": "0.00000001",
            "maxIcebergSz": "9999999999.0000000000000000",
            "maxLmtAmt": "1000000",
            "maxLmtSz": "9999999999",
            "maxMktAmt": "1000000",
            "maxMktSz": "1000000",
            "maxStopSz": "1000000",
            "maxTriggerSz": "9999999999.0000000000000000",
            "maxTwapSz": "9999999999.0000000000000000",
            "minSz": "0.00001",
            "optType": "",
            "openType": "call_auction",
            "quoteCcy": "EUR",
            "tradeQuoteCcyList": [
                "EUR"
            ],
            "settleCcy": "",
            "state": "live",
            "ruleType": "normal",
            "stk": "",
            "tickSz": "1",
            "uly": ""
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID, e.g. `BTC-USD-SWAP` BTC-USD-SWAP |
| uly | String | Underlying, e.g. `BTC-USD` BTC-USD Only applicable to `MARGIN/FUTURES` MARGIN/FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instFamily | String | Instrument family, e.g. `BTC-USD` BTC-USD Only applicable to `MARGIN/FUTURES` MARGIN/FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| baseCcy | String | Base currency, e.g. `BTC` BTC in `BTC-USDT` BTC-USDT Only applicable to `SPOT` SPOT / `MARGIN` MARGIN |
| quoteCcy | String | Quote currency, e.g. `USDT` USDT in `BTC-USDT` BTC-USDT Only applicable to `SPOT` SPOT / `MARGIN` MARGIN |
| settleCcy | String | Settlement and margin currency, e.g. `BTC` BTC Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| ctVal | String | Contract value Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| ctMult | String | Contract multiplier Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| ctValCcy | String | Contract value currency Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| optType | String | Option type, `C` C : Call `P` P : put Only applicable to `OPTION` OPTION |
| stk | String | Strike price Only applicable to `OPTION` OPTION |
| listTime | String | Listing time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| auctionEndTime | String | The end time of call auction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 Only applicable to `SPOT` SPOT that are listed through call auctions, return "" in other cases (deprecated, use contTdSwTime) |
| contTdSwTime | String | Continuous trading switch time. The switch time from call auction, prequote to continuous trading, Unix timestamp format in milliseconds. e.g. `1597026383085` 1597026383085 . Only applicable to `SPOT` SPOT / `MARGIN` MARGIN that are listed through call auction or prequote, return "" in other cases. |
| openType | String | Open type `fix\_price` fix\_price : fix price opening `pre\_quote` pre\_quote : pre-quote `call\_auction` call\_auction : call auction Only applicable to `SPOT` SPOT / `MARGIN` MARGIN , return "" for all other business lines |
| expTime | String | Expiry time Applicable to `SPOT` SPOT / `MARGIN` MARGIN / `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION . For `FUTURES` FUTURES / `OPTION` OPTION , it is natural delivery/exercise time. It is the instrument offline time when there is `SPOT/MARGIN/FUTURES/SWAP/` SPOT/MARGIN/FUTURES/SWAP/ manual offline. Update once change. |
| lever | String | Max Leverage, Not applicable to `SPOT` SPOT , `OPTION` OPTION |
| tickSz | String | Tick size, e.g. `0.0001` 0.0001 For Option, it is minimum tickSz among tick band, please use "Get option tick bands" if you want get option tickBands. |
| lotSz | String | Lot size If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| minSz | String | Minimum order size If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| ctType | String | Contract type `linear` linear : linear contract `inverse` inverse : inverse contract Only applicable to `FUTURES` FUTURES / `SWAP` SWAP |
| state | String | Instrument status `live` live `suspend` suspend `preopen` preopen e.g. Futures and options contracts rollover from generation to trading start; certain symbols before they go live `test` test : Test pairs, can't be traded |
| ruleType | String | Trading rule types `normal` normal : normal trading `pre\_market` pre\_market : pre-market trading |
| maxLmtSz | String | The maximum order quantity of a single limit order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| maxMktSz | String | The maximum order quantity of a single market order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `USDT` USDT . |
| maxLmtAmt | String | Max USD amount for a single limit order |
| maxMktAmt | String | Max USD amount for a single market order Only applicable to `SPOT` SPOT / `MARGIN` MARGIN |
| maxTwapSz | String | The maximum order quantity of a single TWAP order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . The minimum order quantity of a single TWAP order is minSz\*2 |
| maxIcebergSz | String | The maximum order quantity of a single iceBerg order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| maxTriggerSz | String | The maximum order quantity of a single trigger order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| maxStopSz | String | The maximum order quantity of a single stop market order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `USDT` USDT . |
| futureSettlement | Boolean | Whether daily settlement for expiry feature is enabled Applicable to `FUTURES` FUTURES `cross` cross |
| tradeQuoteCcyList | Array of strings | List of quote currencies available for trading, e.g. ["USD", "USDC"]. |

listTime and contTdSwTime  
For spot symbols listed through a call auction or pre-open, listTime represents the start time of the auction or pre-open, and contTdSwTime indicates the end of the auction or pre-open and the start of continuous trading. For other scenarios, listTime will mark the beginning of continuous trading, and contTdSwTime will return an empty value "".

state  
The state will always change from `preopen` to `live` when the listTime is reached.  
When a product is going to be delisted (e.g. when a FUTURES contract is settled or OPTION contract is exercised), the instrument will not be available.

### Get balance

Retrieve a list of assets (with non-zero balance), remaining balance, and available amount in the trading account.

#### Rate Limit: 10 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/account/balance`

> Request Example

```highlight
# Get the balance of all assets in the account
GET /api/v5/account/balance

# Get the balance of BTC and ETH assets in the account
GET /api/v5/account/balance?ccy=BTC,ETH

```

```highlight
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get account balance
result = accountAPI.get_account_balance()
print(result)

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ccy | String | No | Single currency or multiple currencies (no more than 20) separated with comma, e.g. `BTC` BTC or `BTC,ETH` BTC,ETH . |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "adjEq": "55415.624719833286",
            "availEq": "624719833286",
            "borrowFroz": "0",
            "details": [
                {
                    "availBal": "4834.317093622894",
                    "availEq": "4834.3170936228935",
                    "borrowFroz": "0",
                    "cashBal": "4850.435693622894",
                    "ccy": "USDT",
                    "crossLiab": "0",
                    "collateralEnabled": false,
                    "collateralRestrict": false,
                    "colBorrAutoConversion": "0",
                    "disEq": "4991.542013297616",
                    "eq": "4992.890093622894",
                    "eqUsd": "4991.542013297616",
                    "smtSyncEq": "0",
                    "spotCopyTradingEq": "0",
                    "fixedBal": "0",
                    "frozenBal": "158.573",
                    "imr": "",
                    "interest": "0",
                    "isoEq": "0",
                    "isoLiab": "0",
                    "isoUpl": "0",
                    "liab": "0",
                    "maxLoan": "0",
                    "mgnRatio": "",
                    "mmr": "",
                    "notionalLever": "",
                    "ordFrozen": "0",
                    "rewardBal": "0",
                    "spotInUseAmt": "",
                    "clSpotInUseAmt": "",
                    "maxSpotInUse": "",
                    "spotIsoBal": "0",
                    "stgyEq": "150",
                    "twap": "0",
                    "uTime": "1705449605015",
                    "upl": "-7.545600000000006",
                    "uplLiab": "0",
                    "spotBal": "",
                    "openAvgPx": "",
                    "accAvgPx": "",
                    "spotUpl": "",
                    "spotUplRatio": "",
                    "totalPnl": "",
                    "totalPnlRatio": ""
                }
            ],
            "imr": "0",
            "isoEq": "0",
            "mgnRatio": "",
            "mmr": "0",
            "notionalUsd": "0",
            "notionalUsdForBorrow": "0",
            "notionalUsdForFutures": "0",
            "notionalUsdForOption": "0",
            "notionalUsdForSwap": "0",
            "ordFroz": "",
            "totalEq": "55837.43556134779",
            "uTime": "1705474164160",
            "upl": "0",
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameters Parameters | Types Types | Description Description |
| --- | --- | --- |
| uTime | String | Update time of account information, millisecond format of Unix timestamp, e.g. `1597026383085` 1597026383085 |
| totalEq | String | The total amount of equity in `USD` USD |
| isoEq | String | Isolated margin equity in `USD` USD Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| adjEq | String | Adjusted / Effective equity in `USD` USD The net fiat value of the assets in the account that can provide margins for spot, expiry futures, perpetual futures and options under the cross-margin mode. In multi-ccy or PM mode, the asset and margin requirement will all be converted to USD value to process the order check or liquidation. Due to the volatility of each currency market, our platform calculates the actual USD value of each currency based on discount rates to balance market risks. Applicable to `Multi-currency margin` Multi-currency margin and `Portfolio margin` Portfolio margin |
| availEq | String | Account level available equity, excluding currencies that are restricted due to the collateralized borrowing limit. Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| ordFroz | String | Cross margin frozen for pending orders in `USD` USD Only applicable to `Multi-currency margin` Multi-currency margin |
| imr | String | Initial margin requirement in `USD` USD The sum of initial margins of all open positions and pending orders under cross-margin mode in `USD` USD . Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| mmr | String | Maintenance margin requirement in `USD` USD The sum of maintenance margins of all open positions and pending orders under cross-margin mode in `USD` USD . Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| borrowFroz | String | Potential borrowing IMR of the account in `USD` USD Only applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin . It is "" for other margin modes. |
| mgnRatio | String | Maintenance margin ratio in `USD` USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| notionalUsd | String | Notional value of positions in `USD` USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| notionalUsdForBorrow | String | Notional value for `Borrow` Borrow in USD Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| notionalUsdForSwap | String | Notional value of positions for `Perpetual Futures` Perpetual Futures in USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| notionalUsdForFutures | String | Notional value of positions for `Expiry Futures` Expiry Futures in USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| notionalUsdForOption | String | Notional value of positions for `Option` Option in USD Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| upl | String | Cross-margin info of unrealized profit and loss at the account level in `USD` USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| details | Array of objects | Detailed asset information in all currencies |
| > ccy | String | Currency |
| > eq | String | Equity of currency |
| > cashBal | String | Cash balance |
| > uTime | String | Update time of currency balance information, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > isoEq | String | Isolated margin equity of currency Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > availEq | String | Available equity of currency Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > disEq | String | Discount equity of currency in `USD` USD . Applicable to `Spot mode` Spot mode (enabled spot borrow)/ `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > fixedBal | String | Frozen balance for `Dip Sniper` Dip Sniper and `Peak Sniper` Peak Sniper |
| > availBal | String | Available balance of currency |
| > frozenBal | String | Frozen balance of currency |
| > ordFrozen | String | Margin frozen for open orders Applicable to `Spot mode` Spot mode / `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin |
| > liab | String | Liabilities of currency It is a positive value, e.g. `21625.64` 21625.64 Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > upl | String | The sum of the unrealized profit & loss of all margin and derivatives positions of currency. Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > uplLiab | String | Liabilities due to Unrealized loss of currency Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > crossLiab | String | Cross liabilities of currency Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > isoLiab | String | Isolated liabilities of currency Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > mgnRatio | String | Cross maintenance margin ratio of currency The index for measuring the risk of a certain asset in the account. Applicable to `Futures mode` Futures mode and when there is cross position |
| > imr | String | Cross initial margin requirement at the currency level Applicable to `Futures mode` Futures mode and when there is cross position |
| > mmr | String | Cross maintenance margin requirement at the currency level Applicable to `Futures mode` Futures mode and when there is cross position |
| > interest | String | Accrued interest of currency It is a positive value, e.g. `9.01` 9.01 Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > twap | String | Risk indicator of auto liability repayment Divided into multiple levels from 0 to 5, the larger the number, the more likely the auto repayment will be triggered. Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > maxLoan | String | Max loan of currency Applicable to `cross` cross of `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > eqUsd | String | Equity in `USD` USD of currency |
| > borrowFroz | String | Potential borrowing IMR of currency in `USD` USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin . It is "" for other margin modes. |
| > notionalLever | String | Leverage of currency Applicable to `Futures mode` Futures mode |
| > stgyEq | String | Strategy equity |
| > isoUpl | String | Isolated unrealized profit and loss of currency Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > spotInUseAmt | String | Spot in use amount Applicable to `Portfolio margin` Portfolio margin |
| > spotIsoBal | String | Spot isolated balance Applicable to copy trading Applicable to `Spot mode` Spot mode / `Futures mode` Futures mode |
| > spotBal | String | Spot balance. The unit is currency, e.g. BTC. More details More details |
| > openAvgPx | String | Spot average cost price. The unit is USD. More details More details |
| > accAvgPx | String | Spot accumulated cost price. The unit is USD. More details More details |
| > spotUpl | String | Spot unrealized profit and loss. The unit is USD. More details More details |
| > spotUplRatio | String | Spot unrealized profit and loss ratio. More details More details |
| > totalPnl | String | Spot accumulated profit and loss. The unit is USD. More details More details |
| > totalPnlRatio | String | Spot accumulated profit and loss ratio. More details More details |
| > collateralEnabled | Boolean | `true` true : Collateral enabled `false` false : Collateral disabled Applicable to `Multi-currency margin` Multi-currency margin More details More details |
| > collateralRestrict | Boolean | Platform level collateralized borrow restriction `true` true `false` false |
| > colBorrAutoConversion | String | Indicator of forced repayment when the collateralized borrowing on a crypto reaches the platform limit and users' trading accounts hold this crypto. Divided into multiple levels from 1-5, the larger the number, the more likely the repayment will be triggered. The default will be 0, indicating there is no risk currently. 5 means this user is undergoing auto conversion now. Applicable to `Spot mode` Spot mode / `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |

"" will be returned for inapplicable fields under the current account level.

The currency details will not be returned when cashBal and eq is both 0.

Distribution of applicable fields under each account level are as follows:

| Parameters Parameters | Spot mode Spot mode | Futures mode Futures mode | Multi-currency margin mode Multi-currency margin mode | Portfolio margin mode Portfolio margin mode |
| --- | --- | --- | --- | --- |
| uTime | Yes | Yes | Yes | Yes |
| totalEq | Yes | Yes | Yes | Yes |
| isoEq |  | Yes | Yes | Yes |
| adjEq |  |  | Yes | Yes |
| availEq |  |  | Yes | Yes |
| ordFroz |  |  | Yes | Yes |
| imr |  |  | Yes | Yes |
| mmr |  |  | Yes | Yes |
| mgnRatio |  |  | Yes | Yes |
| notionalUsd |  |  | Yes | Yes |
| notionalUsdForSwap |  |  | Yes | Yes |
| notionalUsdForFutures |  |  | Yes | Yes |
| notionalUsdForOption | Yes |  | Yes | Yes |
| notionalUsdForBorrow | Yes |  | Yes | Yes |
| upl |  |  | Yes | Yes |
| details |  |  | Yes | Yes |
| > ccy | Yes | Yes | Yes | Yes |
| > eq | Yes | Yes | Yes | Yes |
| > cashBal | Yes | Yes | Yes | Yes |
| > uTime | Yes | Yes | Yes | Yes |
| > isoEq |  | Yes | Yes | Yes |
| > availEq |  | Yes | Yes | Yes |
| > disEq | Yes |  | Yes | Yes |
| > availBal | Yes | Yes | Yes | Yes |
| > frozenBal | Yes | Yes | Yes | Yes |
| > ordFrozen | Yes | Yes | Yes | Yes |
| > liab |  |  | Yes | Yes |
| > upl |  | Yes | Yes | Yes |
| > uplLiab |  |  | Yes | Yes |
| > crossLiab |  |  | Yes | Yes |
| > isoLiab |  |  | Yes | Yes |
| > mgnRatio |  | Yes |
| > interest |  |  | Yes | Yes |
| > twap |  |  | Yes | Yes |
| > maxLoan | Yes |  | Yes | Yes |
| > eqUsd | Yes | Yes | Yes | Yes |
| > notionalLever |  | Yes |
| > stgyEq | Yes | Yes | Yes | Yes |
| > isoUpl |  | Yes | Yes | Yes |
| > spotInUseAmt |  |  |  | Yes |
| > spotIsoBal | Yes | Yes |
| > imr |  | Yes |
| > mmr |  | Yes |
| > spotBal | Yes | Yes | Yes | Yes |
| > openAvgPx | Yes | Yes | Yes | Yes |
| > accAvgPx | Yes | Yes | Yes | Yes |
| > spotUpl | Yes | Yes | Yes | Yes |
| > spotUplRatio | Yes | Yes | Yes | Yes |
| > totalPnl | Yes | Yes | Yes | Yes |
| > totalPnlRatio | Yes | Yes | Yes | Yes |

### Get bills details (last 7 days)

Retrieve the bills of the account. The bill refers to all transaction records that result in changing the balance of an account. Pagination is supported, and the response is sorted with the most recent first. This endpoint can retrieve data from the last 7 days.

#### Rate Limit: 5 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/account/bills`

> Request Example

```highlight
GET /api/v5/account/bills

GET /api/v5/account/bills?instType=SPOT

```

```highlight
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get bills details (last 7 days)
result = accountAPI.get_account_bills()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | No | Instrument type `SPOT` SPOT |
| ccy | String | No | Bill currency |
| type | String | No | Bill type `1` 1 : Transfer `2` 2 : Trade `27` 27 : Convert `30` 30 : Simple trade |
| subType | String | No | Bill subtype `1` 1 : Buy `2` 2 : Sell `11` 11 : Transfer in `12` 12 : Transfer out `318` 318 : Convert in `319` 319 : Convert out `320` 320 : Simple buy `321` 321 : Simple sell |
| after | String | No | Pagination of data to return records earlier than the requested bill ID. |
| before | String | No | Pagination of data to return records newer than the requested bill ID. |
| begin | String | No | Filter with a begin timestamp. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| end | String | No | Filter with an end timestamp. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. The maximum is `100` 100 . The default is `100` 100 . |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [{
        "bal": "8694.2179403378290202",
        "balChg": "0.0219338232210000",
        "billId": "623950854533513219",
        "ccy": "USDT",
        "clOrdId": "",
        "execType": "T",
        "fee": "-0.000021955779",
        "fillFwdPx": "",
        "fillIdxPx": "27104.1",
        "fillMarkPx": "",
        "fillMarkVol": "",
        "fillPxUsd": "",
        "fillPxVol": "",
        "fillTime": "1695033476166",
        "from": "",
        "instId": "BTC-USDT",
        "instType": "SPOT",
        "interest": "0",
        "mgnMode": "isolated",
        "notes": "",
        "ordId": "623950854525124608",
        "pnl": "0",
        "posBal": "0",
        "posBalChg": "0",
        "px": "27105.9",
        "subType": "1",
        "sz": "0.021955779",
        "tag": "",
        "to": "",
        "tradeId": "586760148",
        "ts": "1695033476167",
        "type": "2"
    }]
} 

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| instType | String | Instrument type |
| billId | String | Bill ID |
| type | String | Bill type |
| subType | String | Bill subtype |
| ts | String | The time when the balance complete update, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| balChg | String | Change in balance amount at the account level |
| posBalChg | String | Change in balance amount at the position level |
| bal | String | Balance at the account level |
| posBal | String | Balance at the position level |
| sz | String | Quantity For `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION , it is fill quantity or position quantity, the unit is contract. The value is always positive. For other scenarios. the unit is account balance currency( `ccy` ccy ). |
| px | String | Price which related to subType Trade filled price for Trade filled price for `1` 1 : Buy `2` 2 : Sell |
| ccy | String | Account balance currency |
| pnl | String | Profit and loss |
| fee | String | Fee Negative number represents the user transaction fee charged by the platform. Positive number represents rebate. |
| mgnMode | String | Margin mode `isolated` isolated `cross` cross `cash` cash When bills are not generated by trading, the field returns "" |
| instId | String | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| ordId | String | Order ID |
| execType | String | Liquidity taker or maker `T` T : taker `M` M : maker |
| from | String | The remitting account `6` 6 : Funding account `18` 18 : Trading account Only applicable to `transfer` transfer . When bill type is not `transfer` transfer , the field returns "". |
| to | String | The beneficiary account `6` 6 : Funding account `18` 18 : Trading account Only applicable to `transfer` transfer . When bill type is not `transfer` transfer , the field returns "". |
| notes | String | Notes |
| interest | String | Interest |
| tag | String | Order tag |
| fillTime | String | Last filled time |
| tradeId | String | Last traded ID |
| clOrdId | String | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| fillIdxPx | String | Index price at the moment of trade execution For cross currency spot pairs, it returns baseCcy-USDT index price. For example, for LTC-ETH, this field returns the index price of LTC-USDT. |
| fillMarkPx | String | Mark price when filled Applicable to FUTURES/SWAP/OPTIONS, return "" for other instrument types |
| fillPxVol | String | Implied volatility when filled Only applicable to options; return "" for other instrument types |
| fillPxUsd | String | Options price when filled, in the unit of USD Only applicable to options; return "" for other instrument types |
| fillMarkVol | String | Mark volatility when filled Only applicable to options; return "" for other instrument types |
| fillFwdPx | String | Forward price when filled Only applicable to options; return "" for other instrument types |

### Get bills details (last 3 months)

Retrieve the account’s bills. The bill refers to all transaction records that result in changing the balance of an account. Pagination is supported, and the response is sorted with most recent first. This endpoint can retrieve data from the last 3 months.

#### Rate Limit: 5 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/account/bills-archive`

> Request Example

```highlight
GET /api/v5/account/bills-archive

GET /api/v5/account/bills-archive?instType=SPOT

```

```highlight
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get bills details (last 3 months)
result = accountAPI.get_account_bills_archive()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | No | Instrument type `SPOT` SPOT |
| ccy | String | No | Bill currency |
| type | String | No | Bill type `1` 1 : Transfer `2` 2 : Trade `6` 6 : Margin transfer |
| subType | String | No | Bill subtype `1` 1 : Buy `2` 2 : Sell `11` 11 : Transfer in `12` 12 : Transfer out `236` 236 : Easy convert in `237` 237 : Easy convert out |
| after | String | No | Pagination of data to return records earlier than the requested bill ID. |
| before | String | No | Pagination of data to return records newer than the requested bill ID. |
| begin | String | No | Filter with a begin timestamp. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| end | String | No | Filter with an end timestamp. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. The maximum is `100` 100 . The default is `100` 100 . |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [{
        "bal": "8694.2179403378290202",
        "balChg": "0.0219338232210000",
        "billId": "623950854533513219",
        "ccy": "USDT",
        "clOrdId": "",
        "execType": "T",
        "fee": "-0.000021955779",
        "fillFwdPx": "",
        "fillIdxPx": "27104.1",
        "fillMarkPx": "",
        "fillMarkVol": "",
        "fillPxUsd": "",
        "fillPxVol": "",
        "fillTime": "1695033476166",
        "from": "",
        "instId": "BTC-USDT",
        "instType": "SPOT",
        "interest": "0",
        "mgnMode": "isolated",
        "notes": "",
        "ordId": "623950854525124608",
        "pnl": "0",
        "posBal": "0",
        "posBalChg": "0",
        "px": "27105.9",
        "subType": "1",
        "sz": "0.021955779",
        "tag": "",
        "to": "",
        "tradeId": "586760148",
        "ts": "1695033476167",
        "type": "2"
    }]
} 

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| instType | String | Instrument type |
| billId | String | Bill ID |
| type | String | Bill type |
| subType | String | Bill subtype |
| ts | String | The time when the balance complete update, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| balChg | String | Change in balance amount at the account level |
| posBalChg | String | Change in balance amount at the position level |
| bal | String | Balance at the account level |
| posBal | String | Balance at the position level |
| sz | String | Quantity For `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION , it is fill quantity or position quantity, the unit is contract. The value is always positive. For other scenarios. the unit is account balance currency( `ccy` ccy ). |
| px | String | Price which related to subType Trade filled price for Trade filled price for `1` 1 : Buy `2` 2 : Sell |
| ccy | String | Account balance currency |
| pnl | String | Profit and loss |
| fee | String | Fee Negative number represents the user transaction fee charged by the platform. Positive number represents rebate. |
| mgnMode | String | Margin mode `isolated` isolated `cross` cross `cash` cash When bills are not generated by trading, the field returns "" |
| instId | String | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| ordId | String | Order ID When bill type is not `trade` trade , the field returns "" |
| execType | String | Liquidity taker or maker `T` T : taker `M` M : maker |
| from | String | The remitting account `6` 6 : Funding account `18` 18 : Trading account Only applicable to `transfer` transfer . When bill type is not `transfer` transfer , the field returns "". |
| to | String | The beneficiary account `6` 6 : Funding account `18` 18 : Trading account Only applicable to `transfer` transfer . When bill type is not `transfer` transfer , the field returns "". |
| notes | String | Notes |
| interest | String | Interest |
| tag | String | Order tag |
| fillTime | String | Last filled time |
| tradeId | String | Last traded ID |
| clOrdId | String | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| fillIdxPx | String | Index price at the moment of trade execution For cross currency spot pairs, it returns baseCcy-USDT index price. For example, for LTC-ETH, this field returns the index price of LTC-USDT. |
| fillMarkPx | String | Mark price when filled Applicable to FUTURES/SWAP/OPTIONS, return "" for other instrument types |
| fillPxVol | String | Implied volatility when filled Only applicable to options; return "" for other instrument types |
| fillPxUsd | String | Options price when filled, in the unit of USD Only applicable to options; return "" for other instrument types |
| fillMarkVol | String | Mark volatility when filled Only applicable to options; return "" for other instrument types |
| fillFwdPx | String | Forward price when filled Only applicable to options; return "" for other instrument types |

**Funding Fee expense (subType = 173)**  
You may refer to "pnl" for the fee payment

### Apply bills details (since 2021)

Apply for bill data since 1 February, 2021 except for the current quarter.

#### Rate Limit：12 requests per day

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`POST /api/v5/account/bills-history-archive`

> Request Example

```highlight
POST /api/v5/account/bills-history-archive
body
{
    "year":"2023",
    "quarter":"Q1"
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| year | String | Yes | 4 digits year |
| quarter | String | Yes | Quarter, valid value is `Q1` Q1 , `Q2` Q2 , `Q3` Q3 , `Q4` Q4 |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "result": "true",
            "ts": "1646892328000"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| result | String | Whether there is already a download link for this section `true` true : Existed, can check from "Get bills details (since 2021)". `false` false : Does not exist and is generating, can check the download link after 2 hours The data of file is in reverse chronological order using `billId` billId . |
| ts | String | The first request time when the server receives. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

The rule introduction, only applicable to the file generated after 11 October, 2024  
1. Taking 2024 Q2 as an example. The date range are [2024-07-01, 2024-10-01). The begin date is included, The end date is excluded.  
2. The data of file is in reverse chronological order using `billId`

Check the file link from the "Get bills details (since 2021)" endpoint in 2 hours to allow for data generation.   
During peak demand, data generation may take longer. If the file link is still unavailable after 3 hours, reach out to customer support for assistance.

It is only applicable to the data from the unified account.

### Get bills details (since 2021)

Apply for bill data since 1 February, 2021 except for the current quarter.

#### Rate Limit: 10 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/account/bills-history-archive`

> Response Example

```highlight
GET /api/v5/account/bills-history-archive?year=2023&quarter=Q4

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| year | String | Yes | 4 digits year |
| quarter | String | Yes | Quarter, valid value is `Q1` Q1 , `Q2` Q2 , `Q3` Q3 , `Q4` Q4 |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "fileHref": "http://xxx",
            "state": "finished",
            "ts": "1646892328000"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| fileHref | String | Download file link. The expiration of every link is 5 and a half hours. If you already apply the files for the same quarter, then it don’t need to apply again within 30 days. |
| ts | String | The first request time when the server receives. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| state | String | Download link status "finished" "ongoing" "failed": Failed, please apply again |

It is only applicable to the data from the unified account.

#### Field descriptions in the decompressed CSV file

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| billId | String | Bill ID |
| subType | String | Bill subtype |
| ts | String | The time when the balance complete update, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| balChg | String | Change in balance amount at the account level |
| posBalChg | String | Change in balance amount at the position level |
| bal | String | Balance at the account level |
| posBal | String | Balance at the position level |
| sz | String | Quantity |
| px | String | Price which related to subType Trade filled price for Trade filled price for `1` 1 : Buy `2` 2 : Sell `3` 3 : Open long `4` 4 : Open short `5` 5 : Close long `6` 6 : Close short `204` 204 : block trade buy `205` 205 : block trade sell `206` 206 : block trade open long `207` 207 : block trade open short `208` 208 : block trade close long `209` 209 : block trade close short `114` 114 : Forced repayment buy `115` 115 : Forced repayment sell Liquidation Price for Liquidation Price for `100` 100 : Partial liquidation close long `101` 101 : Partial liquidation close short `102` 102 : Partial liquidation buy `103` 103 : Partial liquidation sell `104` 104 : Liquidation long `105` 105 : Liquidation short `106` 106 : Liquidation buy `107` 107 : Liquidation sell `16` 16 : Repay forcibly `17` 17 : Repay interest by borrowing forcibly `110` 110 : Liquidation transfer in `111` 111 : Liquidation transfer out Delivery price for Delivery price for `112` 112 : Delivery long `113` 113 : Delivery short Exercise price for Exercise price for `170` 170 : Exercised `171` 171 : Counterparty exercised `172` 172 : Expired OTM Mark price for Mark price for `173` 173 : Funding fee expense `174` 174 : Funding fee income |
| ccy | String | Account balance currency |
| pnl | String | Profit and loss |
| fee | String | Fee Negative number represents the user transaction fee charged by the platform. Positive number represents rebate. Trading fee rule Trading fee rule |
| mgnMode | String | Margin mode `isolated` isolated `cross` cross `cash` cash When bills are not generated by trading, the field returns "" |
| instId | String | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| ordId | String | Order ID Return order ID when the type is `2` 2 / `5` 5 / `9` 9 Return "" when there is no order. |
| execType | String | Liquidity taker or maker `T` T : taker `M` M : maker |
| interest | String | Interest |
| tag | String | Order tag |
| fillTime | String | Last filled time |
| tradeId | String | Last traded ID |
| clOrdId | String | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| fillIdxPx | String | Index price at the moment of trade execution For cross currency spot pairs, it returns baseCcy-USDT index price. For example, for LTC-ETH, this field returns the index price of LTC-USDT. |
| fillMarkPx | String | Mark price when filled Applicable to FUTURES/SWAP/OPTIONS, return "" for other instrument types |
| fillPxVol | String | Implied volatility when filled Only applicable to options; return "" for other instrument types |
| fillPxUsd | String | Options price when filled, in the unit of USD Only applicable to options; return "" for other instrument types |
| fillMarkVol | String | Mark volatility when filled Only applicable to options; return "" for other instrument types |
| fillFwdPx | String | Forward price when filled Only applicable to options; return "" for other instrument types |

### Get account configuration

Retrieve current account configuration.

#### Rate Limit: 5 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/account/config`

> Request Example

```highlight
GET /api/v5/account/config

```

```highlight
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve current account configuration
result = accountAPI.get_account_config()
print(result)

```

#### Request Parameters

none

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "acctLv": "2",
            "acctStpMode": "cancel_maker",
            "autoLoan": false,
            "ctIsoMode": "automatic",
            "enableSpotBorrow": false,
            "greeksType": "PA",
            "ip": "",
            "type": "0",
            "kycLv": "3",
            "label": "v5 test",
            "level": "Lv1",
            "levelTmp": "",
            "liquidationGear": "-1",
            "mainUid": "44705892343619584",
            "mgnIsoMode": "automatic",
            "opAuth": "1",
            "perm": "read_only,withdraw,trade",
            "posMode": "long_short_mode",
            "roleType": "0",
            "spotBorrowAutoRepay": false,
            "spotOffsetType": "",
            "spotRoleType": "0",
            "spotTraderInsts": [],
            "traderInsts": [],
            "uid": "44705892343619584"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| uid | String | Account ID of current request. |
| mainUid | String | Main Account ID of current request. The current request account is main account if uid = mainUid. The current request account is sub-account if uid != mainUid. |
| acctLv | String | Account mode `1` 1 : Spot mode `2` 2 : Futures mode `3` 3 : Multi-currency margin `4` 4 : Portfolio margin |
| acctStpMode | String | Account self-trade prevention mode `cancel\_maker` cancel\_maker `cancel\_taker` cancel\_taker `cancel\_both` cancel\_both The default value is `cancel\_maker` cancel\_maker . Users can log in to the webpage through the master account to modify this configuration |
| posMode | String | Position mode `long\_short\_mode` long\_short\_mode : long/short, only applicable to `FUTURES` FUTURES / `SWAP` SWAP `net\_mode` net\_mode : net |
| autoLoan | Boolean | Whether to borrow coins automatically `true` true : borrow coins automatically `false` false : not borrow coins automatically |
| greeksType | String | Current display type of Greeks `PA` PA : Greeks in coins `BS` BS : Black-Scholes Greeks in dollars |
| level | String | The user level of the current real trading volume on the platform, e.g `Lv1` Lv1 , which means regular user level. |
| levelTmp | String | Temporary experience user level of special users, e.g `Lv1` Lv1 |
| ctIsoMode | String | Contract isolated margin trading settings `automatic` automatic : Auto transfers `autonomy` autonomy : Manual transfers |
| mgnIsoMode | String | Margin isolated margin trading settings `auto\_transfers\_ccy` auto\_transfers\_ccy : New auto transfers, enabling both base and quote currency as the margin for isolated margin trading `automatic` automatic : Auto transfers `quick\_margin` quick\_margin : Quick Margin Mode (For new accounts, including subaccounts, some defaults will be `automatic` automatic , and others will be `quick\_margin` quick\_margin ) |
| spotOffsetType | String | Risk offset type `1` 1 : Spot-Derivatives(USDT) to be offsetted `2` 2 : Spot-Derivatives(Coin) to be offsetted `3` 3 : Only derivatives to be offsetted Only applicable to `Portfolio margin` Portfolio margin (Deprecated) |
| roleType | String | Role type `0` 0 : General user `1` 1 : Leading trader `2` 2 : Copy trader |
| traderInsts | Array of strings | Leading trade instruments, only applicable to Leading trader |
| spotRoleType | String | SPOT copy trading role type. `0` 0 : General user； `1` 1 : Leading trader； `2` 2 : Copy trader |
| spotTraderInsts | Array of strings | Spot lead trading instruments, only applicable to lead trader |
| opAuth | String | Whether the optional trading was activated `0` 0 : not activate `1` 1 : activated |
| kycLv | String | Main account KYC level `0` 0 : No verification `1` 1 : level 1 completed `2` 2 : level 2 completed `3` 3 : level 3 completed If the request originates from a subaccount, kycLv is the KYC level of the main account. If the request originates from the main account, kycLv is the KYC level of the current account. |
| label | String | API key note of current request API key. No more than 50 letters (case sensitive) or numbers, which can be pure letters or pure numbers. |
| ip | String | IP addresses that linked with current API key, separate with commas if more than one, e.g. `117.37.203.58,117.37.203.57` 117.37.203.58,117.37.203.57 . It is an empty string "" if there is no IP bonded. |
| perm | String | The permission of the current requesting API key or Access token `read\_only` read\_only : Read `trade` trade : Trade `withdraw` withdraw : Withdraw |
| liquidationGear | String | The maintenance margin ratio level of liquidation alert `3` 3 and `-1` -1 means that you will get hourly liquidation alerts on app and channel "Position risk warning" when your margin level drops to or below 300%. `-1` -1 is the initial value which has the same effect as `-3` -3 `0` 0 means that there is not alert |
| enableSpotBorrow | Boolean | Whether borrow is allowed or not in `Spot mode` Spot mode `true` true : Enabled `false` false : Disabled |
| spotBorrowAutoRepay | Boolean | Whether auto-repay is allowed or not in `Spot mode` Spot mode `true` true : Enabled `false` false : Disabled |
| type | String | Account type `0` 0 : Main account `1` 1 : Standard sub-account `2` 2 : Managed trading sub-account `5` 5 : Custody trading sub-account - Copper `9` 9 : Managed trading sub-account - Copper `12` 12 : Custody trading sub-account - Komainu |

### Get maximum order quantity

The maximum quantity to buy or sell. It corresponds to the "sz" from placement.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/account/max-size`

> Request Example

```highlight
GET /api/v5/account/max-size?instId=BTC-USDT&tdMode=cash

```

```highlight
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get maximum buy/sell amount or open amount
result = accountAPI.get_max_order_size(
    instId="BTC-USDT",
    tdMode="cash"
)
print(result)

```

#### Request Parameters

| Parameter Parameter | Type Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Single instrument or multiple instruments (no more than 5) in the smae instrument type separated with comma, e.g. `BTC-USDT,ETH-USDT` BTC-USDT,ETH-USDT |
| tdMode | String | Yes | Trade mode `cash` cash |
| px | String | No | Price The parameter will be ignored when multiple instruments are specified. |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [{
        "ccy": "BTC",
        "instId": "BTC-USDT",
        "maxBuy": "0.0500695098559788",
        "maxSell": "64.4798671570072269"
  }]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instId | String | Instrument ID |
| ccy | String | Currency used for margin |
| maxBuy | String | `SPOT` SPOT : The maximum quantity in base currency that you can buy |
| maxSell | String | `SPOT` SPOT : The maximum quantity in quote currency that you can sell |

### Get maximum available balance/equity

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/account/max-avail-size`

> Request Example

```highlight
# Query maximum available transaction amount for SPOT BTC-USDT
GET /api/v5/account/max-avail-size?instId=BTC-USDT&tdMode=cash

```

```highlight
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get maximum available transaction amount for SPOT BTC-USDT
result = accountAPI.get_max_avail_size(
    instId="BTC-USDT",
    tdMode="cash"
)
print(result)

```

#### Request Parameters

| Parameter Parameter | Type Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Single instrument or multiple instruments (no more than 5) separated with comma, e.g. `BTC-USDT,ETH-USDT` BTC-USDT,ETH-USDT |
| tdMode | String | Yes | Trade mode `cash` cash |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "instId": "BTC-USDT",
      "availBuy": "100",
      "availSell": "1"
    }
  ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instId | String | Instrument ID |
| availBuy | String | Amount available to buy |
| availSell | String | Amount available to sell |

In the case of SPOT, availBuy is in the quote currency, and availSell is in the base currency.  

### Get fee rates

#### Rate Limit: 5 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/account/trade-fee`

> Request Example

```highlight
# Query trade fee rate of SPOT BTC-USDT
GET /api/v5/account/trade-fee?instType=SPOT&instId=BTC-USDT

```

```highlight
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get trading fee rates of current account
result = accountAPI.get_fee_rates(
    instType="SPOT",
    instId="BTC-USDT"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | Yes | Instrument type `SPOT` SPOT |
| instId | String | No | Instrument ID, e.g. `BTC-USDT` BTC-USDT Applicable to `SPOT` SPOT |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [{
    "category": "1", //Deprecated
    "delivery": "",
    "exercise": "",
    "instType": "SPOT",
    "level": "lv1",
    "maker": "-0.0008",
    "makerU": "",
    "makerUSDC": "",
    "taker": "-0.001",
    "takerU": "",
    "takerUSDC": "",
    "ts": "1608623351857",
    "fiat": []
   }
  ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| level | String | Fee rate Level |
| taker | String | For `SPOT` SPOT , it is taker fee rate of the USDT trading pairs. |
| maker | String | For `SPOT` SPOT , it is maker fee rate of the USDT trading pairs. |
| takerU | String | Taker fee rate of USDT-margined contracts, only applicable to `FUTURES` FUTURES / `SWAP` SWAP |
| makerU | String | Maker fee rate of USDT-margined contracts, only applicable to `FUTURES` FUTURES / `SWAP` SWAP |
| delivery | String | Delivery fee rate |
| exercise | String | Fee rate for exercising the option |
| instType | String | Instrument type |
| takerUSDC | String | For `SPOT` SPOT , it is taker fee rate of the USDⓈ&Crypto trading pairs. |
| makerUSDC | String | For `SPOT` SPOT , it is maker fee rate of the USDⓈ&Crypto trading pairs. |
| ts | String | Data return time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| category | String | Currency category. Note: this parameter is already deprecated |
| fiat | Array of objects | Details of fiat fee rate |
| > ccy | String | Fiat currency. |
| > taker | String | Taker fee rate |
| > maker | String | Maker fee rate |

Remarks:   
The fee rate like maker and taker: positive number, which means the rate of rebate; negative number, which means the rate of commission.

USDⓈ represent the stablecoin besides USDT and USDC

## WebSocket

### Account channel

Retrieve account information. Data will be pushed when triggered by events such as placing order, canceling order, transaction execution, etc.
It will also be pushed in regular interval according to subscription granularity.

Concurrent connection to this channel will be restricted by the following rules: [WebSocket connection count limit](https://my.okx.com/docs-v5/en/#overview-websocket-connection-count-limit).

#### URL Path

/ws/v5/private (required login)

> Request Example : single

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "account",
      "ccy": "BTC"
    }
  ]
}

```

```highlight
import asyncio

from okx.websocket.WsPrivateAsync import WsPrivateAsync

def callbackFunc(message):
    print(message)

async def main():

    ws = WsPrivateAsync(
        apiKey = "YOUR_API_KEY",
        passphrase = "YOUR_PASSPHRASE",
        secretKey = "YOUR_SECRET_KEY",
        url = "wss://ws.okx.com:8443/ws/v5/private",
        useServerTime=False
    )
    await ws.start()
    args = [
        {
          "channel": "account",
          "ccy": "BTC"
        }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "account",
      "extraParams": "
        {
          \"updateInterval\": \"0\"
        }
      "
    }
  ]
}

```

```highlight
import asyncio

from okx.websocket.WsPrivateAsync import WsPrivateAsync

def callbackFunc(message):
    print(message)

async def main():

    ws = WsPrivateAsync(
        apiKey = "YOUR_API_KEY",
        passphrase = "YOUR_PASSPHRASE",
        secretKey = "YOUR_SECRET_KEY",
        url = "wss://ws.okx.com:8443/ws/v5/private",
        useServerTime=False
    )
    await ws.start()
    args = [
        {
          "channel": "account",
          "extraParams": "{\"updateInterval\": \"0\"}"
        }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `account` account |
| > ccy | String | No | Currency |
| > extraParams | String | No | Additional configuration |
| >> updateInterval | int | No | `0` 0 : only push due to account events The data will be pushed both by events and regularly if this field is omitted or set to other values than 0. The following format should be strictly obeyed when using this field. "extraParams": " { \"updateInterval\": \"0\" } " |

> Successful Response Example : single

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "account",
    "ccy": "BTC"
  },
  "connId": "a4d3ae55"
}

```

> Successful Response Example

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "account"
  },
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"account\", \"ccy\" : \"BTC\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name `account` account |
| > ccy | String | No | Currency |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example

```highlight
{
    "arg": {
        "channel": "account",
        "uid": "44*********584"
    },
    "eventType": "snapshot",
    "curPage": 1,
    "lastPage": true,
    "data": [{
        "adjEq": "55444.12216906034",
    "availEq": "55415.624719833286",
        "borrowFroz": "0",
        "details": [{
            "availBal": "4734.371190691436",
            "availEq": "4734.371190691435",
            "borrowFroz": "0",
            "cashBal": "4750.426970691436",
            "ccy": "USDT",
            "coinUsdPrice": "0.99927",
            "crossLiab": "0",
      "collateralEnabled": false,
      "collateralRestrict": false,
      "colBorrAutoConversion": "0",
            "disEq": "4889.379316336831",
            "eq": "4892.951170691435",
            "eqUsd": "4889.379316336831",
            "smtSyncEq": "0",
            "spotCopyTradingEq": "0",
            "fixedBal": "0",
            "frozenBal": "158.57998",
            "imr": "",
            "interest": "0",
            "isoEq": "0",
            "isoLiab": "0",
            "isoUpl": "0",
            "liab": "0",
            "maxLoan": "0",
            "mgnRatio": "",
            "mmr": "",
            "notionalLever": "",
            "ordFrozen": "0",
            "rewardBal": "0",
            "spotInUseAmt": "",
            "clSpotInUseAmt": "",
            "maxSpotInUseAmt": "",          
            "spotIsoBal": "0",
            "stgyEq": "150",
            "twap": "0",
            "uTime": "1705564213903",
            "upl": "-7.475800000000003",
            "uplLiab": "0",
            "spotBal": "",
            "openAvgPx": "",
            "accAvgPx": "",
            "spotUpl": "",
            "spotUplRatio": "",
            "totalPnl": "",
            "totalPnlRatio": ""
        }],
        "imr": "0",
        "isoEq": "0",
        "mgnRatio": "",
        "mmr": "0",
        "notionalUsd": "0",
        "notionalUsdForBorrow": "0",
        "notionalUsdForFutures": "0",
        "notionalUsdForOption": "0",
        "notionalUsdForSwap": "0",
        "ordFroz": "0",
        "totalEq": "",
        "uTime": "1705564223311",
        "upl": "0"
    }]
}

```

#### Push data parameters

| Parameters Parameters | Types Types | Description Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| > uid | String | User Identifier |
| eventType | String | Event type: `snapshot` snapshot : Initial and regular snapshot push `event\_update` event\_update : Event-driven update push |
| curPage | Integer | Current page number. Only applicable for `snapshot` snapshot events. Not included in `event\_update` event\_update events. |
| lastPage | Boolean | Whether this is the last page of pagination: `true` true `false` false Only applicable for `snapshot` snapshot events. Not included in `event\_update` event\_update events. |
| data | Array of objects | Subscribed data |
| > uTime | String | The latest time to get account information, millisecond format of Unix timestamp, e.g. `1597026383085` 1597026383085 |
| > totalEq | String | The total amount of equity in `USD` USD |
| > isoEq | String | Isolated margin equity in `USD` USD Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > adjEq | String | Adjusted / Effective equity in `USD` USD The net fiat value of the assets in the account that can provide margins for spot, expiry futures, perpetual futures and options under the cross-margin mode. In multi-ccy or PM mode, the asset and margin requirement will all be converted to USD value to process the order check or liquidation. Due to the volatility of each currency market, our platform calculates the actual USD value of each currency based on discount rates to balance market risks. Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > availEq | String | Account level available equity, excluding currencies that are restricted due to the collateralized borrowing limit. Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > ordFroz | String | Margin frozen for pending cross orders in `USD` USD Only applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin |
| > imr | String | Initial margin requirement in `USD` USD The sum of initial margins of all open positions and pending orders under cross-margin mode in `USD` USD . Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > mmr | String | Maintenance margin requirement in `USD` USD The sum of maintenance margins of all open positions and pending orders under cross-margin mode in `USD` USD . Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > borrowFroz | String | Potential borrowing IMR of the account in `USD` USD Only applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin . It is "" for other margin modes. |
| > mgnRatio | String | Maintenance margin ratio in `USD` USD . Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > notionalUsd | String | Notional value of positions in `USD` USD Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > notionalUsdForBorrow | String | Notional value for `Borrow` Borrow in USD Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > notionalUsdForSwap | String | Notional value of positions for `Perpetual Futures` Perpetual Futures in USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > notionalUsdForFutures | String | Notional value of positions for `Expiry Futures` Expiry Futures in USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > notionalUsdForOption | String | Notional value of positions for `Option` Option in USD Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > upl | String | Cross-margin info of unrealized profit and loss at the account level in `USD` USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > details | Array of objects | Detailed asset information in all currencies |
| >> ccy | String | Currency |
| >> eq | String | Equity of currency |
| >> cashBal | String | Cash Balance |
| >> uTime | String | Update time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| >> isoEq | String | Isolated margin equity of currency Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> availEq | String | Available equity of currency Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> disEq | String | Discount equity of currency in `USD` USD |
| >> fixedBal | String | Frozen balance for `Dip Sniper` Dip Sniper and `Peak Sniper` Peak Sniper |
| >> availBal | String | Available balance of currency |
| >> frozenBal | String | Frozen balance of currency |
| >> ordFrozen | String | Margin frozen for open orders Applicable to `Spot mode` Spot mode / `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin |
| >> liab | String | Liabilities of currency It is a positive value, e.g. `21625.64` 21625.64 . Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> upl | String | The sum of the unrealized profit & loss of all margin and derivatives positions of currency. Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> uplLiab | String | Liabilities due to Unrealized loss of currency Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> crossLiab | String | Cross Liabilities of currency Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> isoLiab | String | Isolated Liabilities of currency Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> rewardBal | String | Trial fund balance |
| >> mgnRatio | String | Cross Maintenance margin ratio of currency The index for measuring the risk of a certain asset in the account. Applicable to `Futures mode` Futures mode and when there is cross position |
| >> imr | String | Cross initial margin requirement at the currency level Applicable to `Futures mode` Futures mode and when there is cross position |
| >> mmr | String | Cross maintenance margin requirement at the currency level Applicable to `Futures mode` Futures mode and when there is cross position |
| >> interest | String | Interest of currency It is a positive value, e.g."9.01". Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> twap | String | System is forced repayment(TWAP) indicator Divided into multiple levels from 0 to 5, the larger the number, the more likely the auto repayment will be triggered. Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> maxLoan | String | Max loan of currency Applicable to `cross` cross of `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> eqUsd | String | Equity `USD` USD of currency |
| >> borrowFroz | String | Potential borrowing IMR of currency in `USD` USD Only applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin . It is "" for other margin modes. |
| >> notionalLever | String | Leverage of currency Applicable to `Futures mode` Futures mode |
| >> coinUsdPrice | String | Price index `USD` USD of currency |
| >> stgyEq | String | strategy equity |
| >> isoUpl | String | Isolated unrealized profit and loss of currency Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> spotInUseAmt | String | Spot in use amount Applicable to `Portfolio margin` Portfolio margin |
| >> clSpotInUseAmt | String | User-defined spot risk offset amount Applicable to `Portfolio margin` Portfolio margin |
| >> maxSpotInUseAmt | String | Max possible spot risk offset amount Applicable to `Portfolio margin` Portfolio margin |
| >> spotIsoBal | String | Spot isolated balance Applicable to copy trading Applicable to `Spot mode` Spot mode / `Futures mode` Futures mode |
| >> smtSyncEq | String | Smart sync equity The default is "0", only applicable to copy trader. |
| >> spotCopyTradingEq | String | Spot smart sync equity. The default is "0", only applicable to copy trader. |
| >> spotBal | String | Spot balance. The unit is currency, e.g. BTC. More details More details |
| >> openAvgPx | String | Spot average cost price. The unit is USD. More details More details |
| >> accAvgPx | String | Spot accumulated cost price. The unit is USD. More details More details |
| >> spotUpl | String | Spot unrealized profit and loss. The unit is USD. More details More details |
| >> spotUplRatio | String | Spot unrealized profit and loss ratio. More details More details |
| >> totalPnl | String | Spot accumulated profit and loss. The unit is USD. More details More details |
| >> totalPnlRatio | String | Spot accumulated profit and loss ratio. More details More details |
| >> collateralEnabled | Boolean | `true` true : Collateral enabled `false` false : Collateral disabled Applicable to `Multi-currency margin` Multi-currency margin |
| >> collateralRestrict | Boolean | Platform level collateralized borrow restriction `true` true `false` false |
| >> colBorrAutoConversion | String | Indicator of forced repayment when the collateralized borrowing on a crypto reaches the platform limit and users' trading accounts hold this crypto. Divided into multiple levels from 1-5, the larger the number, the more likely the repayment will be triggered. The default will be 0, indicating there is no risk currently. 5 means this user is undergoing auto conversion now. Applicable to `Spot mode` Spot mode / `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |

"" will be returned for inapplicable fields under the current account level.

  
 - The account data is sent on event basis and regular basis.
  
 - The event push is not pushed in real-time. It is aggregated and pushed at a fixed time interval, around 50ms. For example, if multiple events occur within a fixed time interval, the system will aggregate them into a single message and push it at the end of the fixed time interval. If the data volume is too large, it may be split into multiple messages.
  
 - The regular push sends updates regardless of whether there are activities in the trading account or not.

  
 - Only currencies with non-zero balance will be pushed. Definition of non-zero balance: any value of eq, availEq, availBql parameters is not 0. If the data is too large to be sent in a single push message, it will be split into multiple messages.
  
 - For example, when subscribing to account channel without specifying ccy and there are 5 currencies are with non-zero balance, all 5 currencies data will be pushed in initial snapshot and in regular update. Subsequently when there is change in balance or equity of an token, only the incremental data of that currency will be pushed triggered by this change.

# Order Book Trading

## Trade

All `Trade` API endpoints require authentication.

### POST / Place order

You can place an order only if you have sufficient funds.

#### Rate Limit: 60 requests per 2 seconds

#### Rate limit rule : User ID + Instrument ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/trade/order`

> Request Example

```highlight
 place order for SPOT
 POST /api/v5/trade/order
 body
 {
    "instId":"BTC-USDT",
    "tdMode":"cash",
    "clOrdId":"b15",
    "side":"buy",
    "ordType":"limit",
    "px":"2.15",
    "sz":"2"
}

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Spot mode, limit order
result = tradeAPI.place_order(
    instId="BTC-USDT",
    tdMode="cash",
    clOrdId="b15",
    side="buy",
    ordType="limit",
    px="2.15",
    sz="2"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| tdMode | String | Yes | Trade mode `cash` cash |
| clOrdId | String | No | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| tag | String | No | Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters. |
| side | String | Yes | Order side `buy` buy `sell` sell |
| ordType | String | Yes | Order type `market` market : Market order `limit` limit : Limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order |
| sz | String | Yes | Quantity to buy or sell |
| px | String | Conditional | Order price. Only applicable to `limit` limit , `post\_only` post\_only , `fok` fok , `ioc` ioc order. |
| tgtCcy | String | No | Whether the target currency uses the quote or base currency. `base\_ccy` base\_ccy : Base currency `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| banAmend | Boolean | No | Whether to disallow the system from amending the size of the SPOT Market Order. Valid options: `true` true or `false` false . The default value is `false` false . If `true` true , system will not amend and reject the market order if user does not have sufficient funds. Only applicable to SPOT Market Orders |
| stpId | String | No | Self trade prevention ID. Orders from the same master account with the same ID will be prevented from self trade. Numerical integers defined by user in the range of 1<= x<= 999999999 (deprecated) |
| stpMode | String | No | Self trade prevention mode. Default to cancel maker `cancel\_maker` cancel\_maker , `cancel\_taker` cancel\_taker , `cancel\_both` cancel\_both Cancel both does not support FOK. |
| tradeQuoteCcy | String | No | The quote currency used for trading. Only applicable to `SPOT` SPOT . The default value is the quote currency of the `instId` instId , for example: for `BTC-USD` BTC-USD , the default is `USD` USD . |
| attachAlgoOrds | Array of objects | No | TP/SL information attached when placing order |
| > attachAlgoClOrdId | String | No | Client-supplied Algo ID when placing order attaching TP/SL A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to `algoClOrdId` algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > tpTriggerPx | String | Conditional | Take-profit trigger price If you fill in this parameter, you should fill in the take-profit order price as well. |
| > tpOrdPx | String | Conditional | Take-profit order price If you fill in this parameter, you should fill in the take-profit trigger price as well. If the price is -1, take-profit will be executed at the market price. |
| > slTriggerPx | String | Conditional | Stop-loss trigger price If you fill in this parameter, you should fill in the stop-loss order price. |
| > slOrdPx | String | Conditional | Stop-loss order price If you fill in this parameter, you should fill in the stop-loss trigger price. If the price is -1, stop-loss will be executed at the market price. |
| > tpTriggerPxType | String | No | Take-profit trigger price type `last` last : last price The default is last |
| > slTriggerPxType | String | No | Stop-loss trigger price type `last` last : last price The default is last |
| > sz | String | Conditional | Size. Only applicable to TP order of split TPs, and it is required for TP order of split TPs |
| > amendPxOnTriggerType | String | No | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. Whether `slTriggerPx` slTriggerPx will move to `avgPx` avgPx when the first TP order is triggered `0` 0 : disable, the default value `1` 1 : Enable |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "clOrdId": "oktswap6",
      "ordId": "312269865356374016",
      "tag": "",
      "sCode": "0",
      "sMsg": ""
    }
  ],
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| code | String | The result code, `0` 0 means success |
| msg | String | The error message, empty if the code is 0 |
| data | Array of objects | Array of objects contains the response results |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > tag | String | Order tag |
| > sCode | String | The code of the event execution result, `0` 0 means success. |
| > sMsg | String | Rejection or success message of event execution. |
| inTime | String | Timestamp at REST gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 The time is recorded after authentication. |
| outTime | String | Timestamp at REST gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

clOrdId  
clOrdId is a user-defined unique ID used to identify the order. It will be included in the response parameters if you have specified during order submission, and can be used as a request parameter to the endpoints to query, cancel and amend orders.   
clOrdId must be unique among the clOrdIds of all pending orders.

ordType   
Order type. When creating a new order, you must specify the order type. The order type you specify will affect: 1) what order parameters are required, and 2) how the matching system executes your order. The following are valid order types:   
limit: Limit order, which requires specified sz and px.   
market: Market order. For SPOT and MARGIN, market order will be filled with market price (by swiping opposite order book). For Expiry Futures and Perpetual Futures, market order will be placed to order book with most aggressive price allowed by Price Limit Mechanism. For OPTION, market order is not supported yet. As the filled price for market orders cannot be determined in advance, OKX reserves/freezes your quote currency by an additional 5% for risk check.   
post\_only: Post-only order, which the order can only provide liquidity to the market and be a maker. If the order would have executed on placement, it will be canceled instead.   
fok: Fill or kill order. If the order cannot be fully filled, the order will be canceled. The order would not be partially filled.   
ioc: Immediate or cancel order. Immediately execute the transaction at the order price, cancel the remaining unfilled quantity of the order, and the order quantity will not be displayed in the order book.   
optimal\_limit\_ioc: Market order with ioc (immediate or cancel). Immediately execute the transaction of this market order, cancel the remaining unfilled quantity of the order, and the order quantity will not be displayed in the order book. Only applicable to Expiry Futures and Perpetual Futures.

sz  
Quantity to buy or sell.   
For SPOT Buy and Sell Limit Orders, it refers to the quantity in base currency.   
For SPOT Buy Market Orders, it refers to the quantity in quote currency.   
For SPOT Sell Market Orders, it refers to the quantity in base currency.   
For SPOT Market Orders, it is set by tgtCcy.

tgtCcy  
This parameter is used to specify the order quantity in the order request is denominated in the quantity of base or quote currency. This is applicable to SPOT Market Orders only.  
Base currency: base\_ccy  
Quote currency: quote\_ccy
  
If you use the Base Currency quantity for buy market orders or the Quote Currency for sell market orders, please note:
  
1. If the quantity you enter is greater than what you can buy or sell, the system will execute the order according to your maximum buyable or sellable quantity. If you want to trade according to the specified quantity, you should use Limit orders.
  
2. When the market price is too volatile, the locked balance may not be sufficient to buy the Base Currency quantity or sell to receive the Quote Currency that you specified. We will change the quantity of the order to execute the order based on best effort principle based on your account balance. In addition, we will try to over lock a fraction of your balance to avoid changing the order quantity.
  
2.1 Example of base currency buy market order:
  
Taking the market order to buy 10 LTCs as an example, and the user can buy 11 LTC. At this time, if 10 < 11, the order is accepted. When the LTC-USDT market price is 200, and the locked balance of the user is 3,000 USDT, as 200\*10 < 3,000, the market order of 10 LTC is fully executed;
If the market is too volatile and the LTC-USDT market price becomes 400, 400\*10 > 3,000, the user's locked balance is not sufficient to buy using the specified amount of base currency, the user's maximum locked balance of 3,000 USDT will be used to settle the trade. Final transaction quantity becomes 3,000/400 = 7.5 LTC.
  
2.2 Example of quote currency sell market order:
  
Taking the market order to sell 1,000 USDT as an example, and the user can sell 1,200 USDT, 1,000 < 1,200, the order is accepted. When the LTC-USDT market price is 200, and the locked balance of the user is 6 LTC, as 1,000/200 < 6, the market order of 1,000 USDT is fully executed;
If the market is too volatile and the LTC-USDT market price becomes 100, 100\*6 < 1,000, the user's locked balance is not sufficient to sell using the specified amount of quote currency, the user's maximum locked balance of 6 LTC will be used to settle the trade. Final transaction quantity becomes 6 \* 100 = 600 USDT.

For placing order with TP/Sl, TP/SL algo order will be generated only when this order is filled fully, or there is no TP/SL algo order generated.

Mandatory self trade prevention (STP)  
The trading platform imposes mandatory self trade prevention at master account level, which means the accounts under the same master account, including master account itself and all its affiliated sub-accounts, will be prevented from self trade. The default STP mode is `Cancel Maker`. Users can also utilize the stpMode request parameter of the placing order endpoint to determine the stpMode of a certain order.  
Mandatory self trade prevention will not lead to latency.   
There are three STP modes. The STP mode is always taken based on the configuration in the taker order.  
1. Cancel Maker: This is the default STP mode, which cancels the maker order to prevent self-trading. Then, the taker order continues to match with the next order based on the order book priority.  
2. Cancel Taker: The taker order is canceled to prevent self-trading. If the user's own maker order is lower in the order book priority, the taker order is partially filled and then canceled. FOK orders are always honored and canceled if they would result in self-trading.  
3. Cancel Both: Both taker and maker orders are canceled to prevent self-trading. If the user's own maker order is lower in the order book priority, the taker order is partially filled. Then, the remaining quantity of the taker order and the first maker order are canceled. FOK orders are not supported in this mode.

### POST / Place multiple orders

Place orders in batches. Maximum 20 orders can be placed per request.   
Request parameters should be passed in the form of an array. Orders will be placed in turn

#### Rate Limit: 300 orders per 2 seconds

#### Rate limit rule: User ID + Instrument ID

#### Permission: Trade

Unlike other endpoints, the rate limit of this endpoint is determined by the number of orders. If there is only one order in the request, it will consume the rate limit of `Place order`.

#### HTTP Request

`POST /api/v5/trade/batch-orders`

> Request Example

```highlight
# batch place order for SPOT
POST /api/v5/trade/batch-orders
body
[
    {
        "instId":"BTC-USDT",
        "tdMode":"cash",
        "clOrdId":"b15",
        "side":"buy",
        "ordType":"limit",
        "px":"2.15",
        "sz":"2"
    },
    {
        "instId":"BTC-USDT",
        "tdMode":"cash",
        "clOrdId":"b16",
        "side":"buy",
        "ordType":"limit",
        "px":"2.15",
        "sz":"2"
    }
]

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Place multiple orders 
place_orders_without_clOrdId = [
    {"instId": "BTC-USDT", "tdMode": "cash", "clOrdId": "b15", "side": "buy", "ordType": "limit", "px": "2.15", "sz": "2"},
    {"instId": "BTC-USDT", "tdMode": "cash", "clOrdId": "b16", "side": "buy", "ordType": "limit", "px": "2.15", "sz": "2"}
]

result = tradeAPI.place_multiple_orders(place_orders_without_clOrdId)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| tdMode | String | Yes | Trade mode `cash` cash |
| clOrdId | String | No | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| tag | String | No | Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters. |
| side | String | Yes | Order side `buy` buy `sell` sell |
| ordType | String | Yes | Order type `market` market : Market order `limit` limit : Limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order |
| sz | String | Yes | Quantity to buy or sell |
| px | String | Conditional | Order price. Only applicable to `limit` limit , `post\_only` post\_only , `fok` fok , `ioc` ioc order. |
| tgtCcy | String | No | Whether the target currency uses the quote or base currency. `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| banAmend | Boolean | No | Whether to disallow the system from amending the size of the SPOT Market Order. Valid options: `true` true or `false` false . The default value is `false` false . If `true` true , system will not amend and reject the market order if user does not have sufficient funds. Only applicable to SPOT Market Orders |
| stpId | String | No | Self trade prevention ID. Orders from the same master account with the same ID will be prevented from self trade. Numerical integers defined by user in the range of 1<= x<= 999999999 (deprecated) |
| stpMode | String | No | Self trade prevention mode. Default to cancel maker `cancel\_maker` cancel\_maker , `cancel\_taker` cancel\_taker , `cancel\_both` cancel\_both Cancel both does not support FOK. |
| tradeQuoteCcy | String | No | The quote currency used for trading. Only applicable to `SPOT` SPOT . The default value is the quote currency of the `instId` instId , for example: for `BTC-USD` BTC-USD , the default is `USD` USD . |
| attachAlgoOrds | Array of objects | No | TP/SL information attached when placing order |
| > attachAlgoClOrdId | String | No | Client-supplied Algo ID when placing order attaching TP/SL A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to `algoClOrdId` algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > tpTriggerPx | String | Conditional | Take-profit trigger price If you fill in this parameter, you should fill in the take-profit order price as well. |
| > tpOrdPx | String | Conditional | Take-profit order price If you fill in this parameter, you should fill in the take-profit trigger price as well. If the price is -1, take-profit will be executed at the market price. |
| > slTriggerPx | String | Conditional | Stop-loss trigger price If you fill in this parameter, you should fill in the stop-loss order price. |
| > slOrdPx | String | Conditional | Stop-loss order price If you fill in this parameter, you should fill in the stop-loss trigger price. If the price is -1, stop-loss will be executed at the market price. |
| > tpTriggerPxType | String | No | Take-profit trigger price type `last` last : last price The default is last |
| > slTriggerPxType | String | No | Stop-loss trigger price type `last` last : last price The default is last |
| > sz | String | Conditional | Size. Only applicable to TP order of split TPs, and it is required for TP order of split TPs |
| > amendPxOnTriggerType | String | No | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. Whether `slTriggerPx` slTriggerPx will move to `avgPx` avgPx when the first TP order is triggered `0` 0 : disable, the default value `1` 1 : Enable |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "clOrdId":"oktswap6",
            "ordId":"12345689",
            "tag":"",
            "sCode":"0",
            "sMsg":""
        },
        {
            "clOrdId":"oktswap7",
            "ordId":"12344",
            "tag":"",
            "sCode":"0",
            "sMsg":""
        }
    ],
    "inTime": "1695190491421339",
    "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| code | String | The result code, `0` 0 means success |
| msg | String | The error message, empty if the code is 0 |
| data | Array of objects | Array of objects contains the response results |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > tag | String | Order tag |
| > sCode | String | The code of the event execution result, `0` 0 means success. |
| > sMsg | String | Rejection or success message of event execution. |
| inTime | String | Timestamp at REST gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 The time is recorded after authentication. |
| outTime | String | Timestamp at REST gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

clOrdId  
clOrdId is a user-defined unique ID used to identify the order. It will be included in the response parameters if you have specified during order submission, and can be used as a request parameter to the endpoints to query, cancel and amend orders.   
clOrdId must be unique among all pending orders and the current request.

### POST / Cancel order

Cancel an incomplete order.

#### Rate Limit: 60 requests per 2 seconds

#### Rate limit rule: User ID + Instrument ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/trade/cancel-order`

> Request Example

```highlight
POST /api/v5/trade/cancel-order
body
{
    "ordId":"590908157585625111",
    "instId":"BTC-USDT"
}

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Cancel order
result = tradeAPI.cancel_order(instId="BTC-USDT", ordId = "590908157585625111")
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| ordId | String | Conditional | Order ID Either `ordId` ordId or `clOrdId` clOrdId is required. If both are passed, ordId will be used. |
| clOrdId | String | Conditional | Client Order ID as assigned by the client |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "clOrdId":"oktswap6",
            "ordId":"12345689",
            "sCode":"0",
            "sMsg":""
        }
    ],
    "inTime": "1695190491421339",
    "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| code | String | The result code, `0` 0 means success |
| msg | String | The error message, empty if the code is 0 |
| data | Array of objects | Array of objects contains the response results |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > sCode | String | The code of the event execution result, `0` 0 means success. |
| > sMsg | String | Rejection message if the request is unsuccessful. |
| inTime | String | Timestamp at REST gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 The time is recorded after authentication. |
| outTime | String | Timestamp at REST gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

Cancel order returns with sCode equal to 0. It is not strictly considered that the order has been canceled. It only means that your cancellation request has been accepted by the system server. The result of the cancellation is subject to the state pushed by the order channel or the get order state.  

### POST / Cancel multiple orders

Cancel incomplete orders in batches. Maximum 20 orders can be canceled per request. Request parameters should be passed in the form of an array.

#### Rate Limit: 300 orders per 2 seconds

#### Rate limit rule: User ID + Instrument ID

#### Permission: Trade

Unlike other endpoints, the rate limit of this endpoint is determined by the number of orders. If there is only one order in the request, it will consume the rate limit of `Cancel order`.

#### HTTP Request

`POST /api/v5/trade/cancel-batch-orders`

> Request Example

```highlight
POST /api/v5/trade/cancel-batch-orders
body
[
    {
        "instId":"BTC-USDT",
        "ordId":"590908157585625111"
    },
    {
        "instId":"BTC-USDT",
        "ordId":"590908544950571222"
    }
]

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Cancel multiple orders by ordId
cancel_orders_with_orderId = [
    {"instId": "BTC-USDT", "ordId": "590908157585625111"},
    {"instId": "BTC-USDT", "ordId": "590908544950571222"}
]

result = tradeAPI.cancel_multiple_orders(cancel_orders_with_orderId)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| ordId | String | Conditional | Order ID Either `ordId` ordId or `clOrdId` clOrdId is required. If both are passed, `ordId` ordId will be used. |
| clOrdId | String | Conditional | Client Order ID as assigned by the client |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "clOrdId":"oktswap6",
            "ordId":"12345689",
            "sCode":"0",
            "sMsg":""
        },
        {
            "clOrdId":"oktswap7",
            "ordId":"12344",
            "sCode":"0",
            "sMsg":""
        }
    ],
    "inTime": "1695190491421339",
    "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| code | String | The result code, `0` 0 means success |
| msg | String | The error message, empty if the code is 0 |
| data | Array of objects | Array of objects contains the response results |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > sCode | String | The code of the event execution result, `0` 0 means success. |
| > sMsg | String | Rejection message if the request is unsuccessful. |
| inTime | String | Timestamp at REST gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 The time is recorded after authentication. |
| outTime | String | Timestamp at REST gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

### POST / Amend order

Amend an incomplete order.

#### Rate Limit: 60 requests per 2 seconds

#### Rate limit rule: User ID + Instrument ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/trade/amend-order`

> Request Example

```highlight
POST /api/v5/trade/amend-order
body
{
    "ordId":"590909145319051111",
    "newSz":"2",
    "instId":"BTC-USDT"
}

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Amend order
result = tradeAPI.amend_order(
    instId="BTC-USDT",
    ordId="590909145319051111",
    newSz="2"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID |
| cxlOnFail | Boolean | No | Whether the order needs to be automatically canceled when the order amendment fails Valid options: `false` false or `true` true , the default is `false` false . |
| ordId | String | Conditional | Order ID Either `ordId` ordId or `clOrdId` clOrdId is required. If both are passed, `ordId` ordId will be used. |
| clOrdId | String | Conditional | Client Order ID as assigned by the client |
| reqId | String | No | Client Request ID as assigned by the client for order amendment A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. The response will include the corresponding `reqId` reqId to help you identify the request if you provide it in the request. |
| newSz | String | Conditional | New quantity after amendment. When amending a partially-filled order, the `newSz` newSz should include the amount that has been filled. |
| newPx | String | Conditional | New price after amendment. |
| attachAlgoOrds | Array of objects | No | TP/SL information attached when placing order |
| > attachAlgoId | String | Conditional | The order ID of attached TP/SL order. It is required to identity the TP/SL order when amending. It will not be posted to algoId when placing TP/SL order after the general order is filled completely. |
| > attachAlgoClOrdId | String | Conditional | Client-supplied Algo ID when placing order attaching TP/SL A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to `algoClOrdId` algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > newTpTriggerPx | String | Conditional | Take-profit trigger price. Either the take profit trigger price or order price is 0, it means that the take profit is deleted. Only applicable to Expiry Futures and Perpetual Futures. |
| > newTpOrdPx | String | Conditional | Take-profit order price If the price is -1, take-profit will be executed at the market price. Only applicable to Expiry Futures and Perpetual Futures. |
| > newSlTriggerPx | String | Conditional | Stop-loss trigger price Either the stop loss trigger price or order price is 0, it means that the stop loss is deleted. Only applicable to Expiry Futures and Perpetual Futures. |
| > newSlOrdPx | String | Conditional | Stop-loss order price If the price is -1, stop-loss will be executed at the market price. Only applicable to Expiry Futures and Perpetual Futures. |
| > newTpTriggerPxType | String | Conditional | Take-profit trigger price type `last` last : last price `index` index : index price `mark` mark : mark price Only applicable to `FUTURES` FUTURES / `SWAP` SWAP If you want to add the take-profit, this parameter is required |
| > newSlTriggerPxType | String | Conditional | Stop-loss trigger price type `last` last : last price `index` index : index price `mark` mark : mark price Only applicable to `FUTURES` FUTURES / `SWAP` SWAP If you want to add the stop-loss, this parameter is required |
| > sz | String | Conditional | New size. Only applicable to TP order of split TPs, and it is required for TP order of split TPs |
| > amendPxOnTriggerType | String | No | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
        {
         "clOrdId":"",
         "ordId":"12344",
         "reqId":"b12344",
         "sCode":"0",
         "sMsg":""
        }
    ],
    "inTime": "1695190491421339",
    "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| code | String | The result code, `0` 0 means success |
| msg | String | The error message, empty if the code is 0 |
| data | Array of objects | Array of objects contains the response results |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > reqId | String | Client Request ID as assigned by the client for order amendment. |
| > sCode | String | The code of the event execution result, `0` 0 means success. |
| > sMsg | String | Rejection message if the request is unsuccessful. |
| inTime | String | Timestamp at REST gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 The time is recorded after authentication. |
| outTime | String | Timestamp at REST gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

newSz   
If the new quantity of the order is less than or equal to the filled quantity when you are amending a partially-filled order, the order status will be changed to filled.

The amend order returns sCode equal to 0. It is not strictly considered that the order has been amended. It only means that your amend order request has been accepted by the system server. The result of the amend is subject to the status pushed by the order channel or the order status query

### POST / Amend multiple orders

Amend incomplete orders in batches. Maximum 20 orders can be amended per request. Request parameters should be passed in the form of an array.

#### Rate Limit: 300 orders per 2 seconds

#### Rate limit rule: User ID + Instrument ID

#### Permission: Trade

Rate limit of this endpoint will also be affected by the rules [Sub-account rate limit](https://my.okx.com/docs-v5/en/#overview-rate-limits-sub-account-rate-limit) and [Fill ratio based sub-account rate limit](https://my.okx.com/docs-v5/en/#overview-rate-limits-fill-ratio-based-sub-account-rate-limit).

Unlike other endpoints, the rate limit of this endpoint is determined by the number of orders. If there is only one order in the request, it will consume the rate limit of `Amend order`.

#### HTTP Request

`POST /api/v5/trade/amend-batch-orders`

> Request Example

```highlight
POST /api/v5/trade/amend-batch-orders
body
[
    {
        "ordId":"590909308792049444",
        "newSz":"2",
        "instId":"BTC-USDT"
    },
    {
        "ordId":"590909308792049555",
        "newSz":"2",
        "instId":"BTC-USDT"
    }
]

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Amend incomplete orders in batches by ordId
amend_orders_with_orderId = [
    {"instId": "BTC-USDT", "ordId": "590909308792049444","newSz":"2"},
    {"instId": "BTC-USDT", "ordId": "590909308792049555","newSz":"2"}
]

result = tradeAPI.amend_multiple_orders(amend_orders_with_orderId)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID |
| cxlOnFail | Boolean | No | Whether the order needs to be automatically canceled when the order amendment fails `false` false `true` true , the default is `false` false . |
| ordId | String | Conditional | Order ID Either `ordId` ordId or `clOrdId` clOrdId is required, if both are passed, `ordId` ordId will be used. |
| clOrdId | String | Conditional | Client Order ID as assigned by the client |
| reqId | String | No | Client Request ID as assigned by the client for order amendment A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. The response will include the corresponding `reqId` reqId to help you identify the request if you provide it in the request. |
| newSz | String | Conditional | New quantity after amendment. When amending a partially-filled order, the `newSz` newSz should include the amount that has been filled. |
| newPx | String | Conditional | New price after amendment. |
| attachAlgoOrds | Array of objects | No | TP/SL information attached when placing order |
| > attachAlgoId | String | Conditional | The order ID of attached TP/SL order. It is required to identity the TP/SL order when amending. It will not be posted to algoId when placing TP/SL order after the general order is filled completely. |
| > attachAlgoClOrdId | String | Conditional | Client-supplied Algo ID when placing order attaching TP/SL A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to `algoClOrdId` algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > newTpTriggerPx | String | Conditional | Take-profit trigger price. Either the take profit trigger price or order price is 0, it means that the take profit is deleted. Only applicable to Expiry Futures and Perpetual Futures. |
| > newTpOrdPx | String | Conditional | Take-profit order price If the price is -1, take-profit will be executed at the market price. Only applicable to Expiry Futures and Perpetual Futures. |
| > newSlTriggerPx | String | Conditional | Stop-loss trigger price Either the stop loss trigger price or order price is 0, it means that the stop loss is deleted. Only applicable to Expiry Futures and Perpetual Futures. |
| > newSlOrdPx | String | Conditional | Stop-loss order price If the price is -1, stop-loss will be executed at the market price. Only applicable to Expiry Futures and Perpetual Futures. |
| > newTpTriggerPxType | String | Conditional | Take-profit trigger price type `last` last : last price `index` index : index price `mark` mark : mark price Only applicable to `FUTURES` FUTURES / `SWAP` SWAP If you want to add the take-profit, this parameter is required |
| > newSlTriggerPxType | String | Conditional | Stop-loss trigger price type `last` last : last price `index` index : index price `mark` mark : mark price Only applicable to `FUTURES` FUTURES / `SWAP` SWAP If you want to add the stop-loss, this parameter is required |
| > sz | String | Conditional | New size. Only applicable to TP order of split TPs, and it is required for TP order of split TPs |
| > amendPxOnTriggerType | String | No | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "clOrdId":"oktswap6",
            "ordId":"12345689",
            "reqId":"b12344",
            "sCode":"0",
            "sMsg":""
        },
        {
            "clOrdId":"oktswap7",
            "ordId":"12344",
            "reqId":"b12344",
            "sCode":"0",
            "sMsg":""
        }
    ],
    "inTime": "1695190491421339",
    "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| code | String | The result code, `0` 0 means success |
| msg | String | The error message, empty if the code is 0 |
| data | Array of objects | Array of objects contains the response results |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > reqId | String | Client Request ID as assigned by the client for order amendment. |
| > sCode | String | The code of the event execution result, `0` 0 means success. |
| > sMsg | String | Rejection message if the request is unsuccessful. |
| inTime | String | Timestamp at REST gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 The time is recorded after authentication. |
| outTime | String | Timestamp at REST gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

newSz   
If the new quantity of the order is less than or equal to the filled quantity when you are amending a partially-filled order, the order status will be changed to filled.

### GET / Order details

Retrieve order details.

#### Rate Limit: 60 requests per 2 seconds

#### Rate limit rule (except Options): User ID + Instrument ID

#### Rate limit rule (Options only): User ID + Instrument Family

#### Permission: Read

#### HTTP Request

`GET /api/v5/trade/order`

> Request Example

```highlight
GET /api/v5/trade/order?ordId=1753197687182819328&instId=BTC-USDT

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve order details by ordId
result = tradeAPI.get_order(
    instId="BTC-USDT",
    ordId="680800019749904384"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT Only applicable to live instruments |
| ordId | String | Conditional | Order ID Either `ordId` ordId or `clOrdId` clOrdId is required, if both are passed, `ordId` ordId will be used |
| clOrdId | String | Conditional | Client Order ID as assigned by the client If the `clOrdId` clOrdId is associated with multiple orders, only the latest one will be returned. |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "accFillSz": "0.00192834",
            "algoClOrdId": "",
            "algoId": "",
            "attachAlgoClOrdId": "",
            "attachAlgoOrds": [],
            "avgPx": "51858",
            "cTime": "1708587373361",
            "cancelSource": "",
            "cancelSourceReason": "",
            "category": "normal",
            "ccy": "",
            "clOrdId": "",
            "fee": "-0.00000192834",
            "feeCcy": "BTC",
            "fillPx": "51858",
            "fillSz": "0.00192834",
            "fillTime": "1708587373361",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "isTpLimit": "false",
            "lever": "",
            "linkedAlgoOrd": {
                "algoId": ""
            },
            "ordId": "680800019749904384",
            "ordType": "market",
            "pnl": "0",
            "posSide": "net",
            "px": "",
            "pxType": "",
            "pxUsd": "",
            "pxVol": "",
            "quickMgnType": "",
            "rebate": "0",
            "rebateCcy": "USDT",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "source": "",
            "state": "filled",
            "stpId": "",
            "stpMode": "",
            "sz": "100",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "quote_ccy",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "",
            "tradeId": "744876980",
            "tradeQuoteCcy": "USDT",
            "uTime": "1708587373362"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION |
| instId | String | Instrument ID |
| tgtCcy | String | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| ccy | String | Margin currency Applicable to all `isolated` isolated `MARGIN` MARGIN orders and `cross` cross `MARGIN` MARGIN orders in `Futures mode` Futures mode . |
| ordId | String | Order ID |
| clOrdId | String | Client Order ID as assigned by the client |
| tag | String | Order tag |
| px | String | Price For options, use coin as unit (e.g. BTC, ETH) |
| pxUsd | String | Options price in USDOnly applicable to options; return "" for other instrument types |
| pxVol | String | Implied volatility of the options orderOnly applicable to options; return "" for other instrument types |
| pxType | String | Price type of options `px` px : Place an order based on price, in the unit of coin (the unit for the request parameter px is BTC or ETH) `pxVol` pxVol : Place an order based on pxVol `pxUsd` pxUsd : Place an order based on pxUsd, in the unit of USD (the unit for the request parameter px is USD) |
| sz | String | Quantity to buy or sell |
| pnl | String | Profit and loss, Applicable to orders which have a trade and aim to close position. It always is 0 in other conditions |
| ordType | String | Order type `market` market : Market order `limit` limit : Limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order `optimal\_limit\_ioc` optimal\_limit\_ioc : Market order with immediate-or-cancel order `mmp` mmp : Market Maker Protection (only applicable to Option in Portfolio Margin mode) `mmp\_and\_post\_only` mmp\_and\_post\_only : Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode) `op\_fok` op\_fok : Simple options (fok) |
| side | String | Order side |
| posSide | String | Position side |
| tdMode | String | Trade mode |
| accFillSz | String | Accumulated fill quantity The unit is `base\_ccy` base\_ccy for SPOT and MARGIN, e.g. BTC-USDT, the unit is BTC; For market orders, the unit both is `base\_ccy` base\_ccy when the tgtCcy is `base\_ccy` base\_ccy or `quote\_ccy` quote\_ccy ; The unit is contract for `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| fillPx | String | Last filled price. If none is filled, it will return "". |
| tradeId | String | Last traded ID |
| fillSz | String | Last filled quantity The unit is `base\_ccy` base\_ccy for SPOT and MARGIN, e.g. BTC-USDT, the unit is BTC; For market orders, the unit both is `base\_ccy` base\_ccy when the tgtCcy is `base\_ccy` base\_ccy or `quote\_ccy` quote\_ccy ; The unit is contract for `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| fillTime | String | Last filled time |
| avgPx | String | Average filled price. If none is filled, it will return "". |
| state | String | State `canceled` canceled `live` live `partially\_filled` partially\_filled `filled` filled `mmp\_canceled` mmp\_canceled |
| stpId | String | Self trade prevention ID Return "" if self trade prevention is not applicable (deprecated) |
| stpMode | String | Self trade prevention mode |
| lever | String | Leverage, from `0.01` 0.01 to `125` 125 . Only applicable to `MARGIN/FUTURES/SWAP` MARGIN/FUTURES/SWAP |
| attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL. |
| tpTriggerPx | String | Take-profit trigger price. |
| tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| tpOrdPx | String | Take-profit order price. |
| slTriggerPx | String | Stop-loss trigger price. |
| slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| slOrdPx | String | Stop-loss order price. |
| attachAlgoOrds | Array of objects | TP/SL information attached when placing order |
| > attachAlgoId | String | The order ID of attached TP/SL order. It can be used to identity the TP/SL order when amending. It will not be posted to algoId when placing TP/SL order after the general order is filled completely. |
| > attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to `algoClOrdId` algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > tpOrdKind | String | TP order kind `condition` condition `limit` limit |
| > tpTriggerPx | String | Take-profit trigger price. |
| > tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > tpOrdPx | String | Take-profit order price. |
| > slTriggerPx | String | Stop-loss trigger price. |
| > slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > slOrdPx | String | Stop-loss order price. |
| > sz | String | Size. Only applicable to TP order of split TPs |
| > amendPxOnTriggerType | String | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |
| > amendPxOnTriggerType | String | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |
| > failCode | String | The error code when failing to place TP/SL order, e.g. 51020 The default is "" |
| > failReason | String | The error reason when failing to place TP/SL order. The default is "" |
| linkedAlgoOrd | Object | Linked SL order detail, only applicable to the order that is placed by one-cancels-the-other (OCO) order that contains the TP limit order. |
| > algoId | String | Algo ID |
| feeCcy | String | Fee currency |
| fee | String | Fee and rebate For spot and margin, it is accumulated fee charged by the platform. It is always negative, e.g. -0.01. For Expiry Futures, Perpetual Futures and Options, it is accumulated fee and rebate |
| rebateCcy | String | Rebate currency |
| source | String | Order source `6` 6 : The normal order triggered by the `trigger order` trigger order `7` 7 :The normal order triggered by the `TP/SL order` TP/SL order `13` 13 : The normal order triggered by the algo order `25` 25 :The normal order triggered by the `trailing stop order` trailing stop order `34` 34 : The normal order triggered by the chase order |
| rebate | String | Rebate amount, only applicable to spot and margin, the reward of placing orders from the platform (rebate) given to user who has reached the specified trading level. If there is no rebate, this field is "". |
| category | String | Category `normal` normal `twap` twap `adl` adl `full\_liquidation` full\_liquidation `partial\_liquidation` partial\_liquidation `delivery` delivery `ddh` ddh : Delta dynamic hedge |
| reduceOnly | String | Whether the order can only reduce the position size. Valid options: true or false. |
| isTpLimit | String | Whether it is TP limit order. true or false |
| cancelSource | String | Code of the cancellation source. |
| cancelSourceReason | String | Reason for the cancellation. |
| quickMgnType | String | Quick Margin type, Only applicable to Quick Margin Mode of isolated margin `manual` manual , `auto\_borrow` auto\_borrow , `auto\_repay` auto\_repay |
| algoClOrdId | String | Client-supplied Algo ID. There will be a value when algo order attaching `algoClOrdId` algoClOrdId is triggered, or it will be "". |
| algoId | String | Algo ID. There will be a value when algo order is triggered, or it will be "". |
| uTime | String | Update time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| cTime | String | Creation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| tradeQuoteCcy | String | The quote currency used for trading. |

### GET / Order List

Retrieve all incomplete orders under the current account.

#### Rate Limit: 60 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/trade/orders-pending`

> Request Example

```highlight
GET /api/v5/trade/orders-pending?ordType=post_only,fok,ioc&instType=SPOT

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve all incomplete orders
result = tradeAPI.get_order_list(
    instType="SPOT",
    ordType="post_only,fok,ioc"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | No | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION |
| uly | String | No | Underlying Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instFamily | String | No | Instrument family Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instId | String | No | Instrument ID, e.g. `BTC-USD-200927` BTC-USD-200927 |
| ordType | String | No | Order type `market` market : Market order `limit` limit : Limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order `optimal\_limit\_ioc` optimal\_limit\_ioc : Market order with immediate-or-cancel order `mmp` mmp : Market Maker Protection (only applicable to Option in Portfolio Margin mode) `mmp\_and\_post\_only` mmp\_and\_post\_only : Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode) `op\_fok` op\_fok : Simple options (fok) |
| state | String | No | State `live` live `partially\_filled` partially\_filled |
| after | String | No | Pagination of data to return records earlier than the requested `ordId` ordId |
| before | String | No | Pagination of data to return records newer than the requested `ordId` ordId |
| limit | String | No | Number of results per request. The maximum is `100` 100 ; The default is `100` 100 |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "accFillSz": "0",
            "algoClOrdId": "",
            "algoId": "",
            "attachAlgoClOrdId": "",
            "attachAlgoOrds": [],
            "avgPx": "",
            "cTime": "1724733617998",
            "cancelSource": "",
            "cancelSourceReason": "",
            "category": "normal",
            "ccy": "",
            "clOrdId": "",
            "fee": "0",
            "feeCcy": "BTC",
            "fillPx": "",
            "fillSz": "0",
            "fillTime": "",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "isTpLimit": "false",
            "lever": "",
            "linkedAlgoOrd": {
                "algoId": ""
            },
            "ordId": "1752588852617379840",
            "ordType": "post_only",
            "pnl": "0",
            "posSide": "net",
            "px": "13013.5",
            "pxType": "",
            "pxUsd": "",
            "pxVol": "",
            "quickMgnType": "",
            "rebate": "0",
            "rebateCcy": "USDT",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "source": "",
            "state": "live",
            "stpId": "",
            "stpMode": "cancel_maker",
            "sz": "0.001",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "",
            "tradeId": "",
            "tradeQuoteCcy": "USDT",
            "uTime": "1724733617998"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID |
| tgtCcy | String | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| ccy | String | Margin currency Applicable to all `isolated` isolated `MARGIN` MARGIN orders and `cross` cross `MARGIN` MARGIN orders in `Futures mode` Futures mode . |
| ordId | String | Order ID |
| clOrdId | String | Client Order ID as assigned by the client |
| tag | String | Order tag |
| px | String | Price For options, use coin as unit (e.g. BTC, ETH) |
| pxUsd | String | Options price in USDOnly applicable to options; return "" for other instrument types |
| pxVol | String | Implied volatility of the options orderOnly applicable to options; return "" for other instrument types |
| pxType | String | Price type of options `px` px : Place an order based on price, in the unit of coin (the unit for the request parameter px is BTC or ETH) `pxVol` pxVol : Place an order based on pxVol `pxUsd` pxUsd : Place an order based on pxUsd, in the unit of USD (the unit for the request parameter px is USD) |
| sz | String | Quantity to buy or sell |
| pnl | String | Profit and loss, Applicable to orders which have a trade and aim to close position. It always is 0 in other conditions |
| ordType | String | Order type `market` market : Market order `limit` limit : Limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order `optimal\_limit\_ioc` optimal\_limit\_ioc : Market order with immediate-or-cancel order `mmp` mmp : Market Maker Protection (only applicable to Option in Portfolio Margin mode) `mmp\_and\_post\_only` mmp\_and\_post\_only : Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode) `op\_fok` op\_fok : Simple options (fok) |
| side | String | Order side |
| posSide | String | Position side |
| tdMode | String | Trade mode |
| accFillSz | String | Accumulated fill quantity |
| fillPx | String | Last filled price |
| tradeId | String | Last trade ID |
| fillSz | String | Last filled quantity |
| fillTime | String | Last filled time |
| avgPx | String | Average filled price. If none is filled, it will return "". |
| state | String | State `live` live `partially\_filled` partially\_filled |
| lever | String | Leverage, from `0.01` 0.01 to `125` 125 . Only applicable to `MARGIN/FUTURES/SWAP` MARGIN/FUTURES/SWAP |
| attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL. |
| tpTriggerPx | String | Take-profit trigger price. |
| tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| tpOrdPx | String | Take-profit order price. |
| slTriggerPx | String | Stop-loss trigger price. |
| slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| slOrdPx | String | Stop-loss order price. |
| attachAlgoOrds | Array of objects | TP/SL information attached when placing order |
| > attachAlgoId | String | The order ID of attached TP/SL order. It can be used to identity the TP/SL order when amending. It will not be posted to algoId when placing TP/SL order after the general order is filled completely. |
| > attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to `algoClOrdId` algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > tpOrdKind | String | TP order kind `condition` condition `limit` limit |
| > tpTriggerPx | String | Take-profit trigger price. |
| > tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > tpOrdPx | String | Take-profit order price. |
| > slTriggerPx | String | Stop-loss trigger price. |
| > slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > slOrdPx | String | Stop-loss order price. |
| > sz | String | Size. Only applicable to TP order of split TPs |
| > amendPxOnTriggerType | String | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |
| > failCode | String | The error code when failing to place TP/SL order, e.g. 51020 The default is "" |
| > failReason | String | The error reason when failing to place TP/SL order. The default is "" |
| linkedAlgoOrd | Object | Linked SL order detail, only applicable to the order that is placed by one-cancels-the-other (OCO) order that contains the TP limit order. |
| > algoId | String | Algo ID |
| stpId | String | Self trade prevention ID Return "" if self trade prevention is not applicable (deprecated) |
| stpMode | String | Self trade prevention mode |
| feeCcy | String | Fee currency |
| fee | String | Fee and rebate For spot and margin, it is accumulated fee charged by the platform. It is always negative, e.g. -0.01. For Expiry Futures, Perpetual Futures and Options, it is accumulated fee and rebate |
| rebateCcy | String | Rebate currency |
| source | String | Order source `6` 6 : The normal order triggered by the `trigger order` trigger order `7` 7 :The normal order triggered by the `TP/SL order` TP/SL order `13` 13 : The normal order triggered by the algo order `25` 25 :The normal order triggered by the `trailing stop order` trailing stop order `34` 34 : The normal order triggered by the chase order |
| rebate | String | Rebate amount, only applicable to spot and margin, the reward of placing orders from the platform (rebate) given to user who has reached the specified trading level. If there is no rebate, this field is "". |
| category | String | Category `normal` normal |
| reduceOnly | String | Whether the order can only reduce the position size. Valid options: true or false. |
| quickMgnType | String | Quick Margin type, Only applicable to Quick Margin Mode of isolated margin `manual` manual , `auto\_borrow` auto\_borrow , `auto\_repay` auto\_repay |
| algoClOrdId | String | Client-supplied Algo ID. There will be a value when algo order attaching `algoClOrdId` algoClOrdId is triggered, or it will be "". |
| algoId | String | Algo ID. There will be a value when algo order is triggered, or it will be "". |
| isTpLimit | String | Whether it is TP limit order. true or false |
| uTime | String | Update time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| cTime | String | Creation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| cancelSource | String | Code of the cancellation source. |
| cancelSourceReason | String | Reason for the cancellation. |
| tradeQuoteCcy | String | The quote currency used for trading. |

### GET / Order history (last 7 days)

Get completed orders which are placed in the last 7 days, including those placed 7 days ago but completed in the last 7 days.

The incomplete orders that have been canceled are only reserved for 2 hours.

#### Rate Limit: 40 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/trade/orders-history`

> Request Example

```highlight
GET /api/v5/trade/orders-history?ordType=post_only,fok,ioc&instType=SPOT

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Get completed SPOT orders which are placed in the last 7 days
# The incomplete orders that have been canceled are only reserved for 2 hours
result = tradeAPI.get_orders_history(
    instType="SPOT",
    ordType="post_only,fok,ioc"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | yes | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION |
| uly | String | No | Underlying Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instFamily | String | No | Instrument family Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instId | String | No | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| ordType | String | No | Order type `market` market : market order `limit` limit : limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order `optimal\_limit\_ioc` optimal\_limit\_ioc : Market order with immediate-or-cancel order `mmp` mmp : Market Maker Protection (only applicable to Option in Portfolio Margin mode) `mmp\_and\_post\_only` mmp\_and\_post\_only : Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode) `op\_fok` op\_fok : Simple options (fok) |
| state | String | No | State `canceled` canceled `filled` filled `mmp\_canceled` mmp\_canceled : Order canceled automatically due to Market Maker Protection |
| category | String | No | Category `twap` twap `adl` adl `full\_liquidation` full\_liquidation `partial\_liquidation` partial\_liquidation `delivery` delivery `ddh` ddh : Delta dynamic hedge |
| after | String | No | Pagination of data to return records earlier than the requested `ordId` ordId |
| before | String | No | Pagination of data to return records newer than the requested `ordId` ordId |
| begin | String | No | Filter with a begin timestamp `cTime` cTime . Unix timestamp format in milliseconds, e.g. 1597026383085 |
| end | String | No | Filter with an end timestamp `cTime` cTime . Unix timestamp format in milliseconds, e.g. 1597026383085 |
| limit | String | No | Number of results per request. The maximum is `100` 100 ; The default is `100` 100 |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "accFillSz": "0.00192834",
            "algoClOrdId": "",
            "algoId": "",
            "attachAlgoClOrdId": "",
            "attachAlgoOrds": [],
            "avgPx": "51858",
            "cTime": "1708587373361",
            "cancelSource": "",
            "cancelSourceReason": "",
            "category": "normal",
            "ccy": "",
            "clOrdId": "",
            "fee": "-0.00000192834",
            "feeCcy": "BTC",
            "fillPx": "51858",
            "fillSz": "0.00192834",
            "fillTime": "1708587373361",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "lever": "",
            "linkedAlgoOrd": {
                "algoId": ""
            },
            "ordId": "680800019749904384",
            "ordType": "market",
            "pnl": "0",
            "posSide": "",
            "px": "",
            "pxType": "",
            "pxUsd": "",
            "pxVol": "",
            "quickMgnType": "",
            "rebate": "0",
            "rebateCcy": "USDT",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "source": "",
            "state": "filled",
            "stpId": "",
            "stpMode": "",
            "sz": "100",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "quote_ccy",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "",
            "tradeId": "744876980",
            "tradeQuoteCcy": "USDT",
            "uTime": "1708587373362",
            "isTpLimit": "false"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID |
| tgtCcy | String | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| ccy | String | Margin currency Applicable to all `isolated` isolated `MARGIN` MARGIN orders and `cross` cross `MARGIN` MARGIN orders in `Futures mode` Futures mode . |
| ordId | String | Order ID |
| clOrdId | String | Client Order ID as assigned by the client |
| tag | String | Order tag |
| px | String | Price For options, use coin as unit (e.g. BTC, ETH) |
| pxUsd | String | Options price in USDOnly applicable to options; return "" for other instrument types |
| pxVol | String | Implied volatility of the options orderOnly applicable to options; return "" for other instrument types |
| pxType | String | Price type of options `px` px : Place an order based on price, in the unit of coin (the unit for the request parameter px is BTC or ETH) `pxVol` pxVol : Place an order based on pxVol `pxUsd` pxUsd : Place an order based on pxUsd, in the unit of USD (the unit for the request parameter px is USD) |
| sz | String | Quantity to buy or sell |
| ordType | String | Order type `market` market : market order `limit` limit : limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order `optimal\_limit\_ioc` optimal\_limit\_ioc : Market order with immediate-or-cancel order `mmp` mmp : Market Maker Protection (only applicable to Option in Portfolio Margin mode) `mmp\_and\_post\_only` mmp\_and\_post\_only : Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode) `op\_fok` op\_fok : Simple options (fok) |
| side | String | Order side |
| posSide | String | Position side |
| tdMode | String | Trade mode |
| accFillSz | String | Accumulated fill quantity |
| fillPx | String | Last filled price. If none is filled, it will return "". |
| tradeId | String | Last trade ID |
| fillSz | String | Last filled quantity |
| fillTime | String | Last filled time |
| avgPx | String | Average filled price. If none is filled, it will return "". |
| state | String | State `canceled` canceled `filled` filled `mmp\_canceled` mmp\_canceled |
| lever | String | Leverage, from `0.01` 0.01 to `125` 125 . Only applicable to `MARGIN/FUTURES/SWAP` MARGIN/FUTURES/SWAP |
| attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL. |
| tpTriggerPx | String | Take-profit trigger price. |
| tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| tpOrdPx | String | Take-profit order price. |
| slTriggerPx | String | Stop-loss trigger price. |
| slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| slOrdPx | String | Stop-loss order price. |
| attachAlgoOrds | Array of objects | TP/SL information attached when placing order |
| > attachAlgoId | String | The order ID of attached TP/SL order. It can be used to identity the TP/SL order when amending. It will not be posted to algoId when placing TP/SL order after the general order is filled completely. |
| > attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to `algoClOrdId` algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > tpOrdKind | String | TP order kind `condition` condition `limit` limit |
| > tpTriggerPx | String | Take-profit trigger price. |
| > tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > tpOrdPx | String | Take-profit order price. |
| > slTriggerPx | String | Stop-loss trigger price. |
| > slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > slOrdPx | String | Stop-loss order price. |
| > sz | String | Size. Only applicable to TP order of split TPs |
| > amendPxOnTriggerType | String | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |
| > failCode | String | The error code when failing to place TP/SL order, e.g. 51020 The default is "" |
| > failReason | String | The error reason when failing to place TP/SL order. The default is "" |
| linkedAlgoOrd | Object | Linked SL order detail, only applicable to the order that is placed by one-cancels-the-other (OCO) order that contains the TP limit order. |
| > algoId | String | Algo ID |
| stpId | String | Self trade prevention ID Return "" if self trade prevention is not applicable (deprecated) |
| stpMode | String | Self trade prevention mode |
| feeCcy | String | Fee currency |
| fee | String | Fee and rebate For spot and margin, it is accumulated fee charged by the platform. It is always negative, e.g. -0.01. For Expiry Futures, Perpetual Futures and Options, it is accumulated fee and rebate |
| rebateCcy | String | Rebate currency |
| source | String | Order source `6` 6 : The normal order triggered by the `trigger order` trigger order `7` 7 :The normal order triggered by the `TP/SL order` TP/SL order `13` 13 : The normal order triggered by the algo order `25` 25 :The normal order triggered by the `trailing stop order` trailing stop order `34` 34 : The normal order triggered by the chase order |
| rebate | String | Rebate amount, only applicable to spot and margin, the reward of placing orders from the platform (rebate) given to user who has reached the specified trading level. If there is no rebate, this field is "". |
| pnl | String | Profit and loss, Applicable to orders which have a trade and aim to close position. It always is 0 in other conditions |
| category | String | Category `normal` normal `twap` twap `adl` adl `full\_liquidation` full\_liquidation `partial\_liquidation` partial\_liquidation `delivery` delivery `ddh` ddh : Delta dynamic hedge |
| reduceOnly | String | Whether the order can only reduce the position size. Valid options: true or false. |
| cancelSource | String | Code of the cancellation source. |
| cancelSourceReason | String | Reason for the cancellation. |
| algoClOrdId | String | Client-supplied Algo ID. There will be a value when algo order attaching `algoClOrdId` algoClOrdId is triggered, or it will be "". |
| algoId | String | Algo ID. There will be a value when algo order is triggered, or it will be "". |
| isTpLimit | String | Whether it is TP limit order. true or false |
| uTime | String | Update time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| cTime | String | Creation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| quickMgnType | String | Quick Margin type, Only applicable to Quick Margin Mode of isolated margin `manual` manual , `auto\_borrow` auto\_borrow , `auto\_repay` auto\_repay (Deprecated) |
| tradeQuoteCcy | String | The quote currency used for trading. |

### GET / Order history (last 3 months)

Get completed orders which are placed in the last 3 months, including those placed 3 months ago but completed in the last 3 months.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/trade/orders-history-archive`

> Request Example

```highlight
GET /api/v5/trade/orders-history-archive?ordType=post_only,fok,ioc&instType=SPOT

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Get completed SPOT orders which are placed in the last 3 months
result = tradeAPI.get_orders_history_archive(
    instType="SPOT",
    ordType="post_only,fok,ioc"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | yes | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION |
| uly | String | No | Underlying Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instFamily | String | No | Instrument family Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instId | String | No | Instrument ID, e.g. `BTC-USD-200927` BTC-USD-200927 |
| ordType | String | No | Order type `market` market : Market order `limit` limit : Limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order `optimal\_limit\_ioc` optimal\_limit\_ioc : Market order with immediate-or-cancel order `mmp` mmp : Market Maker Protection (only applicable to Option in Portfolio Margin mode) `mmp\_and\_post\_only` mmp\_and\_post\_only : Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode) `op\_fok` op\_fok : Simple options (fok) |
| state | String | No | State `canceled` canceled `filled` filled `mmp\_canceled` mmp\_canceled : Order canceled automatically due to Market Maker Protection |
| category | String | No | Category `twap` twap `adl` adl `full\_liquidation` full\_liquidation `partial\_liquidation` partial\_liquidation `delivery` delivery `ddh` ddh : Delta dynamic hedge |
| after | String | No | Pagination of data to return records earlier than the requested `ordId` ordId |
| before | String | No | Pagination of data to return records newer than the requested `ordId` ordId |
| begin | String | No | Filter with a begin timestamp `cTime` cTime . Unix timestamp format in milliseconds, e.g. 1597026383085 |
| end | String | No | Filter with an end timestamp `cTime` cTime . Unix timestamp format in milliseconds, e.g. 1597026383085 |
| limit | String | No | Number of results per request. The maximum is `100` 100 ; The default is `100` 100 |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "accFillSz": "0.00192834",
            "algoClOrdId": "",
            "algoId": "",
            "attachAlgoClOrdId": "",
            "attachAlgoOrds": [],
            "avgPx": "51858",
            "cTime": "1708587373361",
            "cancelSource": "",
            "cancelSourceReason": "",
            "category": "normal",
            "ccy": "",
            "clOrdId": "",
            "fee": "-0.00000192834",
            "feeCcy": "BTC",
            "fillPx": "51858",
            "fillSz": "0.00192834",
            "fillTime": "1708587373361",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "lever": "",
            "ordId": "680800019749904384",
            "ordType": "market",
            "pnl": "0",
            "posSide": "",
            "px": "",
            "pxType": "",
            "pxUsd": "",
            "pxVol": "",
            "quickMgnType": "",
            "rebate": "0",
            "rebateCcy": "USDT",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "source": "",
            "state": "filled",
            "stpId": "",
            "stpMode": "",
            "sz": "100",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "quote_ccy",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "",
            "tradeId": "744876980",
            "tradeQuoteCcy": "USDT",
            "uTime": "1708587373362",
            "isTpLimit": "false",
            "linkedAlgoOrd": {
                "algoId": ""
            }
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID |
| tgtCcy | String | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| ccy | String | Margin currency Applicable to all `isolated` isolated `MARGIN` MARGIN orders and `cross` cross `MARGIN` MARGIN orders in `Futures mode` Futures mode . |
| ordId | String | Order ID |
| clOrdId | String | Client Order ID as assigned by the client |
| tag | String | Order tag |
| px | String | Price For options, use coin as unit (e.g. BTC, ETH) |
| pxUsd | String | Options price in USDOnly applicable to options; return "" for other instrument types |
| pxVol | String | Implied volatility of the options orderOnly applicable to options; return "" for other instrument types |
| pxType | String | Price type of options `px` px : Place an order based on price, in the unit of coin (the unit for the request parameter px is BTC or ETH) `pxVol` pxVol : Place an order based on pxVol `pxUsd` pxUsd : Place an order based on pxUsd, in the unit of USD (the unit for the request parameter px is USD) |
| sz | String | Quantity to buy or sell |
| ordType | String | Order type `market` market : Market order `limit` limit : Limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order `optimal\_limit\_ioc` optimal\_limit\_ioc : Market order with immediate-or-cancel order `mmp` mmp : Market Maker Protection (only applicable to Option in Portfolio Margin mode) `mmp\_and\_post\_only` mmp\_and\_post\_only : Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode) `op\_fok` op\_fok : Simple options (fok) |
| side | String | Order side |
| posSide | String | Position side |
| tdMode | String | Trade mode |
| accFillSz | String | Accumulated fill quantity |
| fillPx | String | Last filled price. If none is filled, it will return "". |
| tradeId | String | Last trade ID |
| fillSz | String | Last filled quantity |
| fillTime | String | Last filled time |
| avgPx | String | Average filled price. If none is filled, it will return "". |
| state | String | State `canceled` canceled `filled` filled `mmp\_canceled` mmp\_canceled |
| lever | String | Leverage, from `0.01` 0.01 to `125` 125 . Only applicable to `MARGIN/FUTURES/SWAP` MARGIN/FUTURES/SWAP |
| attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL. |
| tpTriggerPx | String | Take-profit trigger price. |
| tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| tpOrdPx | String | Take-profit order price. |
| slTriggerPx | String | Stop-loss trigger price. |
| slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| slOrdPx | String | Stop-loss order price. |
| attachAlgoOrds | Array of objects | TP/SL information attached when placing order |
| > attachAlgoId | String | The order ID of attached TP/SL order. It can be used to identity the TP/SL order when amending. It will not be posted to algoId when placing TP/SL order after the general order is filled completely. |
| > attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to `algoClOrdId` algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > tpOrdKind | String | TP order kind `condition` condition `limit` limit |
| > tpTriggerPx | String | Take-profit trigger price. |
| > tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > tpOrdPx | String | Take-profit order price. |
| > slTriggerPx | String | Stop-loss trigger price. |
| > slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > slOrdPx | String | Stop-loss order price. |
| > sz | String | Size. Only applicable to TP order of split TPs |
| > amendPxOnTriggerType | String | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |
| > failCode | String | The error code when failing to place TP/SL order, e.g. 51020 The default is "" |
| > failReason | String | The error reason when failing to place TP/SL order. The default is "" |
| linkedAlgoOrd | Object | Linked SL order detail, only applicable to the order that is placed by one-cancels-the-other (OCO) order that contains the TP limit order. |
| > algoId | String | Algo ID |
| stpId | String | Self trade prevention ID Return "" if self trade prevention is not applicable (deprecated) |
| stpMode | String | Self trade prevention mode |
| feeCcy | String | Fee currency |
| fee | String | Fee and rebate For spot and margin, it is accumulated fee charged by the platform. It is always negative, e.g. -0.01. For Expiry Futures, Perpetual Futures and Options, it is accumulated fee and rebate |
| source | String | Order source `6` 6 : The normal order triggered by the `trigger order` trigger order `7` 7 :The normal order triggered by the `TP/SL order` TP/SL order `13` 13 : The normal order triggered by the algo order `25` 25 :The normal order triggered by the `trailing stop order` trailing stop order `34` 34 : The normal order triggered by the `chase order` chase order |
| rebateCcy | String | Rebate currency |
| rebate | String | Rebate amount, only applicable to spot and margin, the reward of placing orders from the platform (rebate) given to user who has reached the specified trading level. If there is no rebate, this field is "". |
| pnl | String | Profit and loss, Applicable to orders which have a trade and aim to close position. It always is 0 in other conditions |
| category | String | Category `normal` normal `twap` twap `adl` adl `full\_liquidation` full\_liquidation `partial\_liquidation` partial\_liquidation `delivery` delivery `ddh` ddh : Delta dynamic hedge |
| reduceOnly | String | Whether the order can only reduce the position size. Valid options: true or false. |
| cancelSource | String | Code of the cancellation source. |
| cancelSourceReason | String | Reason for the cancellation. |
| algoClOrdId | String | Client-supplied Algo ID. There will be a value when algo order attaching `algoClOrdId` algoClOrdId is triggered, or it will be "". |
| algoId | String | Algo ID. There will be a value when algo order is triggered, or it will be "". |
| isTpLimit | String | Whether it is TP limit order. true or false |
| uTime | String | Update time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| cTime | String | Creation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| quickMgnType | String | Quick Margin type, Only applicable to Quick Margin Mode of isolated margin `manual` manual , `auto\_borrow` auto\_borrow , `auto\_repay` auto\_repay (Deprecated) |
| tradeQuoteCcy | String | The quote currency used for trading. |

This interface does not contain the order data of the `Canceled orders without any fills` type, which can be obtained through the `Get Order History (last 7 days)` interface.   

As far as OPTION orders that are complete, pxVol and pxUsd will update in time for px order, pxVol will update in time for pxUsd order, pxUsd will update in time for pxVol order.   

### GET / Transaction details (last 3 days)

Retrieve recently-filled transaction details in the last 3 day.

#### Rate Limit: 60 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/trade/fills`

> Request Example

```highlight
GET /api/v5/trade/fills

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve recently-filled transaction details
result = tradeAPI.get_fills()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | No | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION |
| uly | String | No | Underlying Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instFamily | String | No | Instrument family Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instId | String | No | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| ordId | String | No | Order ID |
| subType | String | No | Transaction type `1` 1 : Buy `2` 2 : Sell `3` 3 : Open long `4` 4 : Open short `5` 5 : Close long `6` 6 : Close short `100` 100 : Partial liquidation close long `101` 101 : Partial liquidation close short `102` 102 : Partial liquidation buy `103` 103 : Partial liquidation sell `104` 104 : Liquidation long `105` 105 : Liquidation short `106` 106 : Liquidation buy `107` 107 : Liquidation sell `110` 110 : Liquidation transfer in `111` 111 : Liquidation transfer out `118` 118 : System token conversion transfer in `119` 119 : System token conversion transfer out `125` 125 : ADL close long `126` 126 : ADL close short `127` 127 : ADL buy `128` 128 : ADL sell `212` 212 : Auto borrow of quick margin `213` 213 : Auto repay of quick margin `204` 204 : block trade buy `205` 205 : block trade sell `206` 206 : block trade open long `207` 207 : block trade open short `208` 208 : block trade close long `209` 209 : block trade close short `236` 236 : Easy convert in `237` 237 : Easy convert out `270` 270 : Spread trading buy `271` 271 : Spread trading sell `272` 272 : Spread trading open long `273` 273 : Spread trading open short `274` 274 : Spread trading close long `275` 275 : Spread trading close short `324` 324 : Move position buy `325` 325 : Move position sell `326` 326 : Move position open long `327` 327 : Move position open short `328` 328 : Move position close long `329` 329 : Move position close short `376` 376 : Collateralized borrowing auto conversion buy `377` 377 : Collateralized borrowing auto conversion sell |
| after | String | No | Pagination of data to return records earlier than the requested `billId` billId |
| before | String | No | Pagination of data to return records newer than the requested `billId` billId |
| begin | String | No | Filter with a begin timestamp `ts` ts . Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| end | String | No | Filter with an end timestamp `ts` ts . Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. The maximum is `100` 100 ; The default is `100` 100 |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "side": "buy",
            "fillSz": "0.00192834",
            "fillPx": "51858",
            "fillPxVol": "",
            "fillFwdPx": "",
            "fee": "-0.00000192834",
            "fillPnl": "0",
            "ordId": "680800019749904384",
            "feeRate": "-0.001",
            "instType": "SPOT",
            "fillPxUsd": "",
            "instId": "BTC-USDT",
            "clOrdId": "",
            "posSide": "net",
            "billId": "680800019754098688",
            "subType": "1",
            "fillMarkVol": "",
            "tag": "",
            "fillTime": "1708587373361",
            "execType": "T",
            "fillIdxPx": "",
            "tradeId": "744876980",
            "fillMarkPx": "",
            "feeCcy": "BTC",
            "ts": "1708587373362"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID |
| tradeId | String | Last trade ID |
| ordId | String | Order ID |
| clOrdId | String | Client Order ID as assigned by the client |
| billId | String | Bill ID |
| subType | String | Transaction type |
| tag | String | Order tag |
| fillPx | String | Last filled price. It is the same as the px from "Get bills details". |
| fillSz | String | Last filled quantity |
| fillIdxPx | String | Index price at the moment of trade execution For cross currency spot pairs, it returns baseCcy-USDT index price. For example, for LTC-ETH, this field returns the index price of LTC-USDT. |
| fillPnl | String | Last filled profit and loss, applicable to orders which have a trade and aim to close position. It always is 0 in other conditions |
| fillPxVol | String | Implied volatility when filled Only applicable to options; return "" for other instrument types |
| fillPxUsd | String | Options price when filled, in the unit of USD Only applicable to options; return "" for other instrument types |
| fillMarkVol | String | Mark volatility when filled Only applicable to options; return "" for other instrument types |
| fillFwdPx | String | Forward price when filled Only applicable to options; return "" for other instrument types |
| fillMarkPx | String | Mark price when filled Applicable to `FUTURES` FUTURES , `SWAP` SWAP , `OPTION` OPTION |
| side | String | Order side, `buy` buy `sell` sell |
| posSide | String | Position side `long` long `short` short it returns `net` net in `net` net mode. |
| execType | String | Liquidity taker or maker `T` T : taker `M` M : maker Not applicable to system orders such as ADL and liquidation |
| feeCcy | String | Trading fee or rebate currency |
| fee | String | The amount of trading fee or rebate. The trading fee deduction is negative, such as '-0.01'; the rebate is positive, such as '0.01'. |
| ts | String | Data generation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 . |
| fillTime | String | Trade time which is the same as `fillTime` fillTime for the order channel. |
| feeRate | String | Fee rate. This field is returned for `SPOT` SPOT and `MARGIN` MARGIN only |

tradeId  
For partial\_liquidation, full\_liquidation, or adl, when it comes to fill information, this field will be assigned a negative value to distinguish it from other matching transaction scenarios, when it comes to order information, this field will be 0.

ordId  
Order ID, always "" for block trading.  

clOrdId  
Client-supplied order ID, always "" for block trading.

### GET / Transaction details (last 1 year)

This endpoint can retrieve data from the last 1 year since July 1, 2024.

#### Rate Limit: 10 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/trade/fills-history`

> Request Example

```highlight
GET /api/v5/trade/fills-history?instType=SPOT

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve SPOT transaction details in the last 3 months.
result = tradeAPI.get_fills_history(
    instType="SPOT"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | YES | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION |
| uly | String | No | Underlying Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instFamily | String | No | Instrument family Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instId | String | No | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| ordId | String | No | Order ID |
| subType | String | No | Transaction type `1` 1 : Buy `2` 2 : Sell `3` 3 : Open long `4` 4 : Open short `5` 5 : Close long `6` 6 : Close short `100` 100 : Partial liquidation close long `101` 101 : Partial liquidation close short `102` 102 : Partial liquidation buy `103` 103 : Partial liquidation sell `104` 104 : Liquidation long `105` 105 : Liquidation short `106` 106 : Liquidation buy `107` 107 : Liquidation sell `110` 110 : Liquidation transfer in `111` 111 : Liquidation transfer out `118` 118 : System token conversion transfer in `119` 119 : System token conversion transfer out `125` 125 : ADL close long `126` 126 : ADL close short `127` 127 : ADL buy `128` 128 : ADL sell `212` 212 : Auto borrow of quick margin `213` 213 : Auto repay of quick margin `204` 204 : block trade buy `205` 205 : block trade sell `206` 206 : block trade open long `207` 207 : block trade open short `208` 208 : block trade close long `209` 209 : block trade close short `236` 236 : Easy convert in `237` 237 : Easy convert out `270` 270 : Spread trading buy `271` 271 : Spread trading sell `272` 272 : Spread trading open long `273` 273 : Spread trading open short `274` 274 : Spread trading close long `275` 275 : Spread trading close short `324` 324 : Move position buy `325` 325 : Move position sell `326` 326 : Move position open long `327` 327 : Move position open short `328` 328 : Move position close long `329` 329 : Move position close short `376` 376 : Collateralized borrowing auto conversion buy `377` 377 : Collateralized borrowing auto conversion sell |
| after | String | No | Pagination of data to return records earlier than the requested `billId` billId |
| before | String | No | Pagination of data to return records newer than the requested `billId` billId |
| begin | String | No | Filter with a begin timestamp `ts` ts . Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| end | String | No | Filter with an end timestamp `ts` ts . Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. The maximum is `100` 100 ; The default is `100` 100 |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "side": "buy",
            "fillSz": "0.00192834",
            "fillPx": "51858",
            "fillPxVol": "",
            "fillFwdPx": "",
            "fee": "-0.00000192834",
            "fillPnl": "0",
            "ordId": "680800019749904384",
            "feeRate": "-0.001",
            "instType": "SPOT",
            "fillPxUsd": "",
            "instId": "BTC-USDT",
            "clOrdId": "",
            "posSide": "net",
            "billId": "680800019754098688",
            "subType": "1",
            "fillMarkVol": "",
            "tag": "",
            "fillTime": "1708587373361",
            "execType": "T",
            "fillIdxPx": "",
            "tradeId": "744876980",
            "fillMarkPx": "",
            "feeCcy": "BTC",
            "ts": "1708587373362"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID |
| tradeId | String | Last trade ID |
| ordId | String | Order ID |
| clOrdId | String | Client Order ID as assigned by the client |
| billId | String | Bill ID |
| subType | String | Transaction type |
| tag | String | Order tag |
| fillPx | String | Last filled price |
| fillSz | String | Last filled quantity |
| fillIdxPx | String | Index price at the moment of trade execution For cross currency spot pairs, it returns baseCcy-USDT index price. For example, for LTC-ETH, this field returns the index price of LTC-USDT. |
| fillPnl | String | Last filled profit and loss, applicable to orders which have a trade and aim to close position. It always is 0 in other conditions |
| fillPxVol | String | Implied volatility when filled Only applicable to options; return "" for other instrument types |
| fillPxUsd | String | Options price when filled, in the unit of USD Only applicable to options; return "" for other instrument types |
| fillMarkVol | String | Mark volatility when filled Only applicable to options; return "" for other instrument types |
| fillFwdPx | String | Forward price when filled Only applicable to options; return "" for other instrument types |
| fillMarkPx | String | Mark price when filled Applicable to `FUTURES` FUTURES , `SWAP` SWAP , `OPTION` OPTION |
| side | String | Order side `buy` buy `sell` sell |
| posSide | String | Position side `long` long `short` short it returns `net` net in `net` net mode. |
| execType | String | Liquidity taker or maker `T` T : taker `M` M : maker Not applicable to system orders such as ADL and liquidation |
| feeCcy | String | Trading fee or rebate currency |
| fee | String | The amount of trading fee or rebate. The trading fee deduction is negative, such as '-0.01'; the rebate is positive, such as '0.01'. |
| ts | String | Data generation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 . |
| fillTime | String | Trade time which is the same as `fillTime` fillTime for the order channel. |
| feeRate | String | Fee rate. This field is returned for `SPOT` SPOT and `MARGIN` MARGIN only |

tradeId  
When the order category to which the transaction details belong is partial\_liquidation, full\_liquidation, or adl, this field will be assigned a negative value to distinguish it from other matching transaction scenarios.  

ordId  
Order ID, always "" for block trading.  

clOrdId  
Client-supplied order ID, always "" for block trading.

We advise you to use Get Transaction details (last 3 days)when you request data for recent 3 days.

### POST / Cancel All After

Cancel all pending orders after the countdown timeout. Applicable to all trading symbols through order book (except Spread trading)

#### Rate Limit: 1 request per second

#### Rate limit rule: User ID + tag

#### Permission: Trade

#### HTTP Request

`POST /api/v5/trade/cancel-all-after`

> Request Example

```highlight
POST /api/v5/trade/cancel-all-after
{
   "timeOut":"60"
}

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Set cancel all after
result = tradeAPI.cancel_all_after(
    timeOut="10"
)

print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| timeOut | String | Yes | The countdown for order cancellation, with second as the unit. Range of value can be 0, [10, 120]. Setting timeOut to 0 disables Cancel All After. |
| tag | String | No | CAA order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters. |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "triggerTime":"1587971460",
            "tag":"",
            "ts":"1587971400"
        }
    ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| triggerTime | String | The time the cancellation is triggered. triggerTime=0 means Cancel All After is disabled. |
| tag | String | CAA order tag |
| ts | String | The time the request is received. |

Users are recommended to send heartbeat to the exchange every second. When the cancel all after is triggered, the trading engine will cancel orders on behalf of the client one by one and this operation may take up to a few seconds. This feature is intended as a protection mechanism for clients only and clients should not use this feature as part of their trading strategies.

  
To use tag level CAA, first, users need to set tags for their orders using the `tag` request parameter in the placing orders endpoint. When calling the CAA endpoint, if the `tag` request parameter is not provided, the default will be to set CAA at the account level. In this case, all pending orders for all order book trading symbols under that sub-account will be cancelled when CAA triggers, consistent with the existing logic. If the `tag` request parameter is provided, CAA will be set at the order tag level. When triggered, only pending orders of order book trading symbols with the specified tag will be canceled, while orders with other tags or no tags will remain unaffected.
  
  
Users can run a maximum of 20 tag level CAAs simultaneously under the same sub-account. The system will only count live tag level CAAs. CAAs that have been triggered or revoked by the user will not be counted. The user will receive error code 51071 when exceeding the limit.

### GET / Account rate limit

Get account rate limit related information.

Only new order requests and amendment order requests will be counted towards this limit. For batch order requests consisting of multiple orders, each order will be counted individually.

For details, please refer to [Fill ratio based sub-account rate limit](https://my.okx.com/docs-v5/en/#overview-rate-limits-fill-ratio-based-sub-account-rate-limit)

#### Rate Limit: 1 request per second

#### Rate limit rule: User ID

#### HTTP Request

`GET /api/v5/trade/account-rate-limit`

> Request Example

```highlight
# Get the account rate limit
GET /api/v5/trade/account-rate-limit

```

#### Request Parameters

None

> Response Example

```highlight
{
   "code":"0",
   "data":[
      {
         "accRateLimit":"2000",
         "fillRatio":"0.1234",
         "mainFillRatio":"0.1234",
         "nextAccRateLimit":"2000",
         "ts":"123456789000"
      }
   ],
   "msg":""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| fillRatio | String | Sub account fill ratio during the monitoring period Applicable for users with trading fee level >= VIP 5 and return "" for others For accounts with no trading volume during the monitoring period, return "0". For accounts with trading volume but no order count due to our counting logic, return "9999". |
| mainFillRatio | String | Master account aggregated fill ratio during the monitoring period Applicable for users with trading fee level >= VIP 5 and return "" for others For accounts with no trading volume during the monitoring period, return "0" |
| accRateLimit | String | Current sub-account rate limit per two seconds |
| nextAccRateLimit | String | Expected sub-account rate limit (per two seconds) in the next period Applicable for users with trading fee level >= VIP 5 and return "" for others |
| ts | String | Data update time For users with trading fee level >= VIP 5, the data will be generated at 08:00 am (UTC) For users with trading fee level < VIP 5, return the current timestamp |

### WS / Order channel

Retrieve order information. Data will not be pushed when first subscribed. Data will only be pushed when there are order updates.

Concurrent connection to this channel will be restricted by the following rules: [WebSocket connection count limit](https://my.okx.com/docs-v5/en/#overview-websocket-connection-count-limit).

#### URL Path

/ws/v5/private (required login)

> Request Example : single

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "orders",
      "instType": "FUTURES",
      "instId": "BTC-USD-200329"
    }
  ]
}

```

```highlight
import asyncio

from okx.websocket.WsPrivateAsync import WsPrivateAsync

def callbackFunc(message):
    print(message)

async def main():

    ws = WsPrivateAsync(
        apiKey = "YOUR_API_KEY",
        passphrase = "YOUR_PASSPHRASE",
        secretKey = "YOUR_SECRET_KEY",
        url = "wss://ws.okx.com:8443/ws/v5/private",
        useServerTime=False
    )
    await ws.start()
    args = [
        {
          "channel": "orders",
          "instType": "FUTURES",
          "instId": "BTC-USD-200329"
        }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "orders",
      "instType": "FUTURES",
      "instFamily": "BTC-USD"
    }
  ]
}

```

```highlight
import asyncio

from okx.websocket.WsPrivateAsync import WsPrivateAsync

def callbackFunc(message):
    print(message)

async def main():

    ws = WsPrivateAsync(
        apiKey = "YOUR_API_KEY",
        passphrase = "YOUR_PASSPHRASE",
        secretKey = "YOUR_SECRET_KEY",
        url = "wss://ws.okx.com:8443/ws/v5/private",
        useServerTime=False
    )
    await ws.start()
    args =[
        {
          "channel": "orders",
          "instType": "FUTURES",
          "instFamily": "BTC-USD"
        }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `orders` orders |
| > instType | String | Yes | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION `ANY` ANY |
| > instFamily | String | No | Instrument family Applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| > instId | String | No | Instrument ID |

> Successful Response Example : single

```highlight
{
  "id": "1512",
    "event": "subscribe",
    "arg": {
        "channel": "orders",
        "instType": "FUTURES",
        "instId": "BTC-USD-200329"
    },
    "connId": "a4d3ae55"
}

```

> Successful Response Example

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "orders",
    "instType": "FUTURES",
    "instFamily": "BTC-USD"
  },
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"orders\", \"instType\" : \"FUTURES\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Event `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name |
| > instType | String | Yes | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `OPTION` OPTION `ANY` ANY |
| > instFamily | String | No | Instrument family |
| > instId | String | No | Instrument ID |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example

```highlight
{
    "arg": {
        "channel": "orders",
        "instType": "SPOT",
        "instId": "BTC-USDT",
        "uid": "614488474791936"
    },
    "data": [
        {
            "accFillSz": "0.001",
            "algoClOrdId": "",
            "algoId": "",
            "amendResult": "",
            "amendSource": "",
            "avgPx": "31527.1",
            "cancelSource": "",
            "category": "normal",
            "ccy": "",
            "clOrdId": "",
            "code": "0",
            "cTime": "1654084334977",
            "execType": "M",
            "fee": "-0.02522168",
            "feeCcy": "USDT",
            "fillFee": "-0.02522168",
            "fillFeeCcy": "USDT",
            "fillNotionalUsd": "31.50818374",
            "fillPx": "31527.1",
            "fillSz": "0.001",
            "fillPnl": "0.01",
            "fillTime": "1654084353263",
            "fillPxVol": "",
            "fillPxUsd": "",
            "fillMarkVol": "",
            "fillFwdPx": "",
            "fillMarkPx": "",
            "fillIdxPx": "",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "lever": "0",
            "msg": "",
            "notionalUsd": "31.50818374",
            "ordId": "452197707845865472",
            "ordType": "limit",
            "pnl": "0",
            "posSide": "",
            "px": "31527.1",
            "pxUsd":"",
            "pxVol":"",
            "pxType":"",
            "quickMgnType": "",
            "rebate": "0",
            "rebateCcy": "BTC",
            "reduceOnly": "false",
            "reqId": "",
            "side": "sell",
            "attachAlgoClOrdId": "",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "last",
            "source": "",
            "state": "filled",
            "stpId": "",
            "stpMode": "",
            "sz": "0.001",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "last",
            "attachAlgoOrds": [],
            "tradeId": "242589207",
            "tradeQuoteCcy": "USDT",
            "lastPx": "38892.2",
            "uTime": "1654084353264",
            "isTpLimit": "false",
            "linkedAlgoOrd": {
                "algoId": ""
            }
        }
    ]
}

```

#### Push data parameters

| Parameter | Type | Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| > uid | String | User Identifier |
| > instType | String | Instrument type |
| > instFamily | String | Instrument family |
| > instId | String | Instrument ID |
| data | Array of objects | Subscribed data |
| > instType | String | Instrument type |
| > instId | String | Instrument ID |
| > tgtCcy | String | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market orders. Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| > ccy | String | Margin currency Applicable to all `isolated` isolated `MARGIN` MARGIN orders and `cross` cross `MARGIN` MARGIN orders in `Futures mode` Futures mode . |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > tag | String | Order tag |
| > px | String | Price For options, use coin as unit (e.g. BTC, ETH) |
| > pxUsd | String | Options price in USDOnly applicable to options; return "" for other instrument types |
| > pxVol | String | Implied volatility of the options orderOnly applicable to options; return "" for other instrument types |
| > pxType | String | Price type of options `px` px : Place an order based on price, in the unit of coin (the unit for the request parameter px is BTC or ETH) `pxVol` pxVol : Place an order based on pxVol `pxUsd` pxUsd : Place an order based on pxUsd, in the unit of USD (the unit for the request parameter px is USD) |
| > sz | String | The original order quantity, `SPOT` SPOT / `MARGIN` MARGIN , in the unit of currency; `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION , in the unit of contract |
| > notionalUsd | String | Estimated national value in `USD` USD of order |
| > ordType | String | Order type `market` market : market order `limit` limit : limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order `optimal\_limit\_ioc` optimal\_limit\_ioc : Market order with immediate-or-cancel order (applicable only to Expiry Futures and Perpetual Futures) `mmp` mmp : Market Maker Protection (only applicable to Option in Portfolio Margin mode) `mmp\_and\_post\_only` mmp\_and\_post\_only : Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode). `op\_fok` op\_fok : Simple options (fok) |
| > side | String | Order side, `buy` buy `sell` sell |
| > posSide | String | Position side `net` net `long` long or `short` short Only applicable to `FUTURES` FUTURES / `SWAP` SWAP |
| > tdMode | String | Trade mode, `cross` cross : cross `isolated` isolated : isolated `cash` cash : cash |
| > fillPx | String | Last filled price |
| > tradeId | String | Last trade ID |
| > fillSz | String | Last filled quantity The unit is `base\_ccy` base\_ccy for SPOT and MARGIN, e.g. BTC-USDT, the unit is BTC; For market orders, the unit both is `base\_ccy` base\_ccy when the tgtCcy is `base\_ccy` base\_ccy or `quote\_ccy` quote\_ccy ; The unit is contract for `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| > fillPnl | String | Last filled profit and loss, applicable to orders which have a trade and aim to close position. It always is 0 in other conditions |
| > fillTime | String | Last filled time |
| > fillFee | String | last filled fee amount or rebate amount: Negative number represents the user transaction fee charged by the platform; Positive number represents rebate |
| > fillFeeCcy | String | last filled fee currency or rebate currency. It is fee currency when fillFee is less than 0; It is rebate currency when fillFee>=0. |
| > fillPxVol | String | Implied volatility when filled Only applicable to options; return "" for other instrument types |
| > fillPxUsd | String | Options price when filled, in the unit of USD Only applicable to options; return "" for other instrument types |
| > fillMarkVol | String | Mark volatility when filled Only applicable to options; return "" for other instrument types |
| > fillFwdPx | String | Forward price when filled Only applicable to options; return "" for other instrument types |
| > fillMarkPx | String | Mark price when filled Applicable to `FUTURES` FUTURES , `SWAP` SWAP , `OPTION` OPTION |
| > fillIdxPx | String | Index price at the moment of trade execution For cross currency spot pairs, it returns baseCcy-USDT index price. For example, for LTC-ETH, this field returns the index price of LTC-USDT. |
| > execType | String | Liquidity taker or maker of the last filled, T: taker M: maker |
| > accFillSz | String | Accumulated fill quantity The unit is `base\_ccy` base\_ccy for SPOT and MARGIN, e.g. BTC-USDT, the unit is BTC; For market orders, the unit both is `base\_ccy` base\_ccy when the tgtCcy is `base\_ccy` base\_ccy or `quote\_ccy` quote\_ccy ; The unit is contract for `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| > fillNotionalUsd | String | Filled notional value in `USD` USD of order |
| > avgPx | String | Average filled price. If none is filled, it will return `0` 0 . |
| > state | String | Order state `canceled` canceled `live` live `partially\_filled` partially\_filled `filled` filled `mmp\_canceled` mmp\_canceled |
| > lever | String | Leverage, from `0.01` 0.01 to `125` 125 . Only applicable to `MARGIN/FUTURES/SWAP` MARGIN/FUTURES/SWAP |
| > attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL. |
| > tpTriggerPx | String | Take-profit trigger price, it |
| > tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > tpOrdPx | String | Take-profit order price, it |
| > slTriggerPx | String | Stop-loss trigger price, it |
| > slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > slOrdPx | String | Stop-loss order price, it |
| > attachAlgoOrds | Array of objects | TP/SL information attached when placing order |
| >> attachAlgoId | String | The order ID of attached TP/SL order. It can be used to identity the TP/SL order when amending. It will not be posted to algoId when placing TP/SL order after the general order is filled completely. |
| >> attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to `algoClOrdId` algoClOrdId when placing TP/SL order once the general order is filled completely. |
| >> tpOrdKind | String | TP order kind `condition` condition `limit` limit |
| >> tpTriggerPx | String | Take-profit trigger price. |
| >> tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| >> tpOrdPx | String | Take-profit order price. |
| >> slTriggerPx | String | Stop-loss trigger price. |
| >> slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| >> slOrdPx | String | Stop-loss order price. |
| >> sz | String | Size. Only applicable to TP order of split TPs |
| >> amendPxOnTriggerType | String | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |
| > linkedAlgoOrd | Object | Linked SL order detail, only applicable to TP limit order of one-cancels-the-other order(oco) |
| >> algoId | Object | Algo ID |
| > stpId | String | Self trade prevention ID Return "" if self trade prevention is not applicable (deprecated) |
| > stpMode | String | Self trade prevention mode |
| > feeCcy | String | Fee currency `SPOT` SPOT / `MARGIN` MARGIN : If you buy, you will receive `base currency` base currency ; if you sell, you will receive `quota currency` quota currency `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION What is charged is the margin |
| > fee | String | Fee and rebate For spot and margin, it is accumulated fee charged by the platform. It is always negative, e.g. -0.01. For Expiry Futures, Perpetual Futures and Options, it is accumulated fee and rebate |
| > rebateCcy | String | Rebate currency, if there is no rebate, this field is "". |
| > rebate | String | Rebate accumulated amount, only applicable to spot and margin, the reward of placing orders from the platform (rebate) given to user who has reached the specified trading level. If there is no rebate, this field is "". |
| > pnl | String | Profit and loss, applicable to orders which have a trade and aim to close position. It always is 0 in other conditions. For liquidation under cross margin mode, it will include liquidation penalties. |
| > source | String | Order source `6` 6 : The normal order triggered by the `trigger order` trigger order `7` 7 :The normal order triggered by the `TP/SL order` TP/SL order `13` 13 : The normal order triggered by the algo order `25` 25 :The normal order triggered by the `trailing stop order` trailing stop order `34` 34 : The normal order triggered by the chase order |
| > cancelSource | String | Source of the order cancellation. Valid values and the corresponding meanings are: `0` 0 : Order canceled by system `1` 1 : Order canceled by user `2` 2 : Order canceled: Pre reduce-only order canceled, due to insufficient margin in user position `3` 3 : Order canceled: Risk cancellation was triggered. Pending order was canceled due to insufficient maintenance margin ratio and forced-liquidation risk. `4` 4 : Order canceled: Borrowings of crypto reached hard cap, order was canceled by system. `6` 6 : Order canceled: ADL order cancellation was triggered. Pending order was canceled due to a low margin ratio and forced-liquidation risk. `7` 7 : Order canceled: Futures contract delivery. `9` 9 : Order canceled: Insufficient balance after funding fees deducted. `10` 10 : Order canceled: Option contract expiration. `13` 13 : Order canceled: FOK order was canceled due to incompletely filled. `14` 14 : Order canceled: IOC order was partially canceled due to incompletely filled. `15` 15 : Order canceled: The order price is beyond the limit `17` 17 : Order canceled: Close order was canceled, due to the position was already closed at market price. `20` 20 : Cancel all after triggered `21` 21 : Order canceled: The TP/SL order was canceled because the position had been closed `22` 22 Order canceled: Due to a better price was available for the order in the same direction, the current operation reduce-only order was automatically canceled `23` 23 Order canceled: Due to a better price was available for the order in the same direction, the existing reduce-only order was automatically canceled `27` 27 : Order canceled: Price limit verification failed because the price difference between counterparties exceeds 5% `31` 31 : The post-only order will take liquidity in taker orders `32` 32 : Self trade prevention `33` 33 : The order exceeds the maximum number of order matches per taker order `36` 36 : Your TP limit order was canceled because the corresponding SL order was triggered. `37` 37 : Your TP limit order was canceled because the corresponding SL order was canceled. `38` 38 : You have canceled market maker protection (MMP) orders. `39` 39 : Your order was canceled because market maker protection (MMP) was triggered. `42` 42 : Your order was canceled because the difference between the initial and current best bid or ask prices reached the maximum chase difference. `43` 43 : Order cancelled because the buy order price is higher than the index price or the sell order price is lower than the index price. `44` 44 : Your order was canceled because your available balance of this crypto was insufficient for auto conversion. Auto conversion was triggered when the total collateralized liabilities for this crypto reached the platform’s risk control limit. |
| > amendSource | String | Source of the order amendation. `1` 1 : Order amended by user `2` 2 : Order amended by user, but the order quantity is overriden by system due to reduce-only `3` 3 : New order placed by user, but the order quantity is overriden by system due to reduce-only `4` 4 : Order amended by system due to other pending orders `5` 5 : Order modification due to changes in options px, pxVol, or pxUsd as a result of following variations. For example, when iv = 60, USD and px are anchored at iv = 60, the changes in USD or px lead to modification. |
| > category | String | Category `normal` normal `twap` twap `adl` adl `full\_liquidation` full\_liquidation `partial\_liquidation` partial\_liquidation `delivery` delivery `ddh` ddh : Delta dynamic hedge |
| > isTpLimit | String | Whether it is TP limit order. true or false |
| > uTime | String | Update time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > cTime | String | Creation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > reqId | String | Client Request ID as assigned by the client for order amendment. "" will be returned if there is no order amendment. |
| > amendResult | String | The result of amending the order `-1` -1 : failure `0` 0 : success `1` 1 : Automatic cancel (amendment request returned success but amendment subsequently failed then automatically canceled by the system) `2` 2 : Automatic amendation successfully, only applicable to pxVol and pxUsd orders of Option. When amending the order through API and `cxlOnFail` cxlOnFail is set to `true` true in the order amendment request but the amendment is rejected, "" is returned. When amending the order through API, the order amendment acknowledgement returns success and the amendment subsequently failed, `-1` -1 will be returned if `cxlOnFail` cxlOnFail is set to `false` false , `1` 1 will be returned if `cxlOnFail` cxlOnFail is set to `true` true . When amending the order through Web/APP and the amendment failed, `-1` -1 will be returned. |
| > reduceOnly | String | Whether the order can only reduce the position size. Valid options: `true` true or `false` false . |
| > quickMgnType | String | Quick Margin type, Only applicable to Quick Margin Mode of isolated margin `manual` manual , `auto\_borrow` auto\_borrow , `auto\_repay` auto\_repay |
| > algoClOrdId | String | Client-supplied Algo ID. There will be a value when algo order attaching `algoClOrdId` algoClOrdId is triggered, or it will be "". |
| > algoId | String | Algo ID. There will be a value when algo order is triggered, or it will be "". |
| > lastPx | String | Last price |
| > code | String | Error Code, the default is 0 |
| > msg | String | Error Message, The default is "" |
| > tradeQuoteCcy | String | The quote currency used for trading. |

For market orders, it's likely the orders channel will show order state as "filled" while showing the "last filled quantity (fillSz)" as 0.

In exceptional cases, the same message may be sent multiple times (perhaps with the different uTime) . The following guidelines are advised:  
  
1. If a `tradeId` is present, it means a fill. Each `tradeId` should only be returned once per instrument ID, and the later messages that have the same `tradeId` should be discarded.  
2. If `tradeId` is absent and the `state` is "filled," it means that the `SPOT`/`MARGIN` market order is fully filled. For messages with the same `ordId`, process only the first filled message and discard any subsequent messages. State = filled is the terminal state of an order.  
3. If the state is `canceled` or `mmp\_canceled`, it indicates that the order has been canceled. For cancellation messages with the same `ordId`, process the first one and discard later messages. State = canceled / mmp\_canceled is the terminal state of an order.  
4. If `reqId` is present, it indicates a response to a user-requested order modification. It is recommended to use a unique `reqId` for each modification request. For modification messages with the same `reqId`, process only the first message received and discard subsequent messages.

### WS / Place order

You can place an order only if you have sufficient funds.

#### URL Path

/ws/v5/private (required login)

#### Rate Limit: 60 requests per 2 seconds

#### Rate limit rule: User ID + Instrument ID

Rate limit is shared with the `Place order` REST API endpoints
> Request Example

```highlight
{
  "id": "1512",
  "op": "order",
  "args": [
    {
      "side": "buy",
      "instId": "BTC-USDT",
      "tdMode": "cash",
      "ordType": "market",
      "sz": "100"
    }
  ]
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | Yes | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `order` order |
| args | Array of objects | Yes | Request parameters |
| > instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| > tdMode | String | Yes | Trade mode `cash` cash |
| > clOrdId | String | No | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| > tag | String | No | Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters. |
| > side | String | Yes | Order side `buy` buy `sell` sell |
| > ordType | String | Yes | Order type `market` market : market order `limit` limit : limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order |
| > sz | String | Yes | Quantity to buy or sell. |
| > px | String | Conditional | Order price. Only applicable to `limit` limit , `post\_only` post\_only , `fok` fok , `ioc` ioc , `mmp` mmp , `mmp\_and\_post\_only` mmp\_and\_post\_only order. |
| > tgtCcy | String | No | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| > banAmend | Boolean | No | Whether to disallow the system from amending the size of the SPOT Market Order. Valid options: `true` true or `false` false . The default value is `false` false . If `true` true , system will not amend and reject the market order if user does not have sufficient funds. Only applicable to SPOT Market Orders |
| > stpId | String | No | Self trade prevention ID. Orders from the same master account with the same ID will be prevented from self trade. Numerical integers defined by user in the range of 1<= x<= 999999999 (deprecated) |
| > stpMode | String | No | Self trade prevention mode. Default to cancel maker `cancel\_maker` cancel\_maker , `cancel\_taker` cancel\_taker , `cancel\_both` cancel\_both Cancel both does not support FOK. |
| expTime | String | No | Request effective deadline. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| tradeQuoteCcy | String | No | The quote currency used for trading. Only applicable to `SPOT` SPOT . The default value is the quote currency of the `instId` instId , for example: for `BTC-USD` BTC-USD , the default is `USD` USD . |

> Successful Response Example

```highlight
{
  "id": "1512",
  "op": "order",
  "data": [
    {
      "clOrdId": "",
      "ordId": "12345689",
      "tag": "",
      "sCode": "0",
      "sMsg": ""
    }
  ],
  "code": "0",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "op": "order",
  "data": [
    {
      "clOrdId": "",
      "ordId": "",
      "tag": "",
      "sCode": "5XXXX",
      "sMsg": "not exist"
    }
  ],
  "code": "1",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When Format Error

```highlight
{
  "id": "1512",
  "op": "order",
  "data": [],
  "code": "60013",
  "msg": "Invalid args",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the message |
| op | String | Operation |
| code | String | Error Code |
| msg | String | Error message |
| data | Array of objects | Data |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > tag | String | Order tag |
| > sCode | String | Order status code, `0` 0 means success |
| > sMsg | String | Rejection or success message of event execution. |
| inTime | String | Timestamp at Websocket gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |
| outTime | String | Timestamp at Websocket gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

clOrdId  
clOrdId is a user-defined unique ID used to identify the order. It will be included in the response parameters if you have specified during order submission, and can be used as a request parameter to the endpoints to query, cancel and amend orders.   
clOrdId must be unique among the clOrdIds of all pending orders.

ordType   
Order type. When creating a new order, you must specify the order type. The order type you specify will affect: 1) what order parameters are required, and 2) how the matching system executes your order. The following are valid order types:   
limit: Limit order, which requires specified sz and px.   
market: Market order. For SPOT and MARGIN, market order will be filled with market price (by swiping opposite order book). For Expiry Futures and Perpetual Futures, market order will be placed to order book with most aggressive price allowed by Price Limit Mechanism. For OPTION, market order is not supported yet. As the filled price for market orders cannot be determined in advance, OKX reserves/freezes your quote currency by an additional 5% for risk check.   
post\_only: Post-only order, which the order can only provide liquidity to the market and be a maker. If the order would have executed on placement, it will be canceled instead.   
fok: Fill or kill order. If the order cannot be fully filled, the order will be canceled. The order would not be partially filled.   
ioc: Immediate or cancel order. Immediately execute the transaction at the order price, cancel the remaining unfilled quantity of the order, and the order quantity will not be displayed in the order book.   
optimal\_limit\_ioc: Market order with ioc (immediate or cancel). Immediately execute the transaction of this market order, cancel the remaining unfilled quantity of the order, and the order quantity will not be displayed in the order book. Only applicable to Expiry Futures and Perpetual Futures.

sz  
Quantity to buy or sell.   
For SPOT Buy and Sell Limit Orders, it refers to the quantity in base currency.   
For SPOT Buy Market Orders, it refers to the quantity in quote currency.   
For SPOT Sell Market Orders, it refers to the quantity in base currency.   
For SPOT Market Orders, it is set by tgtCcy.   

tgtCcy  
This parameter is used to specify the order quantity in the order request is denominated in the quantity of base or quote currency. This is applicable to SPOT Market Orders only.  
Base currency: base\_ccy  
Quote currency: quote\_ccy
  
If you use the Base Currency quantity for buy market orders or the Quote Currency for sell market orders, please note:
  
1. If the quantity you enter is greater than what you can buy or sell, the system will execute the order according to your maximum buyable or sellable quantity. If you want to trade according to the specified quantity, you should use Limit orders.
  
2. When the market price is too volatile, the locked balance may not be sufficient to buy the Base Currency quantity or sell to receive the Quote Currency that you specified. We will change the quantity of the order to execute the order based on best effort principle based on your account balance. In addition, we will try to over lock a fraction of your balance to avoid changing the order quantity.
  
2.1 Example of base currency buy market order:
  
Taking the market order to buy 10 LTCs as an example, and the user can buy 11 LTC. At this time, if 10 < 11, the order is accepted. When the LTC-USDT market price is 200, and the locked balance of the user is 3,000 USDT, as 200\*10 < 3,000, the market order of 10 LTC is fully executed;
If the market is too volatile and the LTC-USDT market price becomes 400, 400\*10 > 3,000, the user's locked balance is not sufficient to buy using the specified amount of base currency, the user's maximum locked balance of 3,000 USDT will be used to settle the trade. Final transaction quantity becomes 3,000/400 = 7.5 LTC.
  
2.2 Example of quote currency sell market order:
  
Taking the market order to sell 1,000 USDT as an example, and the user can sell 1,200 USDT, 1,000 < 1,200, the order is accepted. When the LTC-USDT market price is 200, and the locked balance of the user is 6 LTC, as 1,000/200 < 6, the market order of 1,000 USDT is fully executed;
If the market is too volatile and the LTC-USDT market price becomes 100, 100\*6 < 1,000, the user's locked balance is not sufficient to sell using the specified amount of quote currency, the user's maximum locked balance of 6 LTC will be used to settle the trade. Final transaction quantity becomes 6 \* 100 = 600 USDT.

Mandatory self trade prevention (STP)  
The trading platform imposes mandatory self trade prevention at master account level, which means the accounts under the same master account, including master account itself and all its affiliated sub-accounts, will be prevented from self trade. The default STP mode is `Cancel Maker`. Users can also utilize the stpMode request parameter of the placing order endpoint to determine the stpMode of a certain order.  
Mandatory self trade prevention will not lead to latency.   
There are three STP modes. The STP mode is always taken based on the configuration in the taker order.  
1. Cancel Maker: This is the default STP mode, which cancels the maker order to prevent self-trading. Then, the taker order continues to match with the next order based on the order book priority.  
2. Cancel Taker: The taker order is canceled to prevent self-trading. If the user's own maker order is lower in the order book priority, the taker order is partially filled and then canceled. FOK orders are always honored and canceled if they would result in self-trading.  
3. Cancel Both: Both taker and maker orders are canceled to prevent self-trading. If the user's own maker order is lower in the order book priority, the taker order is partially filled. Then, the remaining quantity of the taker order and the first maker order are canceled. FOK orders are not supported in this mode.

### WS / Place multiple orders

Place orders in a batch. Maximum 20 orders can be placed per request

#### URL Path

/ws/v5/private (required login)

#### Rate Limit: 300 orders per 2 seconds

#### Rate limit rule: User ID + Instrument ID

Unlike other endpoints, the rate limit of this endpoint is determined by the number of orders. If there is only one order in the request, it will consume the rate limit of `Place order`.

Rate limit is shared with the `Place multiple orders` REST API endpoints
> Request Example

```highlight
{
  "id": "1513",
  "op": "batch-orders",
  "args": [
    {
      "side": "buy",
      "instId": "BTC-USDT",
      "tdMode": "cash",
      "ordType": "market",
      "sz": "100"
    },
    {
      "side": "buy",
      "instId": "LTC-USDT",
      "tdMode": "cash",
      "ordType": "market",
      "sz": "1"
    }
  ]
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | Yes | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `batch-orders` batch-orders |
| args | Array of objects | Yes | Request Parameters |
| > instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| > tdMode | String | Yes | Trade mode `cash` cash |
| > clOrdId | String | No | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| > tag | String | No | Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters. |
| > side | String | Yes | Order side `buy` buy `sell` sell |
| > ordType | String | Yes | Order type `market` market : market order `limit` limit : limit order `post\_only` post\_only : Post-only order `fok` fok : Fill-or-kill order `ioc` ioc : Immediate-or-cancel order |
| > sz | String | Yes | Quantity to buy or sell. |
| > px | String | Conditional | Order price. Only applicable to `limit` limit , `post\_only` post\_only , `fok` fok , `ioc` ioc , `mmp` mmp , `mmp\_and\_post\_only` mmp\_and\_post\_only order. |
| > tgtCcy | String | No | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| > banAmend | Boolean | No | Whether to disallow the system from amending the size of the SPOT Market Order. Valid options: `true` true or `false` false . The default value is `false` false . If `true` true , system will not amend and reject the market order if user does not have sufficient funds. Only applicable to SPOT Market Orders |
| > stpId | String | No | Self trade prevention ID. Orders from the same master account with the same ID will be prevented from self trade. Numerical integers defined by user in the range of 1<= x<= 999999999 (deprecated) |
| > stpMode | String | No | Self trade prevention mode. Default to cancel maker `cancel\_maker` cancel\_maker , `cancel\_taker` cancel\_taker , `cancel\_both` cancel\_both Cancel both does not support FOK. |
| expTime | String | No | Request effective deadline. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| tradeQuoteCcy | String | No | The quote currency used for trading. Only applicable to `SPOT` SPOT . The default value is the quote currency of the `instId` instId , for example: for `BTC-USD` BTC-USD , the default is `USD` USD . |

> Response Example When All Succeed

```highlight
{
  "id": "1513",
  "op": "batch-orders",
  "data": [
    {
      "clOrdId": "",
      "ordId": "12345689",
      "tag": "",
      "sCode": "0",
      "sMsg": ""
    },
    {
      "clOrdId": "",
      "ordId": "12344",
      "tag": "",
      "sCode": "0",
      "sMsg": ""
    }
  ],
  "code": "0",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When Partially Successful

```highlight
{
  "id": "1513",
  "op": "batch-orders",
  "data": [
    {
      "clOrdId": "",
      "ordId": "12345689",
      "tag": "",
      "sCode": "0",
      "sMsg": ""
    },
    {
      "clOrdId": "",
      "ordId": "",
      "tag": "",
      "sCode": "5XXXX",
      "sMsg": "Insufficient margin"
    }
  ],
  "code": "2",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When All Failed

```highlight
{
  "id": "1513",
  "op": "batch-orders",
  "data": [
    {
      "clOrdId": "oktswap6",
      "ordId": "",
      "tag": "",
      "sCode": "5XXXX",
      "sMsg": "Insufficient margin"
    },
    {
      "clOrdId": "oktswap7",
      "ordId": "",
      "tag": "",
      "sCode": "5XXXX",
      "sMsg": "Insufficient margin"
    }
  ],
  "code": "1",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When Format Error

```highlight
{
  "id": "1513",
  "op": "batch-orders",
  "data": [],
  "code": "60013",
  "msg": "Invalid args",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the message |
| op | String | Operation |
| code | String | Error Code |
| msg | String | Error message |
| data | Array of objects | Data |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > tag | String | Order tag |
| > sCode | String | Order status code, `0` 0 means success |
| > sMsg | String | Rejection or success message of event execution. |
| inTime | String | Timestamp at Websocket gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |
| outTime | String | Timestamp at Websocket gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

clOrdId  
clOrdId is a user-defined unique ID used to identify the order. It will be included in the response parameters if you have specified during order submission, and can be used as a request parameter to the endpoints to query, cancel and amend orders.   
clOrdId must be unique among all pending orders and the current request.

### WS / Cancel order

Cancel an incomplete order

#### URL Path

/ws/v5/private (required login)

#### Rate Limit: 60 requests per 2 seconds

#### Rate limit rule: User ID + Instrument ID

Rate limit is shared with the `Cancel order` REST API endpoints
> Request Example

```highlight
{
  "id": "1514",
  "op": "cancel-order",
  "args": [
    {
      "instId": "BTC-USDT",
      "ordId": "2510789768709120"
    }
  ]
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | Yes | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `cancel-order` cancel-order |
| args | Array of objects | Yes | Request Parameters |
| > instId | String | Yes | Instrument ID |
| > ordId | String | Conditional | Order ID Either `ordId` ordId or `clOrdId` clOrdId is required, if both are passed, ordId will be used |
| > clOrdId | String | Conditional | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |

> Successful Response Example

```highlight
{
  "id": "1514",
  "op": "cancel-order",
  "data": [
    {
      "clOrdId": "",
      "ordId": "2510789768709120",
      "sCode": "0",
      "sMsg": ""
    }
  ],
  "code": "0",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Failure Response Example

```highlight
{
  "id": "1514",
  "op": "cancel-order",
  "data": [
    {
      "clOrdId": "",
      "ordId": "2510789768709120",
      "sCode": "5XXXX",
      "sMsg": "Order not exist"
    }
  ],
  "code": "1",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When Format Error

```highlight
{
  "id": "1514",
  "op": "cancel-order",
  "data": [],
  "code": "60013",
  "msg": "Invalid args",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the message |
| op | String | Operation |
| code | String | Error Code |
| msg | String | Error message |
| data | Array of objects | Data |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > sCode | String | Order status code, `0` 0 means success |
| > sMsg | String | Order status message |
| inTime | String | Timestamp at Websocket gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |
| outTime | String | Timestamp at Websocket gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

Cancel order returns with sCode equal to 0. It is not strictly considered that the order has been canceled. It only means that your cancellation request has been accepted by the system server. The result of the cancellation is subject to the state pushed by the order channel or the get order state.  

### WS / Cancel multiple orders

Cancel incomplete orders in batches. Maximum 20 orders can be canceled per request.

#### URL Path

/ws/v5/private (required login)

#### Rate Limit: 300 orders per 2 seconds

#### Rate limit rule: User ID + Instrument ID

Unlike other endpoints, the rate limit of this endpoint is determined by the number of orders. If there is only one order in the request, it will consume the rate limit of `Cancel order`.

Rate limit is shared with the `Cancel multiple orders` REST API endpoints
> Request Example

```highlight
{
  "id": "1515",
  "op": "batch-cancel-orders",
  "args": [
    {
      "instId": "BTC-USDT",
      "ordId": "2517748157541376"
    },
    {
      "instId": "LTC-USDT",
      "ordId": "2517748155771904"
    }
  ]
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | Yes | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `batch-cancel-orders` batch-cancel-orders |
| args | Array of objects | Yes | Request Parameters |
| > instId | String | Yes | Instrument ID |
| > ordId | String | Conditional | Order ID Either `ordId` ordId or `clOrdId` clOrdId is required, if both are passed, ordId will be used |
| > clOrdId | String | Conditional | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |

> Response Example When All Succeed

```highlight
{
  "id": "1515",
  "op": "batch-cancel-orders",
  "data": [
    {
      "clOrdId": "oktswap6",
      "ordId": "2517748157541376",
      "sCode": "0",
      "sMsg": ""
    },
    {
      "clOrdId": "oktswap7",
      "ordId": "2517748155771904",
      "sCode": "0",
      "sMsg": ""
    }
  ],
  "code": "0",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When partially successfully

```highlight
{
  "id": "1515",
  "op": "batch-cancel-orders",
  "data": [
    {
      "clOrdId": "oktswap6",
      "ordId": "2517748157541376",
      "sCode": "0",
      "sMsg": ""
    },
    {
      "clOrdId": "oktswap7",
      "ordId": "2517748155771904",
      "sCode": "5XXXX",
      "sMsg": "order not exist"
    }
  ],
  "code": "2",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When All Failed

```highlight
{
  "id": "1515",
  "op": "batch-cancel-orders",
  "data": [
    {
      "clOrdId": "oktswap6",
      "ordId": "2517748157541376",
      "sCode": "5XXXX",
      "sMsg": "order not exist"
    },
    {
      "clOrdId": "oktswap7",
      "ordId": "2517748155771904",
      "sCode": "5XXXX",
      "sMsg": "order not exist"
    }
  ],
  "code": "1",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When Format Error

```highlight
{
  "id": "1515",
  "op": "batch-cancel-orders",
  "data": [],
  "code": "60013",
  "msg": "Invalid args",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the message |
| op | String | Operation |
| code | String | Error Code |
| msg | String | Error message |
| data | Array of objects | Data |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > sCode | String | Order status code, `0` 0 means success |
| > sMsg | String | Order status message |
| inTime | String | Timestamp at Websocket gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |
| outTime | String | Timestamp at Websocket gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

### WS / Amend order

Amend an incomplete order.

#### URL Path

/ws/v5/private (required login)

#### Rate Limit: 60 requests per 2 seconds

#### Rate limit rule: User ID + Instrument ID

Rate limit is shared with the `Amend order` REST API endpoints
> Request Example

```highlight
{
  "id": "1512",
  "op": "amend-order",
  "args": [
    {
      "instId": "BTC-USDT",
      "ordId": "2510789768709120",
      "newSz": "2"
    }
  ]
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | Yes | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `amend-order` amend-order |
| args | Array of objects | Yes | Request Parameters |
| > instId | String | Yes | Instrument ID |
| > cxlOnFail | Boolean | No | Whether the order needs to be automatically canceled when the order amendment fails Valid options: false or true, the default is false. |
| > ordId | String | Conditional | Order ID Either `ordId` ordId or `clOrdId` clOrdId is required, if both are passed, `ordId` ordId will be used. |
| > clOrdId | String | Conditional | Client Order ID as assigned by the client |
| > reqId | String | No | Client Request ID as assigned by the client for order amendment A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| > newSz | String | Conditional | New quantity after amendment. Either `newSz` newSz or `newPx` newPx is required. When amending a partially-filled order, the `newSz` newSz should include the amount that has been filled. |
| > newPx | String | Conditional | New price after amendment. |
| expTime | String | No | Request effective deadline. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

> Successful Response Example

```highlight
{
  "id": "1512",
  "op": "amend-order",
  "data": [
    {
      "clOrdId": "",
      "ordId": "2510789768709120",
      "reqId": "b12344",
      "sCode": "0",
      "sMsg": ""
    }
  ],
  "code": "0",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "op": "amend-order",
  "data": [
    {
      "clOrdId": "",
      "ordId": "2510789768709120",
      "reqId": "b12344",
      "sCode": "5XXXX",
      "sMsg": "order not exist"
    }
  ],
  "code": "1",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When Format Error

```highlight
{
  "id": "1512",
  "op": "amend-order",
  "data": [],
  "code": "60013",
  "msg": "Invalid args",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the message |
| op | String | Operation |
| code | String | Error Code |
| msg | String | Error message |
| data | Array of objects | Data |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > reqId | String | Client Request ID as assigned by the client for order amendment |
| > sCode | String | Order status code, `0` 0 means success |
| > sMsg | String | Order status message |
| inTime | String | Timestamp at Websocket gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |
| outTime | String | Timestamp at Websocket gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

newSz   
If the new quantity of the order is less than or equal to the filled quantity when you are amending a partially-filled order, the order status will be changed to filled.

The amend order returns sCode equal to 0. It is not strictly considered that the order has been amended. It only means that your amend order request has been accepted by the system server. The result of the amend is subject to the status pushed by the order channel or the order status query

### WS / Amend multiple orders

Amend incomplete orders in batches. Maximum 20 orders can be amended per request.

#### URL Path

/ws/v5/private (required login)

#### Rate Limit: 300 orders per 2 seconds

#### Rate limit rule: User ID + Instrument ID

Unlike other endpoints, the rate limit of this endpoint is determined by the number of orders. If there is only one order in the request, it will consume the rate limit of `Amend order`.

Rate limit is shared with the `Amend multiple orders` REST API endpoints
> Request Example

```highlight
{
  "id": "1513",
  "op": "batch-amend-orders",
  "args": [
    {
      "instId": "BTC-USDT",
      "ordId": "12345689",
      "newSz": "2"
    },
    {
      "instId": "BTC-USDT",
      "ordId": "12344",
      "newSz": "2"
    }
  ]
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | Yes | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `batch-amend-orders` batch-amend-orders |
| args | Array of objects | Yes | Request Parameters |
| > instId | String | Yes | Instrument ID |
| > cxlOnFail | Boolean | No | Whether the order needs to be automatically canceled when the order amendment fails Valid options: `false` false or `true` true , the default is `false` false . |
| > ordId | String | Conditional | Order ID Either `ordId` ordId or `clOrdId` clOrdId is required, if both are passed, `ordId` ordId will be used. |
| > clOrdId | String | Conditional | Client Order ID as assigned by the client |
| > reqId | String | No | Client Request ID as assigned by the client for order amendment A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| > newSz | String | Conditional | New quantity after amendment. Either `newSz` newSz or `newPx` newPx is required. When amending a partially-filled order, the `newSz` newSz should include the amount that has been filled. |
| > newPx | String | Conditional | New price after amendment. |
| expTime | String | No | Request effective deadline. Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

> Response Example When All Succeed

```highlight
{
  "id": "1513",
  "op": "batch-amend-orders",
  "data": [
    {
      "clOrdId": "oktswap6",
      "ordId": "12345689",
      "reqId": "b12344",
      "sCode": "0",
      "sMsg": ""
    },
    {
      "clOrdId": "oktswap7",
      "ordId": "12344",
      "reqId": "b12344",
      "sCode": "0",
      "sMsg": ""
    }
  ],
  "code": "0",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When All Failed

```highlight
{
  "id": "1513",
  "op": "batch-amend-orders",
  "data": [
    {
      "clOrdId": "",
      "ordId": "12345689",
      "reqId": "b12344",
      "sCode": "5XXXX",
      "sMsg": "order not exist"
    },
    {
      "clOrdId": "oktswap7",
      "ordId": "",
      "reqId": "b12344",
      "sCode": "5XXXX",
      "sMsg": "order not exist"
    }
  ],
  "code": "1",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When Partially Successful

```highlight
{
  "id": "1513",
  "op": "batch-amend-orders",
  "data": [
    {
      "clOrdId": "",
      "ordId": "12345689",
      "reqId": "b12344",
      "sCode": "0",
      "sMsg": ""
    },
    {
      "clOrdId": "oktswap7",
      "ordId": "",
      "reqId": "b12344",
      "sCode": "5XXXX",
      "sMsg": "order not exist"
    }
  ],
  "code": "2",
  "msg": "",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

> Response Example When Format Error

```highlight
{
  "id": "1513",
  "op": "batch-amend-orders",
  "data": [],
  "code": "60013",
  "msg": "Invalid args",
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the message |
| op | String | Operation |
| code | String | Error Code |
| msg | String | Error message |
| data | Array of objects | Data |
| > ordId | String | Order ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > reqId | String | Client Request ID as assigned by the client for order amendment If the user provides reqId in the request, the corresponding reqId will be returned |
| > sCode | String | Order status code, `0` 0 means success |
| > sMsg | String | Order status message |
| inTime | String | Timestamp at Websocket gateway when the request is received, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |
| outTime | String | Timestamp at Websocket gateway when the response is sent, Unix timestamp format in microseconds, e.g. `1597026383085123` 1597026383085123 |

newSz   
If the new quantity of the order is less than or equal to the filled quantity when you are amending a partially-filled order, the order status will be changed to filled.

## Algo Trading

### POST / Place algo order

The algo order includes `trigger` order, `oco` order, `conditional` order and trailing order.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: User ID + Instrument ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/trade/order-algo`

> Request Example

```highlight
# Place Take Profit / Stop Loss Order
POST /api/v5/trade/order-algo
body
{
    "instId":"BTC-USDT",
    "tdMode":"cash",
    "side":"buy",
    "ordType":"conditional",
    "sz":"2",
    "tpTriggerPx":"15",
    "tpOrdPx":"18"
}

# Place Trigger Order
POST /api/v5/trade/order-algo
body
{
    "instId": "BTC-USDT",
    "tdMode": "cash",
    "side": "buy",
    "ordType": "trigger",
    "sz": "10",
    "triggerPx": "100",
    "orderPx": "-1"
}

# Place Trailing Stop Order
POST /api/v5/trade/order-algo
body
{
    "instId": "BTC-USDT",
    "tdMode": "cash",
    "side": "buy",
    "ordType": "move_order_stop",
    "sz": "10",
    "callbackRatio": "0.05"
}

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# One-way stop order
result = tradeAPI.place_algo_order(
    instId="BTC-USDT",
    tdMode="cash",
    side="buy",
    ordType="conditional",
    sz="2",
    tpTriggerPx="15",
    tpOrdPx="18"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| tdMode | String | Yes | Trade mode `cash` cash |
| side | String | Yes | Order side `buy` buy `sell` sell |
| ordType | String | Yes | Order type `conditional` conditional : One-way stop order `oco` oco : One-cancels-the-other order `trigger` trigger : Trigger order `move\_order\_stop` move\_order\_stop : Trailing order |
| sz | String | Yes | Quantity to buy or sell |
| tag | String | No | Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters. |
| tgtCcy | String | No | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT traded with Market buy `conditional` conditional order Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| algoClOrdId | String | No | Client-supplied Algo ID A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |

**Take Profit / Stop Loss Order**

Predefine the price you want the order to trigger a market order to execute immediately or it will place a limit order.   
This type of order will not freeze your free margin in advance.

learn more about [Take Profit / Stop Loss Order](https://my.okx.com/help/11015447687437)

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| tpTriggerPx | String | No | Take-profit trigger price If you fill in this parameter, you should fill in the take-profit order price as well. |
| tpTriggerPxType | String | No | Take-profit trigger price type `last` last : last price The default is `last` last |
| tpOrdPx | String | No | Take-profit order price If you fill in this parameter, you should fill in the take-profit trigger price as well. If the price is `-1` -1 , take-profit will be executed at the market price. |
| slTriggerPx | String | No | Stop-loss trigger price If you fill in this parameter, you should fill in the stop-loss order price. |
| slTriggerPxType | String | No | Stop-loss trigger price type `last` last : last price The default is `last` last |
| slOrdPx | String | No | Stop-loss order price If you fill in this parameter, you should fill in the stop-loss trigger price. If the price is `-1` -1 , stop-loss will be executed at the market price. |

Take Profit / Stop Loss Order  
When placing net TP/SL order (ordType=conditional) and both take-profit and stop-loss parameters are sent, only stop-loss logic will be performed and take-profit logic will be ignored.

**Trigger Order**

Use a trigger order to place a market or limit order when a specific price level is crossed.   
When a Trigger Order is triggered, if your account balance is lower than the order amount, the system will automatically place the order based on your current balance.   
Trigger orders do not freeze assets when placed.

learn more about [Trigger Order](https://my.okx.com/help/11015447687437)

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| triggerPx | String | Yes | Trigger price |
| orderPx | String | Yes | Order Price If the price is `-1` -1 , the order will be executed at the market price. |
| triggerPxType | String | No | Trigger price type `last` last : last price The default is `last` last |

**Trailing Stop Order**

A trailing stop order is a stop order that tracks the market price. Its trigger price changes with the market price. Once the trigger price is reached, a market order is placed.  
Actual trigger price for sell orders and short positions = Highest price after order placement – Trail variance (Var.), or Highest price after placement × (1 – Trail variance) (Ratio).  
Actual trigger price for buy orders and long positions = Lowest price after order placement + Trail variance, or Lowest price after order placement × (1 + Trail variance).  
You can use the activation price to set the activation condition for a trailing stop order.

learn more about [Trailing Stop Order](https://my.okx.com/help/11015447687437)

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| callbackRatio | String | Conditional | Callback price ratio, e.g. `0.01` 0.01 represents `1%` 1% Either `callbackRatio` callbackRatio or `callbackSpread` callbackSpread is allowed to be passed. |
| callbackSpread | String | Conditional | Callback price variance |
| activePx | String | No | Active price The system will only start tracking the market and calculating your trigger price after the activation price is reached. If you don’t set a price, your order will be activated as soon as it’s placed. |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "algoClOrdId": "order1234",
            "algoId": "1836487817828872192",
            "clOrdId": "",
            "sCode": "0",
            "sMsg": "",
            "tag": ""
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| algoId | String | Algo ID |
| clOrdId | String | Client Order ID as assigned by the client Client Order ID as assigned by the client (Deprecated) |
| algoClOrdId | String | Client-supplied Algo ID |
| sCode | String | The code of the event execution result, `0` 0 means success. |
| sMsg | String | Rejection message if the request is unsuccessful. |

### POST / Cancel algo order

Cancel unfilled algo orders. A maximum of 10 orders can be canceled per request. Request parameters should be passed in the form of an array.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: User ID + Instrument ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/trade/cancel-algos`

> Request Example

```highlight
POST /api/v5/trade/cancel-algos
body
[
    {
        "algoId":"198273485",
        "instId":"BTC-USDT"
    },
    {
        "algoId":"198273485",
        "instId":"BTC-USDT"
    }
]

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| algoId | String | Yes | Algo ID |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "algoClOrdId": "",
            "algoId": "1836489397437468672",
            "clOrdId": "",
            "sCode": "0",
            "sMsg": "",
            "tag": ""
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| algoId | String | Algo ID |
| sCode | String | The code of the event execution result, `0` 0 means success. |
| sMsg | String | Rejection message if the request is unsuccessful. |
| clOrdId | String | Client Order ID as assigned by the client Client Order ID as assigned by the client (Deprecated) |
| algoClOrdId | String | Client-supplied Algo ID Client-supplied Algo ID (Deprecated) |
| tag | String | Order tag Order tag (Deprecated) |

### POST / Amend algo order

Amend unfilled algo orders (Support Stop order and Trigger order only, not including Move\_order\_stop order, Iceberg order, TWAP order, Trailing Stop order).

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: User ID + Instrument ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/trade/amend-algos`

> Request Example

```highlight
POST /api/v5/trade/amend-algos
body
{
    "algoId":"2510789768709120",
    "newSz":"2",
    "instId":"BTC-USDT"
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID |
| algoId | String | Conditional | Algo ID Either `algoId` algoId or `algoClOrdId` algoClOrdId is required. If both are passed, `algoId` algoId will be used. |
| algoClOrdId | String | Conditional | Client-supplied Algo ID Either `algoId` algoId or `algoClOrdId` algoClOrdId is required. If both are passed, `algoId` algoId will be used. |
| cxlOnFail | Boolean | No | Whether the order needs to be automatically canceled when the order amendment fails Valid options: `false` false or `true` true , the default is `false` false . |
| reqId | String | Conditional | Client Request ID as assigned by the client for order amendment A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. The response will include the corresponding `reqId` reqId to help you identify the request if you provide it in the request. |
| newSz | String | Conditional | New quantity after amendment and it has to be larger than 0. |

**Take Profit / Stop Loss Order**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| newTpTriggerPx | String | Conditional | Take-profit trigger price. Either the take-profit trigger price or order price is 0, it means that the take-profit is deleted |
| newTpOrdPx | String | Conditional | Take-profit order price If the price is -1, take-profit will be executed at the market price. |
| newSlTriggerPx | String | Conditional | Stop-loss trigger price. Either the stop-loss trigger price or order price is 0, it means that the stop-loss is deleted |
| newSlOrdPx | String | Conditional | Stop-loss order price If the price is -1, stop-loss will be executed at the market price. |
| newTpTriggerPxType | String | Conditional | Take-profit trigger price type `last` last : last price `index` index : index price `mark` mark : mark price |
| newSlTriggerPxType | String | Conditional | Stop-loss trigger price type `last` last : last price `index` index : index price `mark` mark : mark price |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "algoClOrdId":"algo_01",
            "algoId":"2510789768709120",
            "reqId":"po103ux",
            "sCode":"0",
            "sMsg":""
        }
    ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| algoId | String | Algo ID |
| algoClOrdId | String | Client-supplied Algo ID |
| reqId | String | Client Request ID as assigned by the client for order amendment. |
| sCode | String | The code of the event execution result, `0` 0 means success. |
| sMsg | String | Rejection message if the request is unsuccessful. |

### GET / Algo order details

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/trade/order-algo`

> Request Example

```highlight
GET /api/v5/trade/order-algo?algoId=1753184812254216192

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| algoId | String | Conditional | Algo ID Either `algoId` algoId or `algoClOrdId` algoClOrdId is required.If both are passed, `algoId` algoId will be used. |
| algoClOrdId | String | Conditional | Client-supplied Algo ID A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "activePx": "",
            "actualPx": "",
            "actualSide": "",
            "actualSz": "0",
            "algoClOrdId": "",
            "algoId": "1753184812254216192",
            "amendPxOnTriggerType": "0",
            "attachAlgoOrds": [],
            "cTime": "1724751378980",
            "callbackRatio": "",
            "callbackSpread": "",
            "ccy": "",
            "chaseType": "",
            "chaseVal": "",
            "clOrdId": "",
            "closeFraction": "",
            "failCode": "0",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "isTradeBorrowMode": "",
            "last": "62916.5",
            "lever": "",
            "linkedOrd": {
                "ordId": ""
            },
            "maxChaseType": "",
            "maxChaseVal": "",
            "moveTriggerPx": "",
            "ordId": "",
            "ordIdList": [],
            "ordPx": "",
            "ordType": "conditional",
            "posSide": "net",
            "pxLimit": "",
            "pxSpread": "",
            "pxVar": "",
            "quickMgnType": "",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "state": "live",
            "sz": "10",
            "szLimit": "",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "quote_ccy",
            "timeInterval": "",
            "tpOrdPx": "-1",
            "tpTriggerPx": "10000",
            "tpTriggerPxType": "last",
            "triggerPx": "",
            "triggerPxType": "",
            "triggerTime": "",
            "tradeQuoteCcy": "USDT",
            "uTime": "1724751378980"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID |
| ccy | String | Margin currency Applicable to all `isolated` isolated `MARGIN` MARGIN orders and `cross` cross `MARGIN` MARGIN orders in `Futures mode` Futures mode . |
| ordId | String | Latest order ID. It will be deprecated soon |
| ordIdList | Array of strings | Order ID list. There will be multiple order IDs when there is TP/SL splitting order. |
| algoId | String | Algo ID |
| clOrdId | String | Client Order ID as assigned by the client |
| sz | String | Quantity to buy or sell |
| closeFraction | String | Fraction of position to be closed when the algo order is triggered |
| ordType | String | Order type |
| side | String | Order side |
| posSide | String | Position side |
| tdMode | String | Trade mode |
| tgtCcy | String | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| state | String | State `live` live `pause` pause `partially\_effective` partially\_effective `effective` effective `canceled` canceled `order\_failed` order\_failed `partially\_failed` partially\_failed |
| lever | String | Leverage, from `0.01` 0.01 to `125` 125 . Only applicable to `MARGIN/FUTURES/SWAP` MARGIN/FUTURES/SWAP |
| tpTriggerPx | String | Take-profit trigger price. |
| tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| tpOrdPx | String | Take-profit order price. |
| slTriggerPx | String | Stop-loss trigger price. |
| slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| slOrdPx | String | Stop-loss order price. |
| triggerPx | String | trigger price. |
| triggerPxType | String | trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| ordPx | String | Order price for the trigger order |
| actualSz | String | Actual order quantity |
| actualPx | String | Actual order price |
| tag | String | Order tag |
| actualSide | String | Actual trigger side, `tp` tp : take profit `sl` sl : stop loss Only applicable to oco order and conditional order |
| triggerTime | String | Trigger time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| pxVar | String | Price ratio Only applicable to `iceberg` iceberg order or `twap` twap order |
| pxSpread | String | Price variance Only applicable to `iceberg` iceberg order or `twap` twap order |
| szLimit | String | Average amount Only applicable to `iceberg` iceberg order or `twap` twap order |
| pxLimit | String | Price Limit Only applicable to `iceberg` iceberg order or `twap` twap order |
| timeInterval | String | Time interval Only applicable to `twap` twap order |
| callbackRatio | String | Callback price ratio Only applicable to `move\_order\_stop` move\_order\_stop order |
| callbackSpread | String | Callback price variance Only applicable to `move\_order\_stop` move\_order\_stop order |
| activePx | String | Active price Only applicable to `move\_order\_stop` move\_order\_stop order |
| moveTriggerPx | String | Trigger price Only applicable to `move\_order\_stop` move\_order\_stop order |
| reduceOnly | String | Whether the order can only reduce the position size. Valid options: true or false. |
| quickMgnType | String | Quick Margin type, Only applicable to Quick Margin Mode of isolated margin `manual` manual , `auto\_borrow` auto\_borrow , `auto\_repay` auto\_repay |
| last | String | Last filled price while placing |
| failCode | String | It represents that the reason that algo order fails to trigger. It is "" when the state is `effective` effective / `canceled` canceled . There will be value when the state is `order\_failed` order\_failed , e.g. 51008; Only applicable to Stop Order, Trailing Stop Order, Trigger order. |
| algoClOrdId | String | Client-supplied Algo ID |
| amendPxOnTriggerType | String | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |
| attachAlgoOrds | Array of objects | Attached SL/TP orders info Applicable to `Futures mode/Multi-currency margin/Portfolio margin` Futures mode/Multi-currency margin/Portfolio margin |
| > attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > tpTriggerPx | String | Take-profit trigger price If you fill in this parameter, you should fill in the take-profit order price as well. |
| > tpTriggerPxType | String | Take-profit trigger price type `last` last : last price `index` index : index price `mark` mark : mark price |
| > tpOrdPx | String | Take-profit order price If you fill in this parameter, you should fill in the take-profit trigger price as well. If the price is `-1` -1 , take-profit will be executed at the market price. |
| > slTriggerPx | String | Stop-loss trigger price If you fill in this parameter, you should fill in the stop-loss order price. |
| > slTriggerPxType | String | Stop-loss trigger price type `last` last : last price `index` index : index price `mark` mark : mark price |
| > slOrdPx | String | Stop-loss order price If you fill in this parameter, you should fill in the stop-loss trigger price. If the price is `-1` -1 , stop-loss will be executed at the market price. |
| linkedOrd | Object | Linked TP order detail, only applicable to SL order that comes from the one-cancels-the-other (OCO) order that contains the TP limit order. |
| > ordId | String | Order ID |
| cTime | String | Creation time Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| uTime | String | Order updated time, Unix timestamp format in milliseconds, e.g. 1597026383085 |
| isTradeBorrowMode | String | Whether borrowing currency automatically true false Only applicable to `trigger order` trigger order , `trailing order` trailing order and `twap order` twap order |
| chaseType | String | Chase type. Only applicable to `chase` chase order. |
| chaseVal | String | Chase value. Only applicable to `chase` chase order. |
| maxChaseType | String | Maximum chase type. Only applicable to `chase` chase order. |
| maxChaseVal | String | Maximum chase value. Only applicable to `chase` chase order. |
| tradeQuoteCcy | String | The quote currency used for trading. |

### GET / Algo order list

Retrieve a list of untriggered Algo orders under the current account.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/trade/orders-algo-pending`

> Request Example

```highlight
GET /api/v5/trade/orders-algo-pending?ordType=conditional

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve a list of untriggered one-way stop orders
result = tradeAPI.order_algos_list(
    ordType="conditional"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ordType | String | Yes | Order type `conditional` conditional : One-way stop order `oco` oco : One-cancels-the-other order `trigger` trigger : Trigger order `move\_order\_stop` move\_order\_stop : Trailing order |
| algoId | String | No | Algo ID |
| instType | String | No | Instrument type `SPOT` SPOT |
| instId | String | No | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| after | String | No | Pagination of data to return records earlier than the requested `algoId` algoId . |
| before | String | No | Pagination of data to return records newer than the requested `algoId` algoId . |
| limit | String | No | Number of results per request. The maximum is `100` 100 . The default is `100` 100 |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "activePx": "",
            "actualPx": "",
            "actualSide": "buy",
            "actualSz": "0",
            "algoClOrdId": "",
            "algoId": "681096944655273984",
            "amendPxOnTriggerType": "",
            "attachAlgoOrds": [],
            "cTime": "1708658165774",
            "callbackRatio": "",
            "callbackSpread": "",
            "ccy": "",
            "clOrdId": "",
            "closeFraction": "",
            "failCode": "",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "last": "51014.6",
            "lever": "",
            "moveTriggerPx": "",
            "ordId": "",
            "ordIdList": [],
            "ordPx": "-1",
            "ordType": "trigger",
            "posSide": "net",
            "pxLimit": "",
            "pxSpread": "",
            "pxVar": "",
            "quickMgnType": "",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "state": "live",
            "sz": "10",
            "szLimit": "",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "",
            "timeInterval": "",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "",
            "triggerPx": "100",
            "triggerPxType": "last",
            "triggerTime": "0"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID |
| ccy | String | Margin currency Applicable to all `isolated` isolated `MARGIN` MARGIN orders and `cross` cross `MARGIN` MARGIN orders in `Futures mode` Futures mode . |
| ordId | String | Latest order ID |
| ordIdList | Array of strings | Order ID list. There will be multiple order IDs when there is TP/SL splitting order. |
| algoId | String | Algo ID |
| clOrdId | String | Client Order ID as assigned by the client |
| sz | String | Quantity to buy or sell |
| closeFraction | String | Fraction of position to be closed when the algo order is triggered |
| ordType | String | Order type |
| side | String | Order side |
| posSide | String | Position side |
| tdMode | String | Trade mode |
| tgtCcy | String | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT traded with Market order |
| state | String | State, `live` live `pause` pause |
| lever | String | Leverage, from `0.01` 0.01 to `125` 125 . Only applicable to `MARGIN/FUTURES/SWAP` MARGIN/FUTURES/SWAP |
| tpTriggerPx | String | Take-profit trigger price |
| tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| tpOrdPx | String | Take-profit order price |
| slTriggerPx | String | Stop-loss trigger price |
| slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| slOrdPx | String | Stop-loss order price |
| triggerPx | String | Trigger price |
| triggerPxType | String | Trigger price type `last` last : last price `index` index : index price `mark` mark : mark price |
| ordPx | String | Order price for the trigger order |
| actualSz | String | Actual order quantity |
| tag | String | Order tag |
| actualPx | String | Actual order price |
| actualSide | String | Actual trigger side `tp` tp : take profit `sl` sl : stop loss Only applicable to oco order and conditional order |
| triggerTime | String | Trigger time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| pxVar | String | Price ratio Only applicable to `iceberg` iceberg order or `twap` twap order |
| pxSpread | String | Price variance Only applicable to `iceberg` iceberg order or `twap` twap order |
| szLimit | String | Average amount Only applicable to `iceberg` iceberg order or `twap` twap order |
| pxLimit | String | Price Limit Only applicable to `iceberg` iceberg order or `twap` twap order |
| timeInterval | String | Time interval Only applicable to `twap` twap order |
| callbackRatio | String | Callback price ratio Only applicable to `move\_order\_stop` move\_order\_stop order |
| callbackSpread | String | Callback price variance Only applicable to `move\_order\_stop` move\_order\_stop order |
| activePx | String | Active price Only applicable to `move\_order\_stop` move\_order\_stop order |
| moveTriggerPx | String | Trigger price Only applicable to `move\_order\_stop` move\_order\_stop order |
| reduceOnly | String | Whether the order can only reduce the position size. Valid options: true or false. |
| quickMgnType | String | Quick Margin type, Only applicable to Quick Margin Mode of isolated margin `manual` manual , `auto\_borrow` auto\_borrow , `auto\_repay` auto\_repay |
| last | String | Last filled price while placing |
| failCode | String | It represents that the reason that algo order fails to trigger. There will be value when the state is `order\_failed` order\_failed , e.g. 51008; For this endpoint, it always is "". |
| algoClOrdId | String | Client-supplied Algo ID |
| amendPxOnTriggerType | String | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |
| attachAlgoOrds | Array of objects | Attached SL/TP orders info Applicable to `Futures mode/Multi-currency margin/Portfolio margin` Futures mode/Multi-currency margin/Portfolio margin |
| > attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > tpTriggerPx | String | Take-profit trigger price If you fill in this parameter, you should fill in the take-profit order price as well. |
| > tpTriggerPxType | String | Take-profit trigger price type `last` last : last price `index` index : index price `mark` mark : mark price The default is `last` last |
| > tpOrdPx | String | Take-profit order price If you fill in this parameter, you should fill in the take-profit trigger price as well. If the price is `-1` -1 , take-profit will be executed at the market price. |
| > slTriggerPx | String | Stop-loss trigger price If you fill in this parameter, you should fill in the stop-loss order price. |
| > slTriggerPxType | String | Stop-loss trigger price type `last` last : last price `index` index : index price `mark` mark : mark price The default is `last` last |
| > slOrdPx | String | Stop-loss order price If you fill in this parameter, you should fill in the stop-loss trigger price. If the price is `-1` -1 , stop-loss will be executed at the market price. |
| cTime | String | Creation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### GET / Algo order history

Retrieve a list of all algo orders under the current account in the last 3 months.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/trade/orders-algo-history`

> Request Example

```highlight
GET /api/v5/trade/orders-algo-history?ordType=conditional&state=effective

```

```highlight
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve a list of all one-way stop algo orders
result = tradeAPI.order_algos_history(
    state="effective",
    ordType="conditional"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ordType | String | Yes | Order type `conditional` conditional : One-way stop order `oco` oco : One-cancels-the-other order `trigger` trigger : Trigger order `move\_order\_stop` move\_order\_stop : Trailing order |
| state | String | Conditional | State `effective` effective `canceled` canceled `order\_failed` order\_failed Either `state` state or `algoId` algoId is required |
| algoId | String | Conditional | Algo ID Either `state` state or `algoId` algoId is required. |
| instType | String | No | Instrument type `SPOT` SPOT |
| instId | String | No | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| after | String | No | Pagination of data to return records earlier than the requested `algoId` algoId |
| before | String | No | Pagination of data to return records new than the requested `algoId` algoId |
| limit | String | No | Number of results per request. The maximum is `100` 100 . The default is `100` 100 |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "activePx": "",
            "actualPx": "",
            "actualSide": "buy",
            "actualSz": "0",
            "algoClOrdId": "",
            "algoId": "681096944655273984",
            "amendPxOnTriggerType": "",
            "attachAlgoOrds": [],
            "cTime": "1708658165774",
            "callbackRatio": "",
            "callbackSpread": "",
            "ccy": "",
            "clOrdId": "",
            "closeFraction": "",
            "failCode": "",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "last": "51014.6",
            "lever": "",
            "moveTriggerPx": "",
            "ordId": "",
            "ordIdList": [],
            "ordPx": "-1",
            "ordType": "trigger",
            "posSide": "net",
            "pxLimit": "",
            "pxSpread": "",
            "pxVar": "",
            "quickMgnType": "",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "state": "canceled",
            "sz": "10",
            "szLimit": "",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "",
            "timeInterval": "",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "",
            "triggerPx": "100",
            "triggerPxType": "last",
            "triggerTime": ""
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID |
| ccy | String | Margin currency Applicable to all `isolated` isolated `MARGIN` MARGIN orders and `cross` cross `MARGIN` MARGIN orders in `Futures mode` Futures mode . |
| ordId | String | Latest order ID |
| ordIdList | Array of strings | Order ID list. There will be multiple order IDs when there is TP/SL splitting order. |
| algoId | String | Algo ID |
| clOrdId | String | Client Order ID as assigned by the client |
| sz | String | Quantity to buy or sell |
| closeFraction | String | Fraction of position to be closed when the algo order is triggered |
| ordType | String | Order type |
| side | String | Order side |
| posSide | String | Position side |
| tdMode | String | Trade mode |
| tgtCcy | String | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| state | String | State `effective` effective `canceled` canceled `order\_failed` order\_failed `partially\_failed` partially\_failed |
| lever | String | Leverage, from `0.01` 0.01 to `125` 125 . Only applicable to `MARGIN/FUTURES/SWAP` MARGIN/FUTURES/SWAP |
| tpTriggerPx | String | Take-profit trigger price. |
| tpTriggerPxType | String | Take-profit trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| tpOrdPx | String | Take-profit order price. |
| slTriggerPx | String | Stop-loss trigger price. |
| slTriggerPxType | String | Stop-loss trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| slOrdPx | String | Stop-loss order price. |
| triggerPx | String | trigger price. |
| triggerPxType | String | trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| ordPx | String | Order price for the trigger order |
| actualSz | String | Actual order quantity |
| actualPx | String | Actual order price |
| tag | String | Order tag |
| actualSide | String | Actual trigger side, `tp` tp : take profit `sl` sl : stop loss Only applicable to oco order and conditional order |
| triggerTime | String | Trigger time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| pxVar | String | Price ratio Only applicable to `iceberg` iceberg order or `twap` twap order |
| pxSpread | String | Price variance Only applicable to `iceberg` iceberg order or `twap` twap order |
| szLimit | String | Average amount Only applicable to `iceberg` iceberg order or `twap` twap order |
| pxLimit | String | Price Limit Only applicable to `iceberg` iceberg order or `twap` twap order |
| timeInterval | String | Time interval Only applicable to `twap` twap order |
| callbackRatio | String | Callback price ratio Only applicable to `move\_order\_stop` move\_order\_stop order |
| callbackSpread | String | Callback price variance Only applicable to `move\_order\_stop` move\_order\_stop order |
| activePx | String | Active price Only applicable to `move\_order\_stop` move\_order\_stop order |
| moveTriggerPx | String | Trigger price Only applicable to `move\_order\_stop` move\_order\_stop order |
| reduceOnly | String | Whether the order can only reduce the position size. Valid options: true or false. |
| quickMgnType | String | Quick Margin type, Only applicable to Quick Margin Mode of isolated margin `manual` manual , `auto\_borrow` auto\_borrow , `auto\_repay` auto\_repay |
| last | String | Last filled price while placing |
| failCode | String | It represents that the reason that algo order fails to trigger. It is "" when the state is `effective` effective / `canceled` canceled . There will be value when the state is `order\_failed` order\_failed , e.g. 51008; Only applicable to Stop Order, Trailing Stop Order, Trigger order. |
| algoClOrdId | String | Client Algo Order ID as assigned by the client. |
| amendPxOnTriggerType | String | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |
| attachAlgoOrds | Array of objects | Attached SL/TP orders info Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to algoClOrdId when placing TP/SL order once the general order is filled completely. |
| > tpTriggerPx | String | Take-profit trigger price If you fill in this parameter, you should fill in the take-profit order price as well. |
| > tpTriggerPxType | String | Take-profit trigger price type `last` last : last price `index` index : index price `mark` mark : mark price The default is `last` last |
| > tpOrdPx | String | Take-profit order price If you fill in this parameter, you should fill in the take-profit trigger price as well. If the price is `-1` -1 , take-profit will be executed at the market price. |
| > slTriggerPx | String | Stop-loss trigger price If you fill in this parameter, you should fill in the stop-loss order price. |
| > slTriggerPxType | String | Stop-loss trigger price type `last` last : last price `index` index : index price `mark` mark : mark price The default is `last` last |
| > slOrdPx | String | Stop-loss order price If you fill in this parameter, you should fill in the stop-loss trigger price. If the price is `-1` -1 , stop-loss will be executed at the market price. |
| cTime | String | Creation time Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### WS / Algo orders channel

Retrieve algo orders (includes `trigger` order, `oco` order, `conditional` order). Data will not be pushed when first subscribed. Data will only be pushed when there are order updates.

#### URL Path

/ws/v5/business (required login)

> Request Example : single

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "orders-algo",
      "instType": "ANY"
    }
  ]
}

```

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "orders-algo",
      "instType": "ANY"
    }
  ]
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `orders-algo` orders-algo |
| > instType | String | Yes | Instrument type `ANY` ANY |
| > instId | String | No | Instrument ID |

> Successful Response Example : single

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "orders-algo",
    "instType": "ANY"
  },
  "connId": "a4d3ae55"
}

```

> Successful Response Example

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "orders-algo",
    "instType": "ANY"
  },
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"orders-algo\", \"instType\" : \"FUTURES\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Event `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name |
| > instType | String | Yes | Instrument type `ANY` ANY |
| > instId | String | No | Instrument ID |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example: single

```highlight
{
    "arg": {
        "channel": "orders-algo",
        "uid": "77982378738415879",
        "instType": "ANY"
    },
    "data": [{
        "actualPx": "0",
        "actualSide": "",
        "actualSz": "0",
        "algoClOrdId": "",
        "algoId": "581878926302093312",
        "attachAlgoOrds": [],
        "amendResult": "",
        "cTime": "1685002746818",
        "ccy": "",
        "clOrdId": "",
        "closeFraction": "",
        "failCode": "",
        "instId": "BTC-USDC",
        "instType": "SPOT",
        "last": "26174.8",
        "lever": "0",
        "notionalUsd": "11.0",
        "ordId": "",
        "ordIdList": [],
        "ordPx": "",
        "ordType": "conditional",
        "posSide": "",
        "quickMgnType": "",
        "reduceOnly": "false",
        "reqId": "",
        "side": "buy",
        "slOrdPx": "",
        "slTriggerPx": "",
        "slTriggerPxType": "",
        "state": "live",
        "sz": "11",
        "tag": "",
        "tdMode": "cross",
        "tgtCcy": "quote_ccy",
        "tpOrdPx": "-1",
        "tpTriggerPx": "1",
        "tpTriggerPxType": "last",
        "triggerPx": "",
        "triggerTime": "",
        "amendPxOnTriggerType": "0"
    }]
}

```

#### Response parameters when data is pushed.

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| > uid | String | User Identifier |
| > instType | String | Instrument type |
| > instFamily | String | Instrument family |
| > instId | String | Instrument ID |
| data | Array of objects | Subscribed data |
| > instType | String | Instrument type |
| > instId | String | Instrument ID |
| > ccy | String | Margin currency Applicable to all `isolated` isolated `MARGIN` MARGIN orders and `cross` cross `MARGIN` MARGIN orders in `Futures mode` Futures mode . |
| > ordId | String | Latest order ID, the order ID associated with the algo order. |
| > ordIdList | Array of strings | Order ID list. There will be multiple order IDs when there is TP/SL splitting order. |
| > algoId | String | Algo ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > sz | String | Quantity to buy or sell. `SPOT` SPOT / `MARGIN` MARGIN : in the unit of currency. `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION : in the unit of contract. |
| > ordType | String | Order type `conditional` conditional : One-way stop order `oco` oco : One-cancels-the-other order `trigger` trigger : Trigger order |
| > side | String | Order side `buy` buy `sell` sell |
| > posSide | String | Position side `net` net `long` long or `short` short Only applicable to `FUTURES` FUTURES / `SWAP` SWAP |
| > tdMode | String | Trade mode `cross` cross : cross `isolated` isolated : isolated `cash` cash : cash |
| > tgtCcy | String | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| > lever | String | Leverage, from `0.01` 0.01 to `125` 125 . Only applicable to `MARGIN/FUTURES/SWAP` MARGIN/FUTURES/SWAP |
| > state | String | Order status `live` live : to be effective `effective` effective : effective `canceled` canceled : canceled `order\_failed` order\_failed : order failed `partially\_failed` partially\_failed : partially failed `partially\_effective` partially\_effective : partially effective |
| > tpTriggerPx | String | Take-profit trigger price. |
| > tpTriggerPxType | String | Take-profit trigger price type `last` last : last price `index` index : index price `mark` mark : mark price |
| > tpOrdPx | String | Take-profit order price. |
| > slTriggerPx | String | Stop-loss trigger price. |
| > slTriggerPxType | String | Stop-loss trigger price type `last` last : last price `index` index : index price `mark` mark : mark price |
| > slOrdPx | String | Stop-loss order price. |
| > triggerPx | String | Trigger price |
| > triggerPxType | String | Trigger price type. `last` last : last price `index` index : index price `mark` mark : mark price |
| > ordPx | String | Order price for the trigger order |
| > last | String | Last filled price while placing |
| > actualSz | String | Actual order quantity |
| > actualPx | String | Actual order price |
| > notionalUsd | String | Estimated national value in `USD` USD of order |
| > tag | String | Order tag |
| > actualSide | String | Actual trigger side Only applicable to oco order and conditional order |
| > triggerTime | String | Trigger time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > reduceOnly | String | Whether the order can only reduce the position size. Valid options: `true` true or `false` false . |
| > failCode | String | It represents that the reason that algo order fails to trigger. It is "" when the state is `effective` effective / `canceled` canceled . There will be value when the state is `order\_failed` order\_failed , e.g. 51008; Only applicable to Stop Order, Trailing Stop Order, Trigger order. |
| > algoClOrdId | String | Client Algo Order ID as assigned by the client. |
| > cTime | String | Creation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > reqId | String | Client Request ID as assigned by the client for order amendment. "" will be returned if there is no order amendment. |
| > amendResult | String | The result of amending the order `-1` -1 : failure `0` 0 : success |
| > amendPxOnTriggerType | String | Whether to enable Cost-price SL. Only applicable to SL order of split TPs. `0` 0 : disable, the default value `1` 1 : Enable |
| > attachAlgoOrds | Array of objects | Attached SL/TP orders info Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| >> attachAlgoClOrdId | String | Client-supplied Algo ID when placing order attaching TP/SL. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. It will be posted to algoClOrdId when placing TP/SL order once the general order is filled completely. |
| >> tpTriggerPx | String | Take-profit trigger price If you fill in this parameter, you should fill in the take-profit order price as well. |
| >> tpTriggerPxType | String | Take-profit trigger price type `last` last : last price `index` index : index price `mark` mark : mark price The default is `last` last |
| >> tpOrdPx | String | Take-profit order price If you fill in this parameter, you should fill in the take-profit trigger price as well. If the price is `-1` -1 , take-profit will be executed at the market price. |
| >> slTriggerPx | String | Stop-loss trigger price If you fill in this parameter, you should fill in the stop-loss order price. |
| >> slTriggerPxType | String | Stop-loss trigger price type `last` last : last price `index` index : index price `mark` mark : mark price The default is `last` last |
| >> slOrdPx | String | Stop-loss order price If you fill in this parameter, you should fill in the stop-loss trigger price. If the price is `-1` -1 , stop-loss will be executed at the market price. |

### WS / Advance algo orders channel

Retrieve advance algo orders (including Iceberg order, TWAP order, Trailing order). Data will be pushed when first subscribed. Data will be pushed when triggered by events such as placing/canceling order.

#### URL Path

/ws/v5/business (required login)

> Request Example : single

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "algo-advance",
      "instType": "SPOT",
      "instId": "BTC-USDT"
    }
  ]
}

```

```highlight
import asyncio

from okx.websocket.WsPrivateAsync import WsPrivateAsync

def callbackFunc(message):
    print(message)

async def main():

    ws = WsPrivateAsync(
        apiKey = "YOUR_API_KEY",
        passphrase = "YOUR_PASSPHRASE",
        secretKey = "YOUR_SECRET_KEY",
        url = "wss://ws.okx.com:8443/ws/v5/business",
        useServerTime=False
    )
    await ws.start()
    args = [
        {
          "channel": "algo-advance",
          "instType": "SPOT",
          "instId": "BTC-USDT"
        }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "algo-advance",
      "instType": "SPOT"
    }
  ]
}

```

```highlight
import asyncio

from okx.websocket.WsPrivateAsync import WsPrivateAsync

def callbackFunc(message):
    print(message)

async def main():

    ws = WsPrivateAsync(
        apiKey = "YOUR_API_KEY",
        passphrase = "YOUR_PASSPHRASE",
        secretKey = "YOUR_SECRET_KEY",
        url = "wss://ws.okx.com:8443/ws/v5/business",
        useServerTime=False
    )
    await ws.start()
    args = [
        {
          "channel": "algo-advance",
          "instType": "SPOT"
        }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `algo-advance` algo-advance |
| > instType | String | Yes | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `ANY` ANY |
| > instId | String | No | Instrument ID |
| > algoId | String | No | Algo Order ID |

> Successful Response Example : single

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "algo-advance",
    "instType": "SPOT",
    "instId": "BTC-USDT"
  },
  "connId": "a4d3ae55"
}

```

> Successful Response Example

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "algo-advance",
    "instType": "SPOT"
  },
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"algo-advance\", \"instType\" : \"FUTURES\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Event `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name |
| > instType | String | Yes | Instrument type `SPOT` SPOT `MARGIN` MARGIN `SWAP` SWAP `FUTURES` FUTURES `ANY` ANY |
| > instId | String | No | Instrument ID |
| > algoId | String | No | Algo Order ID |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example: single

```highlight
{
    "arg":{
        "channel":"algo-advance",
        "uid": "77982378738415879",
        "instType":"SPOT",
        "instId":"BTC-USDT"
    },
    "data":[
        {
            "actualPx":"",
            "actualSide":"",
            "actualSz":"0",
            "algoId":"355056228680335360",
            "cTime":"1630924001545",
            "ccy":"",
            "clOrdId": "",
            "count":"1",
            "instId":"BTC-USDT",
            "instType":"SPOT",
            "lever":"0",
            "notionalUsd":"",
            "ordPx":"",
            "ordType":"iceberg",
            "pTime":"1630924295204",
            "posSide":"net",
            "pxLimit":"10",
            "pxSpread":"1",
            "pxVar":"",
            "side":"buy",
            "slOrdPx":"",
            "slTriggerPx":"",
            "state":"pause",
            "sz":"0.1",
            "szLimit":"0.1",
            "tdMode":"cash",
            "timeInterval":"",
            "tpOrdPx":"",
            "tpTriggerPx":"",
            "tag": "adadadadad",
            "triggerPx":"",
            "triggerTime":"",
            "tradeQuoteCcy": "USDT",
            "callbackRatio":"",
            "callbackSpread":"",
            "activePx":"",
            "moveTriggerPx":"",
            "failCode": "",
                "algoClOrdId": "",
            "reduceOnly": "",
            "isTradeBorrowMode": true
        }
    ]
}

```

#### Response parameters when data is pushed.

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| > uid | String | User Identifier |
| > instType | String | Instrument type |
| > instId | String | Instrument ID |
| > algoId | String | Algo Order ID |
| data | Array of objects | Subscribed data |
| > instType | String | Instrument type |
| > instId | String | Instrument ID |
| > ccy | String | Margin currency Applicable to all `isolated` isolated `MARGIN` MARGIN orders and `cross` cross `MARGIN` MARGIN orders in `Futures mode` Futures mode . |
| > ordId | String | Order ID, the order ID associated with the algo order. |
| > algoId | String | Algo ID |
| > clOrdId | String | Client Order ID as assigned by the client |
| > sz | String | Quantity to buy or sell. `SPOT` SPOT / `MARGIN` MARGIN : in the unit of currency. `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION : in the unit of contract. |
| > ordType | String | Order type `iceberg` iceberg : Iceberg order `twap` twap : TWAP order `move\_order\_stop` move\_order\_stop : Trailing order |
| > side | String | Order side, `buy` buy `sell` sell |
| > posSide | String | Position side `net` net `long` long or `short` short Only applicable to `FUTURES` FUTURES / `SWAP` SWAP |
| > tdMode | String | Trade mode, `cross` cross : cross `isolated` isolated : isolated `cash` cash : cash |
| > tgtCcy | String | Order quantity unit setting for `sz` sz `base\_ccy` base\_ccy : Base currency , `quote\_ccy` quote\_ccy : Quote currency Only applicable to `SPOT` SPOT Market Orders Default is `quote\_ccy` quote\_ccy for buy, `base\_ccy` base\_ccy for sell |
| > lever | String | Leverage, from `0.01` 0.01 to `125` 125 . Only applicable to `MARGIN/FUTURES/SWAP` MARGIN/FUTURES/SWAP |
| > state | String | Order status `live` live : to be effective `effective` effective : effective `partially\_effective` partially\_effective : partially effective `canceled` canceled : canceled `order\_failed` order\_failed : order failed `pause` pause : pause |
| > tpTriggerPx | String | Take-profit trigger price. |
| > tpOrdPx | String | Take-profit order price. |
| > slTriggerPx | String | Stop-loss trigger price. |
| > slOrdPx | String | Stop-loss order price. |
| > triggerPx | String | Trigger price |
| > ordPx | String | Order price |
| > actualSz | String | Actual order quantity |
| > actualPx | String | Actual order price |
| > notionalUsd | String | Estimated national value in `USD` USD of order |
| > tag | String | Order tag |
| > actualSide | String | Actual trigger side |
| > triggerTime | String | Trigger time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > cTime | String | Creation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > pxVar | String | Price ratio Only applicable to `iceberg` iceberg order or `twap` twap order |
| > pxSpread | String | Price variance Only applicable to `iceberg` iceberg order or `twap` twap order |
| > szLimit | String | Average amount Only applicable to `iceberg` iceberg order or `twap` twap order |
| > pxLimit | String | Price limit Only applicable to `iceberg` iceberg order or `twap` twap order |
| > timeInterval | String | Time interval Only applicable to `twap` twap order |
| > count | String | Algo Order count Only applicable to `iceberg` iceberg order or `twap` twap order |
| > callbackRatio | String | Callback price ratio Only applicable to `move\_order\_stop` move\_order\_stop order |
| > callbackSpread | String | Callback price variance Only applicable to `move\_order\_stop` move\_order\_stop order |
| > activePx | String | Active price Only applicable to `move\_order\_stop` move\_order\_stop order |
| > moveTriggerPx | String | Trigger price Only applicable to `move\_order\_stop` move\_order\_stop order |
| > failCode | String | It represents that the reason that algo order fails to trigger. It is "" when the state is `effective` effective / `canceled` canceled . There will be value when the state is `order\_failed` order\_failed , e.g. 51008; Only applicable to Stop Order, Trailing Stop Order, Trigger order. |
| > algoClOrdId | String | Client Algo Order ID as assigned by the client. |
| > reduceOnly | String | Whether the order can only reduce the position size. Valid options: `true` true or `false` false . |
| > pTime | String | Push time of algo order information, millisecond format of Unix timestamp, e.g. `1597026383085` 1597026383085 |
| > isTradeBorrowMode | Boolean | Whether borrowing currency automatically true false Only applicable to `trigger order` trigger order , `trailing order` trailing order and `twap order` twap order |
| > tradeQuoteCcy | String | The quote currency used for trading. |

## Market Data

The API endpoints of `Market Data` do not require authentication.  
There are multiple services for market data, and each service has an independent cache. A random service will be requested for every request. So for two requests, it’s expected that the data obtained in the second request is earlier than the first request.

### GET / Tickers

Retrieve the latest price snapshot, best bid/ask price, and trading volume in the last 24 hours. Best ask price may be lower than the best bid price during the pre-open period.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: IP

#### HTTP Request

`GET /api/v5/market/tickers`

> Request Example

```highlight
GET /api/v5/market/tickers?instType=SPOT

```

```highlight
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve the latest price snapshot, best bid/ask price, and trading volume in the last 24 hours
result = marketDataAPI.get_tickers(
    instType="SPOT"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | Yes | Instrument type `SPOT` SPOT |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "instType": "SPOT",
            "instId": "BTC-USDT",
            "last": "51230",
            "lastSz": "0.18531491",
            "askPx": "51229.4",
            "askSz": "2.1683067",
            "bidPx": "51229.3",
            "bidSz": "0.28249897",
            "open24h": "51635.7",
            "high24h": "52080",
            "low24h": "50936",
            "volCcy24h": "539658490.410419122",
            "vol24h": "10476.2229261",
            "ts": "1708669508505",
            "sodUtc0": "51290.1",
            "sodUtc8": "51602.4"
        }
    ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID |
| last | String | Last traded price |
| lastSz | String | Last traded size |
| askPx | String | Best ask price |
| askSz | String | Best ask size |
| bidPx | String | Best bid price |
| bidSz | String | Best bid size |
| open24h | String | Open price in the past 24 hours |
| high24h | String | Highest price in the past 24 hours |
| low24h | String | Lowest price in the past 24 hours |
| volCcy24h | String | 24h trading volume If it is `SPOT` SPOT , the value is the quantity in quote currency. |
| vol24h | String | 24h trading volume If it is `SPOT` SPOT , the value is the quantity in base currency. |
| sodUtc0 | String | Open price in the UTC 0 |
| sodUtc8 | String | Open price in the UTC 8 |
| ts | String | Ticker data generation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### GET / Ticker

Retrieve the latest price snapshot, best bid/ask price, and trading volume in the last 24 hours. Best ask price may be lower than the best bid price during the pre-open period.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: IP

#### HTTP Request

`GET /api/v5/market/ticker`

> Request Example

```highlight
GET /api/v5/market/ticker?instId=BTC-USDT

```

```highlight
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve the latest price snapshot, best bid/ask price, and trading volume in the last 24 hours
result = marketDataAPI.get_ticker(
    instId="BTC-USDT"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "instType": "SPOT",
            "instId": "BTC-USDT",
            "last": "51240",
            "lastSz": "0.49011124",
            "askPx": "51240",
            "askSz": "0.64278176",
            "bidPx": "51239.9",
            "bidSz": "1.68139044",
            "open24h": "51695.6",
            "high24h": "52080",
            "low24h": "50936",
            "volCcy24h": "539533972.680195094",
            "vol24h": "10474.12353007",
            "ts": "1708669925904",
            "sodUtc0": "51290.1",
            "sodUtc8": "51602.4"
        }
    ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID |
| last | String | Last traded price |
| lastSz | String | Last traded size |
| askPx | String | Best ask price |
| askSz | String | Best ask size |
| bidPx | String | Best bid price |
| bidSz | String | Best bid size |
| open24h | String | Open price in the past 24 hours |
| high24h | String | Highest price in the past 24 hours |
| low24h | String | Lowest price in the past 24 hours |
| volCcy24h | String | 24h trading volume If it is `SPOT` SPOT , the value is the quantity in quote currency. |
| vol24h | String | 24h trading volume If it is `SPOT` SPOT , the value is the quantity in base currency. |
| sodUtc0 | String | Open price in the UTC 0 |
| sodUtc8 | String | Open price in the UTC 8 |
| ts | String | Ticker data generation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 . |

### GET / Order book

Retrieve order book of the instrument. The data will be updated once every 50 milliseconds. Best ask price may be lower than the best bid price during the pre-open period.  
This endpoint does not return data immediately. Instead, it returns the latest data once the server-side cache has been updated.

#### Rate Limit: 40 requests per 2 seconds

#### Rate limit rule: IP

#### HTTP Request

`GET /api/v5/market/books`

> Request Example

```highlight
GET /api/v5/market/books?instId=BTC-USDT

```

```highlight
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve order book of the instrument
result = marketDataAPI.get_orderbook(
    instId="BTC-USDT"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| sz | String | No | Order book depth per side. Maximum 400, e.g. 400 bids + 400 asks Default returns to `1` 1 depth data |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "asks": [
                [
                    "41006.8",
                    "0.60038921",
                    "0",
                    "1"
                ]
            ],
            "bids": [
                [
                    "41006.3",
                    "0.30178218",
                    "0",
                    "2"
                ]
            ],
            "ts": "1629966436396"
        }
    ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| asks | Array of Arrays | Order book on sell side |
| bids | Array of Arrays | Order book on buy side |
| ts | String | Order book generation time |

An example of the array of asks and bids values: ["411.8", "10", "0", "4"]  
- "411.8" is the depth price  
- "10" is the quantity at the price (number of contracts for derivatives, quantity in base currency for Spot and Spot Margin)  
- "0" is part of a deprecated feature and it is always "0"  
- "4" is the number of orders at the price.  

The order book data will be updated around once a second during the call auction.

### GET / Full order book

Retrieve order book of the instrument. The data will be updated once a second. Best ask price may be lower than the best bid price during the pre-open period.  
This endpoint does not return data immediately. Instead, it returns the latest data once the server-side cache has been updated.

#### Rate Limit: 10 requests per 2 seconds

#### Rate limit rule: IP

#### HTTP Request

`GET /api/v5/market/books-full`

> Request Example

```highlight
GET /api/v5/market/books-full?instId=BTC-USDT&sz=1

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| sz | String | No | Order book depth per side. Maximum 5000, e.g. 5000 bids + 5000 asks Default returns to `1` 1 depth data. |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "asks": [
                [
                    "41006.8",
                    "0.60038921",
                    "1"
                ]
            ],
            "bids": [
                [
                    "41006.3",
                    "0.30178218",
                    "2"
                ]
            ],
            "ts": "1629966436396"
        }
    ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| asks | Array of Arrays | Order book on sell side |
| bids | Array of Arrays | Order book on buy side |
| ts | String | Order book generation time |

An example of the array of asks and bids values: ["411.8", "10", "4"]  
- "411.8" is the depth price  
- "10" is the quantity at the price (number of contracts for derivatives, quantity in base currency for Spot and Spot Margin)  
- "4" is the number of orders at the price.  

The order book data will be updated around once a second during the call auction.

### GET / Candlesticks

Retrieve the candlestick charts. This endpoint can retrieve the latest 1,440 data entries. Charts are returned in groups based on the requested bar.

#### Rate Limit: 40 requests per 2 seconds

#### Rate limit rule: IP

#### HTTP Request

`GET /api/v5/market/candles`

> Request Example

```highlight
GET /api/v5/market/candles?instId=BTC-USDT

```

```highlight
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve the candlestick charts
result = marketDataAPI.get_candlesticks(
    instId="BTC-USDT"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| bar | String | No | Bar size, the default is `1m` 1m e.g. [1m/3m/5m/15m/30m/1H/2H/4H] Hong Kong time opening price k-line: [6H/12H/1D/2D/3D/1W/1M/3M] UTC time opening price k-line: [/6Hutc/12Hutc/1Dutc/2Dutc/3Dutc/1Wutc/1Mutc/3Mutc] |
| after | String | No | Pagination of data to return records earlier than the requested `ts` ts |
| before | String | No | Pagination of data to return records newer than the requested `ts` ts . The latest data will be returned when using `before` before individually |
| limit | String | No | Number of results per request. The maximum is `300` 300 . The default is `100` 100 . |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
     [
        "1597026383085",
        "3.721",
        "3.743",
        "3.677",
        "3.708",
        "8422410",
        "22698348.04828491",
        "12698348.04828491",
        "0"
    ],
    [
        "1597026383085",
        "3.731",
        "3.799",
        "3.494",
        "3.72",
        "24912403",
        "67632347.24399722",
        "37632347.24399722",
        "1"
    ]
    ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| ts | String | Opening time of the candlestick, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| o | String | Open price |
| h | String | highest price |
| l | String | Lowest price |
| c | String | Close price |
| vol | String | Trading volume If it is `SPOT` SPOT , the value is the quantity in base currency. |
| volCcy | String | Trading volume If it is `SPOT` SPOT , the value is the quantity in quote currency. |
| volCcyQuote | String | Trading volume, the value is the quantity in quote currency e.g. The unit is `USDT` USDT for `BTC-USDT` BTC-USDT |
| confirm | String | The state of candlesticks. `0` 0 : K line is uncompleted `1` 1 : K line is completed |

The first candlestick data may be incomplete, and should not be polled repeatedly.

The data returned will be arranged in an array like this: [ts,o,h,l,c,vol,volCcy,volCcyQuote,confirm].

For the current cycle of k-line data, when there is no transaction, the opening high and closing low default take the closing price of the previous cycle.

### GET / Candlesticks history

Retrieve history candlestick charts from recent years(It is last 3 months supported for 1s candlestick).

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: IP

#### HTTP Request

`GET /api/v5/market/history-candles`

> Request Example

```highlight
GET /api/v5/market/history-candles?instId=BTC-USDT

```

```highlight
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve history candlestick charts from recent years
result = marketDataAPI.get_history_candlesticks(
    instId="BTC-USDT"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| after | String | No | Pagination of data to return records earlier than the requested `ts` ts |
| before | String | No | Pagination of data to return records newer than the requested `ts` ts . The latest data will be returned when using `before` before individually |
| bar | String | No | Bar size, the default is `1m` 1m e.g. [1s/1m/3m/5m/15m/30m/1H/2H/4H] Hong Kong time opening price k-line: [6H/12H/1D/2D/3D/1W/1M/3M] UTC time opening price k-line: [6Hutc/12Hutc/1Dutc/2Dutc/3Dutc/1Wutc/1Mutc/3Mutc] |
| limit | String | No | Number of results per request. The maximum is `100` 100 . The default is `100` 100 . |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
     [
        "1597026383085",
        "3.721",
        "3.743",
        "3.677",
        "3.708",
        "8422410",
        "22698348.04828491",
        "12698348.04828491",
        "1"
    ],
    [
        "1597026383085",
        "3.731",
        "3.799",
        "3.494",
        "3.72",
        "24912403",
        "67632347.24399722",
        "37632347.24399722",
        "1"
    ]
    ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| ts | String | Opening time of the candlestick, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| o | String | Open price |
| h | String | Highest price |
| l | String | Lowest price |
| c | String | Close price |
| vol | String | Trading volume If it is `SPOT` SPOT , the value is the quantity in base currency. |
| volCcy | String | Trading volume If it is `SPOT` SPOT , the value is the quantity in quote currency. |
| volCcyQuote | String | Trading volume, the value is the quantity in quote currency e.g. The unit is `USDT` USDT for `BTC-USDT` BTC-USDT |
| confirm | String | The state of candlesticks. `0` 0 : K line is uncompleted `1` 1 : K line is completed |

The data returned will be arranged in an array like this: [ts,o,h,l,c,vol,volCcy,confirm]

1s candle is not supported by OPTION, but it is supported by other business lines (SPOT, MARGIN, FUTURES and SWAP)

### GET / Trades

Retrieve the recent transactions of an instrument.

#### Rate Limit: 100 requests per 2 seconds

#### Rate limit rule: IP

#### HTTP Request

`GET /api/v5/market/trades`

> Request Example

```highlight
GET /api/v5/market/trades?instId=BTC-USDT

```

```highlight
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve the recent transactions of an instrument
result = marketDataAPI.get_trades(
    instId="BTC-USDT"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| limit | String | No | Number of results per request. The maximum is `500` 500 ; The default is `100` 100 |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "instId": "BTC-USDT",
            "side": "sell",
            "sz": "0.00001",
            "px": "29963.2",
            "tradeId": "242720720",
            "ts": "1654161646974"
        },
        {
            "instId": "BTC-USDT",
            "side": "sell",
            "sz": "0.00001",
            "px": "29964.1",
            "tradeId": "242720719",
            "ts": "1654161641568"
        }
    ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instId | String | Instrument ID |
| tradeId | String | Trade ID |
| px | String | Trade price |
| sz | String | Trade quantity For spot trading, the unit is base currency For `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION , the unit is contract. |
| side | String | Trade side `buy` buy `sell` sell |
| ts | String | Trade time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 . |

Up to 500 most recent historical public transaction data can be retrieved.

### GET / Trades history

Retrieve the recent transactions of an instrument from the last 3 months with pagination.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: IP

#### HTTP Request

`GET /api/v5/market/history-trades`

> Request Example

```highlight
GET /api/v5/market/history-trades?instId=BTC-USDT

```

```highlight
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve the recent transactions of an instrument from the last 3 months with pagination
result = marketDataAPI.get_history_trades(
    instId="BTC-USD-SWAP"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instId | String | Yes | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| type | String | No | Pagination Type `1` 1 : tradeId `2` 2 : timestamp The default is `1` 1 |
| after | String | No | Pagination of data to return records earlier than the requested tradeId or ts. |
| before | String | No | Pagination of data to return records newer than the requested tradeId. Do not support timestamp for pagination. The latest data will be returned when using `before` before individually |
| limit | String | No | Number of results per request. The maximum and default both are `100` 100 |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "instId": "BTC-USDT",
            "side": "sell",
            "sz": "0.00001",
            "px": "29963.2",
            "tradeId": "242720720",
            "ts": "1654161646974"
        },
        {
            "instId": "BTC-USDT",
            "side": "sell",
            "sz": "0.00001",
            "px": "29964.1",
            "tradeId": "242720719",
            "ts": "1654161641568"
        }
    ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instId | String | Instrument ID |
| tradeId | String | Trade ID |
| px | String | Trade price |
| sz | String | Trade quantity For spot trading, the unit is base currency For `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION , the unit is contract. |
| side | String | Trade side `buy` buy `sell` sell |
| ts | String | Trade time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 . |

### WS / Tickers channel

Retrieve the last traded price, bid price, ask price and 24-hour trading volume of instruments. Best ask price may be lower than the best bid price during the pre-open period.   
The fastest rate is 1 update/100ms. There will be no update if the event is not triggered. The events which can trigger update: trade, the change on best ask/bid.

#### URL Path

/ws/v5/public

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "tickers",
      "instId": "BTC-USDT"
    }
  ]
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `tickers` tickers |
| > instId | String | Yes | Instrument ID |

> Successful Response Example

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "tickers",
    "instId": "BTC-USDT"
  },
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"tickers\", \"instId\" : \"LTC-USD-200327\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Event `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name |
| > instId | String | Yes | Instrument ID |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example

```highlight
{
  "arg": {
    "channel": "tickers",
    "instId": "BTC-USDT"
  },
  "data": [
    {
      "instType": "SPOT",
      "instId": "BTC-USDT",
      "last": "9999.99",
      "lastSz": "0.1",
      "askPx": "9999.99",
      "askSz": "11",
      "bidPx": "8888.88",
      "bidSz": "5",
      "open24h": "9000",
      "high24h": "10000",
      "low24h": "8888.88",
      "volCcy24h": "2222",
      "vol24h": "2222",
      "sodUtc0": "2222",
      "sodUtc8": "2222",
      "ts": "1597026383085"
    }
  ]
}

```

#### Push data parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| > instId | String | Instrument ID |
| data | Array of objects | Subscribed data |
| > instType | String | Instrument type |
| > instId | String | Instrument ID |
| > last | String | Last traded price |
| > lastSz | String | Last traded size |
| > askPx | String | Best ask price |
| > askSz | String | Best ask size |
| > bidPx | String | Best bid price |
| > bidSz | String | Best bid size |
| > open24h | String | Open price in the past 24 hours |
| > high24h | String | Highest price in the past 24 hours |
| > low24h | String | Lowest price in the past 24 hours |
| > volCcy24h | String | 24h trading volume If it is `SPOT` SPOT , the value is the quantity in quote currency. |
| > vol24h | String | 24h trading volume If it is `SPOT` SPOT , the value is the quantity in base currency. |
| > sodUtc0 | String | Open price in the UTC 0 |
| > sodUtc8 | String | Open price in the UTC 8 |
| > ts | String | Ticker data generation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### WS / Candlesticks channel

Retrieve the candlesticks data of an instrument. the push frequency is the fastest interval 1 second push the data.

#### URL Path

/ws/v5/business

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "candle1D",
      "instId": "BTC-USDT"
    }
  ]
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `candle3M` candle3M `candle1M` candle1M `candle1W` candle1W `candle1D` candle1D `candle2D` candle2D `candle3D` candle3D `candle5D` candle5D `candle12H` candle12H `candle6H` candle6H `candle4H` candle4H `candle2H` candle2H `candle1H` candle1H `candle30m` candle30m `candle15m` candle15m `candle5m` candle5m `candle3m` candle3m `candle1m` candle1m `candle1s` candle1s `candle3Mutc` candle3Mutc `candle1Mutc` candle1Mutc `candle1Wutc` candle1Wutc `candle1Dutc` candle1Dutc `candle2Dutc` candle2Dutc `candle3Dutc` candle3Dutc `candle5Dutc` candle5Dutc `candle12Hutc` candle12Hutc `candle6Hutc` candle6Hutc |
| > instId | String | Yes | Instrument ID |

> Successful Response Example

```highlight
{
  "op": "subscribe",
  "event": "subscribe",
  "arg": {
    "channel": "candle1D",
    "instId": "BTC-USDT"
  },
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"candle1D\", \"instId\" : \"BTC-USD-191227\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Event `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | yes | channel name |
| > instId | String | Yes | Instrument ID |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example

```highlight
{
  "arg": {
    "channel": "candle1D",
    "instId": "BTC-USDT"
  },
  "data": [
    [
      "1597026383085",
      "8533.02",
      "8553.74",
      "8527.17",
      "8548.26",
      "45247",
      "529.5858061",
      "5529.5858061",
      "0"
    ]
  ]
}

```

#### Push data parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| > instId | String | Instrument ID |
| data | Array of Arrays | Subscribed data |
| > ts | String | Opening time of the candlestick, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > o | String | Open price |
| > h | String | highest price |
| > l | String | Lowest price |
| > c | String | Close price |
| > vol | String | Trading volume If it is `SPOT` SPOT , the value is the quantity in base currency. |
| > volCcy | String | Trading volume If it is `SPOT` SPOT , the value is the quantity in quote currency. |
| > volCcyQuote | String | Trading volume, the value is the quantity in quote currency e.g. The unit is `USDT` USDT for `BTC-USDT` BTC-USDT |
| > confirm | String | The state of candlesticks `0` 0 : K line is uncompleted `1` 1 : K line is completed |

### WS / Trades channel

Retrieve the recent trades data. Data will be pushed whenever there is a trade. Every update may aggregate multiple trades.

The message is sent only once per taker order, per filled price. The count field is used to represent the number of aggregated matches.

#### URL Path

/ws/v5/public

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "trades",
      "instId": "BTC-USDT"
    }
  ]
}

```

```highlight

import asyncio

from okx.websocket.WsPublicAsync import WsPublicAsync

def callbackFunc(message):
    print(message)

async def main():
    ws = WsPublicAsync(url="wss://wspap.okx.com:8443/ws/v5/public")
    await ws.start()
    args = [
        {
          "channel": "trades",
          "instId": "BTC-USDT"
        }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `trades` trades |
| > instId | String | Yes | Instrument ID |

> Successful Response Example

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
      "channel": "trades",
      "instId": "BTC-USDT"
  },
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"trades\", \"instId\" : \"BTC-USD-191227\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Event `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name |
| > instId | String | Yes | Instrument ID |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example

```highlight
{
  "arg": {
    "channel": "trades",
    "instId": "BTC-USDT"
  },
  "data": [
    {
      "instId": "BTC-USDT",
      "tradeId": "130639474",
      "px": "42219.9",
      "sz": "0.12060306",
      "side": "buy",
      "ts": "1630048897897",
      "count": "3",
      "seqId": 1234
    }
  ]
}

```

#### Push data parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| > instId | String | Instrument ID |
| data | Array of objects | Subscribed data |
| > instId | String | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| > tradeId | String | The last trade ID in the trades aggregation |
| > px | String | Trade price |
| > sz | String | Trade quantity For spot trading, the unit is base currency For `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION , the unit is contract. |
| > side | String | Trade direction `buy` buy `sell` sell |
| > ts | String | Filled time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > count | String | The count of trades aggregated |
| > seqId | Integer | Sequence ID of the current message. |

Aggregation function description:  
1. The system will send only one message per taker order, per filled price. The `count` field will be used to represent the number of aggregated matches.  
2. The `tradeId` field in the message becomes the last trade ID in the aggregation.  
3. When the `count` = 1, it means the taker order matches only one maker order with the specific price.  
4. When the `count` > 1, it means the taker order matches multiple maker orders with the same price. For example, if `tradeId` = 123 and `count` = 3, it means the message aggregates the trades of `tradeId` = 123, 122, and 121. Maker side has filled multiple orders.  
5. Users can use this information to compare with data from the `trades-all` channel.  
6. Order book and the aggregated trades data are still published sequentially.  

The seqId may be the same for different trade updates that occur at the same time.

### WS / All trades channel

Retrieve the recent trades data. Data will be pushed whenever there is a trade. Every update contain only one trade.

#### URL Path

/ws/v5/business

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "trades-all",
      "instId": "BTC-USDT"
    }
  ]
}

```

```highlight

import asyncio

from okx.websocket.WsPublicAsync import WsPublicAsync

def callbackFunc(message):
    print(message)

async def main():
    ws = WsPublicAsync(url="wss://wspap.okx.com:8443/ws/v5/business")
    await ws.start()
    args = [
        {
          "channel": "trades-all",
          "instId": "BTC-USDT"
        }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `trades-all` trades-all |
| > instId | String | Yes | Instrument ID |

> Successful Response Example

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
      "channel": "trades-all",
      "instId": "BTC-USDT"
    },
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"trades-all\", \"instId\" : \"BTC-USD-191227\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Event `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name |
| > instId | String | Yes | Instrument ID |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example

```highlight
{
  "arg": {
    "channel": "trades-all",
    "instId": "BTC-USDT"
  },
  "data": [
    {
      "instId": "BTC-USDT",
      "tradeId": "130639474",
      "px": "42219.9",
      "sz": "0.12060306",
      "side": "buy",
      "ts": "1630048897897"
    }
  ]
}

```

#### Push data parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| > instId | String | Instrument ID |
| data | Array of objects | Subscribed data |
| > instId | String | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| > tradeId | String | Trade ID |
| > px | String | Trade price |
| > sz | String | Trade quantity For spot trading, the unit is base currency For `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION , the unit is contract. |
| > side | String | Trade direction `buy` buy `sell` sell |
| > ts | String | Filled time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### WS / Order book channel

Retrieve order book data. Best ask price may be lower than the best bid price during the pre-open period.

Use `books` for 400 depth levels, `books5` for 5 depth levels, `bbo-tbt` tick-by-tick 1 depth level, `books50-l2-tbt` tick-by-tick 50 depth levels, and `books-l2-tbt` for tick-by-tick 400 depth levels.

- `books`: 400 depth levels will be pushed in the initial full snapshot. Incremental data will be pushed every 100 ms for the changes in the order book during that period of time.
- `books5`: 5 depth levels snapshot will be pushed in the initial push. Snapshot data will be pushed every 100 ms when there are changes in the 5 depth levels snapshot.
- `bbo-tbt`: 1 depth level snapshot will be pushed in the initial push. Snapshot data will be pushed every 10 ms when there are changes in the 1 depth level snapshot.
- `books-l2-tbt`: 400 depth levels will be pushed in the initial full snapshot. Incremental data will be pushed every 10 ms for the changes in the order book during that period of time.
- `books50-l2-tbt`: 50 depth levels will be pushed in the initial full snapshot. Incremental data will be pushed every 10 ms for the changes in the order book during that period of time.
- The push sequence for order book channels within the same connection and trading symbols is fixed as: bbo-tbt -> books-l2-tbt -> books50-l2-tbt -> books -> books5.
- Users can not simultaneously subscribe to `books-l2-tbt` and `books50-l2-tbt/books` channels for the same trading symbol.
  - For more details, please refer to the changelog [2024-07-17](https://my.okx.com/docs-v5/log_en/#2024-07-17)

Only API users who are VIP5 and above in trading fee tier are allowed to subscribe to "books-l2-tbt" 400 depth channels   
Only API users who are VIP4 and above in trading fee tier are allowed to subscribe to "books50-l2-tbt" 50 depth channels  

Identity verification refers to [Login](https://my.okx.com/docs-v5/en/#overview-websocket-login)

#### URL Path

/ws/v5/public

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "books",
      "instId": "BTC-USDT"
    }
  ]
}

```

```highlight

import asyncio

from okx.websocket.WsPublicAsync import WsPublicAsync

def callbackFunc(message):
    print(message)

async def main():
    ws = WsPublicAsync(url="wss://wspap.okx.com:8443/ws/v5/public")
    await ws.start()
    args = [
      {
        "channel": "books",
        "instId": "BTC-USDT"
      }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `books` books `books5` books5 `bbo-tbt` bbo-tbt `books50-l2-tbt` books50-l2-tbt `books-l2-tbt` books-l2-tbt |
| > instId | String | Yes | Instrument ID |

> Response Example

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "books",
    "instId": "BTC-USDT"
  },
  "connId": "a4d3ae55"
}

```

> Failure example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"books\", \"instId\" : \"BTC-USD-191227\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Event `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name |
| > instId | String | Yes | Instrument ID |
| msg | String | No | Error message |
| code | String | No | Error code |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example: Full Snapshot

```highlight
{
  "arg": {
    "channel": "books",
    "instId": "BTC-USDT"
  },
  "action": "snapshot",
  "data": [
    {
      "asks": [
        ["8476.98", "415", "0", "13"],
        ["8477", "7", "0", "2"],
        ["8477.34", "85", "0", "1"],
        ["8477.56", "1", "0", "1"],
        ["8505.84", "8", "0", "1"],
        ["8506.37", "85", "0", "1"],
        ["8506.49", "2", "0", "1"],
        ["8506.96", "100", "0", "2"]
      ],
      "bids": [
        ["8476.97", "256", "0", "12"],
        ["8475.55", "101", "0", "1"],
        ["8475.54", "100", "0", "1"],
        ["8475.3", "1", "0", "1"],
        ["8447.32", "6", "0", "1"],
        ["8447.02", "246", "0", "1"],
        ["8446.83", "24", "0", "1"],
        ["8446", "95", "0", "3"]
      ],
      "ts": "1597026383085",
      "checksum": -855196043,
      "prevSeqId": -1,
      "seqId": 123456
    }
  ]
}

```

> Push Data Example: Incremental Data

```highlight
{
  "arg": {
    "channel": "books",
    "instId": "BTC-USDT"
  },
  "action": "update",
  "data": [
    {
      "asks": [
        ["8476.98", "415", "0", "13"],
        ["8477", "7", "0", "2"],
        ["8477.34", "85", "0", "1"],
        ["8477.56", "1", "0", "1"],
        ["8505.84", "8", "0", "1"],
        ["8506.37", "85", "0", "1"],
        ["8506.49", "2", "0", "1"],
        ["8506.96", "100", "0", "2"]
      ],
      "bids": [
        ["8476.97", "256", "0", "12"],
        ["8475.55", "101", "0", "1"],
        ["8475.54", "100", "0", "1"],
        ["8475.3", "1", "0", "1"],
        ["8447.32", "6", "0", "1"],
        ["8447.02", "246", "0", "1"],
        ["8446.83", "24", "0", "1"],
        ["8446", "95", "0", "3"]
      ],
      "ts": "1597026383085",
      "checksum": -855196043,
      "prevSeqId": 123456,
      "seqId": 123457
    }
  ]
}

```

#### Push data parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| > instId | String | Instrument ID |
| action | String | Push data action, incremental data or full snapshot. `snapshot` snapshot : full `update` update : incremental |
| data | Array of objects | Subscribed data |
| > asks | Array of Arrays | Order book on sell side |
| > bids | Array of Arrays | Order book on buy side |
| > ts | String | Order book generation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > checksum | Integer | Checksum, implementation details below |
| > prevSeqId | Integer | Sequence ID of the last sent message. Only applicable to `books` books , `books-l2-tbt` books-l2-tbt , `books50-l2-tbt` books50-l2-tbt |
| > seqId | Integer | Sequence ID of the current message, implementation details below |

An example of the array of asks and bids values: ["411.8", "10", "0", "4"]  
- "411.8" is the depth price  
- "10" is the quantity at the price (number of contracts for derivatives, quantity in base currency for Spot and Spot Margin)  
- "0" is part of a deprecated feature and it is always "0"  
- "4" is the number of orders at the price.

If you need to subscribe to many 50 or 400 depth level channels, it is recommended to subscribe through multiple websocket connections, with each of less than 30 channels.

The order book data will be updated around once a second during the call auction.

#### Sequence ID

`seqId` is the sequence ID of the market data published. The set of sequence ID received by users is the same if users are connecting to the same channel through multiple websocket connections. Each `instId` has an unique set of sequence ID. Users can use `prevSeqId` and `seqId` to build the message sequencing for incremental order book updates. Generally the value of seqId is larger than prevSeqId. The `prevSeqId` in the new message matches with `seqId` of the previous message. The smallest possible sequence ID value is 0, except in snapshot messages where the prevSeqId is always -1.

Exceptions:  
1. If there are no updates to the depth for an extended period(Around 60 seconds), for the channel that always updates snapshot data, OKX will send the latest snapshot, for the channel that has incremental data, OKX will send a message with `'asks': [], 'bids': []` to inform users that the connection is still active. `seqId` is the same as the last sent message and `prevSeqId` equals to `seqId`.
2. The sequence number may be reset due to maintenance, and in this case, users will receive an incremental message with `seqId` smaller than `prevSeqId`. However, subsequent messages will follow the regular sequencing rule.

##### Example

1. Snapshot message: prevSeqId = -1, seqId = 10
2. Incremental message 1 (normal update): prevSeqId = 10, seqId = 15
3. Incremental message 2 (no update): prevSeqId = 15, seqId = 15
4. Incremental message 3 (sequence reset): prevSeqId = 15, seqId = 3
5. Incremental message 4 (normal update): prevSeqId = 3, seqId = 5

#### Checksum

This mechanism can assist users in checking the accuracy of depth data.

##### Merging incremental data into full data

After subscribing to the incremental load push (such as `books` 400 levels) of Order Book Channel, users first receive the initial full load of market depth. After the incremental load is subsequently received, update the local full load.

1. If there is the same price, compare the size. If the size is 0, delete this depth data. If the size changes, replace the original data.
2. If there is no same price, sort by price (bid in descending order, ask in ascending order), and insert the depth information into the full load.

##### Calculate Checksum

Use the first 25 bids and asks in the full load to form a string (where a colon connects the price and size in an ask or a bid), and then calculate the CRC32 value (32-bit signed integer).

> Calculate Checksum

```highlight
1. More than 25 levels of bid and ask
A full load of market depth (only 2 levels of data are shown here, while 25 levels of data should actually be intercepted):

```

```highlight
{
    "bids": [
        ["3366.1", "7", "0", "3"],
        ["3366", "6", "3", "4"]
    ],
    "asks": [
        ["3366.8", "9", "10", "3"],
        ["3368", "8", "3", "4"]
    ]
}

```

```highlight
Check string:
"3366.1:7:3366.8:9:3366:6:3368:8"

2. Less than 25 levels of bid or ask
A full load of market depth:

```

```highlight
{
    "bids": [
        ["3366.1", "7", "0", "3"]
    ],
    "asks": [
        ["3366.8", "9", "10", "3"],
        ["3368", "8", "3", "4"],
        ["3372", "8", "3", "4"]
    ]
}

```

```highlight
Check string:
"3366.1:7:3366.8:9:3368:8:3372:8"

```

1. When the bid and ask depth data exceeds 25 levels, each of them will intercept 25 levels of data, and the string to be checked is queued in a way that the bid and ask depth data are alternately arranged.   
   Such as: `bid[price:size]`:`ask[price:size]`:`bid[price:size]`:`ask[price:size]`...
2. When the bid or ask depth data is less than 25 levels, the missing depth data will be ignored.  
   Such as: `bid[price:size]`:`ask[price:size]`:`asks[price:size]`:`asks[price:size]`...

> Push Data Example of bbo-tbt channel

```highlight
{
  "arg": {
    "channel": "bbo-tbt",
    "instId": "BCH-USDT-SWAP"
  },
  "data": [
    {
      "asks": [
        [
          "111.06","55154","0","2"
        ]
      ],
      "bids": [
        [
          "111.05","57745","0","2"
        ]
      ],
      "ts": "1670324386802",
      "seqId": 363996337
    }
  ]
}

```

> Push Data Example of books5 channel

```highlight
{
  "arg": {
    "channel": "books5",
    "instId": "BCH-USDT-SWAP"
  },
  "data": [
    {
      "asks": [
        ["111.06","55154","0","2"],
        ["111.07","53276","0","2"],
        ["111.08","72435","0","2"],
        ["111.09","70312","0","2"],
        ["111.1","67272","0","2"]],
      "bids": [
        ["111.05","57745","0","2"],
        ["111.04","57109","0","2"],
        ["111.03","69563","0","2"],
        ["111.02","71248","0","2"],
        ["111.01","65090","0","2"]],
      "instId": "BCH-USDT-SWAP",
      "ts": "1670324386802",
      "seqId": 363996337
    }
  ]
}

```

# Public Data

The API endpoints of `Public Data` do not require authentication.

## REST API

### Get instruments

Retrieve a list of instruments with open contracts.

#### Rate Limit: 20 requests per 2 seconds

#### Rate limit rule: IP + Instrument Type

#### HTTP Request

`GET /api/v5/public/instruments`

> Request Example

```highlight
GET /api/v5/public/instruments?instType=SPOT

```

```highlight
import okx.PublicData as PublicData

flag = "0"  # Production trading: 0, Demo trading: 1

publicDataAPI = PublicData.PublicAPI(flag=flag)

# Retrieve a list of instruments with open contracts
result = publicDataAPI.get_instruments(
    instType="SPOT"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| instType | String | Yes | Instrument type `SPOT` SPOT |
| instId | String | No | Instrument ID |

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
      {
            "alias": "",
            "auctionEndTime": "",
            "baseCcy": "BTC",
            "category": "1",
            "ctMult": "",
            "ctType": "",
            "ctVal": "",
            "ctValCcy": "",
            "expTime": "",
            "futureSettlement": false,
            "instFamily": "",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "lever": "10",
            "listTime": "1606468572000",
            "lotSz": "0.00000001",
            "maxIcebergSz": "9999999999.0000000000000000",
            "maxLmtAmt": "1000000",
            "maxLmtSz": "9999999999",
            "maxMktAmt": "1000000",
            "maxMktSz": "",
            "maxStopSz": "",
            "maxTriggerSz": "9999999999.0000000000000000",
            "maxTwapSz": "9999999999.0000000000000000",
            "minSz": "0.00001",
            "optType": "",
            "openType": "call_auction",
            "quoteCcy": "USDT",
            "settleCcy": "",
            "state": "live",
            "stk": "",
            "tickSz": "0.1",
            "uly": ""
        }
    ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| instType | String | Instrument type |
| instId | String | Instrument ID, e.g. `BTC-USDT` BTC-USDT |
| uly | String | Underlying, e.g. `BTC-USD` BTC-USD Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| instFamily | String | Instrument family, e.g. `BTC-USD` BTC-USD Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| category | String | Currency category. Note: this parameter is already deprecated |
| baseCcy | String | Base currency, e.g. `BTC` BTC in `BTC-USDT` BTC-USDT Only applicable to `SPOT` SPOT / `MARGIN` MARGIN |
| quoteCcy | String | Quote currency, e.g. `USDT` USDT in `BTC-USDT` BTC-USDT Only applicable to `SPOT` SPOT / `MARGIN` MARGIN |
| settleCcy | String | Settlement and margin currency, e.g. `BTC` BTC Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| ctVal | String | Contract value Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| ctMult | String | Contract multiplier Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| ctValCcy | String | Contract value currency Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| optType | String | Option type, `C` C : Call `P` P : put Only applicable to `OPTION` OPTION |
| stk | String | Strike price Only applicable to `OPTION` OPTION |
| listTime | String | Listing time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| auctionEndTime | String | The end time of call auction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 Only applicable to `SPOT` SPOT that are listed through call auctions, return "" in other cases (deprecated, use contTdSwTime) |
| contTdSwTime | String | Continuous trading switch time. The switch time from call auction, prequote to continuous trading, Unix timestamp format in milliseconds. e.g. `1597026383085` 1597026383085 . Only applicable to `SPOT` SPOT / `MARGIN` MARGIN that are listed through call auction or prequote, return "" in other cases. |
| openType | String | Open type `fix\_price` fix\_price : fix price opening `pre\_quote` pre\_quote : pre-quote `call\_auction` call\_auction : call auction Only applicable to `SPOT` SPOT / `MARGIN` MARGIN , return "" for all other business lines |
| expTime | String | Expiry time Applicable to `SPOT` SPOT / `MARGIN` MARGIN / `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION . For `FUTURES` FUTURES / `OPTION` OPTION , it is natural delivery/exercise time. It is the instrument offline time when there is `SPOT/MARGIN/FUTURES/SWAP/` SPOT/MARGIN/FUTURES/SWAP/ manual offline. Update once change. |
| lever | String | Max Leverage, Not applicable to `SPOT` SPOT , `OPTION` OPTION |
| tickSz | String | Tick size, e.g. `0.0001` 0.0001 For Option, it is minimum tickSz among tick band, please use "Get option tick bands" if you want get option tickBands. |
| lotSz | String | Lot size If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| minSz | String | Minimum order size If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| ctType | String | Contract type `linear` linear : linear contract `inverse` inverse : inverse contract Only applicable to `FUTURES` FUTURES / `SWAP` SWAP |
| alias | String | Alias `this\_week` this\_week `next\_week` next\_week `this\_month` this\_month `next\_month` next\_month `quarter` quarter `next\_quarter` next\_quarter `third\_quarter` third\_quarter Only applicable to `FUTURES` FUTURES Not recommended for use, users are encouraged to rely on the expTime field to determine the delivery time of the contract Not recommended for use, users are encouraged to rely on the expTime field to determine the delivery time of the contract |
| state | String | Instrument status `live` live `suspend` suspend `preopen` preopen e.g. Futures and options contracts rollover from generation to trading start; certain symbols before they go live `test` test : Test pairs, can't be traded |
| maxLmtSz | String | The maximum order quantity of a single limit order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| maxMktSz | String | The maximum order quantity of a single market order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `USDT` USDT . |
| maxLmtAmt | String | Max USD amount for a single limit order |
| maxMktAmt | String | Max USD amount for a single market order Only applicable to `SPOT` SPOT / `MARGIN` MARGIN |
| maxTwapSz | String | The maximum order quantity of a single TWAP order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| maxIcebergSz | String | The maximum order quantity of a single iceBerg order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| maxTriggerSz | String | The maximum order quantity of a single trigger order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| maxStopSz | String | The maximum order quantity of a single stop market order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `USDT` USDT . |
| futureSettlement | Boolean | Whether daily settlement for expiry feature is enabled Applicable to `FUTURES` FUTURES `cross` cross |

listTime and contTdSwTime  
For spot symbols listed through a call auction or pre-open, listTime represents the start time of the auction or pre-open, and contTdSwTime indicates the end of the auction or pre-open and the start of continuous trading. For other scenarios, listTime will mark the beginning of continuous trading, and contTdSwTime will return an empty value "".

state  
The state will always change from `preopen` to `live` when the listTime is reached.  
When a product is going to be delisted (e.g. when a FUTURES contract is settled or OPTION contract is exercised), the instrument will not be available.

### Get system time

Retrieve API server time.

#### Rate Limit: 10 requests per 2 seconds

#### Rate limit rule: IP

#### HTTP Request

`GET /api/v5/public/time`

> Request Example

```highlight
GET /api/v5/public/time

```

```highlight
import okx.PublicData as PublicData

flag = "0"  # Production trading: 0, Demo trading: 1

publicDataAPI = PublicData.PublicAPI(flag=flag)

# Retrieve API server time
result = publicDataAPI.get_system_time()
print(result)

```

> Response Example

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
    {
        "ts":"1597026383085"
    }
  ]
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| ts | String | System time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

## WebSocket

### Instruments channel

#### URL Path

/ws/v5/public

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "instruments",
      "instType": "SPOT"
    }
  ]
}

```

```highlight
import asyncio
from okx.websocket.WsPublicAsync import WsPublicAsync

def callbackFunc(message):
    print(message)

async def main():
    ws = WsPublicAsync(url="wss://wspap.okx.com:8443/ws/v5/public")
    await ws.start()
    args = [
        {
          "channel": "instruments",
          "instType": "SPOT"
        }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `instruments` instruments |
| > instType | String | Yes | Instrument type `SPOT` SPOT |

> Successful Response Example

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "instruments",
    "instType": "SPOT"
  },
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"instruments\", \"instType\" : \"FUTURES\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Event `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name |
| > instType | String | Yes | Instrument type `SPOT` SPOT |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example

```highlight
{
  "arg": {
    "channel": "instruments",
    "instType": "SPOT"
  },
  "data": [
    {
        "alias": "",
        "baseCcy": "BTC",
        "category": "1",
        "ctMult": "",
        "ctType": "",
        "ctVal": "",
        "ctValCcy": "",
        "contTdSwTime": "1704876947000",
        "expTime": "",
        "instFamily": "",
        "instId": "BTC-USDT",
        "instType": "SPOT",
        "lever": "10",
        "listTime": "1606468572000",
        "lotSz": "0.00000001",
        "maxIcebergSz": "9999999999.0000000000000000",
        "maxLmtAmt": "1000000",
        "maxLmtSz": "9999999999",
        "maxMktAmt": "1000000",
        "maxMktSz": "",
        "maxStopSz": "",
        "maxTriggerSz": "9999999999.0000000000000000",
        "maxTwapSz": "9999999999.0000000000000000",
        "minSz": "0.00001",
        "optType": "",
        "openType": "call_auction",
        "quoteCcy": "USDT",
        "settleCcy": "",
        "state": "live",
        "stk": "",
        "tickSz": "0.1",
        "uly": ""
    }
  ]
}

```

#### Push data parameters

| Parameter | Type | Description |
| --- | --- | --- |
| arg | Object | Subscribed channel |
| > channel | String | Channel name |
| > instType | String | Instrument type |
| data | Array of objects | Subscribed data |
| > instType | String | Instrument type |
| > instId | String | Instrument ID, e.g. `BTC-UST` BTC-UST |
| > uly | String | Underlying, e.g. `BTC-USD` BTC-USD Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| > instFamily | String | Instrument family, e.g. `BTC-USD` BTC-USD Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| > category | String | Currency category. Note: this parameter is already deprecated |
| > baseCcy | String | Base currency, e.g. `BTC` BTC in `BTC-USDT` BTC-USDT Only applicable to `SPOT` SPOT / `MARGIN` MARGIN |
| > quoteCcy | String | Quote currency, e.g. `USDT` USDT in `BTC-USDT` BTC-USDT Only applicable to `SPOT` SPOT / `MARGIN` MARGIN |
| > settleCcy | String | Settlement and margin currency, e.g. `BTC` BTC Only applicable to `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION |
| > ctVal | String | Contract value |
| > ctMult | String | Contract multiplier |
| > ctValCcy | String | Contract value currency |
| > optType | String | Option type `C` C : Call `P` P : Put Only applicable to `OPTION` OPTION |
| > stk | String | Strike price Only applicable to `OPTION` OPTION |
| > listTime | String | Listing time |
| > auctionEndTime | String | The end time of call auction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 Only applicable to `SPOT` SPOT that are listed through call auctions, return "" in other cases (deprecated, use contTdSwTime) |
| > contTdSwTime | String | Continuous trading switch time. The switch time from call auction, prequote to continuous trading, Unix timestamp format in milliseconds. e.g. `1597026383085` 1597026383085 . Only applicable to `SPOT` SPOT / `MARGIN` MARGIN that are listed through call auction or prequote, return "" in other cases. |
| > openType | String | Open type `fix\_price` fix\_price : fix price opening `pre\_quote` pre\_quote : pre-quote `call\_auction` call\_auction : call auction Only applicable to `SPOT` SPOT / `MARGIN` MARGIN , return "" for all other business lines |
| > expTime | String | Expiry time Applicable to `SPOT` SPOT / `MARGIN` MARGIN / `FUTURES` FUTURES / `SWAP` SWAP / `OPTION` OPTION . For `FUTURES` FUTURES / `OPTION` OPTION , it is the delivery/exercise time. It can also be the delisting time of the trading instrument. Update once change. |
| > lever | String | Max Leverage Not applicable to `SPOT` SPOT / `OPTION` OPTION , used to distinguish between `MARGIN` MARGIN and `SPOT` SPOT . |
| > tickSz | String | Tick size, e.g. `0.0001` 0.0001 For Option, it is minimum tickSz among tick band. |
| > lotSz | String | Lot size If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency |
| > minSz | String | Minimum order size If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency |
| > ctType | String | Contract type `linear` linear : linear contract `inverse` inverse : inverse contract Only applicable to `FUTURES` FUTURES / `SWAP` SWAP |
| > alias | String | Alias `this\_week` this\_week `next\_week` next\_week `this\_month` this\_month `next\_month` next\_month `quarter` quarter `next\_quarter` next\_quarter Only applicable to `FUTURES` FUTURES Not recommended for use, users are encouraged to rely on the expTime field to determine the delivery time of the contract Not recommended for use, users are encouraged to rely on the expTime field to determine the delivery time of the contract |
| > state | String | Instrument status `live` live `suspend` suspend `expired` expired `preopen` preopen . e.g. There will be preopen before the Futures and Options new contracts state is live. `test` test : Test pairs, can't be traded |
| > maxLmtSz | String | The maximum order quantity of a single limit order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| > maxMktSz | String | The maximum order quantity of a single market order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `USDT` USDT . |
| > maxTwapSz | String | The maximum order quantity of a single TWAP order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| > maxIcebergSz | String | The maximum order quantity of a single iceBerg order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| > maxTriggerSz | String | The maximum order quantity of a single trigger order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `base currency` base currency . |
| > maxStopSz | String | The maximum order quantity of a single stop market order. If it is a derivatives contract, the value is the number of contracts. If it is `SPOT` SPOT / `MARGIN` MARGIN , the value is the quantity in `USDT` USDT . |

Instrument status will trigger pushing of incremental data from instruments channel.
When a new contract is going to be listed, the instrument data of the new contract will be available with status preopen.
When a product is going to be delisted (e.g. when a FUTURES contract is settled or OPTION contract is exercised), the instrument status will be changed to expired.

listTime and contTdSwTime  
For spot symbols listed through a call auction or pre-open, listTime represents the start time of the auction or pre-open, and contTdSwTime indicates the end of the auction or pre-open and the start of continuous trading. For other scenarios, listTime will mark the beginning of continuous trading, and contTdSwTime will return an empty value "".

# Funding Account

The API endpoints of `Funding Account` require authentication.

## REST API

### Get currencies

Retrieve a list of all currencies available which are related to the current account's KYC entity.

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/currencies`

> Request Example

```highlight
GET /api/v5/asset/currencies

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Get currencies
result = fundingAPI.get_currencies()
print(result)

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ccy | String | No | Single currency or multiple currencies separated with comma, e.g. `BTC` BTC or `BTC,ETH` BTC,ETH . |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
        "burningFeeRate": "",
        "canDep": true,
        "canInternal": true,
        "canWd": true,
        "ccy": "BTC",
        "chain": "BTC-Bitcoin",
        "ctAddr": "",
        "depEstOpenTime": "",
        "depQuotaFixed": "",
        "depQuoteDailyLayer2": "",
        "fee": "0.00005",
        "logoLink": "https://static.coinall.ltd/cdn/oksupport/asset/currency/icon/btc20230419112752.png",
        "mainNet": true,
        "maxFee": "0.00005",
        "maxFeeForCtAddr": "",
        "maxWd": "500",
        "minDep": "0.0005",
        "minDepArrivalConfirm": "1",
        "minFee": "0.00005",
        "minFeeForCtAddr": "",
        "minInternal": "0.0001",
        "minWd": "0.0005",
        "minWdUnlockConfirm": "2",
        "name": "Bitcoin",
        "needTag": false,
        "usedDepQuotaFixed": "",
        "usedWdQuota": "0",
        "wdEstOpenTime": "",
        "wdQuota": "10000000",
        "wdTickSz": "8"
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency, e.g. `BTC` BTC |
| name | String | Name of currency. There is no related name when it is not shown. |
| logoLink | String | The logo link of currency |
| chain | String | Chain name, e.g. `USDT-ERC20` USDT-ERC20 , `USDT-TRC20` USDT-TRC20 |
| ctAddr | String | Contract address |
| canDep | Boolean | The availability to deposit from chain `false` false : not available `true` true : available |
| canWd | Boolean | The availability to withdraw to chain `false` false : not available `true` true : available |
| canInternal | Boolean | The availability to internal transfer `false` false : not available `true` true : available |
| depEstOpenTime | String | Estimated opening time for deposit, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 if `canDep` canDep is `true` true , it returns `""` "" |
| wdEstOpenTime | String | Estimated opening time for withdraw, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 if `canWd` canWd is `true` true , it returns `""` "" |
| minDep | String | The minimum deposit amount of currency in a single transaction |
| minWd | String | The minimum `on-chain withdrawal` on-chain withdrawal amount of currency in a single transaction |
| minInternal | String | The minimum `internal transfer` internal transfer amount of currency in a single transaction No maximum `internal transfer` internal transfer limit in a single transaction, subject to the withdrawal limit in the past 24 hours( `wdQuota` wdQuota ). |
| maxWd | String | The maximum amount of currency `on-chain withdrawal` on-chain withdrawal in a single transaction |
| wdTickSz | String | The withdrawal precision, indicating the number of digits after the decimal point. The withdrawal fee precision kept the same as withdrawal precision. The accuracy of internal transfer withdrawal is 8 decimal places. |
| wdQuota | String | The withdrawal limit in the past 24 hours (including `on-chain withdrawal` on-chain withdrawal and `internal transfer` internal transfer ), unit in `USD` USD |
| usedWdQuota | String | The amount of currency withdrawal used in the past 24 hours, unit in `USD` USD |
| fee | String | The fixed withdrawal fee Apply to `on-chain withdrawal` on-chain withdrawal |
| minFee | String | The minimum withdrawal fee for normal address Apply to `on-chain withdrawal` on-chain withdrawal (Deprecated) |
| maxFee | String | The maximum withdrawal fee for normal address Apply to `on-chain withdrawal` on-chain withdrawal (Deprecated) |
| minFeeForCtAddr | String | The minimum withdrawal fee for contract address Apply to `on-chain withdrawal` on-chain withdrawal (Deprecated) |
| maxFeeForCtAddr | String | The maximum withdrawal fee for contract address Apply to `on-chain withdrawal` on-chain withdrawal (Deprecated) |
| burningFeeRate | String | Burning fee rate, e.g "0.05" represents "5%". Some currencies may charge combustion fees. The burning fee is deducted based on the withdrawal quantity (excluding gas fee) multiplied by the burning fee rate. Apply to `on-chain withdrawal` on-chain withdrawal |
| mainNet | Boolean | If current chain is main net, then it will return `true` true , otherwise it will return `false` false |
| needTag | Boolean | Whether tag/memo information is required for withdrawal, e.g. `EOS` EOS will return `true` true |
| minDepArrivalConfirm | String | The minimum number of blockchain confirmations to acknowledge fund deposit. The account is credited after that, but the deposit can not be withdrawn |
| minWdUnlockConfirm | String | The minimum number of blockchain confirmations required for withdrawal of a deposit |
| depQuotaFixed | String | The fixed deposit limit, unit in `USD` USD Return empty string if there is no deposit limit |
| usedDepQuotaFixed | String | The used amount of fixed deposit quota, unit in `USD` USD Return empty string if there is no deposit limit |
| depQuoteDailyLayer2 | String | The layer2 network daily deposit limit |

### Get balance

Retrieve the funding account balances of all the assets and the amount that is available or on hold.

Only asset information of a currency with a balance greater than 0 will be returned.

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/balances`

> Request Example

```highlight
GET /api/v5/asset/balances

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Get balane
result = fundingAPI.get_balances()
print(result)

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ccy | String | No | Single currency or multiple currencies (no more than 20) separated with comma, e.g. `BTC` BTC or `BTC,ETH` BTC,ETH . |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "availBal": "37.11827078",
            "bal": "37.11827078",
            "ccy": "ETH",
            "frozenBal": "0"
        }
    ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency |
| bal | String | Balance |
| frozenBal | String | Frozen balance |
| availBal | String | Available balance |

### Get non-tradable assets

Retrieve the funding account balances of all the assets and the amount that is available or on hold.

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/non-tradable-assets`

> Request Example

```highlight
GET /api/v5/asset/non-tradable-assets

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

result = fundingAPI.get_non_tradable_assets()
print(result)

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ccy | String | No | Single currency or multiple currencies (no more than 20) separated with comma, e.g. `BTC` BTC or `BTC,ETH` BTC,ETH . |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "bal": "989.84719571",
            "burningFeeRate": "",
            "canWd": true,
            "ccy": "CELT",
            "chain": "CELT-OKTC",
            "ctAddr": "f403fb",
            "fee": "2",
            "feeCcy": "USDT",
            "logoLink": "https://static.coinall.ltd/cdn/assets/imgs/221/460DA8A592400393.png",
            "minWd": "0.1",
            "name": "",
            "needTag": false,
            "wdAll": false,
            "wdTickSz": "8"
        },
        {
            "bal": "0.001",
            "burningFeeRate": "",
            "canWd": true,
            "ccy": "MEME",
            "chain": "MEME-ERC20",
            "ctAddr": "09b760",
            "fee": "5",
            "feeCcy": "USDT",
            "logoLink": "https://static.coinall.ltd/cdn/assets/imgs/207/2E664E470103C613.png",
            "minWd": "0.001",
            "name": "MEME Inu",
            "needTag": false,
            "wdAll": false,
            "wdTickSz": "8"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency, e.g. `CELT` CELT |
| name | String | Chinese name of currency. There is no related name when it is not shown. |
| logoLink | String | Logo link of currency |
| bal | String | Withdrawable balance |
| canWd | Boolean | Availability to withdraw to chain. `false` false : not available `true` true : available |
| chain | String | Chain for withdrawal |
| minWd | String | Minimum withdrawal amount of currency in a single transaction |
| wdAll | Boolean | Whether all assets in this currency must be withdrawn at one time |
| fee | String | Fixed withdrawal fee |
| feeCcy | String | Fixed withdrawal fee unit, e.g. `USDT` USDT |
| burningFeeRate | String | Burning fee rate, e.g "0.05" represents "5%". Some currencies may charge combustion fees. The burning fee is deducted based on the withdrawal quantity (excluding gas fee) multiplied by the burning fee rate. |
| ctAddr | String | Last 6 digits of contract address |
| wdTickSz | String | Withdrawal precision, indicating the number of digits after the decimal point |
| needTag | Boolean | Whether tag/memo information is required for withdrawal |

### Get account asset valuation

View account asset valuation

#### Rate Limit: 1 request per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/asset-valuation`

> Request Example

```highlight
GET /api/v5/asset/asset-valuation

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Get account asset valuation
result = fundingAPI.get_asset_valuation()
print(result)

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ccy | String | No | Asset valuation calculation unit BTC, USDT USD, CNY, JP, KRW, RUB, EUR VND, IDR, INR, PHP, THB, TRY AUD, SGD, ARS, SAR, AED, IQD The default is the valuation in BTC. |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "details": {
                "classic": "124.6",
                "earn": "1122.73",
                "funding": "0.09",
                "trading": "2544.28"
            },
            "totalBal": "3790.09",
            "ts": "1637566660769"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| totalBal | String | Valuation of total account assets |
| ts | String | Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| details | Object | Asset valuation details for each account |
| > funding | String | Funding account |
| > trading | String | Trading account |
| > classic | String | [Deprecated] Classic account |
| > earn | String | Earn account |

### Funds transfer

Only API keys with `Trade` privilege can call this endpoint.

This endpoint supports the transfer of funds between your funding account and trading account, and from the master account to sub-accounts.

Sub-account can transfer out to master account by default. Need to call [Set permission of transfer out](https://my.okx.com/docs-v5/en/#sub-account-rest-api-set-permission-of-transfer-out) to grant privilege first if you want sub-account transferring to another sub-account (sub-accounts need to belong to same master account.)

Failure of the request does not mean the transfer has failed. Recommend to call "Get funds transfer state" to confirm the status.

#### Rate Limit: 2 requests per second

#### Rate limit rule: User ID + Currency

#### Permission: Trade

#### HTTP Request

`POST /api/v5/asset/transfer`

> Request Example

```highlight
# Transfer 1.5 USDT from funding account to Trading account when current account is master-account
POST /api/v5/asset/transfer
body
{
    "ccy":"USDT",
    "amt":"1.5",
    "from":"6",
    "to":"18"
}

# Transfer 1.5 USDT from funding account to subAccount when current account is master-account
POST /api/v5/asset/transfer
body
{
    "ccy":"USDT",
    "type":"1",
    "amt":"1.5",
    "from":"6",
    "to":"6",
    "subAcct":"mini"
}

# Transfer 1.5 USDT from funding account to subAccount when current account is sub-account
POST /api/v5/asset/transfer
body 
{
    "ccy":"USDT",
    "type":"4",
    "amt":"1.5",
    "from":"6",
    "to":"6",
    "subAcct":"mini"
}

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Funds transfer
result = fundingAPI.funds_transfer(
    ccy="USDT",
    amt="1.5",
    from_="6",
    to="18"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| type | String | No | Transfer type `0` 0 : transfer within account `1` 1 : master account to sub-account (Only applicable to API Key from master account) `2` 2 : sub-account to master account (Only applicable to API Key from master account) `3` 3 : sub-account to master account (Only applicable to APIKey from sub-account) `4` 4 : sub-account to sub-account (Only applicable to APIKey from sub-account, and target account needs to be another sub-account which belongs to same master account. Sub-account directly transfer out permission is disabled by default, set permission please refer to Set permission of transfer out Set permission of transfer out ) The default is `0` 0 . If you want to make transfer between sub-accounts by master account API key, refer to Master accounts manage the transfers between sub-accounts Master accounts manage the transfers between sub-accounts |
| ccy | String | Yes | Transfer currency, e.g. `USDT` USDT |
| amt | String | Yes | Amount to be transferred |
| from | String | Yes | The remitting account `6` 6 : Funding account `18` 18 : Trading account |
| to | String | Yes | The beneficiary account `6` 6 : Funding account `18` 18 : Trading account |
| subAcct | String | Conditional | Name of the sub-account When `type` type is `1` 1 / `2` 2 / `4` 4 , this parameter is required. |
| loanTrans | Boolean | No | Whether or not borrowed coins can be transferred out under `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin `true` true : borrowed coins can be transferred out `false` false : borrowed coins cannot be transferred out the default is `false` false |
| omitPosRisk | String | No | Ignore position risk Default is `false` false Applicable to `Portfolio margin` Portfolio margin |
| clientId | String | No | Client-supplied ID A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "transId": "754147",
      "ccy": "USDT",
      "clientId": "",
      "from": "6",
      "amt": "0.1",
      "to": "18"
    }
  ]
}

```

#### Response Parameters

> Response Example

| Parameter | Type | Description |
| --- | --- | --- |
| transId | String | Transfer ID |
| clientId | String | Client-supplied ID |
| ccy | String | Currency |
| from | String | The remitting account |
| amt | String | Transfer amount |
| to | String | The beneficiary account |

### Get funds transfer state

Retrieve the transfer state data of the last 2 weeks.

#### Rate Limit: 10 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/transfer-state`

> Request Example

```highlight
GET /api/v5/asset/transfer-state?transId=1&type=1

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Get funds transfer state
result = fundingAPI.transfer_state(
    transId="248424899",
    type="0"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| transId | String | Conditional | Transfer ID Either transId or clientId is required. If both are passed, transId will be used. |
| clientId | String | Conditional | Client-supplied ID A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| type | String | No | Transfer type `0` 0 : transfer within account `1` 1 : master account to sub-account (Only applicable to API Key from master account) `2` 2 : sub-account to master account (Only applicable to API Key from master account) `3` 3 : sub-account to master account (Only applicable to APIKey from sub-account) `4` 4 : sub-account to sub-account (Only applicable to APIKey from sub-account, and target account needs to be another sub-account which belongs to same master account) The default is `0` 0 . For Custody accounts, can choose not to pass this parameter or pass `0` 0 . |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "amt": "1.5",
            "ccy": "USDT",
            "clientId": "",
            "from": "18",
            "instId": "", //deprecated
            "state": "success",
            "subAcct": "test",
            "to": "6",
            "toInstId": "", //deprecated
            "transId": "1",
            "type": "1"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| transId | String | Transfer ID |
| clientId | String | Client-supplied ID |
| ccy | String | Currency, e.g. `USDT` USDT |
| amt | String | Amount to be transferred |
| type | String | Transfer type `0` 0 : transfer within account `1` 1 : master account to sub-account (Only applicable to API Key from master account) `2` 2 : sub-account to master account (Only applicable to APIKey from master account) `3` 3 : sub-account to master account (Only applicable to APIKey from sub-account) `4` 4 : sub-account to sub-account (Only applicable to APIKey from sub-account, and target account needs to be another sub-account which belongs to same master account) |
| from | String | The remitting account `6` 6 : Funding account `18` 18 : Trading account |
| to | String | The beneficiary account `6` 6 : Funding account `18` 18 : Trading account |
| subAcct | String | Name of the sub-account |
| instId | String | deprecated |
| toInstId | String | deprecated |
| state | String | Transfer state `success` success `pending` pending `failed` failed |

### Asset bills details

Query the billing record in the past month.

#### Rate Limit: 6 Requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/bills`

> Request Example

```highlight
GET /api/v5/asset/bills

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Get asset bills details
result = fundingAPI.get_bills()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ccy | String | No | Currency |
| type | String | No | Bill type `1` 1 : Deposit `2` 2 : Withdrawal `13` 13 : Canceled withdrawal `20` 20 : Transfer to sub account (for master account) `21` 21 : Transfer from sub account (for master account) `22` 22 : Transfer out from sub to master account (for sub-account) `23` 23 : Transfer in from master to sub account (for sub-account) `28` 28 : Manually claimed Airdrop `47` 47 : System reversal `48` 48 : Event Reward `49` 49 : Event Giveaway `68` 68 : Fee rebate (by rebate card) `72` 72 : Token received `73` 73 : Token given away `74` 74 : Token refunded `75` 75 : [Simple earn flexible] Subscription `76` 76 : [Simple earn flexible] Redemption `77` 77 : Jumpstart distribute `78` 78 : Jumpstart lock up `80` 80 : DEFI/Staking subscription `82` 82 : DEFI/Staking redemption `83` 83 : Staking yield `84` 84 : Violation fee `89` 89 : Deposit yield `116` 116 : [Fiat] Place an order `117` 117 : [Fiat] Fulfill an order `118` 118 : [Fiat] Cancel an order `124` 124 : Jumpstart unlocking `130` 130 : Transferred from Trading account `131` 131 : Transferred to Trading account `132` 132 : [P2P] Frozen by customer service `133` 133 : [P2P] Unfrozen by customer service `134` 134 : [P2P] Transferred by customer service `135` 135 : Cross chain exchange `137` 137 : [ETH Staking] Subscription `138` 138 : [ETH Staking] Swapping `139` 139 : [ETH Staking] Earnings `146` 146 : Customer feedback `150` 150 : Affiliate commission `151` 151 : Referral reward `152` 152 : Broker reward `160` 160 : Dual Investment subscribe `161` 161 : Dual Investment collection `162` 162 : Dual Investment profit `163` 163 : Dual Investment refund `172` 172 : [Affiliate] Sub-affiliate commission `173` 173 : [Affiliate] Fee rebate (by trading fee) `174` 174 : Jumpstart Pay `175` 175 : Locked collateral `176` 176 : Loan `177` 177 : Added collateral `178` 178 : Returned collateral `179` 179 : Repayment `180` 180 : Unlocked collateral `181` 181 : Airdrop payment `185` 185 : [Broker] Convert reward `187` 187 : [Broker] Convert transfer `189` 189 : Mystery box bonus `195` 195 : Untradable asset withdrawal `196` 196 : Untradable asset withdrawal revoked `197` 197 : Untradable asset deposit `198` 198 : Untradable asset collection reduce `199` 199 : Untradable asset collection increase `200` 200 : Buy `202` 202 : Price Lock Subscribe `203` 203 : Price Lock Collection `204` 204 : Price Lock Profit `205` 205 : Price Lock Refund `207` 207 : Dual Investment Lite Subscribe `208` 208 : Dual Investment Lite Collection `209` 209 : Dual Investment Lite Profit `210` 210 : Dual Investment Lite Refund `212` 212 : [Flexible loan] Multi-collateral loan collateral locked `215` 215 : [Flexible loan] Multi-collateral loan collateral released `217` 217 : [Flexible loan] Multi-collateral loan borrowed `218` 218 : [Flexible loan] Multi-collateral loan repaid `232` 232 : [Flexible loan] Subsidized interest received `220` 220 : Delisted crypto `221` 221 : Blockchain's withdrawal fee `222` 222 : Withdrawal fee refund `223` 223 : SWAP lead trading profit share `225` 225 : Shark Fin subscribe `226` 226 : Shark Fin collection `227` 227 : Shark Fin profit `228` 228 : Shark Fin refund `229` 229 : Airdrop `232` 232 : Subsidized interest received `233` 233 : Broker rebate compensation `240` 240 : Snowball subscribe `241` 241 : Snowball refund `242` 242 : Snowball profit `243` 243 : Snowball trading failed `249` 249 : Seagull subscribe `250` 250 : Seagull collection `251` 251 : Seagull profit `252` 252 : Seagull refund `263` 263 : Strategy bots profit share `265` 265 : Signal revenue `266` 266 : SPOT lead trading profit share `270` 270 : DCD broker transfer `271` 271 : DCD broker rebate `272` 272 : [Convert] Buy Crypto/Fiat `273` 273 : [Convert] Sell Crypto/Fiat `284` 284 : [Custody] Transfer out trading sub-account `285` 285 : [Custody] Transfer in trading sub-account `286` 286 : [Custody] Transfer out custody funding account `287` 287 : [Custody] Transfer in custody funding account `288` 288 : [Custody] Fund delegation `289` 289 : [Custody] Fund undelegation `299` 299 : Affiliate recommendation commission `300` 300 : Fee discount rebate `303` 303 : Snowball market maker transfer `304` 304 : [Simple Earn Fixed] Order submission `305` 305 : [Simple Earn Fixed] Order redemption `306` 306 : [Simple Earn Fixed] Principal distribution `307` 307 : [Simple Earn Fixed] Interest distribution (early termination compensation) `308` 308 : [Simple Earn Fixed] Interest distribution `309` 309 : [Simple Earn Fixed] Interest distribution (extension compensation) `311` 311 : Crypto dust auto-transfer in `313` 313 : Sent by gift `314` 314 : Received from gift `315` 315 : Refunded from gift `328` 328 : [SOL staking] Send Liquidity Staking Token reward `329` 329 : [SOL staking] Subscribe Liquidity Staking Token staking `330` 330 : [SOL staking] Mint Liquidity Staking Token `331` 331 : [SOL staking] Redeem Liquidity Staking Token order `332` 332 : [SOL staking] Settle Liquidity Staking Token order `333` 333 : Trial fund reward `339` 339 : [Simple Earn Fixed] Order submission `340` 340 : [Simple Earn Fixed] Order failure refund `341` 341 : [Simple Earn Fixed] Redemption `342` 342 : [Simple Earn Fixed] Principal `343` 343 : [Simple Earn Fixed] Interest `344` 344 : [Simple Earn Fixed] Compensatory interest `345` 345 : [Institutional Loan] Principal repayment `346` 346 : [Institutional Loan] Interest repayment `347` 347 : [Institutional Loan] Overdue penalty `348` 348 : [BTC staking] Subscription `349` 349 : [BTC staking] Redemption `350` 350 : [BTC staking] Earnings `351` 351 : [Institutional Loan] Loan disbursement `354` 354 : Copy and bot rewards `361` 361 : Deposit from closed sub-account `372` 372 : Asset segregation `373` 373 : Asset release |
| clientId | String | No | Client-supplied ID for transfer or withdrawal A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| after | String | No | Pagination of data to return records earlier than the requested `ts` ts or `billId` billId , Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| before | String | No | Pagination of data to return records newer than the requested `ts` ts or `billId` billId , Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. The maximum is `100` 100 . The default is `100` 100 . |
| pagingType | String | No | PagingType `1` 1 : Timestamp of the bill record `2` 2 : Bill ID of the bill record The default is `1` 1 |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [{
        "billId": "12344",
        "ccy": "BTC",
        "clientId": "",
        "balChg": "2",
        "bal": "12",
        "type": "1",
        "ts": "1597026383085",
        "notes": ""
    }]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| billId | String | Bill ID |
| ccy | String | Account balance currency |
| clientId | String | Client-supplied ID for transfer or withdrawal |
| balChg | String | Change in balance at the account level |
| bal | String | Balance at the account level |
| type | String | Bill type |
| notes | String | Notes |
| ts | String | Creation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### Asset bills history

Query the billing records of all time.
⚠️ **IMPORTANT**: Data updates occur every 30 seconds. Update frequency may vary based on data volume - please be aware of potential delays during high-traffic periods.

#### Rate Limit: 1 Requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/bills-history`

> Request Example

```highlight
GET /api/v5/asset/bills-history

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Get asset bills details
result = fundingAPI.get_bills_history()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ccy | String | No | Currency |
| type | String | No | Bill type `1` 1 : Deposit `2` 2 : Withdrawal `13` 13 : Canceled withdrawal `20` 20 : Transfer to sub account (for master account) `21` 21 : Transfer from sub account (for master account) `22` 22 : Transfer out from sub to master account (for sub-account) `23` 23 : Transfer in from master to sub account (for sub-account) `28` 28 : Manually claimed Airdrop `47` 47 : System reversal `48` 48 : Event Reward `49` 49 : Event Giveaway `68` 68 : Fee rebate (by rebate card) `72` 72 : Token received `73` 73 : Token given away `74` 74 : Token refunded `75` 75 : [Simple earn flexible] Subscription `76` 76 : [Simple earn flexible] Redemption `77` 77 : Jumpstart distribute `78` 78 : Jumpstart lock up `80` 80 : DEFI/Staking subscription `82` 82 : DEFI/Staking redemption `83` 83 : Staking yield `84` 84 : Violation fee `89` 89 : Deposit yield `116` 116 : [Fiat] Place an order `117` 117 : [Fiat] Fulfill an order `118` 118 : [Fiat] Cancel an order `124` 124 : Jumpstart unlocking `130` 130 : Transferred from Trading account `131` 131 : Transferred to Trading account `132` 132 : [P2P] Frozen by customer service `133` 133 : [P2P] Unfrozen by customer service `134` 134 : [P2P] Transferred by customer service `135` 135 : Cross chain exchange `137` 137 : [ETH Staking] Subscription `138` 138 : [ETH Staking] Swapping `139` 139 : [ETH Staking] Earnings `146` 146 : Customer feedback `150` 150 : Affiliate commission `151` 151 : Referral reward `152` 152 : Broker reward `160` 160 : Dual Investment subscribe `161` 161 : Dual Investment collection `162` 162 : Dual Investment profit `163` 163 : Dual Investment refund `172` 172 : [Affiliate] Sub-affiliate commission `173` 173 : [Affiliate] Fee rebate (by trading fee) `174` 174 : Jumpstart Pay `175` 175 : Locked collateral `176` 176 : Loan `177` 177 : Added collateral `178` 178 : Returned collateral `179` 179 : Repayment `180` 180 : Unlocked collateral `181` 181 : Airdrop payment `185` 185 : [Broker] Convert reward `187` 187 : [Broker] Convert transfer `189` 189 : Mystery box bonus `195` 195 : Untradable asset withdrawal `196` 196 : Untradable asset withdrawal revoked `197` 197 : Untradable asset deposit `198` 198 : Untradable asset collection reduce `199` 199 : Untradable asset collection increase `200` 200 : Buy `202` 202 : Price Lock Subscribe `203` 203 : Price Lock Collection `204` 204 : Price Lock Profit `205` 205 : Price Lock Refund `207` 207 : Dual Investment Lite Subscribe `208` 208 : Dual Investment Lite Collection `209` 209 : Dual Investment Lite Profit `210` 210 : Dual Investment Lite Refund `212` 212 : [Flexible loan] Multi-collateral loan collateral locked `215` 215 : [Flexible loan] Multi-collateral loan collateral released `217` 217 : [Flexible loan] Multi-collateral loan borrowed `218` 218 : [Flexible loan] Multi-collateral loan repaid `232` 232 : [Flexible loan] Subsidized interest received `220` 220 : Delisted crypto `221` 221 : Blockchain's withdrawal fee `222` 222 : Withdrawal fee refund `223` 223 : SWAP lead trading profit share `225` 225 : Shark Fin subscribe `226` 226 : Shark Fin collection `227` 227 : Shark Fin profit `228` 228 : Shark Fin refund `229` 229 : Airdrop `232` 232 : Subsidized interest received `233` 233 : Broker rebate compensation `240` 240 : Snowball subscribe `241` 241 : Snowball refund `242` 242 : Snowball profit `243` 243 : Snowball trading failed `249` 249 : Seagull subscribe `250` 250 : Seagull collection `251` 251 : Seagull profit `252` 252 : Seagull refund `263` 263 : Strategy bots profit share `265` 265 : Signal revenue `266` 266 : SPOT lead trading profit share `270` 270 : DCD broker transfer `271` 271 : DCD broker rebate `272` 272 : [Convert] Buy Crypto/Fiat `273` 273 : [Convert] Sell Crypto/Fiat `284` 284 : [Custody] Transfer out trading sub-account `285` 285 : [Custody] Transfer in trading sub-account `286` 286 : [Custody] Transfer out custody funding account `287` 287 : [Custody] Transfer in custody funding account `288` 288 : [Custody] Fund delegation `289` 289 : [Custody] Fund undelegation `299` 299 : Affiliate recommendation commission `300` 300 : Fee discount rebate `303` 303 : Snowball market maker transfer `304` 304 : [Simple Earn Fixed] Order submission `305` 305 : [Simple Earn Fixed] Order redemption `306` 306 : [Simple Earn Fixed] Principal distribution `307` 307 : [Simple Earn Fixed] Interest distribution (early termination compensation) `308` 308 : [Simple Earn Fixed] Interest distribution `309` 309 : [Simple Earn Fixed] Interest distribution (extension compensation) `311` 311 : Crypto dust auto-transfer in `313` 313 : Sent by gift `314` 314 : Received from gift `315` 315 : Refunded from gift `328` 328 : [SOL staking] Send Liquidity Staking Token reward `329` 329 : [SOL staking] Subscribe Liquidity Staking Token staking `330` 330 : [SOL staking] Mint Liquidity Staking Token `331` 331 : [SOL staking] Redeem Liquidity Staking Token order `332` 332 : [SOL staking] Settle Liquidity Staking Token order `333` 333 : Trial fund reward `339` 339 : [Simple Earn Fixed] Order submission `340` 340 : [Simple Earn Fixed] Order failure refund `341` 341 : [Simple Earn Fixed] Redemption `342` 342 : [Simple Earn Fixed] Principal `343` 343 : [Simple Earn Fixed] Interest `344` 344 : [Simple Earn Fixed] Compensatory interest `345` 345 : [Institutional Loan] Principal repayment `346` 346 : [Institutional Loan] Interest repayment `347` 347 : [Institutional Loan] Overdue penalty `348` 348 : [BTC staking] Subscription `349` 349 : [BTC staking] Redemption `350` 350 : [BTC staking] Earnings `351` 351 : [Institutional Loan] Loan disbursement `354` 354 : Copy and bot rewards `361` 361 : Deposit from closed sub-account `372` 372 : Asset segregation `373` 373 : Asset release |
| clientId | String | No | Client-supplied ID for transfer or withdrawal A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| after | String | No | Pagination of data to return records earlier than the requested `ts` ts or `billId` billId , Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| before | String | No | Pagination of data to return records newer than the requested `ts` ts or `billId` billId , Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. The maximum is `100` 100 . The default is `100` 100 . |
| pagingType | String | No | PagingType `1` 1 : Timestamp of the bill record `2` 2 : Bill ID of the bill record The default is `1` 1 |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [{
        "billId": "12344",
        "ccy": "BTC",
        "clientId": "",
        "balChg": "2",
        "bal": "12",
        "type": "1",
        "ts": "1597026383085",
        "notes": ""
    }]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| billId | String | Bill ID |
| ccy | String | Account balance currency |
| clientId | String | Client-supplied ID for transfer or withdrawal |
| balChg | String | Change in balance at the account level |
| bal | String | Balance at the account level |
| type | String | Bill type |
| notes | String | Notes |
| ts | String | Creation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### Get deposit address

Retrieve the deposit addresses of currencies, including previously-used addresses.

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/deposit-address`

> Request Example

```highlight
GET /api/v5/asset/deposit-address?ccy=BTC

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Get deposit address
result = fundingAPI.get_deposit_address(
    ccy="USDT"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ccy | String | Yes | Currency, e.g. `BTC` BTC |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "chain": "BTC-Bitcoin",
            "ctAddr": "",
            "ccy": "BTC",
            "to": "6",
            "addr": "39XNxK1Ryqgg3Bsyn6HzoqV4Xji25pNkv6",
            "verifiedName":"John Corner",
            "selected": true
        },
        {
            "chain": "BTC-OKC",
            "ctAddr": "",
            "ccy": "BTC",
            "to": "6",
            "addr": "0x66d0edc2e63b6b992381ee668fbcb01f20ae0428",
            "verifiedName":"John Corner",
            "selected": true
        },
        {
            "chain": "BTC-ERC20",
            "ctAddr": "5807cf",
            "ccy": "BTC",
            "to": "6",
            "addr": "0x66d0edc2e63b6b992381ee668fbcb01f20ae0428",
            "verifiedName":"John Corner",
            "selected": true
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| addr | String | Deposit address |
| tag | String | Deposit tag (This will not be returned if the currency does not require a tag for deposit) |
| memo | String | Deposit memo (This will not be returned if the currency does not require a memo for deposit) |
| pmtId | String | Deposit payment ID (This will not be returned if the currency does not require a payment\_id for deposit) |
| addrEx | Object | Deposit address attachment (This will not be returned if the currency does not require this) e.g. `TONCOIN` TONCOIN attached tag name is `comment` comment , the return will be `{'comment':'123456'}` {'comment':'123456'} |
| ccy | String | Currency, e.g. `BTC` BTC |
| chain | String | Chain name, e.g. `USDT-ERC20` USDT-ERC20 , `USDT-TRC20` USDT-TRC20 |
| to | String | The beneficiary account `6` 6 : Funding account `18` 18 : Trading account The users under some entity (e.g. Brazil) only support deposit to trading account. |
| verifiedName | String | Verified name (for recipient) |
| selected | Boolean | Return `true` true if the current deposit address is selected by the website page |
| ctAddr | String | Last 6 digits of contract address |

### Get deposit history

Retrieve the deposit records according to the currency, deposit status, and time range in reverse chronological order. The 100 most recent records are returned by default.  
Websocket API is also available, refer to [Deposit info channel](https://my.okx.com/docs-v5/en/#funding-account-websocket-deposit-info-channel).

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/deposit-history`

> Request Example

```highlight

GET /api/v5/asset/deposit-history

# Query deposit history from 2022-06-01 to 2022-07-01
GET /api/v5/asset/deposit-history?ccy=BTC&after=1654041600000&before=1656633600000

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Get deposit history
result = fundingAPI.get_deposit_history()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ccy | String | No | Currency, e.g. `BTC` BTC |
| depId | String | No | Deposit ID |
| fromWdId | String | No | Internal transfer initiator's withdrawal ID If the deposit comes from internal transfer, this field displays the withdrawal ID of the internal transfer initiator |
| txId | String | No | Hash record of the deposit |
| type | String | No | Deposit Type `3` 3 : internal transfer `4` 4 : deposit from chain |
| state | String | No | Status of deposit `0` 0 : waiting for confirmation `1` 1 : deposit credited `2` 2 : deposit successful `8` 8 : pending due to temporary deposit suspension on this crypto currency `11` 11 : match the address blacklist `12` 12 : account or deposit is frozen `13` 13 : sub-account deposit interception `14` 14 : KYC limit `17` 17 : Pending response from Travel Rule vendor |
| after | String | No | Pagination of data to return records earlier than the requested ts, Unix timestamp format in milliseconds, e.g. `1654041600000` 1654041600000 |
| before | String | No | Pagination of data to return records newer than the requested ts, Unix timestamp format in milliseconds, e.g. `1656633600000` 1656633600000 |
| limit | string | No | Number of results per request. The maximum is `100` 100 ; The default is `100` 100 |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
        "actualDepBlkConfirm": "2",
        "amt": "1",
        "areaCodeFrom": "",
        "ccy": "USDT",
        "chain": "USDT-TRC20",
        "depId": "88****33",
        "from": "",
        "fromWdId": "",
        "state": "2",
        "to": "TN4hGjVXMzy*********9b4N1aGizqs",
        "ts": "1674038705000",
        "txId": "fee235b3e812********857d36bb0426917f0df1802"
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency |
| chain | String | Chain name |
| amt | String | Deposit amount |
| from | String | Deposit account If the deposit comes from an internal transfer, this field displays the account information of the internal transfer initiator, which can be a mobile phone number, email address, account name, and will return "" in other cases |
| areaCodeFrom | String | If `from` from is a phone number, this parameter return area code of the phone number |
| to | String | Deposit address If the deposit comes from the on-chain, this field displays the on-chain address, and will return "" in other cases |
| txId | String | Hash record of the deposit |
| ts | String | The timestamp that the deposit record is created, Unix timestamp format in milliseconds, e.g. `1655251200000` 1655251200000 |
| state | String | Status of deposit `0` 0 : Waiting for confirmation `1` 1 : Deposit credited `2` 2 : Deposit successful `8` 8 : Pending due to temporary deposit suspension on this crypto currency `11` 11 : Match the address blacklist `12` 12 : Account or deposit is frozen `13` 13 : Sub-account deposit interception `14` 14 : KYC limit |
| depId | String | Deposit ID |
| fromWdId | String | Internal transfer initiator's withdrawal ID If the deposit comes from internal transfer, this field displays the withdrawal ID of the internal transfer initiator, and will return "" in other cases |
| actualDepBlkConfirm | String | The actual amount of blockchain confirmed in a single deposit |

About deposit state  
**Waiting for confirmation** is that the required number of blockchain confirmations has not been reached.   
**Deposit credited** is that there is sufficient number of blockchain confirmations for the currency to be credited to the account, but it cannot be withdrawn yet.   
**Deposit successful** means the crypto has been credited to the account and it can be withdrawn.

### Withdrawal

Only supported withdrawal of assets from funding account. Common sub-account does not support withdrawal.

The API can only make withdrawal to verified addresses/account, and verified addresses can be set by WEB/APP.

About tag  
Some token deposits require a deposit address and a tag (e.g. Memo/Payment ID), which is a string that guarantees the uniqueness of your deposit address. Follow the deposit procedure carefully, or you may risk losing your assets.  
For currencies with labels, if it is a withdrawal between OKX users, please use internal transfer instead of online withdrawal

API withdrawal restrictions for EEA users  
Due to recent updates to the Travel Rule regulations within the EEA, API withdrawal to private wallet is not allowed and the user can continue to withdraw crypto through our website or app. If the user withdraw to the exchange wallet, relevant information about the recipient must be provided. More details please refer to https://eea.okx.com/docs-v5/log\_en/#2025-01-14-withdrawal-api-adjustment-for-eea-entity-users

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### Permission: Withdraw

#### HTTP Request

`POST /api/v5/asset/withdrawal`

> Request Example

```highlight
# Withdrawal to exchange wallet
POST /api/v5/asset/withdrawal
body
{
    "amt": "1000",
    "dest": "4",
    "ccy": "USDT",
    "toAddr": "TYW7C5qjhQtuhjz5qLQtA9bzaeEFo6ueg7",
    "chain": "USDT-TRC20",
    "rcvrInfo": {
        "walletType": "exchange",
        "exchId":"did:ethr:0x401c4bc0241bc787f64510f21a4ae7ec3603487c",
        "rcvrFirstName":"Bruce",
        "rcvrLastName":"Wayne",
        "rcvrCountry":"United States",
        "rcvrStreetName":"Clementi Avenue 1",
        "rcvrTownName":"San Jose",
        "rcvrCountrySubDivision":"California"
    }
}

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Withdrawal
result = fundingAPI.withdrawal(
    ccy="USDT",
    toAddr="TXtvfb7cdrn6VX9H49mgio8bUxZ3DGfvYF",
    amt="100",
    dest="4",
    chain="USDT-TRC20"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ccy | String | Yes | Currency, e.g. `USDT` USDT |
| amt | String | Yes | Withdrawal amount Withdrawal fee is not included in withdrawal amount. Please reserve sufficient transaction fees when withdrawing. You can get fee amount by Get currencies Get currencies . For `internal transfer` internal transfer , transaction fee is always `0` 0 . |
| dest | String | Yes | Withdrawal method `3` 3 : internal transfer `4` 4 : on-chain withdrawal |
| toAddr | String | Yes | `toAddr` toAddr should be a trusted address/account. If your `dest` dest is `4` 4 , some crypto currency addresses are formatted as `'address:tag'` 'address:tag' , e.g. `'ARDOR-7JF3-8F2E-QUWZ-CAN7F:123456'` 'ARDOR-7JF3-8F2E-QUWZ-CAN7F:123456' If your `dest` dest is `3` 3 , `toAddr` toAddr should be a recipient address which can be email, phone or login account name (account name is only for sub-account). |
| chain | String | Conditional | Chain name There are multiple chains under some currencies, such as `USDT` USDT has `USDT-ERC20` USDT-ERC20 , `USDT-TRC20` USDT-TRC20 If the parameter is not filled in, the default will be the main chain. When you withdrawal the non-tradable asset, if the parameter is not filled in, the default will be the unique withdrawal chain. Apply to `on-chain withdrawal` on-chain withdrawal . You can get supported chain name by the endpoint of Get currencies Get currencies . |
| areaCode | String | Conditional | Area code for the phone number, e.g. `86` 86 If `toAddr` toAddr is a phone number, this parameter is required. Apply to `internal transfer` internal transfer |
| rcvrInfo | Object | Conditional | Recipient information For the specific entity users to do on-chain withdrawal/lightning withdrawal, this information is required. |
| > walletType | String | Yes | Wallet Type `exchange` exchange : Withdraw to exchange wallet `private` private : Withdraw to private wallet For the wallet belongs to business recipient, `rcvrFirstName` rcvrFirstName may input the company name, `rcvrLastName` rcvrLastName may input "N/A", location info may input the registered address of the company. |
| > exchId | String | Conditional | Exchange ID You can query supported exchanges through the endpoint of Get exchange list (public) Get exchange list (public) If the exchange is not in the exchange list, fill in '0' in this field. Apply to walletType = `exchange` exchange |
| > rcvrFirstName | String | Conditional | Receiver's first name, e.g. `Bruce` Bruce |
| > rcvrLastName | String | Conditional | Receiver's last name, e.g. `Wayne` Wayne |
| > rcvrCountry | String | Conditional | The recipient's country, e.g. `United States` United States You must enter an English country name or a two letter country code (ISO 3166-1). Please refer to the `Country Name` Country Name and `Country Code` Country Code in the country information table below. |
| > rcvrCountrySubDivision | String | Conditional | State/Province of the recipient, e.g. `California` California |
| > rcvrTownName | String | Conditional | The town/city where the recipient is located, e.g. `San Jose` San Jose |
| > rcvrStreetName | String | Conditional | Recipient's street address, e.g. `Clementi Avenue 1` Clementi Avenue 1 |
| clientId | String | No | Client-supplied ID A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [{
        "amt": "0.1",
        "wdId": "67485",
        "ccy": "BTC",
        "clientId": "",
        "chain": "BTC-Bitcoin"
    }]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency |
| chain | String | Chain name, e.g. `USDT-ERC20` USDT-ERC20 , `USDT-TRC20` USDT-TRC20 |
| amt | String | Withdrawal amount |
| wdId | String | Withdrawal ID |
| clientId | String | Client-supplied ID A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |

#### Country information

| Country name | Country code |
| --- | --- |
| Afghanistan | AF |
| Albania | AL |
| Algeria | DZ |
| Andorra | AD |
| Angola | AO |
| Anguilla | AI |
| Antigua and Barbuda | AG |
| Argentina | AR |
| Armenia | AM |
| Australia | AU |
| Austria | AT |
| Azerbaijan | AZ |
| Bahamas | BS |
| Bahrain | BH |
| Bangladesh | BD |
| Barbados | BB |
| Belarus | BY |
| Belgium | BE |
| Belize | BZ |
| Benin | BJ |
| Bermuda | BM |
| Bhutan | BT |
| Bolivia | BO |
| Bosnia and Herzegovina | BA |
| Botswana | BW |
| Brazil | BR |
| British Virgin Islands | VG |
| Brunei | BN |
| Bulgaria | BG |
| Burkina Faso | BF |
| Burundi | BI |
| Cambodia | KH |
| Cameroon | CM |
| Canada | CA |
| Cape Verde | CV |
| Cayman Islands | KY |
| Central African Republic | CF |
| Chad | TD |
| Chile | CL |
| Colombia | CO |
| Comoros | KM |
| Congo (Republic) | CG |
| Congo (Democratic Republic) | CD |
| Costa Rica | CR |
| Cote d´Ivoire (Ivory Coast) | CI |
| Croatia | HR |
| Cuba | CU |
| Cyprus | CY |
| Czech Republic | CZ |
| Denmark | DK |
| Djibouti | DJ |
| Dominica | DM |
| Dominican Republic | DO |
| Ecuador | EC |
| Egypt | EG |
| El Salvador | SV |
| Equatorial Guinea | GQ |
| Eritrea | ER |
| Estonia | EE |
| Ethiopia | ET |
| Fiji | FJ |
| Finland | FI |
| France | FR |
| Gabon | GA |
| Gambia | GM |
| Georgia | GE |
| Germany | DE |
| Ghana | GH |
| Greece | GR |
| Grenada | GD |
| Guatemala | GT |
| Guinea | GN |
| Guinea-Bissau | GW |
| Guyana | GY |
| Haiti | HT |
| Honduras | HN |
| Hong Kong | HK |
| Hungary | HU |
| Iceland | IS |
| India | IN |
| Indonesia | ID |
| Iran | IR |
| Iraq | IQ |
| Ireland | IE |
| Israel | IL |
| Italy | IT |
| Jamaica | JM |
| Japan | JP |
| Jordan | JO |
| Kazakhstan | KZ |
| Kenya | KE |
| Kiribati | KI |
| North Korea | KP |
| South Korea | KR |
| Kuwait | KW |
| Kyrgyzstan | KG |
| Laos | LA |
| Latvia | LV |
| Lebanon | LB |
| Lesotho | LS |
| Liberia | LR |
| Libya | LY |
| Liechtenstein | LI |
| Lithuania | LT |
| Luxembourg | LU |
| Macau | MO |
| Macedonia | MK |
| Madagascar | MG |
| Malawi | MW |
| Malaysia | MY |
| Maldives | MV |
| Mali | ML |
| Malta | MT |
| Marshall Islands | MH |
| Mauritania | MR |
| Mauritius | MU |
| Mexico | MX |
| Micronesia | FM |
| Moldova | MD |
| Monaco | MC |
| Mongolia | MN |
| Montenegro | ME |
| Morocco | MA |
| Mozambique | MZ |
| Myanmar (Burma) | MM |
| Namibia | NA |
| Nauru | NR |
| Nepal | NP |
| Netherlands | NL |
| New Zealand | NZ |
| Nicaragua | NI |
| Niger | NE |
| Nigeria | NG |
| Norway | NO |
| Oman | OM |
| Pakistan | PK |
| Palau | PW |
| Panama | PA |
| Papua New Guinea | PG |
| Paraguay | PY |
| Peru | PE |
| Philippines | PH |
| Poland | PL |
| Portugal | PT |
| Qatar | QA |
| Romania | RO |
| Russia | RU |
| Rwanda | RW |
| Saint Kitts and Nevis | KN |
| Saint Lucia | LC |
| Saint Vincent and the Grenadines | VC |
| Samoa | WS |
| San Marino | SM |
| Sao Tome and Principe | ST |
| Saudi Arabia | SA |
| Senegal | SN |
| Serbia | RS |
| Seychelles | SC |
| Sierra Leone | SL |
| Singapore | SG |
| Slovakia | SK |
| Slovenia | SI |
| Solomon Islands | SB |
| Somalia | SO |
| South Africa | ZA |
| Spain | ES |
| Sri Lanka | LK |
| Sudan | SD |
| Suriname | SR |
| Swaziland | SZ |
| Sweden | SE |
| Switzerland | CH |
| Syria | SY |
| Taiwan | TW |
| Tajikistan | TJ |
| Tanzania | TZ |
| Thailand | TH |
| Timor-Leste (East Timor) | TL |
| Togo | TG |
| Tonga | TO |
| Trinidad and Tobago | TT |
| Tunisia | TN |
| Turkey | TR |
| Turkmenistan | TM |
| Tuvalu | TV |
| U.S. Virgin Islands | VI |
| Uganda | UG |
| Ukraine | UA |
| United Arab Emirates | AE |
| United Kingdom | GB |
| United States | US |
| Uruguay | UY |
| Uzbekistan | UZ |
| Vanuatu | VU |
| Vatican City | VA |
| Venezuela | VE |
| Vietnam | VN |
| Yemen | YE |
| Zambia | ZM |
| Zimbabwe | ZW |
| Kosovo | XK |
| South Sudan | SS |
| China | CN |
| Palestine | PS |
| Curacao | CW |
| Dominican Republic | DO |
| Dominican Republic | DO |
| Gibraltar | GI |
| New Caledonia | NC |
| Cook Islands | CK |
| Reunion | RE |
| Guernsey | GG |
| Guadeloupe | GP |
| Martinique | MQ |
| French Polynesia | PF |
| Faroe Islands | FO |
| Greenland | GL |
| Jersey | JE |
| Aruba | AW |
| Puerto Rico | PR |
| Isle of Man | IM |
| Guam | GU |
| Sint Maarten | SX |
| Turks and Caicos | TC |
| Åland Islands | AX |
| Caribbean Netherlands | BQ |
| British Indian Ocean Territory | IO |
| Christmas as Island | CX |
| Cocos (Keeling) Islands | CC |
| Falkland Islands (Islas Malvinas) | FK |
| Mayotte | YT |
| Niue | NU |
| Norfolk Island | NF |
| Northern Mariana Islands | MP |
| Pitcairn Islands | PN |
| Saint Helena, Ascension and Tristan da Cunha | SH |
| Collectivity of Saint Martin | MF |
| Saint Pierre and Miquelon | PM |
| Tokelau | TK |
| Wallis and Futuna | WF |
| American Samoa | AS |

### Cancel withdrawal

You can cancel normal withdrawal requests, but you cannot cancel withdrawal requests on Lightning.

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/asset/cancel-withdrawal`

> Request Example

```highlight
POST /api/v5/asset/cancel-withdrawal
body {
   "wdId":"1123456"
}

```

```highlight
import okx.Funding as Funding

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

# Cancel withdrawal
result = fundingAPI.cancel_withdrawal(
    wdId="123456"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| wdId | String | Yes | Withdrawal ID |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "wdId": "1123456"   
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| wdId | String | Withdrawal ID |

If the code is equal to 0, it cannot be strictly considered that the withdrawal has been revoked. It only means that your request is accepted by the server. The actual result is subject to the status in the withdrawal history.

### Get withdrawal history

Retrieve the withdrawal records according to the currency, withdrawal status, and time range in reverse chronological order. The 100 most recent records are returned by default.  
Websocket API is also available, refer to [Withdrawal info channel](https://my.okx.com/docs-v5/en/#funding-account-websocket-withdrawal-info-channel).

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/withdrawal-history`

> Request Example

```highlight

GET /api/v5/asset/withdrawal-history

# Query withdrawal history from 2022-06-01 to 2022-07-01
GET /api/v5/asset/withdrawal-history?ccy=BTC&after=1654041600000&before=1656633600000

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ccy | String | No | Currency, e.g. `BTC` BTC |
| wdId | String | No | Withdrawal ID |
| clientId | String | No | Client-supplied ID A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| txId | String | No | Hash record of the deposit |
| type | String | No | Withdrawal type `3` 3 : Internal transfer `4` 4 : On-chain withdrawal |
| state | String | No | Status of withdrawal<br/>**Stage 1: Pending withdrawal**<br/>• `19`: Insufficient balance in the hot wallet<br/>• `17`: Pending response from Travel Rule vendor<br/>• `10`: Waiting transfer<br/>• `0`: Waiting withdrawal<br/>• `4`/`5`/`6`/`8`/`9`/`12`: Waiting manual review<br/>• `7`: Approved<br/>*Note: `0`, `17`, `19` can be cancelled, other statuses cannot be cancelled*<br/>**Stage 2: Withdrawal in progress** (Applicable to on-chain withdrawals, internal transfers do not have this stage)<br/>• `1`: Broadcasting your transaction to chain<br/>• `15`: Pending transaction validation<br/>• `16`: Due to local laws and regulations, your withdrawal may take up to 24 hours to arrive<br/>• `-3`: Canceling<br/>**Final stage**<br/>• `-2`: Canceled<br/>• `-1`: Failed<br/>• `2`: Success |
| after | String | No | Pagination of data to return records earlier than the requested ts, Unix timestamp format in milliseconds, e.g. `1654041600000` 1654041600000 |
| before | String | No | Pagination of data to return records newer than the requested ts, Unix timestamp format in milliseconds, e.g. `1656633600000` 1656633600000 |
| limit | String | No | Number of results per request. The maximum is `100` 100 ; The default is `100` 100 |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "note": "",
      "chain": "ETH-Ethereum",
      "fee": "0.007",
      "feeCcy": "ETH",
      "ccy": "ETH",
      "clientId": "",
      "amt": "0.029809",
      "txId": "0x35c******b360a174d",
      "from": "156****359",
      "areaCodeFrom": "86",
      "to": "0xa30d1fab********7CF18C7B6C579",
      "areaCodeTo": "",
      "state": "2",
      "ts": "1655251200000",
      "nonTradableAsset": false,
      "wdId": "15447421"
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency |
| chain | String | Chain name, e.g. `USDT-ERC20` USDT-ERC20 , `USDT-TRC20` USDT-TRC20 |
| nonTradableAsset | Boolean | Whether it is a non-tradable asset or not `true` true : non-tradable asset, `false` false : tradable asset |
| amt | String | Withdrawal amount |
| ts | String | Time the withdrawal request was submitted, Unix timestamp format in milliseconds, e.g. `1655251200000` 1655251200000 . |
| from | String | Withdrawal account It can be `email` email / `phone` phone / `sub-account name` sub-account name |
| areaCodeFrom | String | Area code for the phone number If `from` from is a phone number, this parameter returns the area code for the phone number |
| to | String | Receiving address |
| areaCodeTo | String | Area code for the phone number If `to` to is a phone number, this parameter returns the area code for the phone number |
| tag | String | Some currencies require a tag for withdrawals. This is not returned if not required. |
| pmtId | String | Some currencies require a payment ID for withdrawals. This is not returned if not required. |
| memo | String | Some currencies require this parameter for withdrawals. This is not returned if not required. |
| addrEx | Object | Withdrawal address attachment (This will not be returned if the currency does not require this) e.g. TONCOIN attached tag name is comment, the return will be {'comment':'123456'} |
| txId | String | Hash record of the withdrawal This parameter will return "" for internal transfers. |
| fee | String | Withdrawal fee amount |
| feeCcy | String | Withdrawal fee currency, e.g. `USDT` USDT |
| state | String | Status of withdrawal |
| wdId | String | Withdrawal ID |
| clientId | String | Client-supplied ID |
| note | String | Withdrawal note |

### Get deposit withdraw status

Retrieve deposit's and withdrawal's detailed status and estimated complete time.

#### Rate Limit: 1 request per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/deposit-withdraw-status`

> Request Example

```highlight
# For deposit
GET /api/v5/asset/deposit-withdraw-status?txId=xxxxxx&to=1672734730284&ccy=USDT&chain=USDT-ERC20

# For withdrawal
GET /api/v5/asset/deposit-withdraw-status?wdId=200045249

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| wdId | String | Conditional | Withdrawal ID, use to retrieve withdrawal status Required to input one and only one of `wdId` wdId and `txId` txId |
| txId | String | Conditional | Hash record of the deposit, use to retrieve deposit status Required to input one and only one of `wdId` wdId and `txId` txId |
| ccy | String | Conditional | Currency type, e.g. `USDT` USDT Required when retrieving deposit status with `txId` txId |
| to | String | Conditional | To address, the destination address in deposit Required when retrieving deposit status with `txId` txId |
| chain | String | Conditional | Currency chain information, e.g. USDT-ERC20 Required when retrieving deposit status with `txId` txId |

> Response Example

```highlight
{
    "code":"0",
    "data":[
        {
            "wdId": "200045249",
            "txId": "16f3638329xxxxxx42d988f97", 
            "state": "Pending withdrawal: Wallet is under maintenance, please wait.",
            "estCompleteTime": "01/09/2023, 8:10:48 PM"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| estCompleteTime | String | Estimated complete time The timezone is `UTC+8` UTC+8 . The format is MM/dd/yyyy, h:mm:ss AM/PM estCompleteTime is only an approximate estimated time, for reference only. |
| state | String | The detailed stage and status of the deposit/withdrawal The message in front of the colon is the stage; the message after the colon is the ongoing status. |
| txId | String | Hash record on-chain For withdrawal, if the `txId` txId has already been generated, it will return the value, otherwise, it will return "". |
| wdId | String | Withdrawal ID When retrieving deposit status, wdId returns blank "". |

Stage References  
Deposit  
Stage 1: On-chain transaction detection   
Stage 2: Push deposit data to associated account   
Stage 3: Receiving account credit   
Final stage: Deposit complete  
Withdrawal  
Stage 1: Pending withdrawal   
Stage 2: Withdrawal in progress   
Final stage: Withdrawal complete / cancellation complete   

### Get exchange list (public)

Authentication is not required for this public endpoint.

#### Rate Limit: 6 requests per second

#### Rate limit rule: IP

#### HTTP Request

`GET /api/v5/asset/exchange-list`

> Request Example

```highlight
GET /api/v5/asset/exchange-list

```

```highlight

```

#### Request Parameters

None

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
        "exchId": "did:ethr:0xfeb4f99829a9acdf52979abee87e83addf22a7e1",
        "exchName": "1xbet"
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| exchName | String | Exchange name, e.g. `1xbet` 1xbet |
| exchId | String | Exchange ID, e.g. `did:ethr:0xfeb4f99829a9acdf52979abee87e83addf22a7e1` did:ethr:0xfeb4f99829a9acdf52979abee87e83addf22a7e1 |

### Apply for monthly statement (last year)

Apply for monthly statement in the past year.

#### Rate Limit: 20 requests per month

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`POST /api/v5/asset/monthly-statement`

> Request Example

```highlight
POST /api/v5/asset/monthly-statement
body
{
    "month":"Jan"
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| month | String | No | Month,last month by default. Valid value is `Jan` Jan , `Feb` Feb , `Mar` Mar , `Apr` Apr , `May` May , `Jun` Jun , `Jul` Jul , `Aug` Aug , `Sep` Sep , `Oct` Oct , `Nov` Nov , `Dec` Dec |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "ts": "1646892328000"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| ts | String | Download link generation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### Get monthly statement (last year)

Retrieve monthly statement in the past year.

#### Rate Limit: 10 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/monthly-statement`

> Request Example

```highlight
GET /api/v5/asset/monthly-statement?month=Jan

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| month | String | Yes | Month, valid value is `Jan` Jan , `Feb` Feb , `Mar` Mar , `Apr` Apr , `May` May , `Jun` Jun , `Jul` Jul , `Aug` Aug , `Sep` Sep , `Oct` Oct , `Nov` Nov , `Dec` Dec |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "fileHref": "http://xxx",
            "state": "finished",
            "ts": 1646892328000
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| fileHref | String | Download file link |
| ts | Int | Download link generation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| state | String | Download link status "finished" "ongoing" |

### Get convert currencies

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/convert/currencies`

> Request Example

```highlight
GET /api/v5/asset/convert/currencies

```

#### Response parameters

none

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "min": "",  // Deprecated
            "max": "",  // Deprecated
            "ccy": "BTC"
        },
        {
            "min": "",
            "max": "",
            "ccy": "ETH"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency, e.g. BTC |
| min | String | Minimum amount to convert ( Deprecated ) |
| max | String | Maximum amount to convert ( Deprecated ) |

### Get convert currency pair

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/asset/convert/currency-pair`

> Request Example

```highlight
GET /api/v5/asset/convert/currency-pair?fromCcy=USDT&toCcy=BTC

```

#### Response parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| fromCcy | String | Yes | Currency to convert from, e.g. `USDT` USDT |
| toCcy | String | Yes | Currency to convert to, e.g. `BTC` BTC |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "baseCcy": "BTC",
            "baseCcyMax": "0.5",
            "baseCcyMin": "0.0001",
            "instId": "BTC-USDT",
            "quoteCcy": "USDT",
            "quoteCcyMax": "10000",
            "quoteCcyMin": "1"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| instId | String | Currency pair, e.g. `BTC-USDT` BTC-USDT |
| baseCcy | String | Base currency, e.g. `BTC` BTC in `BTC-USDT` BTC-USDT |
| baseCcyMax | String | Maximum amount of base currency |
| baseCcyMin | String | Minimum amount of base currency |
| quoteCcy | String | Quote currency, e.g. `USDT` USDT in `BTC-USDT` BTC-USDT |
| quoteCcyMax | String | Maximum amount of quote currency |
| quoteCcyMin | String | Minimum amount of quote currency |

### Estimate quote

#### Rate Limit: 10 requests per second

#### Rate limit rule: User ID

#### Rate Limit: 1 request per 5 seconds

#### Rate limit rule: Instrument ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/asset/convert/estimate-quote`

> Request Example

```highlight
POST /api/v5/asset/convert/estimate-quote
body
{
    "baseCcy": "ETH",
    "quoteCcy": "USDT",
    "side": "buy",
    "rfqSz": "30",
    "rfqSzCcy": "USDT"
}

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| baseCcy | String | Yes | Base currency, e.g. `BTC` BTC in `BTC-USDT` BTC-USDT |
| quoteCcy | String | Yes | Quote currency, e.g. `USDT` USDT in `BTC-USDT` BTC-USDT |
| side | String | Yes | Trade side based on `baseCcy` baseCcy `buy` buy `sell` sell |
| rfqSz | String | Yes | RFQ amount |
| rfqSzCcy | String | Yes | RFQ currency |
| clQReqId | String | No | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| tag | String | No | Order tag Applicable to broker user |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "baseCcy": "ETH",
            "baseSz": "0.01023052",
            "clQReqId": "",
            "cnvtPx": "2932.40104429",
            "origRfqSz": "30",
            "quoteCcy": "USDT",
            "quoteId": "quoterETH-USDT16461885104612381",
            "quoteSz": "30",
            "quoteTime": "1646188510461",
            "rfqSz": "30",
            "rfqSzCcy": "USDT",
            "side": "buy",
            "ttlMs": "10000"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| quoteTime | String | Quotation generation time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| ttlMs | String | Validity period of quotation in milliseconds |
| clQReqId | String | Client Order ID as assigned by the client |
| quoteId | String | Quote ID |
| baseCcy | String | Base currency, e.g. `BTC` BTC in `BTC-USDT` BTC-USDT |
| quoteCcy | String | Quote currency, e.g. `USDT` USDT in `BTC-USDT` BTC-USDT |
| side | String | Trade side based on `baseCcy` baseCcy |
| origRfqSz | String | Original RFQ amount |
| rfqSz | String | Real RFQ amount |
| rfqSzCcy | String | RFQ currency |
| cnvtPx | String | Convert price based on quote currency |
| baseSz | String | Convert amount of base currency |
| quoteSz | String | Convert amount of quote currency |

### Convert trade

You should make [estimate quote](https://my.okx.com/docs-v5/en/#funding-account-rest-api-estimate-quote) before convert trade.

Only assets in the trading account supported convert.

#### Rate Limit: 10 requests per second

#### Rate limit rule: User ID

#### Permission: Trade

For the same side (buy/sell), there's a trading limit of 1 request per 5 seconds.

#### HTTP Request

`POST /api/v5/asset/convert/trade`

> Request Example

```highlight
POST /api/v5/asset/convert/trade
body
{
    "baseCcy": "ETH",
    "quoteCcy": "USDT",
    "side": "buy",
    "sz": "30",
    "szCcy": "USDT",
    "quoteId": "quoterETH-USDT16461885104612381"
}

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| quoteId | String | Yes | Quote ID |
| baseCcy | String | Yes | Base currency, e.g. `BTC` BTC in `BTC-USDT` BTC-USDT |
| quoteCcy | String | Yes | Quote currency, e.g. `USDT` USDT in `BTC-USDT` BTC-USDT |
| side | String | Yes | Trade side based on `baseCcy` baseCcy `buy` buy `sell` sell |
| sz | String | Yes | Quote amount The quote amount should no more then RFQ amount |
| szCcy | String | Yes | Quote currency |
| clTReqId | String | No | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| tag | String | No | Order tag Applicable to broker user |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "baseCcy": "ETH",
            "clTReqId": "",
            "fillBaseSz": "0.01023052",
            "fillPx": "2932.40104429",
            "fillQuoteSz": "30",
            "instId": "ETH-USDT",
            "quoteCcy": "USDT",
            "quoteId": "quoterETH-USDT16461885104612381",
            "side": "buy",
            "state": "fullyFilled",
            "tradeId": "trader16461885203381437",
            "ts": "1646188520338"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| tradeId | String | Trade ID |
| quoteId | String | Quote ID |
| clTReqId | String | Client Order ID as assigned by the client |
| state | String | Trade state `fullyFilled` fullyFilled : success `rejected` rejected : failed |
| instId | String | Currency pair, e.g. `BTC-USDT` BTC-USDT |
| baseCcy | String | Base currency, e.g. `BTC` BTC in `BTC-USDT` BTC-USDT |
| quoteCcy | String | Quote currency, e.g. `USDT` USDT in `BTC-USDT` BTC-USDT |
| side | String | Trade side based on `baseCcy` baseCcy `buy` buy `sell` sell |
| fillPx | String | Filled price based on quote currency |
| fillBaseSz | String | Filled amount for base currency |
| fillQuoteSz | String | Filled amount for quote currency |
| ts | String | Convert trade time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### Get convert history

#### Rate Limit: 6 requests per second

#### Rate limit rule: User ID

#### HTTP Request

`GET /api/v5/asset/convert/history`

> Request Example

```highlight
GET /api/v5/asset/convert/history

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| clTReqId | String | No | Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| after | String | No | Pagination of data to return records earlier than the requested `ts` ts , Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| before | String | No | Pagination of data to return records newer than the requested `ts` ts , Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. The maximum is `100` 100 . The default is `100` 100 . |
| tag | String | No | Order tag Applicable to broker user If the convert trading used `tag` tag , this parameter is also required. |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "clTReqId": "",
            "instId": "ETH-USDT",
            "side": "buy",
            "fillPx": "2932.401044",
            "baseCcy": "ETH",
            "quoteCcy": "USDT",
            "fillBaseSz": "0.01023052",
            "state": "fullyFilled",
            "tradeId": "trader16461885203381437",
            "fillQuoteSz": "30",
            "ts": "1646188520000"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| tradeId | String | Trade ID |
| clTReqId | String | Client Order ID as assigned by the client |
| state | String | Trade state `fullyFilled` fullyFilled : success `rejected` rejected : failed |
| instId | String | Currency pair, e.g. `BTC-USDT` BTC-USDT |
| baseCcy | String | Base currency, e.g. `BTC` BTC in `BTC-USDT` BTC-USDT |
| quoteCcy | String | Quote currency, e.g. `USDT` USDT in `BTC-USDT` BTC-USDT |
| side | String | Trade side based on `baseCcy` baseCcy `buy` buy `sell` sell |
| fillPx | String | Filled price based on quote currency |
| fillBaseSz | String | Filled amount for base currency |
| fillQuoteSz | String | Filled amount for quote currency |
| ts | String | Convert trade time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### Get deposit payment methods

To display all the available fiat deposit payment methods

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/fiat/deposit-payment-methods`

> Request Example

```highlight
GET /api/v5/fiat/deposit-payment-methods?ccy=TRY
body
{
  "ccy" : "TRY",
}

```

```highlight

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ccy | String | Yes | Fiat currency, ISO-4217 3 digit currency code, e.g. `TRY` TRY |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "ccy": "TRY",
      "paymentMethod": "TR_BANKS",
      "feeRate": "0",
      "minFee": "0",
      "limits": {
        "dailyLimit": "2147483647",
        "dailyLimitRemaining": "2147483647",
        "weeklyLimit": "2147483647",
        "weeklyLimitRemaining": "2147483647",
        "monthlyLimit": "",
        "monthlyLimitRemaining": "",
        "maxAmt": "1000000",
        "minAmt": "1",
        "lifetimeLimit": "2147483647"
      },
      "accounts": [
          {
            "paymentAcctId": "1",
            "acctNum": "TR740001592093703829602611",
            "recipientName": "John Doe",
            "bankName": "VakıfBank",
            "bankCode": "TVBATR2AXXX",
            "state": "active"
          },
          {
            "paymentAcctId": "2",
            "acctNum": "TR740001592093703829602622",
            "recipientName": "John Doe",
            "bankName": "FBHLTRISXXX",
            "bankCode": "",
            "state": "active"
          }
      ]
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Fiat currency |
| paymentMethod | String | The payment method associated with the currency `TR\_BANKS` TR\_BANKS `PIX` PIX `SEPA` SEPA |
| feeRate | String | The fee rate for each deposit, expressed as a percentage e.g. `0.02` 0.02 represents 2 percent fee for each transaction. |
| minFee | String | The minimum fee for each deposit |
| limits | Object | An object containing limits for various transaction intervals |
| > dailyLimit | String | The daily transaction limit |
| > dailyLimitRemaining | String | The remaining daily transaction limit |
| > weeklyLimit | String | The weekly transaction limit |
| > weeklyLimitRemaining | String | The remaining weekly transaction limit |
| > monthlyLimit | String | The monthly transaction limit |
| > monthlyLimitRemaining | String | The remaining monthly transaction limit |
| > maxAmt | String | The maximum amount allowed per transaction |
| > minAmt | String | The minimum amount allowed per transaction |
| > lifetimeLimit | String | The lifetime transaction limit. Return the configured value, "" if not configured |
| accounts | Array of Object | An array containing information about payment accounts associated with the currency and method. |
| > paymentAcctId | String | The account ID for withdrawal |
| > acctNum | String | The account number, which can be an IBAN or other bank account number. |
| > recipientName | String | The name of the recipient |
| > bankName | String | The name of the bank associated with the account |
| > bankCode | String | The SWIFT code / BIC / bank code associated with the account |
| > state | String | The state of the account `active` active |

### Get withdrawal payment methods

To display all the available fiat withdrawal payment methods

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/fiat/withdrawal-payment-methods`

> Request Example

```highlight
 GET /api/v5/fiat/withdrawal-payment-methods?ccy=TRY

```

```highlight

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ccy | String | Yes | Fiat currency, ISO-4217 3 digit currency code. e.g. `TRY` TRY |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "ccy": "TRY",
      "paymentMethod": "TR_BANKS",
      "feeRate": "0.02",
      "minFee": "1",
      "limits": {
        "dailyLimit": "",
        "dailyLimitRemaining": "",
        "weeklyLimit": "",
        "weeklyLimitRemaining": "",
        "monthlyLimit": "",
        "monthlyLimitRemaining": "",
        "maxAmt": "",
        "minAmt": "",
        "lifetimeLimit": ""
      },
      "accounts": [
          {
            "paymentAcctId": "1",
            "acctNum": "TR740001592093703829602668",
            "recipientName": "John Doe",
            "bankName": "VakıfBank",
            "bankCode": "TVBATR2AXXX",
            "state": "active"
          },
          {
            "paymentAcctId": "2",
            "acctNum": "TR740001592093703829603024",
            "recipientName": "John Doe",
            "bankName": "Şekerbank",
            "bankCode": "SEKETR2AXXX",
            "state": "active"
          }
      ]
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Fiat currency |
| paymentMethod | String | The payment method associated with the currency `TR\_BANKS` TR\_BANKS `PIX` PIX `SEPA` SEPA |
| feeRate | String | The fee rate for each deposit, expressed as a percentage e.g. `0.02` 0.02 represents 2 percent fee for each transaction. |
| minFee | String | The minimum fee for each deposit |
| limits | Object | An object containing limits for various transaction intervals |
| > dailyLimit | String | The daily transaction limit |
| > dailyLimitRemaining | String | The remaining daily transaction limit |
| > weeklyLimit | String | The weekly transaction limit |
| > weeklyLimitRemaining | String | The remaining weekly transaction limit |
| > monthlyLimit | String | The monthly transaction limit |
| > monthlyLimitRemaining | String | The remaining monthly transaction limit |
| > minAmt | String | The minimum amount allowed per transaction |
| > maxAmt | String | The maximum amount allowed per transaction |
| > lifetimeLimit | String | The lifetime transaction limit. Return the configured value, "" if not configured |
| accounts | Array of Object | An array containing information about payment accounts associated with the currency and method. |
| > paymentAcctId | String | The account ID for withdrawal |
| > acctNum | String | The account number, which can be an IBAN or other bank account number. |
| > recipientName | String | The name of the recipient |
| > bankName | String | The name of the bank associated with the account |
| > bankCode | String | The SWIFT code / BIC / bank code associated with the account |
| > state | String | The state of the account `active` active |

### Create withdrawal order

Initiate a fiat withdrawal request (Authenticated endpoint, Only for API keys with "Withdrawal" access)  
Only supported withdrawal of assets from funding account.

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Withdraw

#### HTTP Request

`POST /api/v5/fiat/create-withdrawal`

> Request Example

```highlight
 POST /api/v5/fiat/create-withdrawal
 body
 {
    "paymentAcctId": "412323",
    "ccy": "TRY",
    "amt": "10000",
    "paymentMethod": "TR_BANKS",
    "clientId": "194a6975e98246538faeb0fab0d502df"
 }

```

```highlight

```

#### Request Parameters

| Parameters Parameters | Type Type | Required Required | Description Description |
| --- | --- | --- | --- |
| paymentAcctId | String | Yes | Payment account id to withdraw to, retrieved from get withdrawal payment methods API |
| ccy | String | Yes | Currency for withdrawal, must match currency allowed for paymentMethod |
| amt | String | Yes | Requested withdrawal amount before fees. Has to be less than or equal to 2 decimal points double |
| paymentMethod | String | Yes | Payment method to use for withdrawal `TR\_BANKS` TR\_BANKS `PIX` PIX `SEPA` SEPA |
| clientId | String | Yes | Client-supplied ID, A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters e.g. `194a6975e98246538faeb0fab0d502df` 194a6975e98246538faeb0fab0d502df |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
        "cTime": "1707429385000",
        "uTime": "1707429385000",
        "ordId": "124041201450544699",
        "paymentMethod": "TR_BANKS",
        "paymentAcctId": "20",
        "fee": "0",
        "amt": "100",
        "ccy": "TRY",
        "state": "completed",
        "clientId": "194a6975e98246538faeb0fab0d502df"
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ordId | String | The unique order Id |
| clientId | String | The client ID associated with the transaction |
| amt | String | The requested amount for the transaction |
| ccy | String | The currency of the transaction |
| fee | String | The transaction fee |
| paymentAcctId | String | The Id of the payment account used |
| paymentMethod | String | Payment Method `TR\_BANKS` TR\_BANKS `PIX` PIX `SEPA` SEPA |
| state | String | The State of the transaction `processing` processing `completed` completed |
| cTime | String | The creation time of the transaction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| uTime | String | The update time of the transaction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### Cancel withdrawal order

Cancel a pending fiat withdrawal order, currently only applicable to TRY

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/fiat/cancel-withdrawal`

> Request Example

```highlight
 POST /api/v5/fiat/cancel-withdrawal
 body
 {
    "ordId": "124041201450544699"
 }

```

```highlight

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ordId | String | Yes | Payment Order Id |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
        "ordId": "124041201450544699",
        "state": "canceled"
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ordId | String | Payment Order ID |
| state | String | The state of the transaction, e.g. `canceled` canceled |

### Get withdrawal order history

Get fiat withdrawal order history

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/fiat/withdrawal-order-history`

> Request Example

```highlight
 GET /api/v5/fiat/withdrawal-order-history

```

```highlight

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ccy | String | No | Fiat currency, ISO-4217 3 digit currency code, e.g. `TRY` TRY |
| paymentMethod | String | No | Payment Method `TR\_BANKS` TR\_BANKS `PIX` PIX `SEPA` SEPA |
| state | String | No | State of the order `completed` completed `failed` failed `pending` pending `canceled` canceled `inqueue` inqueue `processing` processing |
| after | String | No | Filter with a begin timestamp. Unix timestamp format in milliseconds (inclusive), e.g. `1597026383085` 1597026383085 |
| before | String | No | Filter with an end timestamp. Unix timestamp format in milliseconds (inclusive), e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. Maximum and default is `100` 100 |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
        "cTime": "1707429385000",
        "uTime": "1707429385000",
        "ordId": "124041201450544699",
        "paymentMethod": "TR_BANKS",
        "paymentAcctId": "20",
        "amt": "10000",
        "fee": "0",
        "ccy": "TRY",
        "state": "completed",
        "clientId": "194a6975e98246538faeb0fab0d502df"
    },
    {
        "cTime": "1707429385000",
        "uTime": "1707429385000",
        "ordId": "124041201450544690",
        "paymentMethod": "TR_BANKS",
        "paymentAcctId": "20",
        "amt": "5000",
        "fee": "0",
        "ccy": "TRY",
        "state": "completed",
        "clientId": "164a6975e48946538faeb0fab0d414fg"
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ordId | String | Unique Order Id |
| clientId | String | Client Id of the transaction |
| amt | String | Final amount of the transaction |
| ccy | String | Currency of the transaction |
| fee | String | Transaction fee |
| paymentAcctId | String | ID of the payment account used |
| paymentMethod | String | Payment method type |
| state | String | State of the transaction `completed` completed `failed` failed `pending` pending `canceled` canceled `inqueue` inqueue `processing` processing |
| cTime | String | Creation time of the transaction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| uTime | String | Update time of the transaction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### Get withdrawal order detail

Get fiat withdraw order detail

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/fiat/withdrawal`

> Request Example

```highlight
 GET /api/v5/fiat/withdrawal?ordId=024041201450544699
 body
 {
    "ordId": "024041201450544699"
 }

```

```highlight

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ordId | String | Yes | Order ID |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
        "cTime": "1707429385000",
        "uTime": "1707429385000",
        "ordId": "024041201450544699",
        "paymentMethod": "TR_BANKS",
        "paymentAcctId": "20",
        "amt": "100",
        "fee": "0",
        "ccy": "TRY",
        "state": "completed",
        "clientId": "194a6975e98246538faeb0fab0d502df"
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ordId | String | Order ID |
| clientId | String | The original request ID associated with the transaction |
| ccy | String | The currency of the transaction |
| amt | String | Amount of the transaction |
| fee | String | The transaction fee |
| paymentAcctId | String | The ID of the payment account used |
| paymentMethod | String | Payment method, e.g. `TR\_BANKS` TR\_BANKS |
| state | String | The state of the transaction `completed` completed `failed` failed `pending` pending `canceled` canceled `inqueue` inqueue `processing` processing |
| cTime | String | The creation time of the transaction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| uTime | String | The update time of the transaction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### Get deposit order history

Get fiat deposit order history

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/fiat/deposit-order-history`

> Request Example

```highlight
 GET /api/v5/fiat/deposit-order-history

```

```highlight

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ccy | String | No | ISO-4217 3 digit currency code |
| paymentMethod | String | No | Payment Method `TR\_BANKS` TR\_BANKS `PIX` PIX `SEPA` SEPA |
| state | String | No | State of the order `completed` completed `failed` failed `pending` pending `canceled` canceled `inqueue` inqueue `processing` processing |
| after | String | No | Filter with a begin timestamp. Unix timestamp format in milliseconds (inclusive), e.g. `1597026383085` 1597026383085 |
| before | String | No | Filter with an end timestamp. Unix timestamp format in milliseconds (inclusive), e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. Maximum and default is 100 |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
        "cTime": "1707429385000",
        "uTime": "1707429385000",
        "ordId": "024041201450544699",
        "paymentMethod": "TR_BANKS",
        "paymentAcctId": "20",
        "amt": "10000",
        "fee": "0",
        "ccy": "TRY",
        "state": "completed",
        "clientId": ""
    },
    {
        "cTime": "1707429385000",
        "uTime": "1707429385000",
        "ordId": "024041201450544690",
        "paymentMethod": "TR_BANKS",
        "paymentAcctId": "20",
        "amt": "50000",
        "fee": "0",
        "ccy": "TRY",
        "state": "completed",
        "clientId": ""
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ordId | String | Unique Order ID |
| clientId | String | Client Id of the transaction |
| ccy | String | Currency of the transaction |
| amt | String | Final amount of the transaction |
| fee | String | Transaction fee |
| paymentAcctId | String | ID of the payment account used |
| paymentMethod | String | Payment Method, e.g. `TR\_BANKS` TR\_BANKS |
| state | String | State of the transaction `completed` completed `failed` failed `pending` pending `canceled` canceled `inqueue` inqueue |
| cTime | String | Creation time of the transaction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| uTime | String | Update time of the transaction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

### Get deposit order detail

Get fiat deposit order detail

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/fiat/deposit`

> Request Example

```highlight
GET /api/v5/fiat/deposit?ordId=024041201450544699
body
{
    "ordId": "024041201450544699",
}

```

```highlight

```

#### Request Parameters

| Parameters Parameters | Types Types | Required Required | Description Description |
| --- | --- | --- | --- |
| ordId | String | Yes | Order ID |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
        "cTime": "1707429385000",
        "uTime": "1707429385000",
        "ordId": "024041201450544699",
        "paymentMethod": "TR_BANKS",
        "paymentAcctId": "20",
        "amt": "100",
        "fee": "0",
        "ccy": "TRY",
        "state": "completed",
        "clientId": ""
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ordId | String | Order ID |
| clientId | String | The original request ID associated with the transaction. If it's a deposit, it's most likely an empty string (""). |
| amt | String | Amount of the transaction |
| ccy | String | The currency of the transaction |
| fee | String | The transaction fee |
| paymentAcctId | String | The ID of the payment account used |
| paymentMethod | String | Payment method, e.g. `TR\_BANKS` TR\_BANKS |
| state | String | The state of the transaction `completed` completed `failed` failed `pending` pending `canceled` canceled `inqueue` inqueue `processing` processing |
| cTime | String | The creation time of the transaction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| uTime | String | The update time of the transaction, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |

## WebSocket

### Deposit info channel

A push notification is triggered when a deposit is initiated or the deposit status changes.  
Supports subscriptions for accounts

- If it is a master account subscription, you can receive the push of the deposit info of both the master account and the sub-account.
- If it is a sub-account subscription, only the push of sub-account deposit info you can receive.

#### URL Path

/ws/v5/business (required login)

> Request Example

```highlight
{
    "id": "1512",
    "op": "subscribe",
    "args": [
        {
            "channel": "deposit-info"
        }
    ]
}

```

```highlight
import asyncio
from okx.websocket.WsPrivateAsync import WsPrivateAsync

def callbackFunc(message):
    print(message)

async def main():
    ws = WsPrivateAsync(
        apiKey = "YOUR_API_KEY",
        passphrase = "YOUR_PASSPHRASE",
        secretKey = "YOUR_SECRET_KEY",
        url = "wss://ws.okx.com:8443/ws/v5/business",
        useServerTime=False
    )
    await ws.start()
    args = [
        {
            "channel": "deposit-info"
        }
    ]
    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `deposit-info` deposit-info |
| > ccy | String | No | Currency, e.g. `BTC` BTC |

> Successful Response Example

```highlight
{
    "id": "1512",
    "event": "subscribe",
    "arg": {
        "channel": "deposit-info"
    },
    "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
    "id": "1512",
    "event": "error",
    "code": "60012",
    "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"deposit-info\""}]}",
    "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name `deposit-info` deposit-info |
| > ccy | String | No | Currency, e.g. `BTC` BTC |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example

```highlight
{
    "arg": {
        "channel": "deposit-info",
        "uid": "289320****60975104"
    },
    "data": [{
        "actualDepBlkConfirm": "0",
        "amt": "1",
        "areaCodeFrom": "",
        "ccy": "USDT",
        "chain": "USDT-TRC20",
        "depId": "88165462",
        "from": "",
        "fromWdId": "",
        "pTime": "1674103661147",
        "state": "0",
        "subAcct": "test",
        "to": "TEhFAqpuHa3LY*****8ByNoGnrmexeGMw",
        "ts": "1674103661123",
        "txId": "bc5376817*****************dbb0d729f6b",
        "uid": "289320****60975104"
    }]
}

```

#### Push data parameters

| Parameters Parameters | Types Types | Description Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name `deposit-info` deposit-info |
| > uid | String | User Identifier |
| > ccy | String | Currency, e.g. `BTC` BTC |
| data | Array of objects | Subscribed data |
| > uid | String | User Identifier of the message producer |
| > subAcct | String | Sub-account name If the message producer is master account, the parameter will return "" |
| > pTime | String | Push time, the millisecond format of the Unix timestamp, e.g. `1597026383085` 1597026383085 |
| > ccy | String | Currency |
| > chain | String | Chain name |
| > amt | String | Deposit amount |
| > from | String | Deposit account Only the internal OKX account is returned, not the address on the blockchain. |
| > areaCodeFrom | String | If `from` from is a phone number, this parameter return area code of the phone number |
| > to | String | Deposit address |
| > txId | String | Hash record of the deposit |
| > ts | String | Time of deposit record is created, Unix timestamp format in milliseconds, e.g. `1655251200000` 1655251200000 |
| > state | String | Status of deposit `0` 0 : waiting for confirmation `1` 1 : deposit credited `2` 2 : deposit successful `8` 8 : pending due to temporary deposit suspension on this crypto currency `11` 11 : match the address blacklist `12` 12 : account or deposit is frozen `13` 13 : sub-account deposit interception `14` 14 : KYC limit |
| > depId | String | Deposit ID |
| > fromWdId | String | Internal transfer initiator's withdrawal ID If the deposit comes from internal transfer, this field displays the withdrawal ID of the internal transfer initiator, and will return "" in other cases |
| > actualDepBlkConfirm | String | The actual amount of blockchain confirmed in a single deposit |

### Withdrawal info channel

A push notification is triggered when a withdrawal is initiated or the withdrawal status changes.  
Supports subscriptions for accounts

- If it is a master account subscription, you can receive the push of the withdrawal info of both the master account and the sub-account.
- If it is a sub-account subscription, only the push of sub-account withdrawal info you can receive.

#### URL Path

/ws/v5/business (required login)

> Request Example

```highlight
{
    "id": "1512",
    "op": "subscribe",
    "args": [
        {
            "channel": "withdrawal-info"
        }
    ]
}

```

```highlight
import asyncio
from okx.websocket.WsPrivateAsync import WsPrivateAsync

def callbackFunc(message):
    print(message)

async def main():
    ws = WsPrivateAsync(
        apiKey = "YOUR_API_KEY",
        passphrase = "YOUR_PASSPHRASE",
        secretKey = "YOUR_SECRET_KEY",
        url = "wss://ws.okx.com:8443/ws/v5/business",
        useServerTime=False
    )
    await ws.start()
    args = [
        {
            "channel": "withdrawal-info"
        }
    ]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `withdrawal-info` withdrawal-info |
| > ccy | String | No | Currency, e.g. `BTC` BTC |

> Successful Response Example

```highlight
{
    "id": "1512",
    "event": "subscribe",
    "arg": {
        "channel": "withdrawal-info"
    },
    "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
    "id": "1512",
    "event": "error",
    "code": "60012",
    "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"withdrawal-info\"}]}",
    "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | Operation `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name `withdrawal-info` withdrawal-info |
| > ccy | String | No | Currency, e.g. `BTC` BTC |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example

```highlight
{
    "arg": {
        "channel": "withdrawal-info",
        "uid": "289320*****0975104"
    },
    "data": [{
        "addrEx": null,
        "amt": "2",
        "areaCodeFrom": "",
        "areaCodeTo": "",
        "ccy": "USDT",
        "chain": "USDT-TRC20",
        "clientId": "",
        "fee": "0.8",
        "feeCcy": "USDT",
        "from": "",
        "memo": "",
        "nonTradableAsset": false,
        "note": "",
        "pTime": "1674103268578",
        "pmtId": "",
        "state": "0",
        "subAcct": "test",
        "tag": "",
        "to": "TN8CKTQMnpWfT******8KipbJ24ErguhF",
        "ts": "1674103268472",
        "txId": "",
        "uid": "289333*****1101696",
        "wdId": "63754560"
    }]
}

```

#### Push data parameters

| Parameters Parameters | Types Types | Description Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| > uid | String | User Identifier |
| > ccy | String | Currency, e.g. `BTC` BTC |
| data | Array of objects | Subscribed data |
| > uid | String | User Identifier of the message producer |
| > subAcct | String | Sub-account name If the message producer is master account, the parameter will return "" |
| > pTime | String | Push time, the millisecond format of the Unix timestamp, e.g. `1597026383085` 1597026383085 |
| > ccy | String | Currency |
| > chain | String | Chain name, e.g. `USDT-ERC20` USDT-ERC20 , `USDT-TRC20` USDT-TRC20 |
| > nonTradableAsset | String | Whether it is a non-tradable asset or not `true` true : non-tradable asset, `false` false : tradable asset |
| > amt | String | Withdrawal amount |
| > ts | String | Time the withdrawal request was submitted, Unix timestamp format in milliseconds, e.g. `1655251200000` 1655251200000 . |
| > from | String | Withdrawal account It can be `email` email / `phone` phone / `sub-account name` sub-account name |
| > areaCodeFrom | String | Area code for the phone number If `from` from is a phone number, this parameter returns the area code for the phone number |
| > to | String | Receiving address |
| > areaCodeTo | String | Area code for the phone number If `to` to is a phone number, this parameter returns the area code for the phone number |
| > tag | String | Some currencies require a tag for withdrawals |
| > pmtId | String | Some currencies require a payment ID for withdrawals |
| > memo | String | Some currencies require this parameter for withdrawals |
| > addrEx | Object | Withdrawal address attachment, e.g. `TONCOIN` TONCOIN attached tag name is comment, the return will be {'comment':'123456'} |
| > txId | String | Hash record of the withdrawal This parameter will return "" for internal transfers. |
| > fee | String | Withdrawal fee amount |
| > feeCcy | String | Withdrawal fee currency, e.g. `USDT` USDT |
| > state | String | Status of withdrawal<br/>**Stage 1: Pending withdrawal**<br/>• `17`: Pending response from Travel Rule vendor<br/>• `10`: Waiting transfer<br/>• `0`: Waiting withdrawal<br/>• `4`/`5`/`6`/`8`/`9`/`12`: Waiting manual review<br/>• `7`: Approved<br/>**Stage 2: Withdrawal in progress** (Applicable to on-chain withdrawals, internal transfers do not have this stage)<br/>• `1`: Broadcasting your transaction to chain<br/>• `15`: Pending transaction validation<br/>• `16`: Due to local laws and regulations, your withdrawal may take up to 24 hours to arrive<br/>• `-3`: Canceling<br/>**Final stage**<br/>• `-2`: Canceled<br/>• `-1`: Failed<br/>• `2`: Success |
| > wdId | String | Withdrawal ID |
| > clientId | String | Client-supplied ID |
| > note | String | Withdrawal note |

# Sub-account

The API endpoints of `sub-account` require authentication.

## REST API

### Get sub-account list

Applies to master accounts only

#### Rate limit：2 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP request

`GET /api/v5/users/subaccount/list`

> Request sample

```highlight
GET /api/v5/users/subaccount/list

```

```highlight
import okx.SubAccount as SubAccount

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

subAccountAPI = SubAccount.SubAccountAPI(apikey, secretkey, passphrase, False, flag)

# Get sub-account list
result = subAccountAPI.get_subaccount_list()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| enable | String | No | Sub-account status `true` true : Normal `false` false : Frozen |
| subAcct | String | No | Sub-account name |
| after | String | No | Query the data earlier than the requested subaccount creation timestamp, the value should be a Unix timestamp in millisecond format. e.g. `1597026383085` 1597026383085 |
| before | String | No | Query the data newer than the requested subaccount creation timestamp, the value should be a Unix timestamp in millisecond format. e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. The maximum is 100. The default is 100. |

> Returned results

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "canTransOut": false,
            "enable": true,
            "frozenFunc": [
            ],
            "gAuth": false,
            "label": "D456DDDLx",
            "mobile": "",
            "subAcct": "D456DDDL",
            "ts": "1659334756000",
            "type": "1",
            "uid": "3400***********7413",
            "subAcctLv": "1",
            "firstLvSubAcct": "D456DDDL",
            "ifDma": false
        }
    ]
}

```

#### Response parameters

| Parameter name Parameter name | Type Type | Description Description |
| --- | --- | --- |
| type | String | Sub-account type `1` 1 : Standard sub-account `2` 2 : Managed trading sub-account `5` 5 : Custody trading sub-account - Copper `9` 9 : Managed trading sub-account - Copper `12` 12 : Custody trading sub-account - Komainu |
| enable | Boolean | Sub-account status `true` true : Normal `false` false : Frozen (global) |
| subAcct | String | Sub-account name |
| uid | String | Sub-account uid |
| label | String | Sub-account note |
| mobile | String | Mobile number that linked with the sub-account. |
| gAuth | Boolean | If the sub-account switches on the Google Authenticator for login authentication. `true` true : On `false` false : Off |
| frozenFunc | Array of strings | Frozen functions `trading` trading `convert` convert `transfer` transfer `withdrawal` withdrawal `deposit` deposit `flexible\_loan` flexible\_loan |
| canTransOut | Boolean | Whether the sub-account has the right to transfer out. `true` true : can transfer out `false` false : cannot transfer out |
| ts | String | Sub-account creation time, Unix timestamp in millisecond format. e.g. `1597026383085` 1597026383085 |
| subAcctLv | String | Sub-account level `1` 1 : First level sub-account `2` 2 : Second level sub-account. |
| firstLvSubAcct | String | The first level sub-account. For subAcctLv: 1, firstLvSubAcct is equal to subAcct For subAcctLv: 2, subAcct belongs to firstLvSubAcct. |
| ifDma | Boolean | Whether it is dma broker sub-account. `true` true : Dma broker sub-account `false` false : It is not dma broker sub-account. |

### Create sub-account

Applies to master accounts only and master accounts API Key must be linked to IP addresses.

#### Rate limit：1 request per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP request

`POST /api/v5/users/subaccount/create-subaccount`

> Request sample

```highlight
POST /api/v5/users/subaccount/create-subaccount
body
{
    "subAcct": "subAccount002",
    "type": "1",
    "label": "123456"
}

```

```highlight
import okx.SubAccount as SubAccount

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

subAccountAPI = SubAccount.SubAccountAPI(apikey, secretkey, passphrase, False, flag)

# Reset the API Key of a sub-account
result = subAccountAPI.reset_subaccount_apikey(
    subAcct="hahawang1",
    apiKey="",
    ip=""
)
print(result)

```

#### Request Parameters

| Parameter name | Type | Required | Description |
| --- | --- | --- | --- |
| subAcct | String | Yes | Sub-account name |
| type | String | Yes | Sub-account type `1` 1 : Standard sub-account `5` 5 : Custody trading sub-account - Copper `12` 12 : Custody trading sub-account - Komainu |
| label | String | No | Sub-account notes. 6-32 letters (case sensitive), numbers or special characters like \*. |
| pwd | String | Conditional | Sub-account login password, it is required for KYB users only. Your password must contain: 8 - 32 characters long. 1 lowercase character (a-z). 1 uppercase character (A-Z). 1 number. 1 special character e.g. ! @ # $ % |

> Returned results

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "label": "123456 ",
            "subAcct": "subAccount002",
            "ts": "1744875304520",
            "uid": "698827017768230914"
        }
    ]
}

```

#### Response parameters

| Parameter name Parameter name | Type Type | Description Description |
| --- | --- | --- |
| subAcct | String | Sub-account name |
| label | String | Sub-account notes |
| uid | String | Sub-account ID |
| ts | String | Creation time |

### Create an API Key for a sub-account

Applies to master accounts only and master accounts API Key must be linked to IP addresses.

#### Rate limit：1 request per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP request

`POST /api/v5/users/subaccount/apikey`

> Request sample

```highlight
POST /api/v5/users/subaccount/apikey
body
{
    "subAcct":"panpanBroker2",
    "label":"broker3",
    "passphrase": "******",
    "perm":"trade"
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| subAcct | String | Yes | Sub-account name, supports 6 to 20 characters that include numbers and letters (case sensitive, space symbol is not supported). |
| label | String | Yes | API Key note |
| passphrase | String | Yes | API Key password, supports 8 to 32 alphanumeric characters containing at least 1 number, 1 uppercase letter, 1 lowercase letter and 1 special character. |
| perm | String | No | API Key permissions `read\_only` read\_only : Read only `trade` trade : Trade |
| ip | String | No | Link IP addresses, separate with commas if more than one. Support up to 20 addresses. For security reasons, it is recommended to bind IP addresses. For security reasons, it is recommended to bind IP addresses. For security reasons, it is recommended to bind IP addresses. API keys with trading or withdrawal permissions that are not bound to IPs will expire after 14 days of inactivity. (API keys in demo trading will not be deleted.) API keys with trading or withdrawal permissions that are not bound to IPs will expire after 14 days of inactivity. (API keys in demo trading will not be deleted.) API keys with trading or withdrawal permissions that are not bound to IPs will expire after 14 days of inactivity. (API keys in demo trading will not be deleted.) |

> Returned result

```highlight
{
    "code": "0",
    "msg": "",
    "data": [{
        "subAcct": "test-1",
        "label": "v5",
        "apiKey": "******",
        "secretKey": "******",
        "passphrase": "******",
        "perm": "read_only,trade",
        "ip": "1.1.1.1,2.2.2.2",
        "ts": "1597026383085"
    }]
}

```

#### Response parameters

| Parameter name Parameter name | Type Type | Description Description |
| --- | --- | --- |
| subAcct | String | Sub-account name |
| label | String | API Key note |
| apiKey | String | API public key |
| secretKey | String | API private key |
| passphrase | String | API Key password |
| perm | String | API Key access `read\_only` read\_only : Read only `trade` trade : Trade |
| ip | String | IP address that linked with API Key |
| ts | String | Creation time |

### Query the API Key of a sub-account

Applies to master accounts only

#### Rate limit：1 request per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP request

`GET /api/v5/users/subaccount/apikey`

> Request sample

```highlight
GET /api/v5/users/subaccount/apikey?subAcct=panpanBroker2

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| subAcct | String | Yes | Sub-account name |
| apiKey | String | No | API public key |

> Returned results

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "label": "v5",
            "apiKey": "******",
            "perm": "read_only,trade",
            "ip": "1.1.1.1,2.2.2.2",
            "ts": "1597026383085"
        },
        {
            "label": "v5.1",
            "apiKey": "******",
            "perm": "read_only",
            "ip": "1.1.1.1,2.2.2.2",
            "ts": "1597026383085"
        }
    ]
}

```

#### Response parameters

| Parameter name Parameter name | Type Type | Description Description |
| --- | --- | --- |
| label | String | API Key note |
| apiKey | String | API public key |
| perm | String | API Key access read\_only: Read only; trade: Trade |
| ip | String | IP address that linked with API Key |
| ts | String | Creation time |

### Reset the API Key of a sub-account

Applies to master accounts only and master accounts API Key must be linked to IP addresses.

#### Rate limit：1 request per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP request

`POST /api/v5/users/subaccount/modify-apikey`

> Request sample

```highlight
POST /api/v5/users/subaccount/modify-apikey
body
{
    "subAcct":"yongxu",
    "apiKey":"******"
    "ip":"1.1.1.1"
}

```

```highlight
import okx.SubAccount as SubAccount

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

subAccountAPI = SubAccount.SubAccountAPI(apikey, secretkey, passphrase, False, flag)

# Reset the API Key of a sub-account
result = subAccountAPI.reset_subaccount_apikey(
    subAcct="hahawang1",
    apiKey="",
    ip=""
)
print(result)

```

#### Request Parameters

| Parameter name | Type | Required | Description |
| --- | --- | --- | --- |
| subAcct | String | Yes | Sub-account name |
| apiKey | String | Yes | Sub-account APIKey |
| label | String | No | Sub-account API Key label. The label will be reset if this is passed through. |
| perm | String | No | Sub-account API Key permissions `read\_only` read\_only : Read `trade` trade : Trade Separate with commas if more than one. The permission will be reset if this is passed through. |
| ip | String | No | Sub-account API Key linked IP addresses, separate with commas if more than one. Support up to 20 IP addresses. The IP will be reset if this is passed through. If `ip` ip is set to "", then no IP addresses is linked to the APIKey. |

> Returned results

```highlight
{
    "code": "0",
    "msg": "",
    "data": [{
        "subAcct": "yongxu",
        "label": "v5",
        "apiKey": "******",
        "perm": "read,trade",
        "ip": "1.1.1.1",
        "ts": "1597026383085"
    }]
}

```

#### Response parameters

| Parameter name Parameter name | Type Type | Description Description |
| --- | --- | --- |
| subAcct | String | Sub-account name |
| apiKey | String | Sub-accountAPI public key |
| label | String | Sub-account API Key label |
| perm | String | Sub-account API Key permissions `read\_only` read\_only : Read `trade` trade : Trade |
| ip | String | Sub-account API Key IP addresses that linked with API Key |
| ts | String | Creation time |

### Delete the API Key of sub-accounts

Applies to master accounts only and master accounts API Key must be linked to IP addresses.

#### Rate limit：1 request per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP request

`POST /api/v5/users/subaccount/delete-apikey`

> Request sample

```highlight
POST /api/v5/users/subaccount/delete-apikey
body
{
    "subAcct":"test00001",
    "apiKey":"******"
}

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| subAcct | String | Yes | Sub-account name |
| apiKey | String | Yes | API public key |

> Returned results

```highlight
{
    "code": "0",
    "msg": "",
    "data": [{
        "subAcct": "test00001"
    }]
}

```

#### Response parameters

| Parameter name Parameter name | Type Type | Description Description |
| --- | --- | --- |
| subAcct | String | Sub-account name |

### Get sub-account trading balance

Query detailed balance info of Trading Account of a sub-account via the master account (applies to master accounts only)

#### Rate limit：6 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP request

`GET /api/v5/account/subaccount/balances`

> Request sample

```highlight
GET /api/v5/account/subaccount/balances?subAcct=test1

```

```highlight
import okx.SubAccount as SubAccount

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

subAccountAPI = SubAccount.SubAccountAPI(apikey, secretkey, passphrase, False, flag)

# Get sub-account trading balance
result = subAccountAPI.get_account_balance(
    subAcct="hahawang1"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| subAcct | String | Yes | Sub-account name |

> Returned result

```highlight
{
    "code": "0",
    "data": [
        {
            "adjEq": "101.46752000000001",
            "availEq": "624719833286",
            "borrowFroz": "0",
            "details": [
                {
                    "accAvgPx": "",
                    "availBal": "101.5",
                    "availEq": "101.5",
                    "borrowFroz": "0",
                    "cashBal": "101.5",
                    "ccy": "USDT",
                    "clSpotInUseAmt": "",
                    "crossLiab": "0",
                    "collateralEnabled": false,
                    "collateralRestrict": false,
                    "colBorrAutoConversion": "0",
                    "disEq": "101.46752000000001",
                    "eq": "101.5",
                    "eqUsd": "101.46752000000001",
                    "fixedBal": "0",
                    "frozenBal": "0",
                    "imr": "",
                    "interest": "0",
                    "isoEq": "0",
                    "isoLiab": "0",
                    "isoUpl": "0",
                    "liab": "0",
                    "maxLoan": "1015.0000000000001",
                    "maxSpotInUse": "",
                    "mgnRatio": "",
                    "mmr": "",
                    "notionalLever": "",
                    "openAvgPx": "",
                    "ordFrozen": "0",
                    "rewardBal": "",
                    "smtSyncEq": "0",
                    "spotBal": "",
                    "spotCopyTradingEq": "0",
                    "spotInUseAmt": "",
                    "spotIsoBal": "0",
                    "spotUpl": "",
                    "spotUplRatio": "",
                    "stgyEq": "0",
                    "totalPnl": "",
                    "totalPnlRatio": "",
                    "twap": "0",
                    "uTime": "1663854334734",
                    "upl": "0",
                    "uplLiab": "0"
                }
            ],
            "imr": "0",
            "isoEq": "0",
            "mgnRatio": "",
            "mmr": "0",
            "notionalUsd": "0",
            "notionalUsdForBorrow": "0",
            "notionalUsdForFutures": "0",
            "notionalUsdForOption": "0",
            "notionalUsdForSwap": "0",
            "ordFroz": "0",
            "totalEq": "101.46752000000001",
            "uTime": "1739332269934",
            "upl": "0"
        }
    ],
    "msg": ""
}

```

#### Response parameters

| Parameters Parameters | Types Types | Description Description |
| --- | --- | --- |
| uTime | String | Update time of account information, millisecond format of Unix timestamp, e.g. `1597026383085` 1597026383085 |
| totalEq | String | The total amount of equity in `USD` USD |
| isoEq | String | Isolated margin equity in `USD` USD Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| adjEq | String | Adjusted / Effective equity in `USD` USD The net fiat value of the assets in the account that can provide margins for spot, expiry futures, perpetual futures and options under the cross-margin mode. In multi-ccy or PM mode, the asset and margin requirement will all be converted to USD value to process the order check or liquidation. Due to the volatility of each currency market, our platform calculates the actual USD value of each currency based on discount rates to balance market risks. Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin and `Portfolio margin` Portfolio margin |
| availEq | String | Account level available equity, excluding currencies that are restricted due to the collateralized borrowing limit. Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| ordFroz | String | Cross margin frozen for pending orders in `USD` USD Only applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| imr | String | Initial margin requirement in `USD` USD The sum of initial margins of all open positions and pending orders under cross-margin mode in `USD` USD . Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| mmr | String | Maintenance margin requirement in `USD` USD The sum of maintenance margins of all open positions and pending orders under cross-margin mode in `USD` USD . Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| borrowFroz | String | Potential borrowing IMR of the account in `USD` USD Only applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin . It is "" for other margin modes. |
| mgnRatio | String | Maintenance margin ratio in `USD` USD Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| notionalUsd | String | Notional value of positions in `USD` USD Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| notionalUsdForBorrow | String | Notional value for `Borrow` Borrow in USD Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| notionalUsdForSwap | String | Notional value of positions for `Perpetual Futures` Perpetual Futures in USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| notionalUsdForFutures | String | Notional value of positions for `Expiry Futures` Expiry Futures in USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| notionalUsdForOption | String | Notional value of positions for `Option` Option in USD Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| upl | String | Cross-margin info of unrealized profit and loss at the account level in `USD` USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| details | Array of objects | Detailed asset information in all currencies |
| > ccy | String | Currency |
| > eq | String | Equity of currency |
| > cashBal | String | Cash balance |
| > uTime | String | Update time of currency balance information, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| > isoEq | String | Isolated margin equity of currency Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > availEq | String | Available equity of currency Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > disEq | String | Discount equity of currency in `USD` USD . |
| > fixedBal | String | Frozen balance for `Dip Sniper` Dip Sniper and `Peak Sniper` Peak Sniper |
| > availBal | String | Available balance of currency |
| > frozenBal | String | Frozen balance of currency |
| > ordFrozen | String | Margin frozen for open orders Applicable to `Spot mode` Spot mode / `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin |
| > liab | String | Liabilities of currency It is a positive value, e.g. `21625.64` 21625.64 Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > upl | String | The sum of the unrealized profit & loss of all margin and derivatives positions of currency. Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > uplLiab | String | Liabilities due to Unrealized loss of currency Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > crossLiab | String | Cross liabilities of currency Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > rewardBal | String | Trial fund balance |
| > isoLiab | String | Isolated liabilities of currency Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > mgnRatio | String | Cross Maintenance margin ratio of currency The index for measuring the risk of a certain asset in the account. Applicable to `Futures mode` Futures mode and when there is cross position |
| > imr | String | Cross initial margin requirement at the currency level Applicable to `Futures mode` Futures mode and when there is cross position |
| > mmr | String | Cross maintenance margin requirement at the currency level Applicable to `Futures mode` Futures mode and when there is cross position |
| > interest | String | Accrued interest of currency It is a positive value, e.g. `9.01` 9.01 Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > twap | String | Risk indicator of auto liability repayment Divided into multiple levels from 0 to 5, the larger the number, the more likely the auto repayment will be triggered. Applicable to `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > maxLoan | String | Max loan of currency Applicable to `cross` cross of `Spot mode` Spot mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > eqUsd | String | Equity in `USD` USD of currency |
| > borrowFroz | String | Potential borrowing IMR of currency in `USD` USD Applicable to `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin . It is "" for other margin modes. |
| > notionalLever | String | Leverage of currency Applicable to `Futures mode` Futures mode |
| > stgyEq | String | Strategy equity |
| > isoUpl | String | Isolated unrealized profit and loss of currency Applicable to `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |
| > spotInUseAmt | String | Spot in use amount Applicable to `Portfolio margin` Portfolio margin |
| > clSpotInUseAmt | String | User-defined spot risk offset amount Applicable to `Portfolio margin` Portfolio margin |
| > maxSpotInUse | String | Max possible spot risk offset amount Applicable to `Portfolio margin` Portfolio margin |
| > spotIsoBal | String | Spot isolated balance Applicable to copy trading Applicable to `Spot mode` Spot mode / `Futures mode` Futures mode . |
| > smtSyncEq | String | Smart sync equity The default is "0", only applicable to copy trader. |
| > spotCopyTradingEq | String | Spot smart sync equity. The default is "0", only applicable to copy trader. |
| > spotBal | String | Spot balance. The unit is currency, e.g. BTC. More details More details |
| > openAvgPx | String | Spot average cost price. The unit is USD. More details More details |
| > accAvgPx | String | Spot accumulated cost price. The unit is USD. More details More details |
| > spotUpl | String | Spot unrealized profit and loss. The unit is USD. More details More details |
| > spotUplRatio | String | Spot unrealized profit and loss ratio. More details More details |
| > totalPnl | String | Spot accumulated profit and loss. The unit is USD. More details More details |
| > totalPnlRatio | String | Spot accumulated profit and loss ratio. More details More details |
| > collateralEnabled | Boolean | `true` true : Collateral enabled `false` false : Collateral disabled Applicable to `Multi-currency margin` Multi-currency margin More details More details |
| > collateralRestrict | Boolean | Platform level collateralized borrow restriction `true` true `false` false |
| > colBorrAutoConversion | String | Indicator of forced repayment when the collateralized borrowing on a crypto reaches the platform limit and users' trading accounts hold this crypto. Divided into multiple levels from 1-5, the larger the number, the more likely the repayment will be triggered. The default will be 0, indicating there is no risk currently. 5 means this user is undergoing auto conversion now. Applicable to `Spot mode` Spot mode / `Futures mode` Futures mode / `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin |

"" will be returned for inapplicable fields with the current account level.

### Get sub-account funding balance

Query detailed balance info of Funding Account of a sub-account via the master account (applies to master accounts only)

#### Rate limit：6 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP request

`GET /api/v5/asset/subaccount/balances`

> Request sample

```highlight
GET /api/v5/asset/subaccount/balances?subAcct=test1

```

```highlight
import okx.SubAccount as SubAccount

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

subAccountAPI = SubAccount.SubAccountAPI(apikey, secretkey, passphrase, False, flag)

# Get sub-account funding balance
result = subAccountAPI.get_funding_balance(
    subAcct="hahawang1"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| subAcct | String | Yes | Sub-account name |
| ccy | String | No | Single currency or multiple currencies (no more than 20) separated with comma, e.g. `BTC` BTC or `BTC,ETH` BTC,ETH . |

> Returned result

```highlight
{
    "code": "0",
    "msg": "",
    "data": [{
            "availBal": "37.11827078",
            "bal": "37.11827078",
            "ccy": "ETH",
            "frozenBal": "0"
        }
    ]
}

```

#### Response parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency |
| bal | String | Balance |
| frozenBal | String | Frozen balance |
| availBal | String | Available balance |

### Get sub-account maximum withdrawals

Retrieve the maximum withdrawal information of a sub-account via the master account (applies to master accounts only). If no currency is specified, the transferable amount of all owned currencies will be returned.

#### Rate limit: 20 requests per 2 seconds

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP request

`GET /api/v5/account/subaccount/max-withdrawal`

> Request Example

```highlight
GET /api/v5/account/subaccount/max-withdrawal?subAcct=test1

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| subAcct | String | Yes | Sub-account name |
| ccy | String | No | Single currency or multiple currencies (no more than 20) separated with comma, e.g. `BTC` BTC or `BTC,ETH` BTC,ETH . |

> Response Example

```highlight
{
   "code":"0",
   "data":[
      {
         "ccy":"BTC",
         "maxWd":"3",
         "maxWdEx":"",
         "spotOffsetMaxWd":"3",
         "spotOffsetMaxWdEx":""
      },
      {
         "ccy":"ETH",
         "maxWd":"15",
         "maxWdEx":"",
         "spotOffsetMaxWd":"15",
         "spotOffsetMaxWdEx":""
      },
      {
         "ccy":"USDT",
         "maxWd":"10600",
         "maxWdEx":"",
         "spotOffsetMaxWd":"10600",
         "spotOffsetMaxWdEx":""
      }
   ],
   "msg":""
}

```

#### Response parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency |
| maxWd | String | Max withdrawal (excluding borrowed assets under `Multi-currency margin` Multi-currency margin ) |
| maxWdEx | String | Max withdrawal (including borrowed assets under `Multi-currency margin` Multi-currency margin ) |
| spotOffsetMaxWd | String | Max withdrawal under Spot-Derivatives risk offset mode (excluding borrowed assets under `Portfolio margin` Portfolio margin ) Applicable to `Portfolio margin` Portfolio margin |
| spotOffsetMaxWdEx | String | Max withdrawal under Spot-Derivatives risk offset mode (including borrowed assets under `Portfolio margin` Portfolio margin ) Applicable to `Portfolio margin` Portfolio margin |

### Get history of sub-account transfer

This endpoint is only available for master accounts. Transfer records are available from September 28, 2022 onwards.

#### Rate limit：6 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP request

`GET /api/v5/asset/subaccount/bills`

> Request sample

```highlight
GET /api/v5/asset/subaccount/bills

```

```highlight
import okx.SubAccount as SubAccount

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

subAccountAPI = SubAccount.SubAccountAPI(apikey, secretkey, passphrase, False, flag)

# Get history of sub-account transfer
result = subAccountAPI.bills()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ccy | String | No | Currency, such as BTC |
| type | String | No | Transfer type `0` 0 : Transfers from master account to sub-account `1` 1 : Transfers from sub-account to master account. |
| subAcct | String | No | Sub-account name |
| after | String | No | Query the data prior to the requested bill ID creation time (exclude), the value should be a Unix timestamp in millisecond format. e.g. `1597026383085` 1597026383085 |
| before | String | No | Query the data after the requested bill ID creation time (exclude), the value should be a Unix timestamp in millisecond format. e.g. `1597026383085` 1597026383085 |
| limit | String | No | Number of results per request. The maximum is 100. The default is 100. |

> Returned results

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
      {
        "amt": "1.1",
        "billId": "89887685",
        "ccy": "USDT", 
        "subAcct": "hahatest1",
        "ts": "1712560959000",
        "type": "0"
      }
    ]
}

```

#### Response parameters

| Parameter name Parameter name | Type Type | Description Description |
| --- | --- | --- |
| billId | String | Bill ID |
| ccy | String | Transfer currency |
| amt | String | Transfer amount |
| type | String | Bill type |
| subAcct | String | Sub-account name |
| ts | String | Bill ID creation time, Unix timestamp in millisecond format, e.g. `1597026383085` 1597026383085 |

### Master accounts manage the transfers between sub-accounts

Applies to master accounts only.

Only API keys with `Trade` privilege can call this endpoint.

#### Rate limit：1 request per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP request

`POST /api/v5/asset/subaccount/transfer`

> Request sample

```highlight
POST /api/v5/asset/subaccount/transfer
body
{
    "ccy":"USDT",
    "amt":"1.5",
    "from":"6",
    "to":"6",
    "fromSubAccount":"test-1",
    "toSubAccount":"test-2"
}

```

```highlight
import okx.SubAccount as SubAccount

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

subAccountAPI = SubAccount.SubAccountAPI(apikey, secretkey, passphrase, False, flag)

# Master accounts manage the transfers between sub-accounts
result = subAccountAPI.subAccount_transfer(
    ccy="USDT",
    amt="10",
    froms="6",
    to="6",
    fromSubAccount="test-1",
    toSubAccount="test-2"
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ccy | String | Yes | Currency |
| amt | String | Yes | Transfer amount |
| from | String | Yes | Account type of transfer from sub-account `6` 6 : Funding Account `18` 18 : Trading account |
| to | String | Yes | Account type of transfer to sub-account `6` 6 : Funding Account `18` 18 : Trading account |
| fromSubAccount | String | Yes | Sub-account name of the account that transfers funds out. |
| toSubAccount | String | Yes | Sub-account name of the account that transfers funds in. |
| loanTrans | Boolean | No | Whether or not borrowed coins can be transferred out under `Multi-currency margin` Multi-currency margin / `Portfolio margin` Portfolio margin The default is `false` false |
| omitPosRisk | String | No | Ignore position risk Default is `false` false Applicable to `Portfolio margin` Portfolio margin |

> Returned results

```highlight
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "transId":"12345",
        }
    ]
}

```

#### Response parameters

| Parameter name Parameter name | Type Type | Description Description |
| --- | --- | --- |
| transId | String | Transfer ID |

### Set permission of transfer out

Set permission of transfer out for sub-account (only applicable to master account API key). Sub-account can transfer out to master account by default.

#### Rate Limit: 1 request per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/users/subaccount/set-transfer-out`

> Request Example

```highlight
POST /api/v5/users/subaccount/set-transfer-out
body
{
    "subAcct": "Test001,Test002",
    "canTransOut": true
}

```

```highlight
import okx.SubAccount as SubAccount

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

subAccountAPI = SubAccount.SubAccountAPI(apikey, secretkey, passphrase, False, flag)

# Set permission of transfer out for sub-account
result = subAccountAPI.set_permission_transfer_out(
    subAcct="hahawang1",
    canTransOut=False
)
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| subAcct | String | Yes | Name of the sub-account. Single sub-account or multiple sub-account (no more than 20) separated with comma. |
| canTransOut | Boolean | No | Whether the sub-account has the right to transfer out. The default is `true` true . `false` false : cannot transfer out `true` true : can transfer out |

> Returned result

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "subAcct": "Test001",
            "canTransOut": true
        },
        {
            "subAcct": "Test002",
            "canTransOut": true
        }
    ]
}

```

#### Response parameters

| Parameter Parameter | Type Type | Description Description |
| --- | --- | --- |
| subAcct | String | Name of the sub-account |
| canTransOut | Boolean | Whether the sub-account has the right to transfer out. `false` false : cannot transfer out `true` true : can transfer out |

# Financial Product

## On-chain earn

Only the assets in the funding account can be used for purchase. [More details](https://my.okx.com/earn/onchain-earn)

### GET / Offers

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/finance/staking-defi/offers`

> Request Example

```highlight
GET /api/v5/finance/staking-defi/offers

```

```highlight
import okx.Finance.StakingDefi as StakingDefi

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading:0 , demo trading:1

StakingAPI = StakingDefi.StakingDefiAPI(apikey, secretkey, passphrase, False, flag)

result = StakingAPI.get_offers(ccy="USDT")
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| productId | String | No | Product ID |
| protocolType | String | No | Protocol type `defi` defi : on-chain earn |
| ccy | String | No | Investment currency, e.g. `BTC` BTC |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "ccy": "DOT",
            "productId": "101",
            "protocol": "Polkadot",
            "protocolType": "defi",
            "term": "0",
            "apy": "0.1767",
            "earlyRedeem": false,
            "state": "purchasable",
            "investData": [
                {
                    "bal": "0",
                    "ccy": "DOT",
                    "maxAmt": "0",
                    "minAmt": "2"
                }
            ],
            "earningData": [
                {
                    "ccy": "DOT",
                    "earningType": "0"
                }
            ],
            "fastRedemptionDailyLimit": "",
            "redeemPeriod": [
                "28D",
                "28D"
            ]
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency type, e.g. `BTC` BTC |
| productId | String | Product ID |
| protocol | String | Protocol |
| protocolType | String | Protocol type `defi` defi : on-chain earn |
| term | String | Protocol term It will return the days of fixed term and will return `0` 0 for flexible product |
| apy | String | Estimated annualization If the annualization is 7% , this field is 0.07 |
| earlyRedeem | Boolean | Whether the protocol supports early redemption |
| investData | Array of objects | Current target currency information available for investment |
| > ccy | String | Investment currency, e.g. `BTC` BTC |
| > bal | String | Available balance to invest |
| > minAmt | String | Minimum subscription amount |
| > maxAmt | String | Maximum available subscription amount |
| earningData | Array of objects | Earning data |
| > ccy | String | Earning currency, e.g. `BTC` BTC |
| > earningType | String | Earning type `0` 0 : Estimated earning `1` 1 : Cumulative earning |
| state | String | Product state `purchasable` purchasable : Purchasable `sold\_out` sold\_out : Sold out `Stop` Stop : Suspension of subscription |
| redeemPeriod | Array of strings | Redemption Period, format in [min time,max time] `H` H : Hour, `D` D : Day e.g. ["1H","24H"] represents redemption period is between 1 Hour and 24 Hours. ["14D","14D"] represents redemption period is 14 days. |
| fastRedemptionDailyLimit | String | Fast redemption daily limit If fast redemption is not supported, it will return ''. |

### POST / Purchase

#### Rate Limit: 2 requests per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/finance/staking-defi/purchase`

> Request Example

```highlight
# Invest 100ZIL 30-day staking protocol
POST /api/v5/finance/staking-defi/purchase
body 
{
    "productId":"1234",
    "investData":[
      {
        "ccy":"ZIL",
        "amt":"100"
      }
    ],
    "term":"30"
}

```

```highlight
import okx.Finance.StakingDefi as StakingDefi

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading:0 , demo trading:1

StakingAPI = StakingDefi.StakingDefiAPI(apikey, secretkey, passphrase, False, flag)

result = StakingAPI.purchase(
            productId = "4005", 
            investData = [{
                "ccy":"USDT",
                "amt":"100"
            }]
        )
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| productId | String | Yes | Product ID |
| investData | Array of objects | Yes | Investment data |
| > ccy | String | Yes | Investment currency, e.g. `BTC` BTC |
| > amt | String | Yes | Investment amount |
| term | String | Conditional | Investment term Investment term must be specified for fixed-term product |
| tag | String | No | Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters. |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "ordId": "754147",
      "tag": ""
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ordId | String | Order ID |
| tag | String | Order tag |

### POST / Redeem

#### Rate Limit: 2 requests per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/finance/staking-defi/redeem`

> Request Example

```highlight
# Early redemption of investment
POST /api/v5/finance/staking-defi/redeem
body 
{
    "ordId":"754147",
    "protocolType":"defi",
    "allowEarlyRedeem":true
}

```

```highlight
import okx.Finance.StakingDefi as StakingDefi

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading:0 , demo trading:1

StakingAPI = StakingDefi.StakingDefiAPI(apikey, secretkey, passphrase, False, flag)

result = StakingAPI.redeem(
           ordId = "1234",
           protocolType = "defi"
        )
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ordId | String | Yes | Order ID |
| protocolType | String | Yes | Protocol type `defi` defi : on-chain earn |
| allowEarlyRedeem | Boolean | No | Whether allows early redemption Default is `false` false |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "ordId": "754147",
      "tag": ""
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ordId | String | Order ID |
| tag | String | Order tag |

### POST / Cancel purchases/redemptions

After cancelling, returning funds will go to the funding account.

#### Rate Limit: 2 requests per second

#### Rate limit rule: User ID

#### Permission: Trade

#### HTTP Request

`POST /api/v5/finance/staking-defi/cancel`

> Request Example

```highlight
POST /api/v5/finance/staking-defi/cancel
body 
{
    "ordId":"754147",
    "protocolType":"defi"
}

```

```highlight
import okx.Finance.StakingDefi as StakingDefi

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading:0 , demo trading:1

StakingAPI = StakingDefi.StakingDefiAPI(apikey, secretkey, passphrase, False, flag)

result = StakingAPI.cancel(
           ordId = "1234",
           protocolType = "defi"
        )
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| ordId | String | Yes | Order ID |
| protocolType | String | Yes | Protocol type `defi` defi : on-chain earn |

> Response Example

```highlight
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "ordId": "754147",
      "tag": ""
    }
  ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ordId | String | Order ID |
| tag | String | Order tag |

### GET / Active orders

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/finance/staking-defi/orders-active`

> Request Example

```highlight
GET /api/v5/finance/staking-defi/orders-active

```

```highlight
import okx.Finance.StakingDefi as StakingDefi

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading:0 , demo trading:1

StakingAPI = StakingDefi.StakingDefiAPI(apikey, secretkey, passphrase, False, flag)

result = StakingAPI.get_activity_orders()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| productId | String | No | Product ID |
| protocolType | String | No | Protocol type `defi` defi : on-chain earn |
| ccy | String | No | Investment currency, e.g. `BTC` BTC |
| state | String | No | Order state `8` 8 : Pending `13` 13 : Cancelling `9` 9 : Onchain `1` 1 : Earning `2` 2 : Redeeming |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "ordId": "2413499",
            "ccy": "DOT",
            "productId": "101",
            "state": "1",
            "protocol": "Polkadot",
            "protocolType": "defi",
            "term": "0",
            "apy": "0.1014",
            "investData": [
                {
                    "ccy": "DOT",
                    "amt": "2"
                }
            ],
            "earningData": [
                {
                    "ccy": "DOT",
                    "earningType": "0",
                    "earnings": "0.10615025"
                }
            ],
            "purchasedTime": "1729839328000",
            "tag": "",
            "estSettlementTime": "",
            "cancelRedemptionDeadline": "",
            "fastRedemptionData": []
        },
        {
            "ordId": "2213257",
            "ccy": "USDT",
            "productId": "4005",
            "state": "1",
            "protocol": "On-Chain Defi",
            "protocolType": "defi",
            "term": "0",
            "apy": "0.0323",
            "investData": [
                {
                    "ccy": "USDT",
                    "amt": "1"
                }
            ],
            "earningData": [
                {
                    "ccy": "USDT",
                    "earningType": "0",
                    "earnings": "0.02886582"
                },
                {
                    "ccy": "COMP",
                    "earningType": "1",
                    "earnings": "0.0000627"
                }
            ],
            "purchasedTime": "1725345790000",
            "tag": "",
            "estSettlementTime": "",
            "cancelRedemptionDeadline": "",
            "fastRedemptionData": []
        },
        {
            "ordId": "2210943",
            "ccy": "USDT",
            "productId": "4005",
            "state": "1",
            "protocol": "On-Chain Defi",
            "protocolType": "defi",
            "term": "0",
            "apy": "0.0323",
            "investData": [
                {
                    "ccy": "USDT",
                    "amt": "1"
                }
            ],
            "earningData": [
                {
                    "ccy": "USDT",
                    "earningType": "0",
                    "earnings": "0.02891823"
                },
                {
                    "ccy": "COMP",
                    "earningType": "1",
                    "earnings": "0.0000632"
                }
            ],
            "purchasedTime": "1725280801000",
            "tag": "",
            "estSettlementTime": "",
            "cancelRedemptionDeadline": "",
            "fastRedemptionData": []
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency, e.g. `BTC` BTC |
| ordId | String | Order ID |
| productId | String | Product ID |
| state | String | Order state `8` 8 : Pending `13` 13 : Cancelling `9` 9 : Onchain `1` 1 : Earning `2` 2 : Redeeming |
| protocol | String | Protocol |
| protocolType | String | Protocol type `defi` defi : on-chain earn |
| term | String | Protocol term It will return the days of fixed term and will return `0` 0 for flexible product |
| apy | String | Estimated APY If the estimated APY is 7% , this field is 0.07 Retain to 4 decimal places (truncated) |
| investData | Array of objects | Investment data |
| > ccy | String | Investment currency, e.g. `BTC` BTC |
| > amt | String | Invested amount |
| earningData | Array of objects | Earning data |
| > ccy | String | Earning currency, e.g. `BTC` BTC |
| > earningType | String | Earning type `0` 0 : Estimated earning `1` 1 : Cumulative earning |
| > earnings | String | Earning amount |
| fastRedemptionData | Array of objects | Fast redemption data |
| > ccy | String | Currency, e.g. `BTC` BTC |
| > redeemingAmt | String | Redeeming amount |
| purchasedTime | String | Order purchased time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| estSettlementTime | String | Estimated redemption settlement time |
| cancelRedemptionDeadline | String | Deadline for cancellation of redemption application |
| tag | String | Order tag |

### GET / Order history

#### Rate Limit: 3 requests per second

#### Rate limit rule: User ID

#### Permission: Read

#### HTTP Request

`GET /api/v5/finance/staking-defi/orders-history`

> Request Example

```highlight
GET /api/v5/finance/staking-defi/orders-history

```

```highlight
import okx.Finance.StakingDefi as StakingDefi

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "0"  # Production trading:0 , demo trading:1

StakingAPI = StakingDefi.StakingDefiAPI(apikey, secretkey, passphrase, False, flag)

result = StakingAPI.get_orders_history()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| productId | String | No | Product ID |
| protocolType | String | No | Protocol type `defi` defi : on-chain earn |
| ccy | String | No | Investment currency, e.g. `BTC` BTC |
| after | String | No | Pagination of data to return records earlier than the requested ID. The value passed is the corresponding `ordId` ordId |
| before | String | No | Pagination of data to return records newer than the requested ID. The value passed is the corresponding `ordId` ordId |
| limit | String | No | Number of results per request. The default is `100` 100 . The maximum is `100` 100 . |

> Response Example

```highlight
{
    "code": "0",
    "msg": "",
    "data": [
       {
            "ordId": "1579252",
            "ccy": "DOT",
            "productId": "101",
            "state": "3",
            "protocol": "Polkadot",
            "protocolType": "defi",
            "term": "0",
            "apy": "0.1704",
            "investData": [
                {
                    "ccy": "DOT",
                    "amt": "2"
                }
            ],
            "earningData": [
                {
                    "ccy": "DOT",
                    "earningType": "0",
                    "realizedEarnings": "0"
                }
            ],
            "purchasedTime": "1712908001000",
            "redeemedTime": "1712914294000",
            "tag": ""
       }
    ]
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| ccy | String | Currency, e.g. `BTC` BTC |
| ordId | String | Order ID |
| productId | String | Product ID |
| state | String | Order state `3` 3 : Completed (including canceled and redeemed) |
| protocol | String | Protocol |
| protocolType | String | Protocol type `defi` defi : on-chain earn |
| term | String | Protocol term It will return the days of fixed term and will return `0` 0 for flexible product |
| apy | String | Estimated APY If the estimated APY is 7% , this field is `0.07` 0.07 Retain to 4 decimal places (truncated) |
| investData | Array of objects | Investment data |
| > ccy | String | Investment currency, e.g. `BTC` BTC |
| > amt | String | Invested amount |
| earningData | Array of objects | Earning data |
| > ccy | String | Earning currency, e.g. `BTC` BTC |
| > earningType | String | Earning type `0` 0 : Estimated earning `1` 1 : Cumulative earning |
| > realizedEarnings | String | Cumulative earning of redeemed orders This field is just valid when the order is in redemption state |
| purchasedTime | String | Order purchased time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| redeemedTime | String | Order redeemed time, Unix timestamp format in milliseconds, e.g. `1597026383085` 1597026383085 |
| tag | String | Order tag |

# Status

## GET / Status

Get event status of system upgrade.

Planned system maintenance that may result in short interruption (lasting less than 5 seconds) or websocket disconnection (users can immediately reconnect) will not be announced. The maintenance will only be performed during times of low market volatility.

#### Rate Limit: 1 request per 5 seconds

#### HTTP Request

`GET /api/v5/system/status`

> Request Example

```highlight
GET /api/v5/system/status

GET /api/v5/system/status?state=canceled

```

```highlight
import okx.Status as Status

flag = "0"  # Production trading: 0, Demo trading: 1
statusAPI = Status.StatusAPI(
    domain="https://www.okx.com",
    flag=flag,
)

# Get event status of system upgrade
result = statusAPI.status()
print(result)

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| state | String | No | System maintenance status `scheduled` scheduled : waiting `ongoing` ongoing : processing `pre\_open` pre\_open : pre\_open `completed` completed : completed `canceled` canceled : canceled Generally, `pre\_open` pre\_open last about 10 minutes. There will be `pre\_open` pre\_open when the time of upgrade is too long. If this parameter is not filled, the data with status `scheduled` scheduled , `ongoing` ongoing and `pre\_open` pre\_open will be returned by default |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "begin": "1672823400000",
            "end": "1672823520000",
            "href": "",
            "preOpenBegin": "",
            "scheDesc": "",
            "serviceType": "8",
            "state": "completed",
            "maintType": "1",
            "env": "1",
            "system": "unified",
            "title": "Trading account system upgrade (in batches of accounts)"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| title | String | The title of system maintenance instructions |
| state | String | System maintenance status |
| begin | String | Begin time of system maintenance, Unix timestamp format in milliseconds, e.g. `1617788463867` 1617788463867 |
| end | String | Time of resuming trading totally. Unix timestamp format in milliseconds, e.g. `1617788463867` 1617788463867 . It is expected end time before `completed` completed , changed to actual end time after `completed` completed . |
| preOpenBegin | String | The time of pre\_open. Canceling orders, placing Post Only orders, and transferring funds to trading accounts are back after `preOpenBegin` preOpenBegin . |
| href | String | Hyperlink for system maintenance details, if there is no return value, the default value will be empty. e.g. "" |
| serviceType | String | Service type `0` 0 : WebSocket `5` 5 : Trading service `6` 6 : Block trading `7` 7 : Trading bot `8` 8 : Trading service (in batches of accounts) `9` 9 : Trading service (in batches of products) `10` 10 : Spread trading `11` 11 : Copy trading `99` 99 : Others (e.g. Suspend partial instruments) |
| system | String | System `unified` unified : Trading account |
| scheDesc | String | Rescheduled description, e.g. `Rescheduled from 2021-01-26T16:30:00.000Z` Rescheduled from 2021-01-26T16:30:00.000Z to `2021-01-28T16:30:00.000Z` 2021-01-28T16:30:00.000Z |
| maintType | String | Maintenance type `1` 1 : Scheduled maintenance `2` 2 : Unscheduled maintenance `3` 3 : System disruption |
| env | String | Environment `1` 1 : Production Trading `2` 2 : Demo Trading |

## WS / Status channel

Get the status of system maintenance and push when rescheduling and the system maintenance status and end time changes. First subscription: "Push the latest change data"; every time there is a state change, push the changed content.

Planned system maintenance that may result in short interruption (lasting less than 5 seconds) or websocket disconnection (users can immediately reconnect) will not be announced. The maintenance will only be performed during times of low market volatility.

#### URL Path

/ws/v5/public

> Request Example

```highlight
{
  "id": "1512",
  "op": "subscribe",
  "args": [
    {
      "channel": "status"
    }
  ]
}

```

```highlight
import asyncio
from okx.websocket.WsPublicAsync import WsPublicAsync

def callbackFunc(message):
    print(message)

async def main():
    ws = WsPublicAsync(url="wss://wspap.okx.com:8443/ws/v5/public")
    await ws.start()
    args = [{
        "channel": "status"
    }]

    await ws.subscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

    await ws.unsubscribe(args, callback=callbackFunc)
    await asyncio.sleep(10)

asyncio.run(main())

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message Provided by client. It will be returned in response message for identifying the corresponding request. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters. |
| op | String | Yes | `subscribe` subscribe `unsubscribe` unsubscribe |
| args | Array of objects | Yes | List of subscribed channels |
| > channel | String | Yes | Channel name `status` status |

> Successful Response Example

```highlight
{
  "id": "1512",
  "event": "subscribe",
  "arg": {
    "channel": "status"
  },
  "connId": "a4d3ae55"
}

```

> Failure Response Example

```highlight
{
  "id": "1512",
  "event": "error",
  "code": "60012",
  "msg": "Invalid request: {\"op\": \"subscribe\", \"argss\":[{ \"channel\" : \"statuss\"}]}",
  "connId": "a4d3ae55"
}

```

#### Response parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| id | String | No | Unique identifier of the message |
| event | String | Yes | `subscribe` subscribe `unsubscribe` unsubscribe `error` error |
| arg | Object | No | Subscribed channel |
| > channel | String | Yes | Channel name `status` status |
| code | String | No | Error code |
| msg | String | No | Error message |
| connId | String | Yes | WebSocket connection ID |

> Push Data Example

```highlight
{
    "arg": {
        "channel": "status"
    },
    "data": [
        {
            "begin": "1672823400000",
            "end": "1672825980000",
            "href": "",
            "preOpenBegin": "",
            "scheDesc": "",
            "serviceType": "0",
            "state": "completed",
            "system": "unified",
            "maintType": "1",
            "env": "1",
            "title": "Trading account WebSocket system upgrade",
            "ts": "1672826038470"
        }
    ]
}

```

#### Push data parameters

| Parameter | Type | Description |
| --- | --- | --- |
| arg | Object | Successfully subscribed channel |
| > channel | String | Channel name |
| data | Array of objects | Subscribed data |
| > title | String | The title of system maintenance instructions |
| > state | String | System maintenance status, `scheduled` scheduled : waiting; `ongoing` ongoing : processing; `pre\_open` pre\_open : pre\_open; `completed` completed : completed ; `canceled` canceled : canceled. Generally, `pre\_open` pre\_open last about 10 minutes. There will be `pre\_open` pre\_open when the time of upgrade is too long. |
| > begin | String | Start time of system maintenance, Unix timestamp format in milliseconds, e.g. `1617788463867` 1617788463867 |
| > end | String | Time of resuming trading totally. Unix timestamp format in milliseconds, e.g. `1617788463867` 1617788463867 . It is expected end time before `completed` completed , changed to actual end time after `completed` completed . |
| > preOpenBegin | String | The time of pre\_open. Canceling orders, placing Post Only orders, and transferring funds to trading accounts are back after `preOpenBegin` preOpenBegin . |
| > href | String | Hyperlink for system maintenance details, if there is no return value, the default value will be empty. e.g. “” |
| > serviceType | String | Service type, `0` 0 : WebSocket ; `5` 5 : Trading service; `6` 6 : Block trading; `7` 7 : Trading bot; `8` 8 : Trading service (in batches of accounts); `9` 9 : Trading service (in batches of products); `10` 10 : Spread trading; `11` 11 : Copy trading; `99` 99 : Others (e.g. Suspend partial instruments) |
| > system | String | System, `unified` unified : Trading account |
| > scheDesc | String | Rescheduled description, e.g. `Rescheduled from 2021-01-26T16:30:00.000Z to 2021-01-28T16:30:00.000Z` Rescheduled from 2021-01-26T16:30:00.000Z to 2021-01-28T16:30:00.000Z |
| > maintType | String | Maintenance type `1` 1 : Scheduled maintenance; `2` 2 : Unscheduled maintenance; `3` 3 : System disruption |
| > env | String | Environment. `1` 1 : Production Trading, `2` 2 : Demo Trading |
| > ts | String | Push time due to change event, Unix timestamp format in milliseconds, e.g. `1617788463867` 1617788463867 |

# Announcement

## GET / Announcements

Get announcements, the response is sorted by `pTime` with the most recent first. The sort will not be affected if the announcement is updated. Every page has 20 records

Authentication is optional for this endpoint.

It will be regarded as private endpoint and authentication is required if OK-ACCESS-KEY in HTTP header is delivered.  
It will be regarded as public endpoint and authentication isn't required if OK-ACCESS-KEY in HTTP header isn't delivered.

There are differences between public endpoint and private endpoint.   
For public endpoint, the response is restricted based on your request IP.  
For private endpoint, the response is restricted based on your country of residence.

#### Rate Limit: 5 requests per 2 seconds

#### Rate limit rule: User ID(Private) or IP(Public)

#### Permission: Read

#### HTTP Request

`GET /api/v5/support/announcements`

> Request Example

```highlight
GET /api/v5/support/announcements

```

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| annType | String | No | Announcement type. Delivering the `annType` annType from "GET / Announcement types" Returning all when it is not posted |
| page | String | No | Page for pagination. The default is 1 |

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "details": [
                {
                    "annType": "announcements-latest-announcements",
                    "pTime": "1726128000000",
                    "title": "OKX to delist KISHU margin trading pairs",
                    "url": "https://www.okx.com/help/okx-to-delist-kishu-margin-trading-pairs"
                },
                {
                    "annType": "announcements-latest-announcements",
                    "pTime": "1725967800000",
                    "title": "OKX completed MATIC token migration",
                    "url": "https://www.okx.com/help/okx-completed-matic-token-migration"
                }
            ],
            "totalPage": "90"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| totalPage | String | Total number of pages |
| details | Array of objects | List of announcements |
| > title | String | Announcement title |
| > annType | String | Announcement type |
| > pTime | String | Publish time. Unix timestamp format in milliseconds, e.g. 1597026383085 |
| > url | String | Announcement url |

## GET / Announcement types

Authentication is not required for this public endpoint.

Get announcements types

#### Rate Limit: 1 request per 2 seconds

#### Rate limit rule: IP

#### Permission: Read

#### HTTP Request

`GET /api/v5/support/announcement-types`

> Request Example

```highlight
GET /api/v5/support/announcement-types

```

#### Request Parameters

None

> Response Example

```highlight
{
    "code": "0",
    "data": [
        {
            "annType": "announcements-new-listings",
            "annTypeDesc": "New listings"
        },
        {
            "annType": "announcements-delistings",
            "annTypeDesc": "Delistings"
        }
    ],
    "msg": ""
}

```

#### Response Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| annType | String | Announcement type |
| annTypeDesc | String | Announcement type description |

# Error Code

Here is the REST API Error Code

## REST API

REST API Error Code is from 50000 to 59999.

### Public

Error Code from 50000 to 53999

#### General Class

| Error Code | HTTP Status Code | Error Message |
| --- | --- | --- |
| 0 | 200 |
| 1 | 200 | Operation failed. |
| 2 | 200 | Bulk operation partially succeeded. |
| 50000 | 400 | Body for POST request cannot be empty. |
| 50001 | 503 | Service temporarily unavailable. Please try again later. |
| 50002 | 400 | JSON syntax error |
| 50004 | 400 | API endpoint request timeout. (does not mean that the request was successful or failed, please check the request result). |
| 50005 | 410 | API endpoint is inactive or unavailable. |
| 50006 | 400 | Invalid Content-Type. Please use "application/JSON". |
| 50007 | 200 | User blocked. |
| 50008 | 200 | User doesn't exist. |
| 50009 | 200 | Account is frozen due to stop-out. |
| 50010 | 200 | User ID cannot be empty. |
| 50011 | 200 | Rate limit reached. Please refer to API documentation and throttle requests accordingly. |
| 50011 | 429 | Too Many Requests |
| 50012 | 200 | Account status invalid. Check account status |
| 50013 | 429 | Systems are busy. Please try again later. |
| 50014 | 400 | Parameter {param0} can not be empty. |
| 50015 | 400 | Either parameter {param0} or {param1} is required |
| 50016 | 400 | Parameter {param0} does not match parameter {param1} |
| 50017 | 200 | Position frozen and related operations restricted due to auto-deleveraging (ADL). Please try again later. |
| 50018 | 200 | Currency {param0} is frozen due to ADL. Operation restricted. |
| 50019 | 200 | Account frozen and related operations restricted due to auto-deleveraging (ADL). Please try again later. |
| 50020 | 200 | Position frozen and related operations restricted due to forced liquidation. Please try again later. |
| 50021 | 200 | Currency {param0} is frozen due to liquidation. Operation restricted. |
| 50022 | 200 | Account frozen and related operations restricted due to forced liquidation. Please try again later. |
| 50023 | 200 | Funding fees frozen and related operations are restricted. Please try again later. |
| 50024 | 200 | Parameter {param0} and {param1} can not exist at the same time. |
| 50025 | 200 | Parameter {param0} count exceeds the limit {param1}. |
| 50026 | 500 | System error. Try again later |
| 50027 | 200 | This account is restricted from trading. Please contact customer support for assistance. |
| 50028 | 200 | Unable to place the order. Please contact the customer service for details. |
| 50029 | 200 | Your account has triggered OKX risk control and is temporarily restricted from conducting transactions. Please check your email registered with OKX for contact from our customer support team. |
| 50030 | 200 | You don't have permission to use this API endpoint |
| 50032 | 200 | Your account has been set to prohibit transactions in this currency. Please confirm and try again |
| 50033 | 200 | Instrument blocked. Please verify trading this instrument is allowed under account settings and try again. |
| 50035 | 403 | This endpoint requires that APIKey must be bound to IP |
| 50036 | 200 | The expTime can't be earlier than the current system time. Please adjust the expTime and try again. |
| 50037 | 200 | Order expired. |
| 50038 | 200 | This feature is unavailable in demo trading |
| 50039 | 200 | Parameter "before" isn't supported for timestamp pagination |
| 50040 | 200 | Too frequent operations, please try again later |
| 50041 | 200 | Your user ID hasn’t been allowlisted. Please contact customer service for assistance. |
| 50042 | 200 | Repeated request |
| 50044 | 200 | Must select one broker type |
| 50045 | 200 | simPos should be empty because simulated positions cannot be counted when Position Builder is calculating under Spot-Derivatives risk offset mode |
| 50046 | 200 | This feature is temporarily unavailable while we make some improvements to it. Please try again later. |
| 50047 | 200 | {param0} has already settled. To check the relevant candlestick data, please use {param1} |
| 50048 | 200 | Switching risk unit may lead position risk increases and be forced liquidated. Please adjust position size, make sure margin is in a safe status. |
| 50049 | 200 | No information on the position tier. The current instrument doesn’t support margin trading. |
| 50050 | 200 | You’ve already activated options trading. Please don’t activate it again. |
| 50051 | 200 | Due to compliance restrictions in your country or region, you cannot use this feature. |
| 50052 | 200 | Due to local laws and regulations, you cannot trade with your chosen crypto. |
| 50053 | 200 | This feature is only available in demo trading. |
| 50055 | 200 | Reset unsuccessful. Assets can only be reset up to 5 times per day. |
| 50056 | 200 | You have pending orders or open positions with this currency. Please reset after canceling all the pending orders/closing all the open positions. |
| 50057 | 200 | Reset unsuccessful. Try again later. |
| 50058 | 200 | This crypto is not supported in an asset reset. |
| 50059 | 200 | Before you continue, you'll need to complete additional steps as required by your local regulators. Please visit the website or app for more details. |
| 50060 | 200 | For security and compliance purposes, please complete the identity verification process to continue using our services. |
| 50061 | 200 | You've reached the maximum order rate limit for this account. |
| 50062 | 200 | This feature is currently unavailable. |
| 50063 | 200 | You can't activate the credits as they might have expired or are already activated. |
| 50064 | 200 | The borrowing system is unavailable. Try again later. |
| 50067 | 200 | The API doesn't support cross site trading feature |
| 50069 | 200 | Margin ratio verification for this risk unit failed. |
| 50071 | 200 | {param} already exists e.g. clOrdId already exists |

#### API Class

| Error Code | HTTP Status Code | Error Message |
| --- | --- | --- |
| 50100 | 400 | API frozen, please contact customer service. |
| 50101 | 401 | APIKey does not match current environment. |
| 50102 | 401 | Timestamp request expired. |
| 50103 | 401 | Request header "OK-ACCESS-KEY" cannot be empty. |
| 50104 | 401 | Request header "OK-ACCESS-PASSPHRASE" cannot be empty. |
| 50105 | 401 | Request header "OK-ACCESS-PASSPHRASE" incorrect. |
| 50106 | 401 | Request header "OK-ACCESS-SIGN" cannot be empty. |
| 50107 | 401 | Request header "OK-ACCESS-TIMESTAMP" cannot be empty. |
| 50108 | 401 | Exchange ID does not exist. |
| 50109 | 401 | Exchange domain does not exist. |
| 50110 | 401 | Your IP {param0} is not included in your API key's IP whitelist. |
| 50111 | 401 | Invalid OK-ACCESS-KEY. |
| 50112 | 401 | Invalid OK-ACCESS-TIMESTAMP. |
| 50113 | 401 | Invalid signature. |
| 50114 | 401 | Invalid authorization. |
| 50115 | 405 | Invalid request method. |
| 50116 | 200 | Fast API is allowed to create only one API key |
| 50118 | 200 | To link the app using your API key, your broker needs to share their IP to be whitelisted |
| 50119 | 200 | API key doesn't exist |
| 50120 | 200 | This API key doesn't have permission to use this function |
| 50121 | 200 | You can't access our services through the IP address ({param0}) |
| 50122 | 200 | Order amount must exceed minimum amount |

#### Trade Class

| Error Code | HTTP Status code | Error Message |
| --- | --- | --- |
| 51000 | 400 | Parameter {param0} error |
| 51001 | 200 | Instrument ID or Spread ID doesn't exist. |
| 51002 | 200 | Instrument ID doesn't match underlying index. |
| 51003 | 200 | Either client order ID or order ID is required. |
| 51004 | 200 | Order failed. For isolated long/short mode of {param0}, the sum of current order size, position quantity in the same direction, and pending orders in the same direction can’t be more than {param1}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param2}×, current order size: {param3} contracts, position quantity in the same direction: {param4} contracts, pending orders in the same direction: {param5} contracts). |
| 51004 | 200 | Order failed. For cross long/short mode of {param0}, the sum of current order size, position quantity in the long and short directions, and pending orders in the long and short directions can’t be more than {param1}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param2}×, current order size: {param3} contracts, position quantity in the long and short directions: {param4} contracts, pending orders in the long and short directions: {param5} contracts). |
| 51004 | 200 | Order failed. For cross buy/sell mode of {param0} and instFamily {param1}, the sum of current order size, current instId position quantity in the long and short directions, current instId pending orders in the long and short directions, and other contracts of the same instFamily can’t be more than {param2}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param3}×, current order size: {param4} contracts, current instId position quantity in the long and short directions: {param5} contracts, current instId pending orders in the long and short directions: {param6} contracts, other contracts of the same instFamily: {param7} contracts). |
| 51004 | 200 | Order failed. For buy/sell mode of {param0}, the sum of current buy order size, position quantity, and pending buy orders can’t be more than {param1}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param2}×, current buy order size: {param3} contracts, position quantity: {param4} contracts, pending buy orders: {param5} contracts). |
| 51004 | 200 | Order failed. For buy/sell mode of {param0}, the sum of current sell order size, position quantity, and pending sell orders can’t be more than {param1}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param2}×, current sell order size: {param3} contracts, position quantity: {param4} contracts, pending sell orders: {param5} contracts). |
| 51004 | 200 | Order failed. For cross buy/sell mode of {param0} and instFamily {param1}, the sum of current buy order size, current instId position quantity, current instId pending buy orders, and other contracts of the same instFamily can’t be more than {param2}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param3}×, current buy order size: {param4} contracts, current instId position quantity: {param5} contracts, current instId pending buy orders: {param6} contracts, other contracts of the same instFamily: {param7} contracts). |
| 51004 | 200 | Order failed. For cross buy/sell mode of {param0} and instFamily {param1}, the sum of current sell order size, current instId position quantity, current instId pending sell orders, and other contracts of the same instFamily can’t be more than {param2}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param3}×, current sell order size: {param4} contracts, current instId position quantity: {param5} contracts, current instId pending sell orders: {param6} contracts, other contracts of the same instFamily: {param7} contracts). |
| 51004 | 200 | Order amendment failed. For isolated long/short mode of {param0}, the sum of increment order size by amendment, position quantity in the same direction, and pending orders in the same direction can’t be more than {param1}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param2}×, increment order size by amendment: {param3} contracts, position quantity in the same direction: {param4} contracts, pending orders in the same direction: {param5} contracts). |
| 51004 | 200 | Order amendment failed. For cross long/short mode of {param0}, the sum of increment order size by amendment, position quantity in the long and short directions, and pending orders in the long and short directions can’t be more than {param1}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param2}×, increment order size by amendment: {param3} contracts, position quantity in the long and short directions: {param4} contracts, pending orders in the same direction: {param5} contracts). |
| 51004 | 200 | Order amendment failed. For cross buy/sell mode of {param0} and instFamily {param1}, the sum of increment order size by amendment, current instId position quantity in the long and short directions, current instId pending orders in the long and short directions, and other contracts of the same instFamily can’t be more than {param2}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param3}×, increment order size by amendment: {param4} contracts, current instId position quantity in the long and short directions: {param5} contracts, current instId pending orders in the long and short directions: {param6} contracts, other contracts of the same instFamily: {param7} contracts). |
| 51004 | 200 | Order amendment failed. For buy/sell mode of {param0}, the sum of increment order size by amending current buy order, position quantity, and pending buy orders can’t be more than {param1}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param2}×, increment order size by amending current buy order: {param3} contracts, position quantity: {param4} contracts, pending buy orders: {param5} contracts). |
| 51004 | 200 | Order amendment failed. For buy/sell mode of {param0}, the sum of increment order size by amending current sell order, position quantity, and pending sell orders can’t be more than {param1}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param2}×, increment order size by amending current sell order: {param3} contracts, position quantity: {param4} contracts, pending sell orders: {param5} contracts). |
| 51004 | 200 | Order amendment failed. For cross buy/sell mode of {param0} and instFamily {param1}, the sum of increment order size by amending current buy order, current instId position quantity, current instId pending buy orders, and other contracts of the same instFamily can’t be more than {param2}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param3}×, increment order size by amending current buy order: {param4} contracts, current instId position quantity: {param5} contracts, current instId pending buy orders: {param6} contracts, other contracts of the same instFamily: {param7} contracts). |
| 51004 | 200 | Order amendment failed. For cross buy/sell mode of {param0} and instFamily {param1}, the sum of increment order size by amending current sell order, current instId position quantity, current instId pending sell orders, and other contracts of the same instFamily can’t be more than {param2}(contracts) which is the maximum position amount under current leverage. Please lower the leverage or use a new sub-account to place the order again (current leverage: {param3}×, increment order size by amending current sell order: {param4} contracts, current instId position quantity: {param5} contracts, current instId pending sell orders: {param6} contracts, other contracts of the same instFamily: {param7} contracts). |
| 51005 | 200 | Your order amount exceeds the max order amount. |
| 51006 | 200 | Order price is not within the price limit (max buy price: {param0} , min sell price: {param1} ) |
| 51007 | 200 | Order failed. Please place orders of at least 1 contract or more. |
| 51008 | 200 | Order failed. Insufficient {param0} balance in account |
| 51008 | 200 | Order failed. Insufficient {param0} margin in account |
| 51008 | 200 | Order failed. Insufficient {param0} balance in account, and Auto Borrow is not enabled |
| 51008 | 200 | Order failed. Insufficient {param0} margin in account and auto-borrow is not enabled (Portfolio margin mode can try IOC orders to lower the risks) |
| 51008 | 200 | Insufficient {param0} available as your borrowing amount exceeds tier limit. Lower leverage appropriately. New and pending limit orders need borrowings {param1}, remaining quota {param2}, total limit {param3}, in use {param4}. |
| 51008 | 200 | Order failed. Exceeds {param0} borrow limit (Limit of master account plus the allocated VIP quota for the current account) (Existing pending orders and the new order are required to borrow {param1}, Remaining limit {param2}, Limit {param3}, Limit used {param4}) |
| 51008 | 200 | Order failed. Insufficient {param0} borrowing quota results in an insufficient amount available to borrow. |
| 51008 | 200 | Order failed. Insufficient {param0} available in loan pool to borrow. |
| 51008 | 200 | Order failed. Insufficient account balance, and the adjusted equity in `USD` USD is less than IMR (Portfolio margin mode can try IOC orders to lower the risks) |
| 51008 | 200 | Order failed. The order didn't pass delta verification because if the order were to succeed, the change in adjEq would be smaller than the change in IMR. Increase adjEq or reduce IMR (Portfolio margin mode can try IOC orders to lower the risks) |
| 51009 | 200 | Order blocked. Please contact customer support for assistance. |
| 51010 | 200 | Request unsupported under current account mode |
| 51011 | 200 | Order ID already exists. |
| 51012 | 200 | Token doesn't exist. |
| 51014 | 200 | Index doesn't exist. |
| 51015 | 200 | Instrument ID doesn't match instrument type. |
| 51016 | 200 | Client order ID already exists. |
| 51017 | 200 | Loan amount exceeds borrowing limit. |
| 51018 | 200 | Users with options accounts cannot hold net short positions. |
| 51019 | 200 | No net long positions can be held under cross margin mode in options. |
| 51020 | 200 | Your order should meet or exceed the minimum order amount. |
| 51021 | 200 | The pair or contract is not yet listed |
| 51022 | 200 | Contract suspended. |
| 51023 | 200 | Position doesn't exist. |
| 51024 | 200 | Trading account is blocked. |
| 51024 | 200 | In accordance with the terms of service, we regret to inform you that we cannot provide services for you. If you have any questions, please contact our customer support. |
| 51024 | 200 | According to your request, this account has been frozen. If you have any questions, please contact our customer support. |
| 51024 | 200 | Your account has recently changed some security settings. To protect the security of your funds, this action is not allowed for now. If you have any questions, please contact our customer support. |
| 51024 | 200 | You have withdrawn all assets in the account. To protect your personal information, the account has been permanently frozen. If you have any questions, please contact our customer support. |
| 51024 | 200 | Your identity could not be verified. To protect the security of your funds, this action is not allowed. Please contact our customer support. |
| 51024 | 200 | Your verified age doesn't meet the requirement. To protect the security of your funds, we cannot proceed with your request. Please contact our customer support. |
| 51024 | 200 | In accordance with the terms of service, trading is currently unavailable in your verified country or region. Close all open positions or contact customer support if you have any questions. |
| 51024 | 200 | In accordance with the terms of service, multiple account is not allowed. To protect the security of your funds, this action is not allowed. Please contact our customer support. |
| 51024 | 200 | Your account is in judicial freezing, and this action is not allowed for now. If you have any questions, please contact our customer support. |
| 51024 | 200 | Based on your previous requests, this action is not allowed for now. If you have any questions, please contact our customer support. |
| 51024 | 200 | Your account has disputed deposit orders. To protect the security of your funds, this action is not allowed for now. Please contact our customer support. |
| 51024 | 200 | Unable to proceed. Please resolve your existing P2P disputes first. |
| 51024 | 200 | Your account might have compliance risk. To protect the security of your funds, this action is not allowed for now. Please contact our customer support. |
| 51024 | 200 | Based on your trading requests, this action is not allowed for now. If you have any questions, please contact our customer support. |
| 51024 | 200 | Your account has triggered risk control. This action is not allowed for now. Please contact our customer support. |
| 51024 | 200 | This account is temporarily unavailable. Please contact our customer support. |
| 51024 | 200 | Withdrawal function of this account is temporarily unavailable. Please contact our customer support. |
| 51024 | 200 | Transfer function of this account is temporarily unavailable. Please contact our customer support. |
| 51024 | 200 | You violated the "Fiat Trading Rules" when you were doing fiat trade, so we'll no longer provide fiat trading-related services for you. The deposit and withdrawal of your account and other trading functions will not be affected. |
| 51024 | 200 | Please kindly check your mailbox and reply to emails from the verification team. |
| 51024 | 200 | According to your request, this account has been closed. If you have any questions, please contact our customer support. |
| 51024 | 200 | Your account might have security risk. To protect the security of your funds, this action is not allowed for now. Please contact our customer support. |
| 51024 | 200 | Your account might have security risk. Convert is now unavailable. Please contact our customer support. |
| 51024 | 200 | Unable to proceed due to account restrictions. We've sent an email to your OKX registered email address regarding this matter, or you can contact customer support via Chat with AI chatbot on our support center page. |
| 51024 | 200 | In accordance with the terms of service, trading is currently unavailable in your verified country or region. Cancel all orders or contact customer support if you have any questions. |
| 51024 | 200 | In accordance with the terms of service, trading is not available in your verified country. If you have any questions, please contact our customer support. |
| 51024 | 200 | This product isn’t available in your country or region due to local laws and regulations. If you don’t reside in this area, you may continue using OKX Exchange products with a valid government-issued ID. |
| 51024 | 200 | Please note that you may not be able to transfer or trade in the first 30 minutes after establishing custody trading sub-accounts. Please kindly wait and try again later. |
| 51024 | 200 | Feature unavailable. Complete Advanced verification to access this feature. |
| 51024 | 200 | You can't trade or deposit now. Update your personal info to restore full account access immediately. |
| 51024 | 200 | Sub-accounts exceeding the limit aren't allowed to open new positions and can only reduce or close existing ones. Please try again with a different account. |
| 51025 | 200 | Order count exceeds the limit. |
| 51026 | 200 | Instrument type doesn't match underlying index. |
| 51027 | 200 | Contract expired. |
| 51028 | 200 | Contract under delivery. |
| 51029 | 200 | Contract is being settled. |
| 51030 | 200 | Funding fee is being settled. |
| 51031 | 200 | This order price is not within the closing price range. |
| 51032 | 200 | Closing all the positions at the market price. |
| 51033 | 200 | The total amount per order for this pair has reached the upper limit. |
| 51034 | 200 | Fill rate exceeds the limit that you've set. Please reset the market maker protection to inactive for new trades. |
| 51035 | 200 | This account doesn't have permission to submit MM quote order. |
| 51036 | 200 | Only options instrument of the PM account supports MMP orders. |
| 51042 | 200 | Under the Portfolio margin account, users can only place market maker protection orders in cross margin mode in Options. |
| 51043 | 200 | This isolated position doesn't exist. |
| 59509 | 200 | Account does not have permission to reset MMP status |
| 51037 | 200 | This account only supports placing IOC orders to reduce account risk. |
| 51038 | 200 | IOC order already exists under the current risk module. |
| 51039 | 200 | Leverage cannot be adjusted for the cross positions of Expiry Futures and Perpetual Futures under the PM account. |
| 51040 | 200 | Cannot adjust margins for long isolated options positions |
| 51041 | 200 | Portfolio margin account only supports the Buy/Sell mode. |
| 51044 | 200 | The order type {param0}, {param1} is not allowed to set stop loss and take profit |
| 51046 | 200 | The take profit trigger price must be higher than the order price |
| 51047 | 200 | The stop loss trigger price must be lower than the order price |
| 51048 | 200 | The take profit trigger price must be lower than the order price |
| 51049 | 200 | The stop loss trigger price must be higher than the order price |
| 51050 | 200 | The take profit trigger price must be higher than the best ask price |
| 51051 | 200 | The stop loss trigger price must be lower than the best ask price |
| 51052 | 200 | The take profit trigger price must be lower than the best bid price |
| 51053 | 200 | The stop loss trigger price must be higher than the best bid price |
| 51054 | 500 | Request timed out. Please try again. |
| 51055 | 200 | Futures Grid is not available in Portfolio Margin mode |
| 51056 | 200 | Action not allowed |
| 51057 | 200 | This bot isn’t available in current account mode. Switch mode in Settings > Account mode to continue. |
| 51058 | 200 | No available position for this algo order |
| 51059 | 200 | Strategy for the current state does not support this operation |
| 51063 | 200 | OrdId does not exist |
| 51065 | 200 | algoClOrdId already exists. |
| 51066 | 200 | Market orders unavailable for options trading. Place a limit order to close position. |
| 51068 | 200 | {param0} already exists within algoClOrdId and attachAlgoClOrdId. |
| 51069 | 200 | The option contracts related to current {param0} do not exist |
| 51070 | 200 | You do not meet the requirements for switching to this account mode. Please upgrade the account mode on the OKX website or App |
| 51071 | 200 | You've reached the maximum limit for tag level cancel all after timers. |
| 51072 | 200 | As a spot lead trader, you need to set tdMode to spot\_isolated when buying the configured lead trade pairs. |
| 51073 | 200 | As a spot lead trader, you need to use '/copytrading/close-subposition' for selling assets through lead trades |
| 51074 | 200 | Only the tdMode for lead trade pairs configured by spot lead traders can be set to 'spot\_isolated' |
| 51075 | 200 | Order modification failed. You can only modify the price of sell orders in spot copy trading. |
| 51076 | 200 | TP/SL orders in Split TPs only support one-way TP/SL. You can't use slTriggerPx&slOrdPx and tpTriggerPx&tpOrdPx at the same time. |
| 51077 | 200 | Setting multiple TP and cost-price SL orders isn’t supported for spot and margin trading. |
| 51078 | 200 | You are a lead trader. Split TPs are not supported. |
| 51079 | 200 | The number of TP orders with Split TPs attached in a same order cannot exceed {param0} |
| 51080 | 200 | Take-profit trigger price types (tpTriggerPxType) must be the same in an order with Split TPs attached |
| 51081 | 200 | Take-profit trigger prices (tpTriggerPx) cannot be the same in an order with Split TPs attached |
| 51082 | 200 | TP trigger prices (tpOrdPx) in one order with multiple TPs must be market prices. |
| 51083 | 200 | The total size of TP orders with Split TPs attached in a same order should equal the size of this order |
| 51084 | 200 | The number of SL orders with Split TPs attached in a same order cannot exceed {param0} |
| 51085 | 200 | The number of TP orders cannot be less than 2 when cost-price SL is enabled (amendPxOnTriggerType set as 1) for Split TPs |
| 51086 | 200 | The number of orders with Split TPs attached in a same order cannot exceed {param0} |
| 51538 | 200 | You need to use attachAlgoOrds if you used attachAlgoOrds when placing an order. attachAlgoOrds is not supported if you did not use attachAlgoOrds when placing this order. |
| 51539 | 200 | attachAlgoId or attachAlgoClOrdId cannot be identical when modifying any TP/SL within your split TPs order |
| 51527 | 200 | Order modification failed. At least 1 of the attached TP/SL orders does not exist. |
| 51087 | 200 | Listing canceled for this crypto |
| 51088 | 200 | You can only place 1 TP/SL order to close an entire position |
| 51089 | 200 | The size of the TP order among split TPs attached cannot be empty |
| 51090 | 200 | You can't modify the amount of an SL order placed with a TP limit order. |
| 51091 | 200 | All TP orders in one order must be of the same type. |
| 51092 | 200 | TP order prices (tpOrdPx) in one order must be different. |
| 51093 | 200 | TP limit order prices (tpOrdPx) in one order can't be –1 (market price). |
| 51094 | 200 | You can't place TP limit orders in spot, margin, or options trading. |
| 51095 | 200 | To place TP limit orders at this endpoint, you must place an SL order at the same time. |
| 51096 | 200 | cxlOnClosePos needs to be true to place a TP limit order |
| 51098 | 200 | You can't add a new TP order to an SL order placed with a TP limit order. |
| 51099 | 200 | You can't place TP limit orders as a lead trader. |
| 51178 | 200 | tpTriggerPx&tpOrdPx or slTriggerPx&slOrdPx can't be empty when using attachAlgoClOrdId. |
| 51100 | 200 | Unable to place order. Take profit/Stop loss conditions cannot be added to reduce-only orders. |
| 51101 | 200 | Order failed, the sz of the current order can’t be more than {param0} (contracts). |
| 51102 | 200 | Order failed, the number of pending orders for this instId can’t be more than {param0} (orders) |
| 51103 | 200 | Order failed, the number of pending orders across all instIds under the {param0} current instFamily can’t be more than {param1} (orders) |
| 51104 | 200 | Order failed, the aggregated contract quantity for all pending orders across all instIds under the {param0} current instFamily can’t be more than {param1} (contracts) |
| 51105 | 200 | Order failed, the maximal sum of position quantity and pending orders quantity with the same direction for current instId can’t be more than {param0} (contracts) |
| 51106 | 200 | Order failed, the maximal sum of position quantity and pending orders quantity with the same direction across all instIds under the {param0} current instFamily can’t be more than {param1} (contracts) |
| 51107 | 200 | Order failed, the maximal sum of position quantity and pending orders quantity in both directions across all instIds under the {param0} current instFamily can’t be more than {param1} (contracts) |
| 51108 | 200 | Positions exceed the limit for closing out with the market price. |
| 51109 | 200 | No available offers. |
| 51110 | 200 | You can only place a limit order after Call Auction has started. |
| 51111 | 200 | Maximum {param0} orders can be placed in bulk. |
| 51112 | 200 | Close order size exceeds available size for this position. |
| 51113 | 429 | Market-price liquidation requests too frequent. |
| 51115 | 429 | Cancel all pending close-orders before liquidation. |
| 51116 | 200 | Order price or trigger price exceeds {param0}. |
| 51117 | 200 | Pending close-orders count exceeds limit. |
| 51120 | 200 | Order amount is less than {param0}, please try again. |
| 51121 | 200 | Order quantity must be a multiple of the lot size. |
| 51122 | 200 | Order price should higher than the min price {param0} |
| 51123 | 200 | Min price increment is null. |
| 51124 | 200 | You can only place limit orders during call auction. |
| 51125 | 200 | Currently there are pending reduce + reverse position orders in margin trading. Please cancel all pending reduce + reverse position orders and continue. |
| 51126 | 200 | Currently there are pending reduce only orders in margin trading. Please cancel all pending reduce only orders and continue. |
| 51127 | 200 | Available balance is 0. |
| 51128 | 200 | Multi-currency margin accounts cannot do cross-margin trading. |
| 51129 | 200 | The value of the position and buy order has reached the position limit. No further buying is allowed. |
| 51130 | 200 | Fixed margin currency error. |
| 51131 | 200 | Insufficient balance. |
| 51132 | 200 | Your position amount is negative and less than the minimum trading amount. |
| 51133 | 200 | Reduce-only feature is unavailable for spot transactions in multi-currency margin accounts. |
| 51134 | 200 | Closing failed. Please check your margin holdings and pending orders. Turn off the Reduce-only to continue. |
| 51135 | 200 | Your closing price has triggered the limit price, and the max buy price is {param0}. |
| 51136 | 200 | Your closing price has triggered the limit price, and the min sell price is {param0}. |
| 51137 | 200 | The highest price limit for buy orders is {param0}. |
| 51138 | 200 | The lowest price limit for sell orders is {param0}. |
| 51139 | 200 | Reduce-only feature is unavailable for the spot transactions by spot mode. |
| 51140 | 200 | Purchase failed due to insufficient sell orders, please try later. |
| 51142 | 200 | There is no valid quotation in the market, and the order cannot be filled in USDT mode, please try to switch to currency mode |
| 51143 | 200 | Insufficient conversion amount |
| 51144 | 200 | Please use {param0} for closing. |
| 51147 | 200 | To trade options, make sure you have more than 10,000 USD worth of assets in your trading account first, then activate options trading |
| 51148 | 200 | Failed to place order. The new order may execute an opposite trading direction of your existing reduce-only positions. Cancel or edit pending orders to continue order |
| 51149 | 500 | Order timed out. Please try again. |
| 51150 | 200 | The precision of the number of trades or the price exceeds the limit. |
| 51152 | 200 | Unable to place an order that mixes automatic buy with automatic repayment or manual operation in Quick margin mode. |
| 51153 | 200 | Unable to borrow manually in Quick margin mode. The amount you entered exceeds the upper limit. |
| 51154 | 200 | Unable to repay manually in Quick margin mode. The amount you entered exceeds your available balance. |
| 51155 | 200 | Trading of this pair or contract is restricted due to local compliance requirements. |
| 51158 | 200 | Manual transfer unavailable. To proceed, please switch to Quick margin mode (isoMode = quick\_margin) |
| 51164 | 200 | As lead trader, you can't switch to portfolio margin mode. |
| 51169 | 200 | Order failed because you don't have any positions in this direction for this contract to reduce or close. |
| 51170 | 200 | Failed to place order. A reduce-only order can’t be the same trading direction as your existing positions. |
| 51171 | 200 | Failed to edit order. The edited order may execute an opposite trading direction of your existing reduce-only positions. Cancel or edit pending orders to continue. |
| 51173 | 200 | Unable to close all at market price. Your current positions don't have any liabilities. |
| 51174 | 200 | Order failed, number of pending orders for {param0} exceed the limit of {param1}. |
| 51175 | 200 | Parameters {param0} {param1} and {param2} cannot be empty at the same time |
| 51176 | 200 | Only one parameter can be filled among Parameters {param0} {param1} and {param2} |
| 51177 | 200 | Unavailable to amend {param1} because the price type of the current options order is {param0} |
| 51179 | 200 | Unavailable to place options orders using {param0} in simple mode |
| 51180 | 200 | The range of {param0} should be ({param1}~{param2}) |
| 51181 | 200 | ordType must be limit while placing {param0} orders |
| 51182 | 200 | The total number of pending orders under price types pxUsd and pxVol for the current account cannot exceed {param0} |
| 51185 | 200 | The maximum value allowed per order is {maxOrderValue} USD |
| 51186 | 200 | Order failed. The leverage for {param0} in your current margin mode is {param1}x, which exceeds the platform limit of {param2}x. |
| 51187 | 200 | Order failed. For {param0} {param1} in your current margin mode, the sum of your current order amount, position sizes, and open orders is {param2} contracts, which exceeds the platform limit of {param3} contracts. Reduce your order amount, cancel orders, or close positions. |
| 51192 | 200 | The {param0} price corresponding to the IV level you entered is lower than the minimum allowed selling price of {param1} {param2}. Enter a higher IV level. |
| 51193 | 200 | The {param0} price corresponding to the IV level you entered is higher than the maximum allowed buying price of {param1} {param2}. Enter a lower IV level. |
| 51194 | 200 | The {param0} price corresponding to the USD price you entered is lower than the minimum allowed selling price of {param1} {param2}. Enter a higher USD price. |
| 51195 | 200 | The {param0} price corresponding to the USD price you entered is higher than the maximum allowed buying price of {param1} {param2}. Enter a lower USD price. |
| 51196 | 200 | You can only place limit orders during the pre-quote phase. |
| 51197 | 200 | You can only place limit orders after the pre-quote phase begins. |
| 51201 | 200 | The value of a market order can't exceed {param0}. |
| 51202 | 200 | Market order amount exceeds the maximum amount. |
| 51203 | 200 | Order amount exceeds the limit {param0}. |
| 51204 | 200 | The price for the limit order cannot be empty. |
| 51205 | 200 | Reduce Only is not available. |
| 51206 | 200 | Please cancel the Reduce Only order before placing the current {param0} order to avoid opening a reverse position. |
| 51207 | 200 | Trading amount exceeds the limit, and can't be all closed at the market price. You can try closing the position manually in batches. |
| 51220 | 200 | Lead and follow bots only support “Sell” or “Close all positions” when bot stops |
| 51221 | 200 | The profit-sharing ratio must be between 0% and 30% |
| 51222 | 200 | Profit sharing isn’t supported for this type of bot |
| 51223 | 200 | Only lead bot creators can set profit-sharing ratio |
| 51224 | 200 | Profit sharing isn’t supported for this crypto pair |
| 51225 | 200 | Instant trigger isn’t available for follow bots |
| 51226 | 200 | Editing parameters isn’t available for follow bots |
| 51250 | 200 | Algo order price is out of the available range. |
| 51251 | 200 | Bot order type error occurred when placing iceberg order |
| 51252 | 200 | Algo order amount is out of the available range. |
| 51253 | 200 | Average amount exceeds the limit of per iceberg order. |
| 51254 | 200 | Iceberg average amount error occurred. |
| 51255 | 200 | Limit of per iceberg order: Total amount/1000 < x <= Total amount. |
| 51256 | 200 | Iceberg order price variance error. |
| 51257 | 200 | Trailing stop order callback rate error. The callback rate should be {min}< x<={max}%. |
| 51258 | 200 | Trailing stop order placement failed. The trigger price of a sell order must be higher than the last transaction price. |
| 51259 | 200 | Trailing stop order placement failed. The trigger price of a buy order must be lower than the last transaction price. |
| 51260 | 200 | Maximum of {param0} pending trailing stop orders can be held at the same time. |
| 51261 | 200 | Each user can hold up to {param0} pending stop orders at the same time. |
| 51262 | 200 | Maximum {param0} pending iceberg orders can be held at the same time. |
| 51263 | 200 | Maximum {param0} pending time-weighted orders can be held at the same time. |
| 51264 | 200 | Average amount exceeds the limit of per time-weighted order. |
| 51265 | 200 | Time-weighted order limit error. |
| 51267 | 200 | Time-weighted order strategy initiative rate error. |
| 51268 | 200 | Time-weighted order strategy initiative range error. |
| 51269 | 200 | Time-weighted order interval error. Interval must be {%min}<= x<={%max}. |
| 51270 | 200 | The limit of time-weighted order price variance is 0 < x <= 1%. |
| 51271 | 200 | Sweep ratio must be 0 < x <= 100%. |
| 51272 | 200 | Price variance must be 0 < x <= 1%. |
| 51273 | 200 | Total amount must be greater than {param0}. |
| 51274 | 200 | Total quantity of time-weighted order must be larger than single order limit. |
| 51275 | 200 | The amount of single stop-market order cannot exceed the upper limit. |
| 51276 | 200 | Prices cannot be specified for stop market orders. |
| 51277 | 200 | TP trigger price cannot be higher than the last price. |
| 51278 | 200 | SL trigger price cannot be lower than the last price. |
| 51279 | 200 | TP trigger price cannot be lower than the last price. |
| 51280 | 200 | SL trigger price cannot be higher than the last price. |
| 51281 | 200 | Trigger order do not support the tgtCcy parameter. |
| 51282 | 200 | The range of Price variance is {param0}~{param1} |
| 51283 | 200 | The range of Time interval is {param0}~{param1} |
| 51284 | 200 | The range of Average amount is {param0}~{param1} |
| 51285 | 200 | The range of Total amount is {param0}~{param1} |
| 51286 | 200 | The total amount should not be less than {param0} |
| 51287 | 200 | This bot doesn't support current instrument |
| 51288 | 200 | Bot is currently stopping. Do not make multiple attempts to stop. |
| 51289 | 200 | Bot configuration does not exist. Please try again later |
| 51290 | 200 | The Bot engine is being upgraded. Please try again later |
| 51291 | 200 | This Bot does not exist or has been stopped |
| 51292 | 200 | This Bot type does not exist |
| 51293 | 200 | This Bot does not exist |
| 51294 | 200 | This Bot cannot be created temporarily. Please try again later |
| 51295 | 200 | Portfolio margin account does not support ordType {param0} in Trading bot mode |
| 51298 | 200 | Trigger orders are not available in the net mode of Expiry Futures and Perpetual Futures |
| 51299 | 200 | Order did not go through. You can hold a maximum of {param0} orders of this type. |
| 51300 | 200 | TP trigger price cannot be higher than the mark price |
| 51302 | 200 | SL trigger price cannot be lower than the mark price |
| 51303 | 200 | TP trigger price cannot be lower than the mark price |
| 51304 | 200 | SL trigger price cannot be higher than the mark price |
| 51305 | 200 | TP trigger price cannot be higher than the index price |
| 51306 | 200 | SL trigger price cannot be lower than the index price |
| 51307 | 200 | TP trigger price cannot be lower than the index price |
| 51308 | 200 | SL trigger price cannot be higher than the index price |
| 51309 | 200 | Cannot create trading bot during call auction |
| 51310 | 200 | Strategic orders with Iceberg and TWAP order type are not supported when margins are self-transferred in isolated mode. |
| 51311 | 200 | Failed to place trailing stop order. Callback rate should be within {min}<x<={max} |
| 51312 | 200 | Failed to place trailing stop order. Order amount should be within {min}<x<={max} |
| 51313 | 200 | Manual transfer in isolated mode does not support bot trading |
| 51317 | 200 | Trigger orders are not available by margin |
| 51327 | 200 | closeFraction is only available for Expiry Futures and Perpetual Futures |
| 51328 | 200 | closeFraction is only available for reduceOnly orders |
| 51329 | 200 | closeFraction is only available in NET mode |
| 51330 | 200 | closeFraction is only available for stop market orders |
| 51331 | 200 | closeFraction is only available for close position orders |
| 51332 | 200 | closeFraction is not applicable to Portfolio Margin |
| 51333 | 200 | Close position order in hedge-mode or reduce-only order in one-way mode cannot attach TPSL |
| 51340 | 200 | Used margin must be greater than {0}{1} |
| 51341 | 200 | Position closing not allowed |
| 51342 | 200 | Closing order already exists. Please try again later |
| 51343 | 200 | TP price must be less than the lower price |
| 51344 | 200 | SL price must be greater than the upper price |
| 51345 | 200 | Policy type is not grid policy |
| 51346 | 200 | The highest price cannot be lower than the lowest price |
| 51347 | 200 | No profit available |
| 51348 | 200 | Stop loss price must be less than the lower price in the range. |
| 51349 | 200 | Take profit price must be greater than the highest price in the range. |
| 51350 | 200 | No recommended parameters |
| 51351 | 200 | Single income must be greater than 0 |
| 51352 | 200 | You can have {0} to {1} trading pairs |
| 51353 | 200 | Trading pair {0} already exists |
| 51354 | 200 | The percentages of all trading pairs should add up to 100% |
| 51355 | 200 | Select a date within {0} - {1} |
| 51356 | 200 | Select a time within {0} - {1} |
| 51357 | 200 | Select a time zone within {0} - {1} |
| 51358 | 200 | The investment amount of each crypto must be greater than {amount} |
| 51359 | 200 | Recurring buy not supported for the selected crypto {0} |
| 51370 | 200 | The range of lever is {0}~{1} |
| 51380 | 200 | Market conditions do not meet the strategy running configuration. You can try again later or adjust your tp/sl configuration. |
| 51381 | 200 | Per grid profit ratio must be larger than 0.1% and less or equal to 10% |
| 51382 | 200 | Stop triggerAction is not supported by the current strategy |
| 51383 | 200 | The min\_price is lower than the last price |
| 51384 | 200 | The trigger price must be greater than the min price |
| 51385 | 200 | The take profit price needs to be greater than the min price |
| 51386 | 200 | The min price needs to be greater than 1/2 of the last price |
| 51387 | 200 | Stop loss price must be less than the bottom price |
| 51388 | 200 | This Bot is in running status |
| 51389 | 200 | Trigger price should be lower than {0} |
| 51390 | 200 | Trigger price should be lower than the TP price |
| 51391 | 200 | Trigger price should be higher than the SL price |
| 51392 | 200 | TP price should be higher than the trigger price |
| 51393 | 200 | SL price should be lower than the trigger price |
| 51394 | 200 | Trigger price should be higher than the TP price |
| 51395 | 200 | Trigger price should be lower than the SL price |
| 51396 | 200 | TP price should be lower than the trigger price |
| 51397 | 200 | SL price should be higher than the trigger price |
| 51398 | 200 | Current market meets the stop condition. The bot cannot be created. |
| 51399 | 200 | Max margin under current leverage: {amountLimit} {quoteCurrency}. Enter a smaller amount and try again. |
| 51400 | 200 | Order cancellation failed as the order has been filled, canceled or does not exist. |
| 51400 | 200 | Cancellation failed as the order does not exist. (Only applicable to Nitro Spread) |
| 51401 | 200 | Cancellation failed as the order is already canceled. (Only applicable to Nitro Spread) |
| 51402 | 200 | Cancellation failed as the order is already completed. (Only applicable to Nitro Spread) |
| 51403 | 200 | Cancellation failed as the order type doesn't support cancellation. |
| 51404 | 200 | Order cancellation unavailable during the second phase of call auction. |
| 51405 | 200 | Cancellation failed as you don't have any pending orders. |
| 51406 | 400 | Canceled - order count exceeds the limit {param0}. |
| 51407 | 200 | Either order ID or client order ID is required. |
| 51408 | 200 | Pair ID or name doesn't match the order info. |
| 51409 | 200 | Either pair ID or pair name ID is required. |
| 51410 | 200 | Cancellation failed as the order is already in canceling status or pending settlement. |
| 51411 | 200 | Account does not have permission for mass cancellation. |
| 51412 | 200 | Cancellation timed out, please try again later. |
| 51412 | 200 | The order has been triggered and can't be canceled. |
| 51413 | 200 | Cancellation failed as the order type is not supported by endpoint. |
| 51415 | 200 | Unable to place order. Spot trading only supports using the last price as trigger price. Please select "Last" and try again. |
| 51416 | 200 | Order has been triggered and can't be canceled |
| 51500 | 200 | You must enter a price, quantity, or TP/SL |
| 51501 | 400 | Maximum {param0} orders can be modified. |
| 51502 | 200 | Unable to edit order: insufficient balance or margin. |
| 51502 | 200 | Order failed. Insufficient {param0} margin in account |
| 51502 | 200 | Order failed. Insufficient {param0} balance in account and Auto Borrow is not enabled |
| 51502 | 200 | Order failed. Insufficient {param0} margin in account and Auto Borrow is not enabled (Portfolio margin mode can try IOC orders to lower the risks) |
| 51502 | 200 | Order failed. The requested borrowing amount is larger than the available {param0} borrowing amount of your position tier. Existing pending orders and the new order need to borrow {param1}, remaining quota {param2}, total quota {param3}, used {param4} |
| 51502 | 200 | Order failed. The requested borrowing amount is larger than the available {param0} borrowing amount of your position tier. Existing pending orders and the new order need to borrow {param1}, remaining quota {param2}, total quota {param3}, used {param4} |
| 51502 | 200 | Order failed. The requested borrowing amount is larger than the available {param0} borrowing amount of your main account and the allocated VIP quota. Existing pending orders and the new order need to borrow {param1}, remaining quota {param2}, total quota {param3}, used {param4} |
| 51502 | 200 | Order failed. Insufficient available borrowing amount in {param0} crypto pair |
| 51502 | 200 | Order failed. Insufficient available borrowing amount in {param0} loan pool |
| 51502 | 200 | Order failed. Insufficient account balance and the adjusted equity in USD is smaller than the IMR. |
| 51502 | 200 | Order failed. The order didn't pass delta verification. If the order succeeded, the change in adjEq would be smaller than the change in IMR. Increase adjEq or reduce IMR (Portfolio margin mode can try IOC orders to lower the risks) |
| 51503 | 200 | Your order has already been filled or canceled. |
| 51503 | 200 | Order modification failed as the order does not exist. (Only applicable to Nitro Spread) |
| 51505 | 200 | {instId} is not in call auction |
| 51506 | 200 | Order modification unavailable for the order type. |
| 51507 | 200 | You can only place market orders for this crypto at least 5 minutes after its listing. |
| 51508 | 200 | Orders are not allowed to be modified during the call auction. |
| 51509 | 200 | Modification failed as the order has been canceled. (Only applicable to Nitro Spread) |
| 51510 | 200 | Modification failed as the order has been completed. (Only applicable to Nitro Spread) |
| 51511 | 200 | Modification failed as the order price did not meet the requirement for Post Only. |
| 51512 | 200 | Failed to amend orders in batches. You cannot have duplicate orders in the same amend-batch-orders request. |
| 51513 | 200 | Number of modification requests that are currently in progress for an order cannot exceed 3 times. |
| 51514 | 200 | Order modification failed. The price length must be 32 characters or shorter. |
| 51521 | 200 | Failed to edit. Unable to edit reduce-only order because you don't have any positions of this contract. |
| 51522 | 200 | Failed to edit. A reduce-only order can't be in the same trading direction as your existing positions. |
| 51523 | 200 | Unable to modify the order price of a stop order that closes an entire position. Please modify the trigger price instead. |
| 51524 | 200 | Unable to modify the order quantity of a stop order that closes an entire position. Please modify the trigger price instead. |
| 51525 | 200 | Stop order modification is not available for quick margin |
| 51526 | 200 | Order modification unsuccessful. Take profit/Stop loss conditions cannot be added to or removed from stop orders. |
| 51527 | 200 | Order modification unsuccessful. The stop order does not exist. |
| 51528 | 200 | Unable to modify trigger price type |
| 51529 | 200 | Order modification unsuccessful. Stop order modification only applies to Expiry Futures and Perpetual Futures. |
| 51530 | 200 | Order modification unsuccessful. Take profit/Stop loss conditions cannot be added to or removed from reduce-only orders. |
| 51531 | 200 | Order modification unsuccessful. The stop order must have either take profit or stop loss attached. |
| 51532 | 200 | Your TP/SL can't be modified because it was partially triggered |
| 51536 | 200 | Unable to modify the size of the options order if the price type is pxUsd or pxVol. |
| 51537 | 200 | pxUsd or pxVol are not supported by non-options instruments |
| 51543 | 200 | When modifying take-profit or stop-loss orders for spot or margin trading, you can only adjust the price and quantity. Cancel the order and place a new one for other actions. |
| 51600 | 200 | Status not found. |
| 51601 | 200 | Order status and order id cannot exist at the same time. |
| 51602 | 200 | Either order status or order ID is required. |
| 51603 | 200 | Order does not exist. |
| 51604 | 200 | Initiate a download request before obtaining the hyperlink |
| 51605 | 200 | You can only download transaction data from the past 2 years |
| 51606 | 200 | Transaction data for the current quarter is not available |
| 51607 | 200 | Your previous download request is still being processed |
| 51608 | 200 | No transaction data found for the current quarter |
| 51610 | 200 | You can't download billing statements for the current quarter. |
| 51611 | 200 | You can't download billing statements for the current quarter. |
| 51620 | 200 | Only affiliates can perform this action |
| 51621 | 200 | The user isn’t your invitee |
| 51156 | 200 | You're leading trades in long/short mode and can't use this API endpoint to close positions |
| 51159 | 200 | You're leading trades in buy/sell mode. If you want to place orders using this API endpoint, the orders must be in the same direction as your existing positions and open orders. |
| 51162 | 200 | You have {instrument} open orders. Cancel these orders and try again |
| 51163 | 200 | You hold {instrument} positions. Close these positions and try again |
| 51165 | 200 | The number of {instrument} reduce-only orders reached the upper limit of {upLimit}. Cancel some orders to proceed. |
| 51166 | 200 | Currently, we don't support leading trades with this instrument |
| 51167 | 200 | Failed. You have block trading open order(s), please proceed after canceling existing order(s). |
| 51168 | 200 | Failed. You have reduce-only type of open order(s), please proceed after canceling existing order(s) |
| 51320 | 200 | The range of coin percentage is {0}%-{1}% |
| 51321 | 200 | You're leading trades. Currently, we don't support leading trades with arbitrage, iceberg, or TWAP bots |
| 51322 | 200 | You're leading trades that have been filled at market price. We've canceled your open stop orders to close your positions |
| 51323 | 200 | You're already leading trades with take profit or stop loss settings. Cancel your existing stop orders to proceed |
| 51324 | 200 | As a lead trader, you hold positions in {instrument}. To close your positions, place orders in the amount that equals the available amount for closing |
| 51325 | 200 | As a lead trader, you must use market price when placing stop orders |
| 51326 | 200 | As a lead trader, you must use market price when placing orders with take profit or stop loss settings |
| 51820 | 200 | Request failed |
| 51821 | 200 | The payment method is not supported |
| 51822 | 200 | Quote expired |
| 51823 | 200 | Parameter {param} of buy/sell trading is inconsistent with the quotation |
| 54000 | 200 | Margin trading is not supported. |
| 54001 | 200 | Only Multi-currency margin account can be set to borrow coins automatically. |
| 54004 | 200 | Order placement or modification failed because one of the orders in the batch failed. |
| 54005 | 200 | Switch to isolated margin mode to trade pre-market expiry futures. |
| 54006 | 200 | Pre-market expiry future position limit is {posLimit}. Please cancel order or close position |
| 54007 | 200 | Instrument {instId} is not supported |
| 54008 | 200 | This operation is disabled by the 'mass cancel order' endpoint. Please enable it using this endpoint. |
| 54009 | 200 | The range of {param0} should be [{param1}, {param2}]. |
| 54011 | 200 | Pre-market trading contracts are only allowed to reduce the number of positions within 1 hour before delivery. Please modify or cancel the order. |
| 54012 | 200 | Due to insufficient order book depth, we are now taking measures to protect your positions. Currently, you can only cancel orders, add margin to your positions, and place post-only orders. Your positions will not be liquidated. Trade will resume once order book depth returns to a safe level. |
| 54018 | 200 | Buy limit of {param0} USD exceeded. Your remaining limit is {param1} USD. (During the call auction) |
| 54019 | 200 | Buy limit of {param0} USD exceeded. Your remaining limit is {param1} USD. (After the call auction) |
| 54024 | 200 | Your order failed because you must enable {ccy} as collateral to trade expiry futures, perpetual futures, and options in cross-margin mode. |
| 54025 | 200 | Your order failed because you must enable {ccy} as collateral to trade margin, expiry futures, perpetual futures, and options in isolated margin mode. |
| 54026 | 200 | Your order failed because you must enable {ccy} and {ccy1} as collateral to trade the margin pair in isolated margin mode. |
| 54027 | 200 | Your order failed because you must enable {ccy} as collateral to trade options. |
| 54028 | 200 | Your order failed because you must enable {ccy} as collateral to trade spot in isolated margin mode. |
| 54029 | 200 | {param0} doesn’t exist within {param1}. |
| 54030 | 200 | Order failed. Your total value of same-direction {param0} open positions and orders can't exceed {param1} USD or {param2} of the platform's open interest. |
| 54031 | 200 | Order failed. The {param1} USD open position limit for {param0} has been reached. |
| 54035 | 200 | Order failed. The platform has reached the collateral limit for this crypto, so you can only place reduce-only orders. |
| 54036 | 200 | You can't place fill or kill orders when self-trade prevention is set to both maker and taker orders. |

#### Data class

| Error Code | HTTP Status Code | Error Message |
| --- | --- | --- |
| 52000 | 200 | No market data found. |

### Spot/Margin

Error Code from 54000 to 54999

| Error Code | HTTP Status Code | Error Message |
| --- | --- | --- |
| 54000 | 200 | Margin trading is not supported. |
| 54001 | 200 | Only Multi-currency margin account can be set to borrow coins automatically. |
| 54004 | 200 | Order placement or modification failed because one of the orders in the batch failed. |

### Funding

Error Code from 58000 to 58999

| Error Code | HTTP Status Code | Error Message |
| --- | --- | --- |
| 58002 | 200 | Please activate Savings Account first. |
| 58003 | 200 | Savings does not support this currency type |
| 58004 | 200 | Account blocked. |
| 58005 | 200 | The {behavior} amount must be equal to or less than {minNum} |
| 58006 | 200 | Service unavailable for token {0}. |
| 58007 | 200 | Assets interface is currently unavailable. Try again later |
| 58008 | 200 | You do not have assets in this currency. |
| 58009 | 200 | Crypto pair doesn't exist |
| 58010 | 200 | Chain {chain} isn't supported |
| 58011 | 200 | Due to local laws and regulations, our services are unavailable to unverified users in {region}. Please verify your account. |
| 58012 | 200 | Due to local laws and regulations, OKX does not support asset transfers to unverified users in {region}. Please make sure your recipient has a verified account. |
| 58013 | 200 | Withdrawals not supported yet, contact customer support for details |
| 58014 | 200 | Deposits not supported yet, contact customer support for details |
| 58015 | 200 | Transfers not supported yet, contact customer support for details |
| 58016 | 200 | The API can only be accessed and used by the trading team's main account |
| 58100 | 200 | The trading product triggers risk control, and the platform has suspended the fund transfer-out function with related users. Please wait patiently. |
| 58101 | 200 | Transfer suspended |
| 58102 | 429 | Rate limit reached. Please refer to API docs and throttle requests accordingly. |
| 58103 | 200 | This account transfer function is temporarily unavailable. Please contact customer service for details. |
| 58104 | 200 | Since your P2P transaction is abnormal, you are restricted from making fund transfers. Please contact customer support to remove the restriction. |
| 58105 | 200 | Since your P2P transaction is abnormal, you are restricted from making fund transfers. Please transfer funds on our website or app to complete identity verification. |
| 58106 | 200 | USD verification failed. |
| 58107 | 200 | Crypto verification failed. |
| 58110 | 200 | Transfers are suspended due to market risk control triggered by your {businessType} {instFamily} trades or positions. Please try again in a few minutes. Contact customer support if further assistance is needed. |
| 58111 | 200 | Fund transfers are unavailable while perpetual contracts are charging funding fees. Try again later. |
| 58112 | 200 | Transfer failed. Contact customer support for assistance |
| 58113 | 200 | Unable to transfer this crypto |
| 58114 | 400 | Transfer amount must be greater than 0 |
| 58115 | 200 | Sub-account does not exist. |
| 58116 | 200 | Transfer exceeds the available amount. |
| 58117 | 200 | Transfer failed. Resolve any negative assets before transferring again |
| 58119 | 200 | {0} Sub-account has no permission to transfer out, please set first. |
| 58120 | 200 | Transfers are currently unavailable. Try again later |
| 58121 | 200 | This transfer will result in a high-risk level of your position, which may lead to forced liquidation. You need to re-adjust the transfer amount to make sure the position is at a safe level before proceeding with the transfer. |
| 58122 | 200 | A portion of your spot is being used for Delta offset between positions. If the transfer amount exceeds the available amount, it may affect current spot-derivatives risk offset structure, which will result in an increased Maintenance Margin Requirement (MMR) rate. Please be aware of your risk level. |
| 58123 | 200 | The From parameter cannot be the same as the To parameter. |
| 58124 | 200 | Your transfer is being processed, transfer id:{trId}. Please check the latest state of your transfer from the endpoint (GET /api/v5/asset/transfer-state) |
| 58125 | 200 | Non-tradable assets can only be transferred from sub-accounts to main accounts |
| 58126 | 200 | Non-tradable assets can only be transferred between funding accounts |
| 58127 | 200 | Main account API key does not support current transfer 'type' parameter. Please refer to the API documentation. |
| 58128 | 200 | Sub-account API key does not support current transfer 'type' parameter. Please refer to the API documentation. |
| 58129 | 200 | {param} is incorrect or {param} does not match with 'type' |
| 58131 | 200 | For compliance, we're unable to provide services to unverified users. Verify your identity to make a transfer. |
| 58132 | 200 | For compliance, we're unable to provide services to users with Basic verification (Level 1). Complete Advanced verification (Level 2) to make a transfer. |
| 58200 | 200 | Withdrawal from {0} to {1} is currently not supported for this currency. |
| 58201 | 200 | Withdrawal amount exceeds daily withdrawal limit. |
| 58202 | 200 | The minimum withdrawal amount for NEO is 1, and the amount must be an integer. |
| 58203 | 200 | Please add a withdrawal address. |
| 58204 | 200 | Withdrawal suspended due to your account activity triggering risk control. Please contact customer support for assistance. |
| 58205 | 200 | Withdrawal amount exceeds the upper limit. |
| 58206 | 200 | Withdrawal amount is less than the lower limit. |
| 58207 | 200 | Withdrawal address isn't on the verified address list. (The format for withdrawal addresses with a label is “address:label”.) |
| 58208 | 200 | Withdrawal failed. Please link your email. |
| 58209 | 200 | Sub-accounts don't support withdrawals or deposits. Please use your main account instead |
| 58210 | 200 | You can't proceed with withdrawal as we're unable to verify your identity. Please withdraw via our app or website instead. |
| 58212 | 200 | Withdrawal fee must be {0}% of the withdrawal amount |
| 58213 | 200 | The internal transfer address is illegal. It must be an email, phone number, or account name |
| 58214 | 200 | Withdrawals suspended due to {chainName} maintenance |
| 58215 | 200 | Withdrawal ID does not exist. |
| 58216 | 200 | Operation not allowed. |
| 58217 | 200 | Withdrawals are temporarily suspended for your account due to a risk detected in your withdrawal address. Contact customer support for assistance |
| 58218 | 200 | The internal withdrawal failed. Please check the parameters toAddr and areaCode. |
| 58219 | 200 | You cannot withdraw crypto within 24 hours after changing your mobile number, email address, or Google Authenticator. |
| 58220 | 200 | Withdrawal request already canceled. |
| 58221 | 200 | The toAddr parameter format is incorrect, withdrawal address needs labels. The format should be "address:label". |
| 58222 | 200 | Invalid withdrawal address |
| 58223 | 200 | This is a contract address with higher withdrawal fees |
| 58224 | 200 | This crypto currently doesn't support on-chain withdrawals to OKX addresses. Withdraw through internal transfers instead |
| 58225 | 200 | Asset transfers to unverified users in {region} are not supported due to local laws and regulations. |
| 58226 | 200 | {chainName} is delisted and not available for crypto withdrawal. |
| 58227 | 200 | Withdrawal of non-tradable assets can be withdrawn all at once only |
| 58228 | 200 | Withdrawal of non-tradable assets requires that the API key must be bound to an IP |
| 58229 | 200 | Insufficient funding account balance to pay fees {fee} USDT |
| 58230 | 200 | According to the OKX compliance policy, you will need to complete your identity verification (Level 1) in order to withdraw |
| 58231 | 200 | The recipient has not completed personal info verification (Level 1) and cannot receive your transfer |
| 58232 | 200 | You’ve reached the personal information verification (L1) withdrawal limit, complete photo verification (L2) to increase the withdrawal limit |
| 58233 | 200 | For compliance, we're unable to provide services to unverified users. Verify your identity to withdraw. |
| 58234 | 200 | For compliance, the recipient can't receive your transfer yet. They'll need to verify their identity to receive your transfer. |
| 58235 | 200 | For compliance, we're unable to provide services to users with Basic verification (Level 1). Complete Advanced verification (Level 2) to withdraw. |
| 58236 | 200 | For compliance, a recipient with Basic verification (Level 1) is unable to receive your transfer. They'll need to complete Advanced verification (Level 2) to receive it. |
| 58237 | 200 | According to local laws and regulations, please provide accurate recipient information (rcvrInfo). For the exchange address, please also provide exchange information and recipient identity information ({consientParameters}). |
| 58238 | 200 | Incomplete info. The info of the exchange and the recipient are required if you're withdrawing to an exchange platform. |
| 58239 | 200 | You can't withdraw to a private wallet via API. Please withdraw via our app or website instead. |
| 58240 | 200 | For security and compliance purposes, please complete the identity verification process to use our services. If you prefer not to verify, contact customer support for next steps. We're committed to ensuring a safe platform for users and appreciate your understanding. |
| 58241 | 200 | Due to local compliance requirements, internal withdrawal is unavailable |
| 58242 | 200 | The recipient can't receive your transfer due to their local compliance requirements |
| 58243 | 200 | Your recipient can't receive your transfer as they haven't made a cash deposit yet |
| 58244 | 200 | Make a cash deposit to proceed |
| 58248 | 200 | Due to local regulations, API withdrawal isn't allowed. Withdraw using OKX app or web. |
| 58249 | 200 | API withdrawal for this currency is currently unavailable. Try withdrawing via our app or website. |
| 58252 | 200 | Withdrawal is restricted for 48h after your first TRY transaction for asset security. |
| 58300 | 200 | Deposit-address count exceeds the limit. |
| 58301 | 200 | Deposit-address not exist. |
| 58302 | 200 | Deposit-address needs tag. |
| 58303 | 200 | Deposit for chain {chain} is currently unavailable |
| 58304 | 200 | Failed to create invoice. |
| 58305 | 200 | Unable to retrieve deposit address, please complete identity verification and generate deposit address first. |
| 58306 | 200 | According to the OKX compliance policy, you will need to complete your identity verification (Level 1) in order to deposit |
| 58307 | 200 | You've reached the personal information verification (L1) deposit limit, the excess amount has been frozen, complete photo verification (L2) to increase the deposit limit |
| 58308 | 200 | For compliance, we're unable to provide services to unverified users. Verify your identity to deposit. |
| 58309 | 200 | For compliance, we're unable to provide services to users with Basic verification (Level 1). Complete Advanced verification (Level 2) to deposit. |
| 58310 | 200 | Unable to create new deposit address, try again later |
| 58350 | 200 | Insufficient balance. |
| 58351 | 200 | Invoice expired. |
| 58352 | 200 | Invalid invoice. |
| 58353 | 200 | Deposit amount must be within limits. |
| 58354 | 200 | You have reached the daily limit of 10,000 invoices. |
| 58355 | 200 | Permission denied. Please contact your account manager. |
| 58356 | 200 | The accounts of the same node do not support the Lightning network deposit or withdrawal. |
| 58358 | 200 | The fromCcy parameter cannot be the same as the toCcy parameter. |
| 58373 | 200 | The minimum {ccy} conversion amount is {amount} |
| 58400 | 200 | Request Failed |
| 58401 | 200 | Payment method is not supported |
| 58402 | 200 | Invalid payment account |
| 58403 | 200 | Transaction cannot be canceled |
| 58404 | 200 | ClientId already exists |
| 58405 | 200 | Withdrawal suspended |
| 58406 | 200 | Channel is not supported |
| 58407 | 200 | API withdrawal isn't allowed for this payment method. Withdraw using OKX app or web |

### Account

Error Code from 59000 to 59999

| Error Code | HTTP Status Code | Error Message |
| --- | --- | --- |
| 59000 | 200 | Settings failed. Close any open positions or orders before modifying settings. |
| 59001 | 200 | Switching unavailable as you have borrowings. |
| 59002 | 200 | Sub-account settings failed. Close any open positions, orders, or trading bots before modifying settings. |
| 59004 | 200 | Only IDs with the same instrument type are supported |
| 59005 | 200 | When margin is manually transferred in isolated mode, the value of the asset intially allocated to the position must be greater than 10,000 USDT. |
| 59006 | 200 | This feature is unavailable and will go offline soon. |
| 59101 | 200 | Leverage can't be modified. Please cancel all pending isolated margin orders before adjusting the leverage. |
| 59102 | 200 | Leverage exceeds the maximum limit. Please lower the leverage. |
| 59103 | 200 | Account margin is insufficient and leverage is too low. Please increase the leverage. |
| 59104 | 200 | The borrowed position has exceeded the maximum position of this leverage. Please lower the leverage. |
| 59105 | 400 | Leverage can't be less than {0}. Please increase the leverage. |
| 59106 | 200 | The max available margin corresponding to your order tier is {param0}. Please adjust your margin and place a new order. |
| 59107 | 200 | Leverage can't be modified. Please cancel all pending cross-margin orders before adjusting the leverage. |
| 59108 | 200 | Your account leverage is too low and has insufficient margins. Please increase the leverage. |
| 59109 | 200 | Account equity less than the required margin amount after adjustment. Please adjust the leverage. |
| 59110 | 200 | The instrument corresponding to this {param0} does not support the tgtCcy parameter. |
| 59111 | 200 | Leverage query isn't supported in portfolio margin account mode |
| 59112 | 200 | You have isolated/cross pending orders. Please cancel them before adjusting your leverage |
| 59113 | 200 | According to local laws and regulations, margin trading service is not available in your region. If your citizenship is at a different region, please complete KYC2 verification. |
| 59114 | 200 | According to local laws and regulations, margin trading services are not available in your region. |
| 59117 | 200 | Cannot select more than {param0} crypto types |
| 59118 | 200 | Amount placed should greater than {param0} |
| 59119 | 200 | One-click repay is temporarily unavailable. Try again later. |
| 59120 | 200 | One-click convert is temporarily unavailable. Try again later. |
| 59121 | 200 | This batch is still under processing, please wait patiently. |
| 59122 | 200 | This batch has been processed |
| 59123 | 200 | {param0} order amount must be greater than {param1} |
| 59124 | 200 | The order amount of {param0} must be less than {param1}. |
| 59125 | 200 | {param0} doesn't support the current operation. |
| 59132 | 200 | Unable to switch. Please close or cancel all open orders and refer to the pre-check endpoint to stop any incompatible bots. |
| 59133 | 200 | Unable to switch due to insufficient assets for the chosen account mode. |
| 59134 | 200 | Unable to switch. Refer to the pre-check endpoint and close any incompatible positions. |
| 59135 | 200 | Unable to switch. Refer to the pre-check endpoint and adjust your trades from copy trading. |
| 59136 | 200 | Unable to switch. Pre-set leverage for all cross margin contract positions then try again. |
| 59137 | 200 | Lower leverage to {param0} or below for all cross margin contract positions and try again. |
| 59138 | 200 | Unable to switch due to a position tier check failure. |
| 59139 | 200 | Unable to switch due to a margin check failure. |
| 59140 | 200 | You can only repay with your collateral crypto. |
| 59141 | 200 | The minimum repayment amount is {param0}. Select more available crypto or increase your trading account balance. |
| 59142 | 200 | Instant repay failed. You can only repay borrowable crypto. |
| 59200 | 200 | Insufficient account balance. |
| 59201 | 200 | Negative account balance. |
| 59202 | 200 | No access to max opening amount in cross positions for PM accounts. |
| 59300 | 200 | Margin call failed. Position does not exist. |
| 59301 | 200 | Margin adjustment failed for exceeding the max limit. |
| 59302 | 200 | Margin adjustment failed due to pending close order. Please cancel any pending close orders. |
| 59303 | 200 | Insufficient available margin, add margin or reduce the borrowing amount |
| 59304 | 200 | Insufficient equity for borrowing. Keep enough funds to pay interest for at least one day. |
| 59305 | 200 | Use VIP loan first to set the VIP loan priority |
| 59306 | 200 | Your borrowing amount exceeds the max limit |
| 59307 | 200 | You are not eligible for VIP loans |
| 59308 | 200 | Unable to repay VIP loan due to insufficient borrow limit |
| 59309 | 200 | Unable to repay an amount that exceeds the borrowed amount |
| 59310 | 200 | Your account does not support VIP loan |
| 59311 | 200 | Setup cannot continue. An outstanding VIP loan exists. |
| 59312 | 200 | {currency} does not support VIP loans |
| 59313 | 200 | Unable to repay. You haven't borrowed any ${ccy} (${ccyPair}) in Quick margin mode. |
| 59314 | 200 | The current user is not allowed to return the money because the order is not borrowed |
| 59315 | 200 | viploan is upgrade now. Wait for 10 minutes and try again |
| 59316 | 200 | The current user is not allowed to borrow coins because the currency is in the order in the currency borrowing application. |
| 59317 | 200 | The number of pending orders that are using VIP loan for a single currency cannot be more than {maxNumber} (orders) |
| 59319 | 200 | You can’t repay your loan order because your funds are in use. Make them available for full repayment. |
| 59401 | 200 | Holdings limit reached. |
| 59402 | 200 | No passed instIDs are in a live state. Please verify instIDs separately. |
| 59410 | 200 | You can only borrow this crypto if it supports borrowing and borrowing is enabled. |
| 59411 | 200 | Manual borrowing failed. Your account's free margin is insufficient. |
| 59412 | 200 | Manual borrowing failed. The amount exceeds your borrowing limit. |
| 59413 | 200 | You didn't borrow this crypto. No repayment needed. |
| 59414 | 200 | Manual borrowing failed. The minimum borrowing limit is {param0}. |
| 59500 | 200 | Only the API key of the main account has permission. |
| 59501 | 200 | Each account can create up to 50 API keys |
| 59502 | 200 | This note name already exists. Enter a unique API key note name |
| 59503 | 200 | Each API key can bind up to 20 IP addresses |
| 59504 | 200 | Sub-accounts don't support withdrawals. Please use your main account for withdrawals. |
| 59505 | 200 | The passphrase format is incorrect. |
| 59506 | 200 | API key doesn't exist. |
| 59507 | 200 | The two accounts involved in a transfer must be 2 different sub-accounts under the same main account. |
| 59508 | 200 | The sub account of {param0} is suspended. |
| 59509 | 200 | Account doesn't have permission to reset market maker protection (MMP) status. |
| 59510 | 200 | Sub-account does not exist |
| 59512 | 200 | Unable to set up permissions for ND broker subaccounts. By default, all ND subaccounts can transfer funds out. |
| 59515 | 200 | You are currently not on the custody whitelist. Please contact customer service for assistance. |
| 59516 | 200 | Please create the Copper custody funding account first. |
| 59517 | 200 | Please create the Komainu custody funding account first. |
| 59518 | 200 | You can’t create a sub-account using the API; please use the app or web. |
| 59519 | 200 | You can’t use this function/feature while it's frozen, due to: {freezereason} |
| 59601 | 200 | Subaccount name already exists. |
| 59603 | 200 | Maximum number of subaccounts reached. |
| 59604 | 200 | Only the API key of the main account can access this API. |
| 59606 | 200 | Failed to delete sub-account. Transfer all sub-account funds to your main account before deleting your sub-account. |
| 59608 | 200 | Only Broker accounts have permission to access this API. |
| 59609 | 200 | Broker already exists |
| 59610 | 200 | Broker does not exist |
| 59611 | 200 | Broker unverified |
| 59612 | 200 | Cannot convert time format |
| 59613 | 200 | No escrow relationship established with the subaccount. |
| 59614 | 200 | Managed subaccount does not support this operation. |
| 59615 | 200 | The time interval between the Begin Date and End Date cannot be greater than 180 days. |
| 59616 | 200 | The Begin Date cannot be later than the End Date. |
| 59617 | 200 | Sub-account created. Account level setup failed. |
| 59618 | 200 | Failed to create sub-account. |
| 59619 | 200 | This endpoint does not support ND sub accounts. Please use the dedicated endpoint supported for ND brokers. |
| 59622 | 200 | You're creating a sub-account for a non-existing or incorrect sub-account. Create a sub-account under the ND broker first or use the correct sub-account code. |
| 59623 | 200 | Couldn't delete the sub-account under the ND broker as the sub-account has one or more sub-accounts, which must be deleted first. |
| 59648 | 200 | Your modified spot-in-use amount is insufficient, which may lead to liquidation. Adjust the amount. |
| 59649 | 200 | Disabling spot-derivatives risk offset mode may increase the risk of liquidation. Adjust the size of your positions and ensure your maintenance maintenance margin ratio is safe. |
| 59650 | 200 | Switching your offset unit may increase the risk of liquidation. Adjust the size of your positions and ensure your maintenance maintenance margin ratio is safe. |
| 59651 | 200 | Enable spot-derivatives risk offset mode to set your spot-in-use amount. |
| 59652 | 200 | You can only set a spot-in-use amount for crypto that can be used as margin. |
| 59658 | 200 | {ccy} isn’t supported as collateral. |
| 59658 | 200 | {ccy} and {ccy1} aren’t supported as collateral. |
| 59658 | 200 | {ccy}, {ccy1}, and {ccy2} aren’t supported as collateral. |
| 59658 | 200 | {ccy}, {ccy1}, {ccy2}, and {number} other crypto aren’t supported as collateral. |
| 59659 | 200 | Failed to apply settings because you must also enable {ccy} to enable {ccy1} as collateral. |
| 59660 | 200 | Failed to apply settings because you must also disable {ccy} to disable {ccy1} as collateral. |
| 59661 | 200 | Failed to apply settings because you can’t disable {ccy} as collateral. |
| 59662 | 200 | Failed to apply settings because of open orders or positions requiring {ccy} as collateral. |
| 59662 | 200 | Failed to apply settings because of open orders or positions requiring {ccy} and {ccy1} as collateral. |
| 59662 | 200 | Failed to apply settings because of open orders or positions requiring {ccy}, {ccy1}, and {ccy2} as collateral. |
| 59662 | 200 | Failed to apply settings because of open orders or positions requiring {ccy}, {ccy1}, {ccy2}, and {number} other crypto as collateral. |
| 59664 | 200 | Failed to apply settings because you have borrowings in {ccy}. |
| 59664 | 200 | Failed to apply settings because you have borrowings in {ccy} and {ccy1}. |
| 59664 | 200 | Failed to apply settings because you have borrowings in {ccy}, {ccy1}, and {ccy2}. |
| 59664 | 200 | Failed to apply settings because you have borrowings in {ccy}, {ccy1}, {ccy2}, and {number} other crypto. |
| 59665 | 200 | Failed to apply settings. Enable other cryptocurrencies as collateral to meet the position’s margin requirements. |
| 59666 | 200 | Failed to apply settings because you can’t enable and disable a crypto as collateral at the same time. |
| 59668 | 200 | Cancel isolated margin TP/SL, trailing, trigger, and chase orders or stop bots before adjusting your leverage. |
| 59669 | 200 | Cancel cross-margin TP/SL, trailing, trigger, and chase orders or stop bots before adjusting your leverage. |
| 59670 | 200 | You have more than {param0} open orders for this trading pair. Cancel to reduce your orders to {param1} or fewer before adjusting your leverage. |

## WebSocket

### Public

Error Code from 60000 to 64002

#### General Class

| Error Code | Error Message |
| --- | --- |
| 60004 | Invalid timestamp |
| 60005 | Invalid apiKey |
| 60006 | Timestamp request expired |
| 60007 | Invalid sign |
| 60008 | The current WebSocket endpoint does not support subscribing to {0} channels. Please check the WebSocket URL |
| 60009 | Login failure |
| 60011 | Please log in |
| 60012 | Invalid request |
| 60013 | Invalid args |
| 60014 | Requests too frequent |
| 60018 | Wrong URL or {0} doesn't exist. Please use the correct URL, channel and parameters referring to API document. |
| 60019 | Invalid op: {op} |
| 60023 | Bulk login requests too frequent |
| 60024 | Wrong passphrase |
| 60026 | Batch login by APIKey and token simultaneously is not supported. |
| 60027 | Parameter {0} can not be empty. |
| 60028 | The current operation is not supported by this URL. Please use the correct WebSocket URL for the operation. |
| 60029 | Only users who are VIP5 and above in trading fee tier are allowed to subscribe to this channel. |
| 60030 | Only users who are VIP4 and above in trading fee tier are allowed to subscribe to books50-l2-tbt channel. |
| 60031 | The WebSocket endpoint does not allow multiple or repeated logins. |
| 60032 | API key doesn't exist. |
| 63999 | Login failed due to internal error. Please try again later. |
| 64000 | Subscription parameter uly is unavailable anymore, please replace uly with instFamily. More details can refer to: https://www.okx.com/help-center/changes-to-v5-api-websocket-subscription-parameter-and-url. |
| 64001 | This channel has been migrated to the '/business' URL. Please subscribe using the new URL. More details can refer to: https://www.okx.com/help-center/changes-to-v5-api-websocket-subscription-parameter-and-url. |
| 64002 | This channel is not supported by "/business" URL. Please use "/private" URL(for private channels), or "/public" URL(for public channels). More details can refer to: https://www.okx.com/help-center/changes-to-v5-api-websocket-subscription-parameter-and-url. |
| 64003 | Your trading fee tier doesn't meet the requirement to access this channel |
| 64004 | Subscribe to both {channelName} and books-l2-tbt for {instId} is not allowed. Unsubscribe books-l2-tbt first. |
| 64007 | Operation {0} failed due to WebSocket internal error. Please try again later. |
| 64008 | The connection will soon be closed for a service upgrade. Please reconnect. |

#### Close Frame

| Status Code | Reason Text |
| --- | --- |
| 1009 | Request message exceeds the maximum frame length |
| 4001 | Login Failed |
| 4002 | Invalid Request |
| 4003 | APIKey subscription amount exceeds the limit 100 |
| 4004 | No data received in 30s |
| 4005 | Buffer is full, cannot write data |
| 4006 | Abnormal disconnection |
| 4007 | API key has been updated or deleted. Please reconnect. |
| 4008 | The number of subscribed channels exceeds the maximum limit. |
| 4009 | The number of subscription channels for this connection exceeds the limit |