from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import csv

# Define debug print output
def debug_output(text):
    print(str(datetime.now())[0:19] + ': ' + text)

# Start timer
debug_output("The program started!")

# Set path Selenium
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
s = Service(CHROMEDRIVER_PATH)

# Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=s, options=chrome_options)
debug_output("Options have been set!")

# Get the response
url = "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/leagues/?id=4863/"
driver.get(url)
time.sleep(10)
debug_output("Response OK!")

# Close cookies pop-up
try:
    ok_til_cookies = driver.find_element(By.ID, 'didomi-notice-agree-button')
    time.sleep(5)
    ok_til_cookies.click()
    time.sleep(5)
    debug_output("Cookies pop-up clicked!")
except:
    time.sleep(10)
    debug_output("Cookies pop-up not found. Continuing...")

# Find cykelvenner-ligaen
try:
    cykelvenner = driver.find_element(By.LINK_TEXT, '🚴🏻‍♂️ Cykelvenner')
    cykelvenner.click()
    debug_output("Cykelvenner-liga åbnet")
    time.sleep(5)
except:
    time.sleep(5)

# Create data frame to save data to
cykelvenner_tabel = pd.DataFrame(columns=[
    'PLACERING',
    'PLACERING_SAMLET',
    'HOLD',
    'MANAGER',
    'POINT',
    'UPDATE_TIMESTAMP'
])

# Parse HTML-table
soup = BeautifulSoup(driver.page_source, "html.parser")
table = soup.find_all("table")[0]
debug_output("Soup made!")
number_of_rows = 0
for row in table.tbody.find_all("tr"):
    columns = row.find_all("td")
    if len(columns) == 5 and len(columns[0].text.strip()) != 0:
        cykelvenner_tabel = pd.concat([cykelvenner_tabel, pd.DataFrame.from_records([{
            'PLACERING': int(columns[0].text.strip().replace(".", "")),
            'PLACERING_SAMLET': int(columns[1].text.strip().replace("(", "").replace(")", "")),
            'HOLD': columns[2].text.strip(),
            'MANAGER': columns[3].text.strip(),
            'POINT': columns[4].text.strip(),
            'UPDATE_TIMESTAMP': str(datetime.now())[0:19]
        }])])
    number_of_rows += 1
number_of_rows_to_print = "Number of rows found: " + str(number_of_rows)
debug_output(number_of_rows_to_print)
debug_output("Table made!")

# Close the driver
driver.close()

# Save results to text file to track points over time
cykelvenner_tabel.to_csv(r'/var/www/html/cykelvenner.dk/public_html/cykelvenner_tabel.csv', header=None, index=None, sep=',', quoting=csv.QUOTE_ALL, mode='w')

#cykelvenner_tabel.to_csv(r'/var/www/html/cykelvenner.dk/public_html/cykelvenner_tabel_history.csv', header=None, index=None, sep=',', quoting=csv.QUOTE_ALL, mode='a')
debug_output("Results saved to csv!")

debug_output("The program ended!")
print()
