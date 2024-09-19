import random
from app.constants import CHARACTERS, SHORT_ID_LENGTH


def generate_short_id(length: int = SHORT_ID_LENGTH) -> str:
    return ''.join(random.choices(CHARACTERS, k=length))
