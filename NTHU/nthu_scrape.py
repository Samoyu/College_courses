import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from twocaptcha import TwoCaptcha
import os
import time
import csv

def nthu_course_scrape(webdriver_path, csv_path, twocaptcha_apikey):
    service = webdriver.chrome.service.Service(webdriver_path)
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get("https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/6/6.2/6.2.9/JH629001.php" )
    time.sleep(2)
    
    try:
        select_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "dept")))
        options = select_element.find_elements(By.TAG_NAME, "option")
        
        for i in range(1, len(options)):
            if i != 1:
                driver.get("https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/6/6.2/6.2.9/JH629001.php" )
                time.sleep(2)
            
            select_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "dept")))
            options = select_element.find_elements(By.TAG_NAME, "option")
            Select(select_element).select_by_index(i)
            time.sleep(1)
            
            captcha_img = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/form/table[2]/tbody/tr/td/img')))
            captcha_img.screenshot('captchas/captcha.png')
            
            # See more info at: https://pypi.org/project/2captcha-python/
            solver = TwoCaptcha(os.getenv('APIKEY_2CAPTCHA', twocaptcha_apikey))
            result = solver.normal('captchas/captcha.png')
            code = result['code']
            
            driver.find_element(By.NAME, "auth_num").send_keys(code)
            driver.find_element(By.NAME, "Submit").click()
            time.sleep(2)
            
            # If no table in the page then skip
            try:
                table_body = driver.find_element(By.TAG_NAME, 'tbody')
                table_rows = table_body.find_elements(By.TAG_NAME, 'tr')
                
                with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    for row in table_rows:
                        row_data = [data.text for data in row.find_elements(By.TAG_NAME, "td")]
                        writer.writerow(row_data)
            except NoSuchElementException:
                print("No table found on this page.")
                
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    
    finally:
        driver.quit()


# webdriver_path = "/Users/lincheyu/Desktop/Scrape/chromedriver"
# csv_path = "/Users/lincheyu/Desktop/Scrape/nthu/nthu_course.csv"

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 script_name.py <webdriver_path> <url> <csv_path>")
        sys.exit(1)

    webdriver_path = sys.argv[1]
    csv_path = sys.argv[2]
    twocaptcha_apikey = sys.argv[3]

    nthu_course_scrape(webdriver_path, csv_path, twocaptcha_apikey)
