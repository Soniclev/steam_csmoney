import os
from typing import Optional, List


class EnvVar:
    @staticmethod
    def get(key: str, default=None) -> Optional[str]:
        return os.getenv(key, default)

    @staticmethod
    def get_many(keys: List[str]) -> List[Optional[str]]:
        return [os.getenv(key, None) for key in keys]
