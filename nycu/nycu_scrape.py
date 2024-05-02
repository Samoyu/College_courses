from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import sys
import time
import csv

def nycu_course_scrape(webdriver_path, url):
    # Initiate webdriver
    service = webdriver.chrome.service.Service(webdriver_path)
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(2) 

        # Check English course name checkbox
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "cos_othername"))).click()

        # Loop through dropdown options
        for i in range(len(Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fType")))).options)):
            # ========================================= for the first and second options  ==========================================
            if i<=1:
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
                                
                                with open("/Users/lincheyu/Desktop/Startup/Scrape/nycu_course.csv", 
                                        mode="a", newline="", encoding="utf-8") as file:
                                    writer = csv.writer(file)
                                
                                    # Process each tbody separately
                                    for table_body in all_tbody:
                                        # If the current tbody is the excluded one, skip it
                                        if table_body == excluded_tbody: continue
                                        
                                        rows = table_body.find_elements(By.TAG_NAME, 'tr')

                                        all_data = []  # This will store each row's data
                                        for row in rows:
                                            row_data = []
                                            columns = row.find_elements(By.TAG_NAME, "td")
                                            
                                            for column in columns:
                                                # Skip columns with colspan
                                                if column.get_attribute('colspan'): continue
                                                row_data.append(column.text)
                                            
                                            all_data.append(row_data)
                                        
                                        # Write each tbody's data to CSV file
                                        for data in all_data:
                                            writer.writerow(data)
                            except Exception as e:
                                print(f"An error occurred: {e}")
            
            # =============================================== for the third option  ================================================
            elif i==2:
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
                            
                            with open("/Users/lincheyu/Desktop/Startup/Scrape/nycu_course.csv", 
                                    mode="a", newline="", encoding="utf-8") as file:
                                writer = csv.writer(file)
                            
                                # Process each tbody separately
                                for table_body in all_tbody:
                                    # If the current tbody is the excluded one, skip it
                                    if table_body == excluded_tbody: continue
                                    
                                    rows = table_body.find_elements(By.TAG_NAME, 'tr')

                                    all_data = []  # This will store each row's data
                                    for row in rows:
                                        row_data = []
                                        columns = row.find_elements(By.TAG_NAME, "td")
                                        
                                        for column in columns:
                                            # Skip columns with colspan
                                            if column.get_attribute('colspan'): continue
                                            row_data.append(column.text)
                                        
                                        all_data.append(row_data)
                                    
                                    # Write each tbody's data to CSV file
                                    for data in all_data:
                                        writer.writerow(data)
                        except Exception as e:
                            print(f"An error occurred: {e}")
            
            # ========================================== for the fourth to sixth options  ==========================================
            elif 3 <= i <= 5:
                select_grade = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fType"))))
                select_grade.select_by_index(i)
                time.sleep(1)

                for n in range(len(Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fDep")))).options)):
                    select_department = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fDep"))))
                    select_department.select_by_index(n)
                    time.sleep(1)

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "crstime_search"))).click()
                    time.sleep(3)  # Allow time for the page to load results

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
                        
                        with open("/Users/lincheyu/Desktop/Startup/Scrape/nycu_course.csv", 
                                mode="a", newline="", encoding="utf-8") as file:
                            writer = csv.writer(file)
                        
                            # Process each tbody separately
                            for table_body in all_tbody:
                                # If the current tbody is the excluded one, skip it
                                if table_body == excluded_tbody: continue
                                
                                rows = table_body.find_elements(By.TAG_NAME, 'tr')

                                all_data = []  # This will store each row's data
                                for row in rows:
                                    row_data = []
                                    columns = row.find_elements(By.TAG_NAME, "td")
                                    
                                    for column in columns:
                                        # Skip columns with colspan
                                        if column.get_attribute('colspan'): continue
                                        row_data.append(column.text)
                                    
                                    all_data.append(row_data)
                                
                                # Write each tbody's data to CSV file
                                for data in all_data:
                                    writer.writerow(data)
                    except Exception as e:
                        print(f"An error occurred: {e}")
            
            # ================================================ for the last option  ================================================
            else:
                select_grade = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fType"))))
                select_grade.select_by_index(i)
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
                    
                    with open("/Users/lincheyu/Desktop/Startup/Scrape/nycu_course.csv", 
                            mode="a", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                    
                        # Process each tbody separately
                        for table_body in all_tbody:
                            # If the current tbody is the excluded one, skip it
                            if table_body == excluded_tbody: continue
                            
                            rows = table_body.find_elements(By.TAG_NAME, 'tr')

                            all_data = []  # This will store each row's data
                            for row in rows:
                                row_data = []
                                columns = row.find_elements(By.TAG_NAME, "td")
                                
                                for column in columns:
                                    # Skip columns with colspan
                                    if column.get_attribute('colspan'): continue
                                    row_data.append(column.text)
                                
                                all_data.append(row_data)
                            
                            # Write each tbody's data to CSV file
                            for data in all_data:
                                writer.writerow(data)
                except Exception as e:
                    print(f"An error occurred: {e}")

    finally:
        driver.quit()

# webdriver_path = "/Users/lincheyu/Desktop/Startup/Scrape/chromedriver"
# url = "https://timetable.nycu.edu.tw/"
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <webdriver_path> <url>")
    else:
        webdriver_path = sys.argv[1]
        url = sys.argv[2]
        nycu_course_scrape(webdriver_path, url)
