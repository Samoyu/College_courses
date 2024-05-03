<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/1344/1344761.png" alt="College Logo", width="10%"> 
</p>

<h2 align="center">College Courses - Taiwan</h2>

<p align="center">
  Simply scrape courses information from three different colleges with a single command.
</p>
<br>

## Description

The `nthu_scrape.py` and `nycu_scrape.py` scripts automate the retrieval of course data from respective university portals. The data scraped includes course names, times, professors, and other relevant information, which is saved into CSV files for easy analysis and accessibility.

## Prerequisites

- Python 3.x
- ChromeDriver compatible with your version of the Google Chrome browser

## Installation

Follow these steps to set up and run the project:

1. **Clone the Repository**
   ```
   git clone https://github.com/Samoyu/College_courses.git
   cd College_courses
   ```

2. **Set up a Python Virtual Environment**
   ```
   python3 -m venv venv
   source venv/bin/activate  # Use `venv\Scripts\activate` on Windows
   ```

3. **Install Required Dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Download ChromeDriver**
  Download ChromeDriver from [here](https://chromedriver.chromium.org/downloads).
  Ensure it is in your PATH or in the same directory as the scripts.


## Usage

To run the scraping scripts, use the following commands:

**For NTHU:** <br>
   - First create an account to obtain your own twocaptcha apikey [here](https://2captcha.com/)

   ```
   python3 nthu_scrape.py <path_to_chromedriver> "https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/6/6.2/6.2.9/JH629001.php" <path_to_output_csv> <your_twocaptcha_apikey>
   ```

**For NYCU:**
   ```
   python3 nycu_scrape.py <path_to_chromedriver> "https://timetable.nycu.edu.tw/" <path_to_output_csv>
   ```

Replace <path_to_chromedriver>, <path_to_output_csv> with the actual paths on your system.
