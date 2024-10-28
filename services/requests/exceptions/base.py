from dataclasses import dataclass


@dataclass(eq=False)
class RequestException(Exception):
    @property
    def message(self):
        return "❌ Під час обробки запиту виникла помилка."
