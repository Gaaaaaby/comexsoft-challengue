
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

os.makedirs("screenshots", exist_ok=True)

def safe_find_element(driver, by, selector, timeout=5):
    """Busca elementos de forma segura sin stacktraces feos"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except:
        return None

def test_bm_improved():
    PROXY_URL = "brd.superproxy.io:33335"
    PROXY_USER = "brd-customer-hl_60f0fc08-zone-datacenter_proxy1-country-es"
    PROXY_PASS = "nfm9jwtumvpo"

    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Silenciar logs de DevTools
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--log-level=3')
    
    proxy_with_auth = f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}'
    options.add_argument(f'--proxy-server={proxy_with_auth}')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    try:
        print("📍 Step 1: Opening BM homepage...")
        driver.get("https://www.online.bmsupermercados.es/es")
        time.sleep(3)
        print(f"   ➤ Current URL: {driver.current_url}")
        driver.save_screenshot("screenshots/01_homepage.png")
        
        # Manejo de cookies simplificado
        print("🍪 Handling cookies...")
        cookie_selectors = ["#onetrust-accept-btn-handler", ".cookie-accept"]
        for selector in cookie_selectors:
            btn = safe_find_element(driver, By.CSS_SELECTOR, selector, 3)
            if btn and btn.is_displayed():
                btn.click()
                print("   ➤ Cookies accepted")
                time.sleep(1)
                break
        
        driver.save_screenshot("screenshots/02_after_cookies.png")

        # Verificar si hay popup de ubicación (sin errores visibles)
        print("📍 Checking for location popup...")
        zip_input = safe_find_element(driver, By.CSS_SELECTOR, 'input#zipcode', 3)
        
        if zip_input and zip_input.is_displayed():
            print("   ➤ Popup found! Entering postal code...")
            zip_input.clear()
            zip_input.send_keys("20012")
            zip_input.send_keys(Keys.ENTER)
            time.sleep(3)
            driver.save_screenshot("screenshots/03_popup_handled.png")
        else:
            print("   ➤ No popup found - continuing")
        
        # Navegar a Bebidas
        print("📍 Step 3: Navigating to Bebidas...")
        bebidas_url = "https://www.online.bmsupermercados.es/es/c/bebidas/1690"
        driver.get(bebidas_url)
        
        # Esperar a que cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print(f"   ➤ Bebidas page loaded: {driver.current_url}")
        driver.save_screenshot("screenshots/04_bebidas_loaded.png")
        
        # Buscar productos de forma más específica
        print("🔍 Searching for products...")
        
        # Intentar diferentes selectores de productos
        product_selectors = [
            "div[class*='product']",
            ".product-item",
            "[data-product]",
            "article[class*='item']"
        ]
        
        for selector in product_selectors:
            products = driver.find_elements(By.CSS_SELECTOR, selector)
            if products:
                print(f"   ➤ Found {len(products)} products with selector: {selector}")
                if len(products) > 0:
                    # Mostrar información del primer producto
                    try:
                        product_text = products[0].text.split('\n')[0] if products[0].text else "No text"
                        print(f"   ➤ First product: {product_text[:50]}...")
                    except:
                        print("   ➤ Product found but couldn't read details")
                break
        else:
            print("   ➤ No standard product elements found")
            # Mostrar qué elementos sí hay en la página
            all_elements = driver.find_elements(By.CSS_SELECTOR, "div, article, section")
            print(f"   ➤ Page contains {len(all_elements)} div/article/section elements")

        print("\n✅ Test completed successfully!")
        print("📷 Check screenshots folder for visual confirmation")

    except Exception as e:
        print(f"💥 Error: {e}")

    finally:
        if 'driver' in locals():
            time.sleep(2)
            driver.quit()

if __name__ == "__main__":
    test_bm_improved()
