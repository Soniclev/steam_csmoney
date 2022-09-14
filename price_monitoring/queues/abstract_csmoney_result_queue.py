from abc import abstractmethod, ABC

from ..models.csmoney import CsmoneyItemPack


class AbstractCsmoneyReader(ABC):
    @abstractmethod
    async def get(self, timeout: int = 5) -> CsmoneyItemPack | None:
        ...


class AbstractCsmoneyWriter(ABC):
    @abstractmethod
    async def put(self, item: CsmoneyItemPack) -> None:
        ...
