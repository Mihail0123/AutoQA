from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://itcareerhub.de/ru"
OUT = Path("artifacts/payment_methods.png")

def main():
    opts = Options()
    # если нужно — включай headless:
    # opts.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=opts)
    try:
        driver.get(URL)
        driver.set_window_size(1600, 1400)  # чтобы вся секция влезла

        # куки (если появятся)
        for xp in [
            "//button[contains(translate(., 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ','абвгдеёжзийклмнопрстуфхцчшщъыьэюя'),'принять')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'accept')]",
            "//button[normalize-space()='OK' or normalize-space()='Ok']",
        ]:
            try:
                WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, xp))
                ).click()
                break
            except Exception:
                pass

        # прокрутка к заголовку секции
        heading = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[self::h1 or self::h2 or self::h3]"
                           "[contains(normalize-space(.),'Способы оплаты')]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'start'});", heading)
        driver.execute_script("window.scrollBy(0, -80);")  # на случай липкого хедера

        # дождаться, пока в секции появится любая карточка
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(.,'Рассрочка') or contains(.,'100% оплата') or contains(.,'Bildungsgutschein')]")
            )
        )
        time.sleep(0.3)

        OUT.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(OUT))
        print(f"Saved: {OUT.resolve()}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
