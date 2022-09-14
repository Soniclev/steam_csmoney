`# System for monitoring prices between CS.MONEY and Steam market

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

# Steam and CS.MONEY parsers

The Steam parser fetch skins that should be processed from a scheduler. The scheduler for Steam returns a list of items that should be fetched. After successful invoke of Steam endpoint the scheduler postpone the item for 15 minutes. In case of any error the item will be rescheduled without postpone. Throughput of parser depends on amount of free proxy. After each request, a proxy is frozen for 3 seconds to avoid 429 Too Many Requests error. A successful response from Steam is put in a RabbitMQ queue. Also, the Steam parser loads sell history for each skin in similar way, that will be processed by a worker. Can be found [here](price_monitoring/parsers/steam)

The CS.MONEY parser works in a similar way, but has some differences. The parser enumerate inventory by loading 60 items per request. These request grouped in tasks by price range, because it's impossible to load items after 5000th offset. Each request that contains up to 60 items will be put in a RabbitMQ queue. If it's impossible to make successful request after several retries, the task will be marked as failed. Can be found [here](price_monitoring/parsers/csmoney)

At this moment only one instance of each parser can be running at one time.

# Worker

A worker fetch results from queue, process them and pass results to Redis. Applied processors can be found [here](price_monitoring/worker/processing).

For given sell history of skin, a worker determinate stability of 

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