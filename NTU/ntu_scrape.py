import csv
import os
import sys
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import URLError


def ntu_course_scrape(csv_path):
    # Header for the csv file
    header = ['serialNumber', 'chinese_dep', 'courseNumber', 'shift', 'chineseName', 'specific', 
              'credit', 'number', 'year', 'required', 'teacher', 'add', 'classroom', 'limit', 
              'rule', 'note', 'web', 'myCourses']

    # Check if the file exists and determine whether to write the header
    file_exists = os.path.exists(csv_path)

    for i in range(1023):
        url = f"https://nol.ntu.edu.tw/nol/coursesearch/search_for_02_dpt.php?alltime=yes&allproced=yes&selcode=-1&dptname=0&coursename=&teachername=&current_sem=112-2&yearcode=0&op=&startrec={i*15}&week1=&week2=&week3=&week4=&week5=&week6=&proced0=&proced1=&proced2=&proced3=&proced4=&procedE=&proced5=&proced6=&proced7=&proced8=&proced9=&procedA=&procedB=&procedC=&procedD=&allsel=yes&selCode1=&selCode2=&selCode3=&page_cnt=15"
        try:
            with urlopen(url) as response:
                soup = BeautifulSoup(response, 'html.parser')
        except URLError as e:
            print(f"Failed to retrieve data from {url}: {e}")
            continue

        table = soup.find('table', {'border': '1', 'bordercolorlight': '#CCCCCC', 'bordercolordark': '#CCCCCC'})
        
        with open(csv_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write the header only if the file did not exist
            if not file_exists:
                writer.writerow(header)
                file_exists = True

            # Extract and write rows, starting from the second row
            rows = table.find_all('tr')
            for row in rows[1:]:  # This skips the first row
                columns = row.find_all('td')
                if columns:
                    writer.writerow([column.text.strip() for column in columns])
            print(f"Data written for page {i+1}")

# csv_path = "output.csv"
if __name__ == "__main__":
   if len(sys.argv) != 2:
      print("Usage: python3 script_name.py <csv_path>")
      sys.exit(1)

   csv_path = sys.argv[1]
   ntu_course_scrape(csv_path)
