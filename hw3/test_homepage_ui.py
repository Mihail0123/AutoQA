from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC

URL = "https://itcareerhub.de/ru"

def visible_css(d, css, t=10):
    return W(d, t).until(
        lambda x: next((e for e in x.find_elements(By.CSS_SELECTOR, css) if e.is_displayed()), None)
    )

def present_css(d, css, t=10):
    return W(d, t).until(lambda x: x.find_elements(By.CSS_SELECTOR, css))

def click_js(d, el):
    try:
        el.click()
    except Exception:
        d.execute_script("arguments[0].click()", el)

def accept_cookies(d):
    btns = d.find_elements(By.CSS_SELECTOR, "button, a, [role='button']")
    keys = ("принять", "соглас", "ok", "accept", "agree")
    for b in btns:
        text = (b.text or b.get_attribute("aria-label") or "").strip().lower()
        if any(k in text for k in keys) and b.is_displayed():
            click_js(d, b)
            break

def get_lang(d):
    lang = (d.execute_script("return document.documentElement.lang || ''") or "").lower()
    if lang.startswith("ru"): return "ru"
    if lang.startswith("de"): return "de"
    if "/ru" in d.current_url: return "ru"
    if "/de" in d.current_url: return "de"
    return "ru"

def switch_lang(d, target):
    if target == "de":
        links = d.find_elements(By.CSS_SELECTOR, "a[href*='/de']")
    else:
        links = d.find_elements(By.CSS_SELECTOR, "a[href*='/ru']")
    assert links, f"language link '{target}' not found"
    click_js(d, links[0])
    W(d, 10).until(lambda x: target in (x.current_url.lower() + " " + (x.execute_script("return document.documentElement.lang||''") or "").lower()))

def text_in_body(d):
    return (d.execute_script("return document.body && document.body.innerText || ''") or "").lower()

def test_homepage_smoke(driver):
    d = driver
    d.get(URL)
    accept_cookies(d)

    visible_css(d, "header img, header svg, [class*='logo' i], [class*='brand' i]")

    for txt in ["Программы", "Способы оплаты", "Новости", "О нас", "Отзывы"]:
        W(d, 10).until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, txt)))

    present_css(d, "a[href*='/ru']")
    present_css(d, "a[href*='/de']")

    cur = get_lang(d)
    tgt = "de" if cur == "ru" else "ru"
    switch_lang(d, tgt)
    assert get_lang(d) == tgt

    phone = None
    for css in [
        "a[href^='tel:']",
        "[aria-label*='phone' i], [aria-label*='телефон' i]",
        ".phone, .call, .callback",
        "header a, header button",
    ]:
        cand = [e for e in d.find_elements(By.CSS_SELECTOR, css) if e.is_displayed()]
        if cand:
            phone = cand[0]
            break
    if phone:
        click_js(d, phone)

    W(d, 10).until(lambda x: "если вы не дозвонились" in text_in_body(x))
