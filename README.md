# System for monitoring prices between CS.MONEY and Steam Market

## High-Level Features
* Supports proxies (HTTP, SOCKS4, SOCKS5)
* Built using asyncio + uvloop
* Resistant to failure
* Covered by unit tests (almost 100% coverage)
* Most obvious bottlenecks are optimized
* Created a simple CI pipeline
* Added tracing support for some features using Zipkin

## Technologies
* Python 3.10, Asyncio, Poetry
* Docker, Docker Compose
* Redis
* RabbitMQ
* Pytest
* Pylint, mypy, black

## Simplified Flow Chart

```mermaid
graph LR;
    steam_parser(Steam Parser)-->rabbitmq;
    csmoney_parser(CS.MONEY Parser)-->rabbitmq;
    rabbitmq(RabbitMQ);
    rabbitmq-->worker;
    worker(Worker #N)-->Redis;
    Redis[(Redis)];
    Redis-->bot(Telegram Bot);
```

Both parsers send responses to appropriate queues (one for Steam and another for CS.MONEY). After that, a worker fetches the response from the queue and processes it. The result of processing is uploaded to a Redis instance. A Telegram bot periodically retrieves results from Redis and computes profit for each market item.

## How to Run (Last Tested in April 2024)
1. Open the `bot.dev.env` file and locate the line that starts with `TELEGRAM_API_TOKEN=`. Set the value of the `TELEGRAM_API_TOKEN` variable to your own Telegram bot's API token. To obtain the token, you can create a bot on Telegram and follow their instructions.
   Additionally, you need to specify the Telegram user IDs that will have access to this bot. To find your Telegram user ID, you can message the bot at https://t.me/myidbot, and it will provide you with your ID. If you have multiple user IDs, separate them with commas (",").
   Here's an example of how it should look:
   ```
   ...
   TELEGRAM_API_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   TELEGRAM_WHITELIST=12345,45678
   ```
2. Create/open the `utils_mount/csmoney_proxies.txt` and `utils_mount/steam_proxies.txt` files. 
   Add the proxies you want to use in the following format: `<protocol>://<user>:<pass>@<host>:<port>`. 
   If the proxy requires authentication (username and password), include them in the URL.
   If no authentication is needed, simply provide the host and port. Here are some examples:
   * `http://user:pass@1.1.1.1:1234`
   * `http://1.1.1.1:1234`
   * `https://user:pass@1.1.1.1:1234`
   * `socks4://1.1.1.1:1234` - (note: the SOCKS4 protocol doesn't support authorization)
   * `socks5://user:pass@1.1.1.1:1234`
3. Open your terminal or command prompt and run the following command:
   ```
   docker-compose --env-file prod.env up -d
   ```
4. Set up initial settings for your Telegram bot:
   1. `/set_min_price 0` - This command sets the minimum price limit. Any item with a price lower than this value will not be displayed.
   2. `/set_limit -30` - This command sets the profit limit for withdrawals. For example, if you set it to -30, only items with a profit margin greater than -30% will be displayed.

Available Telegram bot commands:
* `/offers` - Displays the currently available offers.
* `/set_min_price <price>` - Sets the minimum price limit. Any item with a price lower than this value will not be displayed.
* `/set_limit <profit margin>` - Sets the profit limit for withdrawals. The profit margin includes any applicable fees and represents the minimum acceptable profit for an item to be displayed.
* `/settings` - Displays the current settings for withdrawals.

With these adjusted instructions, you should be able to easily run the application and configure your Telegram bot for usage. All prices are in dollars.

![Bot work screenshot](images/bot.png "Bot work screenshot")

## Steam and CS.MONEY Parsers

The Steam parser fetches skins that should be processed from a scheduler. The scheduler for Steam returns a list of items that should be fetched. After a successful invocation of the Steam endpoint, the scheduler postpones the item for 15 minutes. In case of any error, the item will be rescheduled without postponement. The throughput of the parser depends on the number of free proxies. After each request, a proxy is frozen for 5 seconds to avoid the 429 Too Many Requests error. A successful response from Steam is put in a RabbitMQ queue. Additionally, the Steam parser loads the sell history for each skin in a similar way, which will be processed by a worker. The implementation can be found [here](price_monitoring/parsers/steam).

The CS.MONEY parser works similarly but has some differences. The parser enumerates the inventory by loading 60 items per request. These requests are grouped into tasks by price range because it's impossible to load items after the 5000th offset. Each request that contains up to 60 items will be put in a RabbitMQ queue. If it's impossible to make a successful request after several retries, the task will be marked as failed. The implementation can be found [here](price_monitoring/parsers/csmoney).

At this moment, only one instance of each parser can be running at a time.

## Worker

A worker fetches results from the queue, processes them, and passes results to Redis. The applied processors can be found [here](price_monitoring/worker/processing).

For the sell history of a skin, a worker determines the stability of the item and the sell probability for each price for the last week: ![Sell history analyzer](images/sell_history.jpg "Sell history analyzer")

Several workers can be running at one time.

## Redis

Prices for items from CS.MONEY are stored directly in keys, allowing for:
* Setting TTL for each pair of a name and price
* Fetching all items in one request

Items can have a 7-day trade ban and cannot be withdrawn immediately. That's why a key contains the "locked" or "unlocked" prefix.
```
prices:csmoney:locked:Sealed Graffiti | Choke (Frog Green):0.25
prices:csmoney:unlocked:StatTrak™ M4A1-S | Leaded Glass (Field-Tested):16.32
```

Prices for items from Steam are stored differently. Each item has its own unique key like `prices:steam:P2000 | Panther Camo (Battle-Scarred)`. Prices are stored as values in a simple format `1.3:1.49`. The first number means the highest buy order, the second one means the lowest sell order.

The implementation can be found [here](price_monitoring/storage).

## Item Orders Histogram Fix
Feel free to adapt to any new changes made by Steam regarding parsing the item orders histogram. To properly retrieve the item orders histogram, you can follow the solution provided in the following link: [Retrieve Item Orders Histogram Solution](https://gist.github.com/Soniclev/981f8adbc7c6a68350aff9e2a877ed1e) or [here](price_monitoring/parsers/steam/parser/steam_orders_parser.py).