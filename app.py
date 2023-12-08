import threading, time, random, yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from colorama import Fore, Back, Style
RED = Fore.RED
GREEN = Fore.GREEN
BLUE = Fore.BLUE
YELLOW = Fore.YELLOW
MAGENTA = Fore.MAGENTA
WHITE = Fore.WHITE

with open('config/world_data_v5.yaml') as f:
    config = yaml.safe_load(f)

# Global variable to store the last chosen color
last_color = None

def random_color():
    global last_color
    colors = [RED, GREEN, BLUE, YELLOW, MAGENTA, WHITE]
    if last_color in colors:
        colors.remove(last_color)
    chosen_color = random.choice(colors)
    last_color = chosen_color

    return chosen_color

RED_BACK = Back.RED
GREEN_BACK = Back.GREEN
BLUE_BACK = Back.BLUE
YELLOW_BACK = Back.YELLOW
MAGENTA_BACK = Back.MAGENTA
WHITE_BACK = Back.WHITE

RESET = Style.RESET_ALL

shared_world_data = []

world_data_url = "https://www.worldometers.info/"

def data_pull_1():

    global world_data_url
    url = world_data_url
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1200")

    with webdriver.Chrome(options=options) as driver:
        driver.get(url)

        consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[2]/div[1]/div[2]/div[2]/button[1]'))
        )
        consent_button.click()

        while True:

            # Start of scraping process
            start_time = time.time()

            span_elements = driver.find_elements(By.CSS_SELECTOR, 'span.rts-counter')
            global shared_world_data
            shared_world_data = [span.text for span in span_elements if span.text != '']
            time.sleep(0.25)
            # End of scraping process
            print(f"{random_color()}Scraped data... it took: {time.time() - start_time} seconds{RESET}")

data_pull_1 = threading.Thread(target=data_pull_1)
data_pull_1.start()

####################
# Quart Web Server #
####################

from quart import Quart, websocket, render_template
import asyncio

app = Quart(__name__)

@app.websocket('/data')
async def data():
    while True:

        if not shared_world_data:
            await asyncio.sleep(1)
            continue

        data = {}

        for item_dict in config['data']:
            for key, value_expr in item_dict.items():
                value = eval(value_expr)
                data[key] = value

        await websocket.send_json(data)
        await asyncio.sleep(1)

@app.route('/')
async def root():
    return await render_template('data.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
