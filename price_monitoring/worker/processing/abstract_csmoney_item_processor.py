from abc import ABC, abstractmethod

from ...models.csmoney import CsmoneyItemPack


class AbstractCsmoneyItemProcessor(ABC):
    @abstractmethod
    async def process(self, pack: CsmoneyItemPack) -> None:
        ...
