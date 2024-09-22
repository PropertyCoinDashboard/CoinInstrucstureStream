from abc import ABC, abstractmethod

import aiohttp
from typing import Any

from common.utils.logger import AsyncLogger

# fmt: off
class AbstractAsyncRequestAcquisition(ABC):
    """비동기 호출의 추상 클래스"""

    def __init__(
        self, 
        url: str, 
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.url = url
        self.params = params
        self.headers = headers
        self.logging = AsyncLogger(target="request", log_file="request.log")

    @abstractmethod
    async def async_source(self, response: aiohttp.ClientSession) -> Any: 
        raise NotImplementedError()
    
    @abstractmethod
    async def async_source(self) -> Any:
        raise NotImplementedError()
