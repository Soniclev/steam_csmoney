class QueueNames:
    CSMONEY_RESULT = "csmoney_result"
    STEAM_MARKET_NAME = "steam_market_name"
    STEAM_RESULT = "steam_result"
    STEAM_SELL_HISTORY_RESULT = "steam_sell_history_result"


class RedisKeys:
    STEAM_SKIN_SCHEDULE = "steam_skin_schedule"
    STEAM_SKIN_HISTORY_SCHEDULE = "steam_skin_history_schedule"
    STEAM_PROXIES = "steam_proxies"
    CSMONEY_PROXIES = "csmoney_proxies"
    CSMONEY_UNLOCKED_ITEMS = "prices:csmoney:unlocked:"
    CSMONEY_LOCKED_ITEMS = "prices:csmoney:locked:"


class TelegramRedisKeys:
    WHITELIST_KEY = "telegram:whitelist"
    SETTINGS_KEY = "telegram:settings"
