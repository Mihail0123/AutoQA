from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC

URL = "https://itcareerhub.de/ru"

def wait_ready(d):
    W(d, 20).until(lambda x: x.execute_script("return document.readyState") == "complete")

def visible_css(d, css, t=12):
    return W(d, t).until(
        lambda x: next((e for e in x.find_elements(By.CSS_SELECTOR, css) if e.is_displayed()), None)
    )

def click_js(d, el):
    try:
        el.click()
    except Exception:
        d.execute_script("arguments[0].click()", el)

def accept_cookies(d):
    keys = ("принять", "соглас", "ok", "accept", "agree")
    for el in d.find_elements(By.CSS_SELECTOR, "button, a, [role='button']"):
        text = (el.text or el.get_attribute("aria-label") or "").strip().lower()
        if any(k in text for k in keys) and el.is_displayed():
            click_js(d, el)
            break

def any_visible_css(d, selectors, t=12):
    for css in selectors:
        try:
            el = visible_css(d, css, t=2)
            if el:
                return el
        except Exception:
            pass
    raise AssertionError("element not found by provided CSS list")

def find_logo_js(d):
    return d.execute_script("""
        const roots=[document.querySelector('header'),
                     document.querySelector('[role=banner]'),
                     document.querySelector('nav'),
                     document.body].filter(Boolean);
        for(const root of roots){
          const all=[...root.querySelectorAll('*')];
          for(const e of all){
            const cls=(e.className||'').toString().toLowerCase();
            const txt=((e.textContent||'')+(e.getAttribute('aria-label')||'')).toLowerCase();
            const bg=getComputedStyle(e).backgroundImage;
            const ok=(e.tagName==='IMG'||e.tagName==='SVG'||cls.includes('logo')||
                      cls.includes('brand')||txt.includes('logo')||txt.includes('itcareerhub')||
                      (bg && bg!=='none'));
            if(ok && e.offsetParent!==null) return e;
          }
        }
        return null;
    """)

def get_lang(d):
    lang = (d.execute_script("return document.documentElement.lang || ''") or "").lower()
    if lang.startswith("ru"): return "ru"
    if lang.startswith("de"): return "de"
    if lang.startswith("en"): return "en"
    u = d.current_url.lower()
    if "/ru" in u: return "ru"
    if "/de" in u: return "de"
    if "/en" in u: return "en"
    return "ru"

def find_lang_el(d, target):
    css_list = [
        f"a[href*='/{target}']",
        f"a[hreflang='{target}']",
        f"[data-lang='{target}'], [data-locale='{target}']",
        f"a[href*='lang={target}']",
    ]
    for css in css_list:
        els = [e for e in d.find_elements(By.CSS_SELECTOR, css) if e.is_displayed()]
        if els:
            return els[0]
    return d.execute_script(r"""
        const t=arguments[0].toLowerCase();
        const nodes=[...document.querySelectorAll("a,button,[role='button'],li,div,span")];
        return nodes.find(n=>{
          if(!n.offsetParent) return false;
          const txt=(n.textContent||"").trim().toLowerCase();
          const lab=(n.getAttribute('aria-label')||"").toLowerCase();
          return txt===t || txt.split(/\s+/).includes(t) || lab.includes(t);
        }) || null;
    """, target)

def available_langs(d):
    langs = set()
    for code in ("ru","de","en"):
        if find_lang_el(d, code) is not None:
            langs.add(code)
    return langs

def try_switch_lang(d, target):
    if get_lang(d) == target:
        return True
    el = find_lang_el(d, target)
    if el is not None:
        href = (el.get_attribute("href") or "").strip()
        if href:
            if href.startswith("http"):
                d.get(href)
            else:
                base = d.execute_script("return location.origin")
                d.get(base + href)
        else:
            click_js(d, el)
    else:
        base = d.execute_script("return location.origin")
        d.get(base + ("/de" if target == "de" else "/en" if target == "en" else "/ru"))
    try:
        W(d, 8).until(lambda x: target in (x.current_url.lower() + " " + (x.execute_script("return document.documentElement.lang||''") or "").lower()))
        accept_cookies(d)
        return True
    except Exception:
        return False

def text_in_body(d):
    return (d.execute_script("return document.body && document.body.innerText || ''") or "").lower()

def has_contact_hint(d):
    txt = text_in_body(d)
    if "не дозвонились" in txt or "свяжемся с вами" in txt or "перезвоним" in txt:
        return True
    if any(e.is_displayed() for e in d.find_elements(By.CSS_SELECTOR, "[role='dialog'], .modal, .popup")):
        return True
    if any(e.is_displayed() for e in d.find_elements(By.CSS_SELECTOR, "form[action*='contact' i], form[action*='feedback' i], input[type='tel'], [name*='phone' i]")):
        return True
    if d.find_elements(By.CSS_SELECTOR, "a[href^='tel:']"):
        return True
    return False

def test_homepage_smoke(driver):
    d = driver
    d.get(URL)
    wait_ready(d)
    accept_cookies(d)

    try:
        any_visible_css(d, [
            "header img, header svg",
            "[role='banner'] img, [role='banner'] svg",
            "[class*='logo' i], [class*='brand' i]",
            "a[href='/'], a[href='/ru']",
        ])
    except AssertionError:
        el = find_logo_js(d)
        assert el is not None, "logo not found"

    for txt in ["Программы", "Способы оплаты", "Новости", "О нас", "Отзывы"]:
        W(d, 12).until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, txt)))

    langs = available_langs(d)
    if "de" in langs or "en" in langs:
        target = "de" if "de" in langs else "en"
        try_switch_lang(d, target)
        try_switch_lang(d, "ru")

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

    W(d, 12).until(lambda x: has_contact_hint(x))
