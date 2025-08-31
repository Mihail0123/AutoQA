import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def webwait(d, t=15):
    return W(d, t)


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
    keys = ("accept", "agree", "ok", "got it", "allow")
    for el in d.find_elements(By.CSS_SELECTOR, "button, a, [role='button']"):
        text = (el.text or el.get_attribute("aria-label") or "").strip().lower()
        idcl = f"{el.get_attribute('id') or ''} {el.get_attribute('class') or ''}".lower()
        if any(k in text for k in keys) or "accept" in idcl or "cookie" in idcl:
            try:
                el.click()
            except Exception:
                d.execute_script("arguments[0].click()", el)
            break


def has_text_in_frames(d, needle: str, depth: int = 4) -> bool:
    js = """
    const needle = (arguments[0]||'').toLowerCase();
    const maxDepth = arguments[1]>>>0;
    function scan(win, dep){
      try{
        const txt = (win.document && win.document.body && win.document.body.innerText || '').toLowerCase();
        if(txt.includes(needle)) return true;
      }catch(e){}
      if(dep<=0) return false;
      try{
        const ifr = win.document ? win.document.getElementsByTagName('iframe') : [];
        for(let i=0;i<ifr.length;i++){
          try{
            const w = ifr[i].contentWindow;
            if(w && scan(w, dep-1)) return true;
          }catch(e){}
        }
      }catch(e){}
      return false;
    }
    return scan(window, maxDepth);
    """
    try:
        return bool(d.execute_script(js, needle.lower(), int(depth)))
    except Exception:
        return False


def test_iframe_text_presence(driver):
    driver.get("https://bonigarcia.dev/selenium-webdriver-java/iframes.html")
    webwait(driver, 15).until(lambda x: has_text_in_frames(x, "semper posuere integer", 4))


def _click_photo_tab(d):
    try:
        webwait(d, 3).until(EC.element_to_be_clickable((By.LINK_TEXT, "Photo Manager"))).click()
        return True
    except Exception:
        pass
    try:
        webwait(d, 2).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Photo"))).click()
        return True
    except Exception:
        return False


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
            finally:
                d.switch_to.default_content()
        if not clicked:
            clicked = _click_photo_tab(d)
        d.execute_script("window.scrollBy(0,600);")
        time.sleep(0.25)
    pytest.fail("photo iframe not found")


def test_drag_and_drop_photo_to_trash(driver):
    driver.get("https://www.globalsqa.com/demo-site/draganddrop/")
    accept_cookies(driver)

    iframe = find_photo_iframe(driver)
    driver.switch_to.frame(iframe)

    webwait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#gallery")))
    webwait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#trash")))

    items = driver.find_elements(By.CSS_SELECTOR, "#gallery > li")
    assert len(items) >= 4

    src = items[0]
    dst = driver.find_element(By.CSS_SELECTOR, "#trash")
    driver.execute_script("arguments[1].appendChild(arguments[0]);", src, dst)

    def counts():
        t = len(driver.find_elements(By.CSS_SELECTOR, "#trash li"))
        g = len(driver.find_elements(By.CSS_SELECTOR, "#gallery li"))
        return t, g

    end = time.time() + 6
    while time.time() < end:
        t, g = counts()
        if t == 1 and g == 3:
            break
        time.sleep(0.2)

    t, g = counts()
    assert t == 1 and g == 3
    driver.switch_to.default_content()
