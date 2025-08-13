import time
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def _find_any(driver: WebDriver, locators: List[tuple], timeout: int = 20):
    for by, selector in locators:
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))
        except Exception:
            continue
    raise RuntimeError("Element not found with provided locator fallbacks.")

def open_pin_creator(driver: WebDriver):
    driver.get("https://www.pinterest.com/pin-creation-tool/")
    WebDriverWait(driver, 30).until(lambda d: "pin-creation-tool" in d.current_url)

def fill_title_description_tags(driver: WebDriver, title: str, description: str, tags: List[str]):
    title_locators = [
        (By.XPATH, "//input[@aria-label='Title']"),
        (By.XPATH, "//textarea[@aria-label='Title']"),
        (By.CSS_SELECTOR, "textarea[data-test-id='PinBuilderTitleField'],input[data-test-id='PinBuilderTitleField']"),
    ]
    desc_locators = [
        (By.XPATH, "//textarea[contains(@aria-label,'Description')]"),
        (By.CSS_SELECTOR, "textarea[data-test-id='PinBuilderDescriptionField']"),
    ]
    title_el = _find_any(driver, title_locators, 20)
    try:
        title_el.clear()
    except Exception:
        pass
    title_el.send_keys(title)
    desc_el = _find_any(driver, desc_locators, 20)
    try:
        desc_el.clear()
    except Exception:
        pass
    desc_el.send_keys(description)
    tags_field_locators = [
        (By.XPATH, "//input[contains(@placeholder,'Add tags')]"),
        (By.XPATH, "//input[@aria-label='Tags']"),
    ]
    tags_input = None
    try:
        tags_input = _find_any(driver, tags_field_locators, 5)
    except Exception:
        tags_input = None
    if tags_input:
        for t in tags:
            tags_input.send_keys(t)
            tags_input.send_keys("\n")
    else:
        if tags:
            hashtags = " " + " ".join(f"#{t.replace(' ', '')}" for t in tags if t)
            desc_el.send_keys(hashtags)

def upload_image(driver: WebDriver, image_path: str):
    upload_button_locators = [
        (By.XPATH, "//input[@type='file' and contains(@accept,'image')]"),
        (By.CSS_SELECTOR, "input[type='file']"),
    ]
    btn = _find_any(driver, upload_button_locators, 20)
    try:
        btn.click()
    except Exception:
        pass
    time.sleep(10)
    btn.send_keys(image_path)
    WebDriverWait(driver, 60).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "img")) > 0)

def select_board(driver: WebDriver, board_name: str):
    open_board_locators = [
        (By.XPATH, "//div[contains(@data-test-id,'board-dropdown')]//button"),
        (By.XPATH, "//button[contains(.,'Select') or contains(.,'Board')]"),
    ]
    btn = _find_any(driver, open_board_locators, 20)
    btn.click()
    item_locators = [
        (By.XPATH, f"//div//div//div[.//div[normalize-space(text())='{board_name}']]"),
        (By.XPATH, f"//div[@role='option' and .//*[normalize-space(text())='{board_name}']]"),
        (By.XPATH, f"//li[.//*[normalize-space(text())='{board_name}']]"),
    ]
    item = _find_any(driver, item_locators, 20)
    item.click()

def set_link(driver: WebDriver, url: str):
    link_locators = [
        (By.XPATH, "//input[contains(@aria-label,'destination') or contains(@placeholder,'Add a destination')]"),
        (By.CSS_SELECTOR, "input[data-test-id='PinBuilderLinkField']"),
    ]
    link_el = _find_any(driver, link_locators, 20)
    try:
        link_el.clear()
    except Exception:
        pass
    link_el.send_keys(url)

def publish(driver: WebDriver):
    publish_locators = [
        (By.XPATH, "//button[normalize-space()='Publish']"),
        (By.XPATH, "//div[@role='button' and normalize-space()='Publish']"),
        (By.CSS_SELECTOR, "button[data-test-id='board-select-done'],button[type='submit']"),
    ]
    btn = _find_any(driver, publish_locators, 20)
    btn.click()
    WebDriverWait(driver, 60).until(lambda d: "pin-creation-tool" not in d.current_url)
