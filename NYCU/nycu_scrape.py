import pandas as pd
import numpy as np
import random
import os
import sys
import time
import csv
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def nycu_courses_cleaning(file_path):
    logging.info(f'Starting cleaning process for {file_path}')
    column_names = ['semester', 'number', 'notes', 'chineseName', 'englishName', 'limit', 'people', 
                    'time_string', 'credit', 'classHour', 'teacher', 'required', 'chinese_dep']
    
    nycu_courses = pd.read_csv(file_path, names=column_names).reset_index(drop=True)
    nycu_courses_chinese_dep = nycu_courses['chinese_dep']

    # Drop unnecessary columns
    nycu_courses = nycu_courses.drop(['notes', 'limit', 'people', 'classHour', 'required', 'chinese_dep'], axis=1)

    # Drop duplicate rows
    nycu_courses = nycu_courses.drop_duplicates()

    # Ensure indices are aligned
    if not nycu_courses.index.equals(nycu_courses_chinese_dep.index):
        logging.warning("Indices are not aligned. Ensure both DataFrames have the same index.")

    nycu_courses['chinese_dep'] = nycu_courses_chinese_dep[nycu_courses.index].loc[nycu_courses.index]

    # Drop rows with null time attribute
    nycu_courses.dropna(subset=['time_string'], inplace=True)
    nycu_courses = nycu_courses.reset_index(drop=True)

    def custom_replace(match):
        results = []
        initial = None  # To keep track of the current uppercase letter
        for char in match.group(0):
            if char.isupper():
                initial = char
            else:
                results.append(f"{initial}{char}")
        return ''.join(results)

    time_split_list = [time.split('-')[0] for time in nycu_courses['time_string']]
    classroom_split_list = [time.split('-')[1] for time in nycu_courses['time_string']]

    time_split_series = pd.Series(time_split_list)
    time_split_series = time_split_series.str.replace(r'[A-Z][\da-z]*', custom_replace, regex=True)

    classroom_split_series = pd.Series(classroom_split_list)
    classroom_split_series = classroom_split_series.str.replace(r'\[.*?\]', '', regex=True)

    dep_series = nycu_courses['chinese_dep'].str.replace(r'\(|\)', '', regex=True)

    nycu_courses['time_string'] = time_split_series
    nycu_courses['classroom'] = classroom_split_series
    nycu_courses['chinese_dep'] = dep_series

    # List of hex values
    hex_values = ['#8FD135', '#358FD1', '#83adb5', '#8ecae6', '#5f9ea0', '#fcbf49', '#e0aaff',
                  '#ffb3c1', '#68d8d6', '#b6ccfe', '#e4e6c3', '#fad643', '#a3c1ad', '#c19ee0',
                  '#ffb563', '#56cfe1', '#fcd2af', '#cbdfbd', '#bfd7ff', '#efc3e6']

    # Generate random colors and add to DataFrame
    nycu_courses['color'] = [random.choice(hex_values) for _ in range(len(nycu_courses))]

    def split_time_correctly(time_str):
        return [time_str[i:i+2] for i in range(0, len(time_str), 2) if time_str[i:i+2].strip()]

    nycu_courses['time'] = nycu_courses['time_string'].apply(split_time_correctly)

    # Export CSV file
    nycu_courses.to_csv(file_path, index=False, encoding="utf-8")
    logging.info(f'Cleaning process completed and saved to {file_path}')

    return nycu_courses

def nycu_course_scrape(csv_path):
    # Initiate webdriver
    logging.info('Starting web scraping process')
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    except Exception as e:
        logging.error(f"Error installing WebDriver: {e}")
        return

    try:
        driver.get("https://timetable.nycu.edu.tw/")
        time.sleep(2) 

        # Check English course name checkbox
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "cos_othername"))).click()

        # Loop through dropdown options
        for i in range(len(Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fType")))).options)):
            # ========================================= for the first and second options  ==========================================
            if i <= 1:
                select_grade = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fType"))))
                select_grade.select_by_index(i)
                time.sleep(1)

                for j in range(len(Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fCategory")))).options)):
                    select_detail = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fCategory"))))
                    select_detail.select_by_index(j)
                    time.sleep(1)

                    for k in range(len(Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fCollege")))).options)):
                        select_faculty = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fCollege"))))
                        select_faculty.select_by_index(k)
                        time.sleep(1)

                        for n in range(len(Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fDep")))).options)):
                            select_department = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fDep"))))
                            select_department.select_by_index(n)
                            current_dep_text = select_department.first_selected_option.text
                            time.sleep(1)

                            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "crstime_search"))).click()
                            time.sleep(3)  # Allow time for the page to load results

                            try:
                                # Refetch dropdown elements after page load
                                select_grade_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "fType")))
                                select_grade_detail = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "fCategory")))
                                select_faculty = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "fCollege")))
                                select_department = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "fDep")))

                                # Scrape the data
                                # Ignore the first table containing dropdown
                                try:
                                    excluded_table = driver.find_element(By.ID, 'tbl_timetable_menu')
                                    excluded_tbody = excluded_table.find_element(By.TAG_NAME, 'tbody')
                                except:
                                    excluded_tbody = None
                                
                                # Find all tbody elements on the page
                                all_tbody = driver.find_elements(By.TAG_NAME, 'tbody')
                                
                                if not all_tbody:
                                    logging.warning("No tables found on the page.")
                                else:
                                    with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
                                        writer = csv.writer(file)
                                    
                                        # Process each tbody separately
                                        for table_body in all_tbody:
                                            # If the current tbody is the excluded one, skip it
                                            if table_body == excluded_tbody:
                                                continue
                                            
                                            rows = table_body.find_elements(By.TAG_NAME, 'tr')
                                            all_data = []  # This will store each row's data
                                            for row in rows:
                                                row_data = []
                                                columns = row.find_elements(By.TAG_NAME, "td")
                                                
                                                for column in columns:
                                                    if column.get_attribute('colspan'):  # Skip columns with colspan attribute
                                                        continue
                                                    row_data.append(column.text)
                                                
                                                if row_data:  # Ensure row_data is not empty before appending department text and adding to all_data
                                                    row_data.append(current_dep_text)
                                                    all_data.append(row_data)
                                            
                                            # Write each tbody's data to CSV file if there is data to write
                                            for data in all_data:
                                                writer.writerow(data)
                            except Exception as e:
                                logging.error(f"An error occurred during scraping: {e}")
            
            # =============================================== for the third option  ================================================
            elif i == 2:
                select_grade = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fType"))))
                select_grade.select_by_index(i)
                time.sleep(1)

                for j in range(len(Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fCategory")))).options)):
                    select_detail = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fCategory"))))
                    select_detail.select_by_index(j)
                    time.sleep(1)

                    for n in range(len(Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fDep")))).options)):
                        select_department = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fDep"))))
                        select_department.select_by_index(n)
                        current_dep_text = select_department.first_selected_option.text
                        time.sleep(1)

                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "crstime_search"))).click()
                        time.sleep(3)  # Allow time for the page to load results

                        try:
                            # Refetch dropdown elements after page load
                            select_grade_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "fType")))
                            select_grade_detail = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "fCategory")))
                            select_department = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "fDep")))

                            # Scrape the data
                            # Ignore the first table containing dropdown
                            try:
                                excluded_table = driver.find_element(By.ID, 'tbl_timetable_menu')
                                excluded_tbody = excluded_table.find_element(By.TAG_NAME, 'tbody')
                            except:
                                excluded_tbody = None
                            
                            # Find all tbody elements on the page
                            all_tbody = driver.find_elements(By.TAG_NAME, 'tbody')
                            
                            if not all_tbody:
                                logging.warning("No tables found on the page.")
                            else:
                                with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
                                    writer = csv.writer(file)
                                
                                    # Process each tbody separately
                                    for table_body in all_tbody:
                                        # If the current tbody is the excluded one, skip it
                                        if table_body == excluded_tbody:
                                            continue
                                        
                                        rows = table_body.find_elements(By.TAG_NAME, 'tr')
                                        all_data = []  # This will store each row's data
                                        for row in rows:
                                            row_data = []
                                            columns = row.find_elements(By.TAG_NAME, "td")
                                            
                                            for column in columns:
                                                if column.get_attribute('colspan'):  # Skip columns with colspan attribute
                                                    continue
                                                row_data.append(column.text)
                                            
                                            if row_data:  # Ensure row_data is not empty before appending department text and adding to all_data
                                                row_data.append(current_dep_text)
                                                all_data.append(row_data)
                                        
                                        # Write each tbody's data to CSV file if there is data to write
                                        for data in all_data:
                                            writer.writerow(data)
                        except Exception as e:
                            logging.error(f"An error occurred during scraping: {e}")
            
            # ========================================== for the fourth to sixth options  ==========================================
            elif 3 <= i <= 5:
                select_grade = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fType"))))
                select_grade.select_by_index(i)
                time.sleep(1)

                for n in range(len(Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fDep")))).options)):
                    select_department = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fDep"))))
                    select_department.select_by_index(n)
                    current_dep_text = select_department.first_selected_option.text
                    time.sleep(1)

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "crstime_search"))).click()
                    time.sleep(10)  # Allow time for the page to load results

                    try:
                        # Refetch dropdown elements after page load
                        select_grade_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "fType")))
                        select_department = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "fDep")))

                        # Scrape the data
                        # Ignore the first table containing dropdown
                        try:
                            excluded_table = driver.find_element(By.ID, 'tbl_timetable_menu')
                            excluded_tbody = excluded_table.find_element(By.TAG_NAME, 'tbody')
                        except:
                            excluded_tbody = None
                        
                        # Find all tbody elements on the page
                        all_tbody = driver.find_elements(By.TAG_NAME, 'tbody')
                        
                        if not all_tbody:
                            logging.warning("No tables found on the page.")
                        else:
                            with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
                                writer = csv.writer(file)
                            
                                # Process each tbody separately
                                for table_body in all_tbody:
                                    # If the current tbody is the excluded one, skip it
                                    if table_body == excluded_tbody:
                                        continue
                                    
                                    rows = table_body.find_elements(By.TAG_NAME, 'tr')
                                    all_data = []  # This will store each row's data
                                    for row in rows:
                                        row_data = []
                                        columns = row.find_elements(By.TAG_NAME, "td")
                                        
                                        for column in columns:
                                            if column.get_attribute('colspan'):  # Skip columns with colspan attribute
                                                continue
                                            row_data.append(column.text)
                                        
                                        if row_data:  # Ensure row_data is not empty before appending department text and adding to all_data
                                            row_data.append(current_dep_text)
                                            all_data.append(row_data)
                                    
                                    # Write each tbody's data to CSV file if there is data to write
                                    for data in all_data:
                                        writer.writerow(data)
                    except Exception as e:
                        logging.error(f"An error occurred during scraping: {e}")
            
            # ================================================ for the last option  ================================================
            else:
                select_grade = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fType"))))
                select_grade.select_by_index(i)
                current_grade_text = select_grade.first_selected_option.text
                time.sleep(1)

                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "crstime_search"))).click()
                time.sleep(3)  # Allow time for the page to load results

                try:
                    # Refetch dropdown elements after page load
                    select_grade_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "fType")))

                    # Scrape the data
                    # Ignore the first table containing dropdown
                    try:
                        excluded_table = driver.find_element(By.ID, 'tbl_timetable_menu')
                        excluded_tbody = excluded_table.find_element(By.TAG_NAME, 'tbody')
                    except:
                        excluded_tbody = None
                    
                    # Find all tbody elements on the page
                    all_tbody = driver.find_elements(By.TAG_NAME, 'tbody')
                    
                    if not all_tbody:
                        logging.warning("No tables found on the page.")
                    else:
                        with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
                            writer = csv.writer(file)
                        
                            # Process each tbody separately
                            for table_body in all_tbody:
                                # If the current tbody is the excluded one, skip it
                                if table_body == excluded_tbody:
                                    continue
                                
                                rows = table_body.find_elements(By.TAG_NAME, 'tr')
                                all_data = []  # This will store each row's data
                                for row in rows:
                                    row_data = []
                                    columns = row.find_elements(By.TAG_NAME, "td")
                                    
                                    for column in columns:
                                        if column.get_attribute('colspan'):  # Skip columns with colspan attribute
                                            continue
                                        row_data.append(column.text)
                                    
                                    if row_data:  # Ensure row_data is not empty before appending department text and adding to all_data
                                        row_data.append(current_grade_text)
                                        all_data.append(row_data)
                                
                                # Write each tbody's data to CSV file if there is data to write
                                for data in all_data:
                                    writer.writerow(data)
                except Exception as e:
                    logging.error(f"An error occurred during scraping: {e}")

    finally:
        driver.quit()
        logging.info('Web scraping process completed')

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(script_dir, 'Data')
    os.makedirs(data_folder, exist_ok=True)

    csv_path = os.path.join(data_folder, 'nycu_courses.csv')

    # Start scraping and cleaning process
    nycu_course_scrape(csv_path)
    nycu_courses_cleaning(csv_path)
