import time


def get_location_cookies(driver):
    initial_url = "https://www.online.bmsupermercados.es/es/c/bebidas/1690"
    
    try:
        driver.get(initial_url)
        print(f"Navegando a: {initial_url} para configurar ubicación.")
        
        time.sleep(10)
        selenium_cookies = driver.get_cookies()
        requests_cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        
        if not requests_cookies:
            print("No se pudieron obtener cookies completas. Intentando con las disponibles...")

        return requests_cookies

    except Exception as e:
        print(f"Error en la configuración de ubicación: {type(e).__name__}: {e}")
        return None
