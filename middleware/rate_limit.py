from slowapi import Limiter
from slowapi.util import get_remote_address
from config import get_settings

settings = get_settings()  # pragma: no cover


def get_client_ip(request):  # pragma: no cover
    return get_remote_address(request)


limiter = Limiter(key_func=get_client_ip)  # pragma: no cover
