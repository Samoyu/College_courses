import sys
import os
import time
import csv
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from twocaptcha import TwoCaptcha

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def nthu_course_scrape(csv_path, twocaptcha_apikey):
    logging.info('Starting web scraping process')

    # Initialize the WebDriver
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    except Exception as e:
        logging.error(f"Error installing WebDriver: {e}")
        return
    
    # Navigate to the target URL
    driver.get("https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/6/6.2/6.2.9/JH629001.php")
    time.sleep(2)
    
    try:
        # Wait for the department selection element to be clickable
        select_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "dept")))
        options = select_element.find_elements(By.TAG_NAME, "option")
        logging.info(f"Found {len(options)} departments to scrape.")

        # Iterate over each department option
        for i in range(1, len(options)):
            if i != 1:
                driver.get("https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/6/6.2/6.2.9/JH629001.php")
                time.sleep(2)
            
            select_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "dept")))
            options = select_element.find_elements(By.TAG_NAME, "option")
            Select(select_element).select_by_index(i)
            logging.info(f"Selected department: {options[i].text}")
            time.sleep(1)
            
            # Capture the captcha image
            captcha_img = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/form/table[2]/tbody/tr/td/img')))
            captcha_path = 'captchas/captcha.png'
            captcha_img.screenshot(captcha_path)
            logging.info("Captcha image saved.")
            
            # Solve the captcha using 2Captcha service
            solver = TwoCaptcha(twocaptcha_apikey)
            result = solver.normal(captcha_path)
            code = result['code']
            logging.info(f"Captcha solved: {code}")
            
            # Submit the captcha code
            driver.find_element(By.NAME, "auth_num").send_keys(code)
            driver.find_element(By.NAME, "Submit").click()
            time.sleep(2)
            
            # Check if the table exists and scrape the data
            try:
                table_body = driver.find_element(By.TAG_NAME, 'tbody')
                table_rows = table_body.find_elements(By.TAG_NAME, 'tr')
                logging.info(f"Found {len(table_rows)} rows in the table.")
                
                # Append the scraped data to the CSV file
                with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    for row in table_rows:
                        row_data = [data.text for data in row.find_elements(By.TAG_NAME, "td")]
                        writer.writerow(row_data)
                        logging.debug(f"Row data written: {row_data}")
            except NoSuchElementException:
                logging.warning("No table found on this page.")
                
    except TimeoutException as e:
        logging.error(f"Timeout occurred: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()
        logging.info("Web scraping process finished.")

if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 2:
        logging.error("Usage: python3 script_name.py <twocaptcha_apikey>")
        sys.exit(1)

    # Get the 2Captcha API key from the command line argument
    twocaptcha_apikey = sys.argv[1]

    # Determine the script directory and create the data folder if it doesn't exist
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(script_dir, 'Data')
    os.makedirs(data_folder, exist_ok=True)
    csv_path = os.path.join(data_folder, 'nthu_courses.csv')

    # Start the web scraping process
    nthu_course_scrape(csv_path, twocaptcha_apikey)
