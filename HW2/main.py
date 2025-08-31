from pathlib import Path
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

URL = "https://itcareerhub.de/ru"
OUT = Path("artifacts/payment_methods.png")

def make_driver():
    opts = FirefoxOptions()
    if os.getenv("HEADLESS") == "1":
        opts.add_argument("-headless")
    opts.set_preference("intl.accept_languages", "ru,ru-RU,en-US,en")
    opts.set_preference("dom.webnotifications.enabled", False)
    d = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=opts)
    d.set_window_size(1600, 1200)
    return d

def click_cookies(d):
    texts = ("принять", "соглас", "ok", "accept", "agree")
    end = time.time() + 6
    while time.time() < end:
        for el in d.find_elements(By.CSS_SELECTOR, "button, a, [role='button']"):
            label = (el.text or el.get_attribute("aria-label") or "").strip().lower()
            if any(t in label for t in texts) and el.is_displayed():
                try:
                    el.click()
                except Exception:
                    d.execute_script("arguments[0].click()", el)
                return
        time.sleep(0.2)

def find_payment_section(d):
    return d.execute_script("""
        const needle="способы оплаты";
        const hs=[...document.querySelectorAll("h1,h2,h3,h4")];
        const h=hs.find(e=>((e.textContent||"").toLowerCase().includes(needle)));
        if(!h) return null;
        let node=h.closest("section")||h.parentElement, cur=node||h;
        for(let i=0;i<6&&cur;i++){
            const r=cur.getBoundingClientRect();
            if(r.height>320) return cur;
            cur=cur.parentElement;
        }
        return node||h;
    """)

def main():
    d = make_driver()
    try:
        d.get(URL)
        click_cookies(d)
        sec = W(d, 15).until(lambda x: find_payment_section(x))
        d.execute_script("arguments[0].scrollIntoView({block:'start'});", sec)
        d.execute_script("window.scrollBy(0,-80);")
        W(d, 10).until(EC.visibility_of(sec))
        time.sleep(0.3)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        sec.screenshot(str(OUT))
        print(f"Saved: {OUT.resolve()}")
    finally:
        d.quit()

if __name__ == "__main__":
    main()
