from typing import Optional

from .rpc.rabbitmq_client import RabbitMQClient


class RabbitmqConnector:
    @staticmethod
    def create(host: str,
               port: str,
               login: str,
               password: str,
               connection_name: Optional[str] = None) -> RabbitMQClient:
        return RabbitMQClient(host=host,
                              port=int(port),
                              login=login,
                              password=password,
                              connection_name=connection_name)

    @staticmethod
    async def connect(host: str,
                      port: str,
                      login: str,
                      password: str,
                      connection_name: Optional[str] = None):
        return await RabbitMQClient(host=host,
                                    port=int(port),
                                    login=login,
                                    password=password,
                                    connection_name=connection_name).connect()
