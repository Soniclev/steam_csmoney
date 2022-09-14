from aioredis import Redis


class RedisConnector:
    @staticmethod
    def create(host: str, port: str, db: str, password: str):
        return Redis(host=host, port=int(port), db=int(db), password=password)
