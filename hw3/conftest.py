import os
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

@pytest.fixture
def driver():
    opts = FirefoxOptions()
    if os.getenv("HEADLESS") == "1":
        opts.add_argument("-headless")
    opts.set_preference("intl.accept_languages", "ru,ru-RU,en-US,en")
    opts.set_preference("dom.webnotifications.enabled", False)
    d = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=opts)
    d.set_window_size(1400, 1000)
    yield d
    d.quit()
