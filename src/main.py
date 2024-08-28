from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
import time
import math
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs.log"),
        logging.StreamHandler()
    ]
)

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 5)

def acceptCookies():
    try: 
        wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Accept all")]'))).click()
        time.sleep(1)
    except Exception: 
        pass

def userName():
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="popover-login" and .//*[contains(text(),"Log in")]]'))).click()

    elem = wait.until(EC.element_to_be_clickable((By.ID, 'username')))
    elem.click()
    elem.send_keys(os.getenv('DISNAT_USER'))
    elem.send_keys(Keys.RETURN)

def securityQuestion(id, value):
    questionId = wait.until(EC.presence_of_element_located((By.ID, 'idQuestion'))).get_attribute('value')
    
    if questionId != id:
        return False
    
    elem = wait.until(EC.element_to_be_clickable((By.ID, 'answer')))
    elem.click()
    elem.send_keys(value)
    elem.send_keys(Keys.RETURN)
    return True

def password():
    elem = wait.until(EC.element_to_be_clickable((By.ID, 'j_password')))
    elem.click()
    elem.send_keys(os.getenv('DISNAT_PASSWORD'))
    elem.send_keys(Keys.RETURN)

def trade(folioName, symbolCode, percentageOfTotalAccount):
    # Does not work for some reason...
    # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="site-header" and .//a[@data-menu-item="orders"]]'))).click()
    browser.get('https://tmw.secure.vmd.ca/s9web/secure/orders')
    time.sleep(1)

    select = Select(wait.until(EC.element_to_be_clickable((By.ID, 'trade-account'))))
    select.select_by_visible_text(folioName)

    select = Select(wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[id^="trade-transaction"]'))))
    select.select_by_visible_text('Buy')

    elem = wait.until(EC.element_to_be_clickable((By.ID, 'trade-symbol')))
    elem.click()
    elem.send_keys(symbolCode)
    time.sleep(1)
    elem.send_keys(Keys.RETURN)

    available = wait.until(EC.presence_of_element_located((By.XPATH, '//*[starts-with(@data-test-field,"buy_power_")]'))).get_attribute("data-test-value")
    currentPrice = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@domid="LastPrice"]'))).text

    qty = math.floor(float(available) * float(percentageOfTotalAccount) / float(currentPrice))

    if qty <= 0:
        logging.info('Not enough funds')
        return

    elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id^="trade-quantity"]')))
    elem.click()
    elem.send_keys(qty)

    wait.until(EC.element_to_be_clickable((By.XPATH, '//label[contains(text(),"Market")]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Verify")]'))).click()
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(),"Confirmation")]'))).click()
    except Exception:
        pass

    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(),"Warning")]'))).click()
    except Exception:
        pass
        
    wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-test-button="submit"]'))).click()
    time.sleep(5)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(),"Your order is executed")]')))
    
    logging.info('TRANSACTION: %s units (%s$/each) %s bought successfully from "%s" for the total price of %s$', qty, currentPrice, symbolCode, folioName, qty * float(currentPrice))

try: 
    browser.get('https://www.disnat.com/en')

    acceptCookies()
    userName()
    if not securityQuestion(os.getenv('DISNAT_SECURITY_QUESTION_ID1'), os.getenv('DISNAT_SECURITY_QUESTION_RESPONSE1')):
        if not securityQuestion(os.getenv('DISNAT_SECURITY_QUESTION_ID2'), os.getenv('DISNAT_SECURITY_QUESTION_RESPONSE2')):
            securityQuestion(os.getenv('DISNAT_SECURITY_QUESTION_ID3'), os.getenv('DISNAT_SECURITY_QUESTION_RESPONSE3'))

    acceptCookies()
    password()

    amoutPercent1 = float(os.getenv('AMOUNT_PERCENTAGE1')) if os.getenv('AMOUNT_PERCENTAGE1') else float(0)
    amoutPercent2 = float(os.getenv('AMOUNT_PERCENTAGE2')) if os.getenv('AMOUNT_PERCENTAGE2') else float(0)
    
    if os.getenv('DISNAT_SYMBOL_CODE1') and amoutPercent1 > 0:
        trade(os.getenv('DISNAT_FOLIO_NAME'), os.getenv('DISNAT_SYMBOL_CODE1'), amoutPercent1)
    if os.getenv('DISNAT_SYMBOL_CODE2') and amoutPercent2 > 0:
        trade(os.getenv('DISNAT_FOLIO_NAME'), os.getenv('DISNAT_SYMBOL_CODE2'), amoutPercent1 + amoutPercent2)
except:
    logging.exception('Exception occurred')
finally:
    time.sleep(10)
    browser.quit()
