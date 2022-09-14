from abc import ABC, abstractmethod

from ....models.csmoney import CsmoneyItemOverpay


class AbstractOverpayStorage(ABC):
    @abstractmethod
    async def add_overpay(self, item_overpay: CsmoneyItemOverpay):
        pass

    @abstractmethod
    async def get_all(self) -> list[CsmoneyItemOverpay]:
        pass
