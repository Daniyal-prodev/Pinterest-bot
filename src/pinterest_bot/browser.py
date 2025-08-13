import os
import time
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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
        try:
            caps = driver.capabilities or {}
            _ = caps.get("browserVersion")
        except Exception:
            pass
        yield driver
    finally:
        try:
            driver.quit()
        except Exception:
            pass

def _is_login_page(driver) -> bool:
    url = driver.current_url.lower()
    if "login" in url or "auth" in url:
        return True
    try:
        btns = driver.find_elements(By.XPATH, "//a[contains(.,'Log in')]|//button[contains(.,'Log in')]")
        if btns:
            return True
    except Exception:
        pass
    return False

def ensure_logged_in(driver, max_wait_seconds: int = 180):
    driver.get("https://www.pinterest.com/")
    try:
        WebDriverWait(driver, 15).until(lambda d: "pinterest.com" in d.current_url)
    except Exception:
        pass
    start = time.time()
    while True:
        if not _is_login_page(driver):
            try:
                driver.get("https://www.pinterest.com/pin-creation-tool/")
                WebDriverWait(driver, 15).until(lambda d: "pin-creation-tool" in d.current_url or not _is_login_page(d))
                if not _is_login_page(driver):
                    return
            except Exception:
                pass
        time.sleep(3)
        if time.time() - start > max_wait_seconds:
            raise RuntimeError("Pinterest login not detected within the expected time window.")
