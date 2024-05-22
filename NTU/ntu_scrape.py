import csv
import os
import re
import sys
import certifi
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import URLError
from http.client import IncompleteRead
import ssl
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ntu_course_cleaning(csv_path):
    try:
        df = pd.read_csv(csv_path)

        # Drop duplicate headers
        df = df[df['chinese_dep'] != 'chinese_dep']

        # Retain specific columns
        df = df[['chinese_dep', 'chineseName', 'credit', 'number', 'teacher', 'classroom']]

        # Remove rows with missing values in 'classroom'
        df = df.dropna(subset=['classroom'])

        # Split classroom and time into separate attributes
        def extract_time_classroom(value):
            times = []
            classrooms = []
            parts = re.findall(r'([一二三四五六][^()]*\([^)]+\))', value)
            for part in parts:
                time_part = re.search(r'([一二三四五六][^()]+)\(', part)
                classroom_part = re.search(r'\(([^)]+)\)', part)
                if time_part and classroom_part:
                    times.append(time_part.group(1))
                    classrooms.append(classroom_part.group(1))
            return ','.join(times), ','.join(classrooms)

        df[['time', 'classroom']] = df.apply(lambda row: extract_time_classroom(row['classroom']), axis=1, result_type='expand')

        # Map Chinese characters to English representations for days of the week
        day_mapping = {'一': 'M', '二': 'T', '三': 'W', '四': 'R', '五': 'F', '六': 'S'}
        df['time'] = df['time'].replace(day_mapping, regex=True)
        df['time'] = df['time'].str.replace(r'\(|\)', '', regex=True)
        
        # Rewrite the csv file
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logging.info("Data cleaned successfully.")
    except Exception as e:
        logging.error(f"Failed to clean data: {e}")

def scrape_page(url, context, retries=3):
    for attempt in range(retries):
        try:
            with urlopen(url, context=context) as response:
                soup = BeautifulSoup(response, 'html.parser')
                return soup
        except IncompleteRead as e:
            logging.warning(f"IncompleteRead error on attempt {attempt+1}/{retries}. Retrying...")
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
            else:
                logging.error(f"Failed to retrieve data from {url} after {retries} attempts: {e}")
                return None
        except URLError as e:
            logging.error(f"Failed to retrieve data from {url}: {e}")
            return None

def write_data_to_csv(csv_path, header, rows, file_exists):
    try:
        with open(csv_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write the header only if the file did not exist
            if not file_exists:
                writer.writerow(header)
                file_exists = True

            for row in rows[1:]:  # Skip the first row
                columns = row.find_all('td')
                if columns:
                    writer.writerow([column.text.strip() for column in columns])

            logging.info(f"Data written to {csv_path}.")
    except Exception as e:
        logging.error(f"Failed to write data to CSV: {e}")

def ntu_course_scrape(csv_path):
    header = ['serialNumber', 'chinese_dep', 'courseNumber', 'shift', 'chineseName', 'specific', 
              'credit', 'number', 'year', 'required', 'teacher', 'add', 'classroom', 'limit', 
              'rule', 'note', 'web', 'myCourses']

    file_exists = os.path.exists(csv_path)
    context = ssl.create_default_context(cafile=certifi.where())

    for i in range(1023):
        url = (f"https://nol.ntu.edu.tw/nol/coursesearch/search_for_02_dpt.php?alltime=yes&allproced=yes&selcode=-1"
               f"&dptname=0&coursename=&teachername=&current_sem=112-2&yearcode=0&op=&startrec={i*15}&week1=&week2="
               f"&week3=&week4=&week5=&week6=&proced0=&proced1=&proced2=&proced3=&proced4=&procedE=&proced5=&proced6="
               f"&proced7=&proced8=&proced9=&procedA=&procedB=&procedC=&procedD=&allsel=yes&selCode1=&selCode2="
               f"&selCode3=&page_cnt=15")
        
        soup = scrape_page(url, context)
        if soup is None:
            continue

        table = soup.find('table', {'border': '1', 'bordercolorlight': '#CCCCCC', 'bordercolordark': '#CCCCCC'})
        if not table:
            logging.warning(f"No data table found on page {i+1}.")
            continue

        rows = table.find_all('tr')
        write_data_to_csv(csv_path, header, rows, file_exists)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python3 script_name.py <csv_path>")
        sys.exit(1)

    csv_path = sys.argv[1]

    ntu_course_scrape(csv_path)
    ntu_course_cleaning(csv_path)
