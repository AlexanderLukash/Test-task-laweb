from aiogram.fsm.state import (
    State,
    StatesGroup,
)


class ChangeUserStatusState(StatesGroup):
    """Стан для зміни статусу користувача"""

    id = State()
    status = State()


class AddDomainToWhitelistState(StatesGroup):
    """Стан для додавання домену до вайтлиста"""

    domain = State()


class DeleteDomainFromWhitelistState(StatesGroup):
    """Стан для видалення домену з вайтлиста"""

    domain = State()


class StartApplicationState(StatesGroup):
    """Стан для налаштування та запуску відправки заявок"""

    url = State()
    duration = State()
    delay = State()
