import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def driver():
    opts = Options()
    if os.getenv("HEADLESS") == "1":
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1600,1200")
    d = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    d.set_window_size(1400, 1000)
    yield d
    d.quit()


def test_text_input_changes_button(driver):
    driver.get("http://uitestingplayground.com/textinput")

    inp = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "newButtonName"))
    )
    btn = driver.find_element(By.ID, "updatingButton")

    inp.clear()
    inp.send_keys("ITCH")
    btn.click()

    WebDriverWait(driver, 10).until(lambda d: btn.text == "ITCH")
    assert btn.text == "ITCH"


def test_loading_images_third_alt_is_award(driver):
    driver.get("https://bonigarcia.dev/selenium-webdriver-java/loading-images.html")

    xpath_imgs = ("//img[translate(@alt,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')="
                  "'compass' or translate(@alt,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='calendar' "
                  "or translate(@alt,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='award' "
                  "or translate(@alt,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='landscape']")
    WebDriverWait(driver, 30).until(lambda d: len(d.find_elements(By.XPATH, xpath_imgs)) >= 3)
    WebDriverWait(driver, 30).until(
        lambda d: all(img.get_attribute("complete") and int(d.execute_script("return arguments[0].naturalWidth;", img)) > 0
                      for img in d.find_elements(By.XPATH, xpath_imgs)[:3])
    )

    imgs = driver.find_elements(By.XPATH, xpath_imgs)
    third_alt = (imgs[2].get_attribute("alt") or "").strip().lower()
    assert third_alt == "award", f"Ожидали alt='award', получили: {third_alt!r}"