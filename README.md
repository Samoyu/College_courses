<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/1344/1344761.png" alt="College Logo", width="10%"> 
</p>

<h2 align="center">College Courses - Taiwan</h2>

<p align="center">
  Simply scrape courses information from three different colleges with a single command.
</p>
<br>

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

### For NTU:
Execute the following command to scrape data for NTU:
   ```
   cd NTU
   python3 ntu_scrape.py <path_to_output_csv>
   ```

### For NTHU:
1. **Obtain a 2Captcha API key:** First, create an account at [2Captcha](https://2captcha.com/) to get your API key.
2. **Scrape data:** Run the command below:

   ```
   cd NTHU
   mkdir captchas
   python3 nthu_scrape.py <path_to_chromedriver> <path_to_output_csv> <your_twocaptcha_apikey>
   ```

### For NYCU:
Execute the following command to scrape data for NYCU:
   ```
   cd NYCU
   python3 nycu_scrape.py <path_to_chromedriver> <path_to_output_csv>
   ```
