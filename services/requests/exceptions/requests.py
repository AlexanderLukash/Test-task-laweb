from dataclasses import dataclass

from services.requests.exceptions.base import RequestException


@dataclass(eq=False)
class FormNotFoundException(RequestException):
    @property
    def message(self):
        return "❌ Форма не знайдена."


@dataclass(eq=False)
class SiteUnavailableException(RequestException):
    @property
    def message(self):
        return "❌ Сайт недоступний."


@dataclass(eq=False)
class ProxyErrorException(RequestException):
    @property
    def message(self):
        return "❌ Проблема з проксі."


@dataclass(eq=False)
class FormSubmissionFailedException(RequestException):
    @property
    def message(self):
        return "❌ Не вдалося відправити заявку."
