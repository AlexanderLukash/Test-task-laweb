import random
import re
from urllib.parse import urlparse

import aiohttp
import phonenumbers
from services.requests.data import (
    operators,
    ukrainian_names,
)


def extract_domain(url: str) -> str | None:
    """Виділяє домен з URL."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain[4:] if domain.startswith("www.") else domain if domain else None


# Функція для генерації випадкового українського імені
def generate_name():
    return random.choice(ukrainian_names)


# Функція для генерації українського номера телефону з кодом оператора
def generate_phone_number():
    operator_name = random.choice(list(operators.keys()))
    operator_code = random.choice(operators[operator_name])
    phone_number = phonenumbers.parse(
        f"+380{operator_code}{random.randint(1000000, 9999999)}",
        None,
    )
    return phonenumbers.format_number(
        phone_number,
        phonenumbers.PhoneNumberFormat.INTERNATIONAL,
    )


def is_valid_url(url):
    url_pattern = re.compile(
        r"^(?:http|ftp)s?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return re.match(url_pattern, url) is not None


async def is_valid_url_aiohttp(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return response.status == 200
    except aiohttp.ClientError:
        return False
