import os
from dotenv import load_dotenv

load_dotenv()

PROXY_URL = os.getenv('PROXY_URL', 'brd.superproxy.io:33335')
PROXY_USER = os.getenv('PROXY_USER', '')
PROXY_PASS = os.getenv('PROXY_PASS', '')

if not PROXY_USER or not PROXY_PASS:
    raise ValueError(
        "Las credenciales del proxy deben estar configuradas en variables de entorno. "
        "Crea un archivo .env con PROXY_USER y PROXY_PASS"
    )

PROXY_WITH_AUTH = f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}'
PROXIES = {'http': PROXY_WITH_AUTH, 'https': PROXY_WITH_AUTH}

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

API_HEADERS = {
    **DEFAULT_HEADERS,
    'Referer': 'https://www.online.bmsupermercados.es/es/c/bebidas/1690',
    'X-Requested-With': 'XMLHttpRequest',
}
