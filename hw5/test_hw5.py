# hw5/test_hw5.py
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def W(d, t=15): return WebDriverWait(d, t)


@pytest.fixture
def driver():
    opts = Options()
    if os.getenv("HEADLESS") == "1":
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1600,1200")
    d = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    d.set_window_size(1500, 1000)
    yield d
    d.quit()


def accept_cookies(d):
    for xp in [
        "//button[normalize-space()='Accept']",
        "//*[@id='accept' or contains(@id,'accept') or contains(@class,'accept')]",
        "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'accept')]",
        "//button[normalize-space()='OK' or normalize-space()='Ok']",
    ]:
        try:
            W(d, 2).until(EC.element_to_be_clickable((By.XPATH, xp))).click()
            break
        except Exception:
            pass


def body_text(d):
    try:
        return (d.execute_script("return document.body && document.body.innerText || ''") or "").lower()
    except Exception:
        return ""


def find_text_in_frames(d, needle, depth=3):
    if needle in body_text(d): return True
    if depth <= 0: return False
    for fr in d.find_elements(By.TAG_NAME, "iframe"):
        try:
            d.switch_to.frame(fr)
            if find_text_in_frames(d, needle, depth - 1): return True
        finally:
            d.switch_to.parent_frame()
    return False


def test_iframe_text_presence(driver):
    driver.get("https://bonigarcia.dev/selenium-webdriver-java/iframes.html")
    W(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "iframe")))
    assert find_text_in_frames(driver, "semper posuere integer", 4)


def find_photo_iframe(d, timeout=15):
    end = time.time() + timeout
    clicked = False
    while time.time() < end:
        for f in d.find_elements(By.TAG_NAME, "iframe"):
            try:
                d.switch_to.default_content()
                d.execute_script("arguments[0].scrollIntoView({block:'center'});", f)
                d.switch_to.frame(f)
                if d.find_elements(By.CSS_SELECTOR, "#gallery") and d.find_elements(By.CSS_SELECTOR, "#trash"):
                    d.switch_to.default_content()
                    return f
            except Exception:
                d.switch_to.default_content()
        d.switch_to.default_content()
        if not clicked:
            for xp in [
                "//a[contains(.,'Photo Manager')]",
                "//a[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'photo')]",
            ]:
                try:
                    el = WebDriverWait(d, 2).until(EC.element_to_be_clickable((By.XPATH, xp)))
                    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                    el.click()
                    clicked = True
                    break
                except Exception:
                    continue
        d.execute_script("window.scrollBy(0,600);")
        time.sleep(0.3)
    pytest.fail("photo iframe not found")


def test_drag_and_drop_photo_to_trash(driver):
    driver.get("https://www.globalsqa.com/demo-site/draganddrop/")
    accept_cookies(driver)

    iframe = find_photo_iframe(driver)
    driver.switch_to.frame(iframe)

    W(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#gallery")))
    W(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#trash")))

    items = driver.find_elements(By.CSS_SELECTOR, "#gallery > li")
    assert len(items) >= 4

    src = items[0]
    dst = driver.find_element(By.CSS_SELECTOR, "#trash")
    driver.execute_script("arguments[1].appendChild(arguments[0]);", src, dst)

    def counts():
        return len(driver.find_elements(By.CSS_SELECTOR, "#trash li")), len(driver.find_elements(By.CSS_SELECTOR, "#gallery li"))

    end = time.time() + 6
    while time.time() < end:
        t, g = counts()
        if t == 1 and g == 3: break
        time.sleep(0.2)

    t, g = counts()
    assert t == 1 and g == 3
    driver.switch_to.default_content()