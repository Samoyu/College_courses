from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import sys
import os
import time
import re
import csv
import pandas as pd
from twocaptcha import TwoCaptcha

webdriver_path = "/Users/lincheyu/Desktop/Startup/Scrape/chromedriver"

# Initialize the service
service = Service(webdriver_path)
chrome_options = Options()
driver = webdriver.Chrome(service=service, options=chrome_options)

# Get in NTHU course web
search_url = "https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/6/6.2/6.2.9/JH629001.php"
driver.get(search_url)
time.sleep(2)

# Locate dropdown list and select
select_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "dept")))
options = select_element.find_elements(By.TAG_NAME, "option")

for i in range(len(options)+2):
    if i != 0:
       driver.get(search_url)
       time.sleep(2)

    select_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "dept")))
    options = select_element.find_elements(By.TAG_NAME, "option")
    select = Select(select_element)
    select.select_by_index(i)
    time.sleep(1)

    # Captcha
    captcha_img = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
                By.XPATH,'/html/body/div[1]/form/table[2]/tbody/tr/td/img')))
    captcha_img.screenshot('captchas/captcha.png')

    api_key = os.getenv('APIKEY_2CAPTCHA', '620ad6adcb8ff4ccff3aefac1346216a')
    solver = TwoCaptcha(api_key)

    try:
        result = solver.solve_captcha('captchas/captcha.png')
        code = result['code']
        driver.find_element(By.NAME, "auth_num").send_keys(code)
        driver.find_element(By.NAME, "Submit").click()
    except Exception as e:
        sys.exit(e)

    time.sleep(2)

    # Scrape table and save in to an CSV file
    try:
        table_body = driver.find_element(By.TAG_NAME, 'tbody')
        table_rows = table_body.find_elements(By.TAG_NAME, 'tr')

        # Check if table_rows is not empty
        if not table_rows:
            print("No rows in table_body, going to next loop iteration.")
            continue  # Skip to the next iteration of the loop

        with open("/Users/lincheyu/Desktop/Startup/Scrape/nthu_course.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            for row in table_rows:
                table_data = row.find_elements(By.TAG_NAME, "td")
                row_data = []
                for data in table_data:
                    row_data.append(data.text)
                writer.writerow(row_data)

    except NoSuchElementException:
        print("No table_body found, going to next loop iteration.")
        continue  