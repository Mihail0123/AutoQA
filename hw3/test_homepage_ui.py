import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://itcareerhub.de/ru"

def w(driver, t=15):
    return WebDriverWait(driver, t)

@pytest.fixture
def driver():
    opts = Options()
    if os.getenv("HEADLESS") == "1":
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1600,1200")
    d = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    d.set_window_size(1600, 1000)
    yield d
    d.quit()

def accept_cookies(d):
    for xp in [
        "//button[contains(translate(.,'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ','абвгдеёжзийклмнопрстуфхцчшщъыьэюя'),'принять')]",
        "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'accept')]",
        "//button[normalize-space()='OK' or normalize-space()='Ok']",
    ]:
        try:
            w(d, 2).until(EC.element_to_be_clickable((By.XPATH, xp))).click()
            break
        except Exception:
            pass

def visible(d, xp, t=12):
    return w(d, t).until(EC.visibility_of_element_located((By.XPATH, xp)))

def present(d, xp, t=8):
    return w(d, t).until(EC.presence_of_element_located((By.XPATH, xp)))

def present_any(d, xps, t=8):
    for xp in xps:
        try:
            return present(d, xp, t)
        except Exception:
            continue
    pytest.fail("Ни один из вариантов локаторов не найден.")

def any_visible(d, xpaths, t=8):
    for xp in xpaths:
        try:
            return visible(d, xp, t)
        except Exception:
            continue
    pytest.fail("Элемент не найден ни по одному из селекторов.")

def open_burger_if_exists(d):
    for xp in [
        "//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ','abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя'),'menu') or contains(.,'Меню')]",
        "//*[self::button or self::div][contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'burger') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'menu')]",
        "//*[@role='button'][contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'menu')]",
    ]:
        try:
            w(d, 2).until(EC.element_to_be_clickable((By.XPATH, xp))).click()
            return True
        except Exception:
            continue
    return False

def find_nav_link(d, text):
    header = "//*[self::header or @role='banner' or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'header')]"
    try:
        return visible(d, f"{header}//a[contains(normalize-space(.), '{text}')]")
    except Exception:
        pass
    try:
        if open_burger_if_exists(d):
            return visible(d, f"{header}//a[contains(normalize-space(.), '{text}')]")
    except Exception:
        pass
    try:
        d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        return visible(d, f"//footer//a[contains(normalize-space(.), '{text}')]")
    except Exception:
        pass
    return present(d, f"//a[contains(normalize-space(.), '{text}')]")

def present_lang(d, code: str):
    code = code.lower()
    return present_any(d, [
        f"//a[contains(@href, '/{code}') or contains(@href, '?lang={code}')]",
        f"//*[@data-lang='{code}']",
        f"//*[@lang='{code}']",
        f"//*[@aria-label='{code}' or @aria-label='lang {code}' or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),' {code} ')]",
        f"//*[self::a or self::button or self::span or self::div][normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'))='{code}']",
    ])

def test_homepage_smoke(driver):
    d = driver
    d.get(URL)
    accept_cookies(d)
    d.execute_script("window.scrollTo(0,0);")

    any_visible(d, [
        "//*[@role='banner']//*[self::img or name()='svg']",
        "//*[@role='banner']//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'logo') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'brand')]",
        "//header//*[self::img or name()='svg']",
        "//header//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'logo') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'brand')]",
        "//a[(@href='/' or @href='/ru' or starts-with(@href,'/ru')) and (.//img or .//*[name()='svg'] or contains(normalize-space(.),'ITCareerHub') or contains(normalize-space(.),'IT Career Hub'))]",
        "//*[contains(normalize-space(.),'ITCareerHub') or contains(normalize-space(.),'IT Career Hub')]",
    ])

    for text in ["Способы оплаты", "Новости", "О нас", "Отзывы"]:
        find_nav_link(d, text)

    d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    present(d, "//a[contains(normalize-space(.),'Программы') or contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'program')]")

    # Языковые переключатели: ru + de (кнопка, ссылка или span с текстом)
    present_lang(d, "ru")
    present_lang(d, "de")

    for xp in [
        "//a[starts-with(@href,'tel:')]",
        "//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ','abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя'),'phone')]",
        "//*[self::a or self::button][contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'phone') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'tel')]",
    ]:
        try:
            w(d, 3).until(EC.element_to_be_clickable((By.XPATH, xp))).click()
            break
        except Exception:
            pass

    present(d, "//*[contains(., 'Если вы не дозвонились') and contains(., 'заполните форму на сайте')]")
