from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

def get_selenium_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("delete navigator.__proto__.webdriver")
    return driver

def set_store_to_20012(driver, postcode="20012", timeout=20):
    driver.get("https://www.online.bmsupermercados.es/es")
    wait = WebDriverWait(driver, timeout)

    try:
        # Click delivery address button
        address_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//*[@id="header__main--delivery"]/cmp-select-delivery-address/div/cmp-triple-element-block/div/div[2]/span'
            ))
        )
        address_btn.click()

        # Type postcode
        zip_input = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="form-input-zip-input"]/input'
            ))
        )
        zip_input.clear()
        zip_input.send_keys(postcode)
        zip_input.send_keys(Keys.ENTER)

        # Wait for store to be applied
        time.sleep(3)
        print(f"✅ Store set to {postcode}")
    except Exception as e:
        print(f"❌ Failed to set store: {e}")
        raise