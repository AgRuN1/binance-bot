from urllib.parse import urlparse, parse_qs
from traceback import print_exception
from collections import deque
from time import sleep
from pickle import load

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions

from bot import bought, unlogin as unlogin_message

base_url = 'https://www.binance.com/ru/nft/market?order=list_time@-1'
base_limit = 16
new_limit = 10
max_price = 2000
base_window = 0
have_bought = deque(maxlen=100)
login = True

driver = webdriver.Chrome()

async def unlogin():
    await unlogin_message()
    global login
    login = False

def get_product_id():
    parsed_url = urlparse(driver.current_url)
    query = parse_qs(parsed_url.query)
    return int(query['productId'][0])

def check_price(price_text):
    price_text = price_text.split()[2]
    price_text = price_text.replace(',', '')
    price = float(price_text)
    return price <= max_price

async def bye():
    link = driver.current_url
    product_id = get_product_id()
    if product_id in list(have_bought):
        return
    have_bought.append(product_id)
    try:
        bye_button = driver.find_element_by_class_name('css-18fem9b')
        bye_button.click()
        wait = WebDriverWait(driver, 2)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-8jjqj6'))).click()
        await bought(link)
    except TimeoutException:
        pass

async def check():
    wait = WebDriverWait(driver, 2)
    try:
        price_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-16uf6x4')))
        if check_price(price_element.text):
            await bye()
    except TimeoutException:
        pass
    driver.close()

async def open_product(product_id):
    url = 'https://www.binance.com/ru/nft/goods/detail?productId={}&isProduct=1'.format(product_id)
    driver.execute_script("window.open()")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)
    await check()
    driver.switch_to.window(base_window)

async def refresh():
    driver.get(base_url)
    wait = WebDriverWait(driver, 2)
    elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-8a1dsu')))
    global login
    try:
        driver.find_element_by_id('header_register')
        if login:
            await unlogin()
        return
    except(NoSuchElementException):
        login = True
    global base_window
    base_window = driver.current_window_handle
    elements = elements[:base_limit]
    last_id = 0
    for element in elements:
        price_element = element.find_element_by_class_name('css-zsxp4z')
        if not check_price(price_element.text): continue
        element.click()
        driver.switch_to.window(driver.window_handles[-1])
        if last_id == 0:
            last_id = get_product_id()
        await check()
        driver.switch_to.window(base_window)
    for product_id in range(last_id + 1, last_id + 1 + new_limit):
        await open_product(product_id)

def change_agent(user_agent):
    global driver
    old_user_agent = driver.execute_script("return navigator.userAgent")
    if old_user_agent != user_agent:
        opts = ChromeOptions()
        # opts.add_argument('--headless')
        opts.add_argument('user-agent=%s' % user_agent)
        driver = webdriver.Chrome(options=opts)
        driver.get(base_url)

async def search():
    while True:
        try:
            with open('settings', 'rb') as f:
                data = load(f)
            global max_price
            max_price = data['price']
            change_agent(data['user_agent'])
            driver.add_cookie({'name': 'cr00', 'value': data['cr']})
            driver.add_cookie({'name': 'p20t', 'value': data['p2']})
            driver.add_cookie({'name': 'nft-init-compliance', 'value': 'true'})
            await refresh()
            if not login:
                sleep(30)
        except Exception as error:
            with open('worker.log.error', 'a') as f:
                print_exception(type(error), error, error.__traceback__, file=f)