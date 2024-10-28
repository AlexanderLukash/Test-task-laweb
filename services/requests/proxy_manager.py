import json
import logging
import random
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    List,
    Optional,
)

from settings.config import Config


config: Config = Config()
logger = logging.getLogger(__name__)

PROXIES_FILE = config.PROXIES_FILE_NAME


@dataclass
class Proxy:
    """Клас для представлення одного проксі-сервера"""

    use_proxy: bool
    ip: str
    port: str
    login: str
    password: str

    def get_proxy_url(self) -> Optional[str]:
        """Формує проксі URL, якщо проксі дозволений"""
        if self.use_proxy:
            return f"http://{self.login}:{self.password}@{self.ip}:{self.port}"
        return None


@dataclass
class ProxyManager:
    """Клас для керування списком проксі-серверів."""

    proxies_file: str = PROXIES_FILE
    proxies: List[Proxy] = field(default_factory=list)

    def __post_init__(self):
        self.load_from_file()

    def load_from_file(self):
        """Завантажує список проксі з JSON файлу."""
        with open(self.proxies_file) as file:
            json_data = json.load(file)
            self.proxies = [
                Proxy(**proxy_data) for proxy_data in json_data.get("proxies", [])
            ]

    def get_proxy(self) -> Optional[str]:
        """Повертає випадковий URL дозволеного проксі або None, якщо проксі не дозволені."""
        available_proxies = [proxy for proxy in self.proxies if proxy.use_proxy]
        if available_proxies:
            return random.choice(available_proxies).get_proxy_url()
        return None
