PROXY_URL = "brd.superproxy.io:33335"
PROXY_USER = "brd-customer-hl_60f0fc08-zone-datacenter_proxy1-country-es"
PROXY_PASS = "nfm9jwtumvpo"
PROXY_WITH_AUTH = f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}'
PROXIES = {'http': PROXY_WITH_AUTH, 'https': PROXY_WITH_AUTH}

API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.online.bmsupermercados.es/es/c/bebidas/1690',
    'Accept': 'application/json, text/plain, */*'
}
