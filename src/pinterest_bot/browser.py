import os
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

def build_chrome_options(user_data_dir: str, profile_dir: str) -> Options:
    opts = Options()
    if user_data_dir:
        opts.add_argument(f"--user-data-dir={user_data_dir}")
    if profile_dir:
        opts.add_argument(f"--profile-directory={profile_dir}")
    opts.add_argument("--start-maximized")
    return opts

@contextmanager
def get_driver(user_data_dir: str, profile_dir: str, timeout: int = 20):
    options = build_chrome_options(user_data_dir, profile_dir)
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    try:
        yield driver
    finally:
        try:
            driver.quit()
        except Exception:
            pass

def ensure_logged_in(driver):
    driver.get("https://www.pinterest.com/")
    try:
        WebDriverWait(driver, 10).until(lambda d: "pinterest.com" in d.current_url)
    except Exception:
        pass
    input("If you are not logged in, please log in to Pinterest in the opened Chrome window. Press Enter here to continue when ready...")
