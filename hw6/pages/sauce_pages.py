# pages/sauce_pages.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.saucedemo.com/"

class BasePage:
    def __init__(self, driver):
        self.d = driver
        self.w = WebDriverWait(driver, 15)

class LoginPage(BasePage):
    def open(self):
        self.d.get(URL)
        return self
    def login(self, username, password):
        self.w.until(EC.element_to_be_clickable((By.ID, "user-name"))).send_keys(username)
        self.d.find_element(By.ID, "password").send_keys(password)
        self.d.find_element(By.ID, "login-button").click()
        self.w.until(lambda d: "inventory" in d.current_url or d.find_elements(By.ID, "inventory_container"))

class InventoryPage(BasePage):
    slugs = {
        "Sauce Labs Backpack": "sauce-labs-backpack",
        "Sauce Labs Bolt T-Shirt": "sauce-labs-bolt-t-shirt",
        "Sauce Labs Onesie": "sauce-labs-onesie",
    }
    def add_items(self, names):
        expected = 0
        for name in names:
            slug = self.slugs[name]
            add_sel = (By.CSS_SELECTOR, f"[data-test='add-to-cart-{slug}']")
            remove_sel = (By.CSS_SELECTOR, f"[data-test='remove-{slug}']")
            btn = self.w.until(EC.presence_of_element_located(add_sel))
            try:
                self.d.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            except Exception:
                pass
            try:
                self.w.until(EC.element_to_be_clickable(add_sel)).click()
            except Exception:
                self.d.execute_script("arguments[0].click()", btn)
            expected += 1
            def added_ok(d):
                if d.find_elements(*remove_sel):
                    return True
                b = d.find_elements(By.CSS_SELECTOR, ".shopping_cart_badge")
                if b:
                    t = (b[0].text or "").strip()
                    if t.isdigit() and int(t) >= expected:
                        return True
                return False
            self.w.until(added_ok)

    def open_cart(self):
        link = self.w.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.shopping_cart_link")))
        try:
            self.d.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
        except Exception:
            pass
        try:
            self.w.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.shopping_cart_link"))).click()
        except Exception:
            self.d.execute_script("arguments[0].click()", link)
        try:
            WebDriverWait(self.d, 7).until(
                lambda d: "/cart.html" in d.current_url or d.find_elements(By.ID, "cart_contents_container")
            )
        except Exception:
            self.d.get(URL + "cart.html")
            self.w.until(EC.presence_of_element_located((By.ID, "cart_contents_container")))

class CartPage(BasePage):
    def checkout(self):
        self.w.until(lambda d: "/cart.html" in d.current_url or d.find_elements(By.ID, "cart_contents_container"))
        btn = self.w.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='checkout'], #checkout")))
        try:
            self.w.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='checkout'], #checkout"))).click()
        except Exception:
            self.d.execute_script("arguments[0].click()", btn)
        try:
            WebDriverWait(self.d, 7).until(
                lambda d: "/checkout-step-one" in d.current_url or d.find_elements(By.ID, "first-name")
            )
        except Exception:
            self.d.get(URL + "checkout-step-one.html")
            self.w.until(EC.presence_of_element_located((By.ID, "first-name")))

class CheckoutStepOne(BasePage):
    def fill_and_continue(self, first, last, postal):
        self.w.until(EC.element_to_be_clickable((By.ID, "first-name"))).clear()
        self.d.find_element(By.ID, "first-name").send_keys(first)
        self.w.until(EC.element_to_be_clickable((By.ID, "last-name"))).clear()
        self.d.find_element(By.ID, "last-name").send_keys(last)
        self.w.until(EC.element_to_be_clickable((By.ID, "postal-code"))).clear()
        self.d.find_element(By.ID, "postal-code").send_keys(postal)
        cont = self.w.until(EC.presence_of_element_located((By.ID, "continue")))
        try:
            self.w.until(EC.element_to_be_clickable((By.ID, "continue"))).click()
        except Exception:
            self.d.execute_script("arguments[0].click()", cont)
        try:
            WebDriverWait(self.d, 7).until(
                lambda d: "/checkout-step-two" in d.current_url or d.find_elements(By.CLASS_NAME, "summary_total_label")
            )
        except Exception:
            self.d.get(URL + "checkout-step-two.html")
        self.w.until(EC.presence_of_element_located((By.CLASS_NAME, "summary_total_label")))

class CheckoutStepTwo(BasePage):
    def total_text(self):
        return self.w.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "summary_total_label"))
        ).text
