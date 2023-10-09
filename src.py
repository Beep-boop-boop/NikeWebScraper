import time
import csv
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)

url = 'https://www.nike.com/w/mens-sale-shoes-3yaepznik1zy7ok'
driver.get(url)

scroll_pause_time = 1
scroll_height = driver.execute_script("return document.documentElement.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(scroll_pause_time)
    
    new_scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_scroll_height == scroll_height:
        break
    scroll_height = new_scroll_height

soup = BeautifulSoup(driver.page_source, 'html.parser')
shoe_links = soup.find_all('a', {'class': 'product-card__link-overlay'})

with open('nike_shoes.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    
    for link in shoe_links:
        driver.execute_script("window.open('{}', '_blank');".format(link['href']))
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(4)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        fieldset = soup.find("fieldset", class_="mt5-sm mb3-sm body-2 css-1pj6y87")
        div = fieldset.find_all("div")[1]
        div_class = div.get("class")
        div_class = " ".join(div_class)

        sizes_container = soup.find('div', {'class': div_class})
        size_inputs = sizes_container.find_all('input')

        available_sizes = []
        for size_input in size_inputs:
            if not size_input.has_attr('disabled'):
                size = size_input['value'].split(':')[1]
                available_sizes.append(size)

        price_pattern = re.compile(r'\$\d+\.\d{2}')
        shoe_price = soup.find(text=price_pattern)
    
        shoe_model = soup.find('h1', {'class': 'headline-2 css-16cqcdq'}).text.strip()
        shoe_style = soup.find('li', {'class': 'description-preview__style-color ncss-li'}).text.strip()

        writer.writerow([shoe_model, shoe_price, shoe_style, available_sizes])

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        time.sleep(1)

driver.quit()
