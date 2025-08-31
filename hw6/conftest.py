import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
