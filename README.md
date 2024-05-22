# System for monitoring prices between CS.MONEY and Steam market

# High level features
* Supports proxies (http, socks4, socks5)
* Built using asyncio
* Resistant to failure
* Covered by unit-tests
* Most obvious bottlenecks are optimized
* Created simple CI pipeline
* For some features added tracing support using Zipkin

# Technologies
* Python 3.10, Asyncio, Poetry
* Docker, docker-compose
* Redis
* RabbitMQ
* Pytest
* Pylint, mypy, black

# Simplified flow chart

```mermaid
graph LR;
    steam_parser(Steam parser)-->rabbitmq;
    csmoney_parser(CS.MONEY parser)-->rabbitmq;
    rabbitmq(RabbitMQ);
    rabbitmq-->worker;
    worker(Worker #N)-->Redis;
    Redis[(Redis)];
    Redis-->bot(Telegram bot);
```

Both parsers send responses to appropriate queues (one for Steam and another one for CS.MONEY). After it, a worker fetch response from the queue and process it. The result of processing is uploaded to a Redis instance. A telegram bot periodically retrieve results from Redis and compute profit for each market item. 

# How to run (last tested in April 2024)
1. Open the bot.dev.env file and locate the line that starts with `TELEGRAM_API_TOKEN=`. Set the value of the `TELEGRAM_API_TOKEN` variable to your own Telegram bot's API token. To obtain the token, you can create a bot on Telegram and follow their instructions.
Additionally, you need to specify the Telegram user IDs that will have access to this bot. To find your Telegram user ID, you can message the bot called https://t.me/myidbot, and it will provide you with your ID. If you have multiple user IDs, separate them with commas (",").
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
   * `socks4://1.1.1.1:1234` - (note: socks4 protocol don't support authorization)
   * `socks5://user:pass@1.1.1.1:1234`
3. Open your terminal or command prompt and run the following command:
```
docker-compose --env-file prod.env up -d
```
4. Setup initial settings for your in your Telegram bot:
   1. `/set_min_price 0` - This command sets the minimum price limit. Any item with a price lower than this value will not be displayed.
   2. `/set_limit -30` - This command sets the profit limit for withdrawals. For example, if you set it to -30, only items with a profit margin greater than -30% will be displayed.

Available Telegram bot commands:
* `/offers` - Displays the current available offers.
* `/set_min_price <price>` - Sets the minimum price limit. Any item with a price lower than this value will not be displayed.
* `/set_limit <profit margin>` - Sets the profit limit for withdrawals. The profit margin includes any applicable fees and represents the minimum acceptable profit for an item to be displayed.
* `/settings` - Displays the current settings for withdrawals.

With these adjusted instructions, you should be able to easily run the application and configure your Telegram bot for usage. All prices are in dollars.

![Bot work screenshot](images/bot.png "Bot work screenshot")

# Steam and CS.MONEY parsers

The Steam parser fetch skins that should be processed from a scheduler. The scheduler for Steam returns a list of items that should be fetched. After successful invoke of Steam endpoint the scheduler postpone the item for 15 minutes. In case of any error the item will be rescheduled without postpone. Throughput of parser depends on amount of free proxy. After each request, a proxy is frozen for 3 seconds to avoid 429 Too Many Requests error. A successful response from Steam is put in a RabbitMQ queue. Also, the Steam parser loads sell history for each skin in similar way, that will be processed by a worker. Can be found [here](price_monitoring/parsers/steam)

The CS.MONEY parser works in a similar way, but has some differences. The parser enumerate inventory by loading 60 items per request. These request grouped in tasks by price range, because it's impossible to load items after 5000th offset. Each request that contains up to 60 items will be put in a RabbitMQ queue. If it's impossible to make successful request after several retries, the task will be marked as failed. Can be found [here](price_monitoring/parsers/csmoney)

At this moment only one instance of each parser can be running at one time.

# Worker

A worker fetch results from queue, process them and pass results to Redis. Applied processors can be found [here](price_monitoring/worker/processing).

For sell history of a skin, a worker determinate stability of the item and sell probability for each price for last week: ![Sell history analyzer](images/sell_history.jpg "Sell history analyzer")

Several workers can be running at one time. 

# Redis

Prices for items from CS.MONEY stored directly in keys, because it allows:
* Set TTL for each pair of a name and price
* Fetch all items in one request

Items can have 7 days trade ban and cannot be withdrawn immediately. That's why
a key contains "locked" or "unlocked" prefix.
```
prices:csmoney:locked:Sealed Graffiti | Choke (Frog Green):0.25
prices:csmoney:unlocked:StatTrak™ M4A1-S | Leaded Glass (Field-Tested):16.32
```

Prices for items from Steam stored in different way. Each item has it's own unique key like `prices:steam:P2000 | Panther Camo (Battle-Scarred)`. Prices stored as value in simple format `1.3:1.49`. The first number means the highest buy order, the second one means the lowest sell order.

Implementation can be found [here](price_monitoring/storage)

# Item Orders Histogram fix
Feel free to adapt to any new changes made by Steam regarding parsing the item orders histogram. To properly retrieve the item orders histogram, you can follow the solution provided in the following link: [Retrieve Item Orders Histogram Solution](https://gist.github.com/Soniclev/981f8adbc7c6a68350aff9e2a877ed1e) or [here](price_monitoring/parsers/steam/parser/steam_orders_parser.py).
