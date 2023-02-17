
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
import pygsheets
import csv

# Define debug print output
def debug_output(text):
    print(str(datetime.now())[0:19] + ': ' + text)

# Start timer
debug_output("The program started!")

# Set path Selenium
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
s = Service(CHROMEDRIVER_PATH)
#WINDOW_SIZE = "1440,900"

# Options
chrome_options = Options()
chrome_options.add_argument("--headless")
#chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=s, options=chrome_options)
debug_output("Options have been set!")

# Get the response
url = "https://www.feltet.dk/manager/saesonspil_2022_uden_kaptajner/statistics/"
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

# Expand the list of riders until all riders are shown
more_riders_to_get = True
total_rows_found = 0
while more_riders_to_get:
    #debug_output("Rows found: " + str(total_rows_found))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find_all("table")[0]
    rows_now = 0
    for row in table.tbody.find_all("tr"):
        rows_now += 1
    if rows_now > total_rows_found:
        total_rows_found = rows_now
        WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#manager_statsContent > table > tbody > tr:last-child > td > a")))
        vis_flere = driver.find_element(By.CSS_SELECTOR, "#manager_statsContent > table > tbody > tr:last-child > td > a")
        time.sleep(1)
        #debug_output("Vis flere-button found!")
        vis_flere.click()
        time.sleep(1)
        #debug_output("Vis flere-button clicked!")
        #print()
    else:
        debug_output("Total number of rows found: " + str(total_rows_found))
        more_riders_to_get = False

# Create data frame to save data to
riders_points = pd.DataFrame(columns=[
    'RIDER_NAME',
    'RIDER_COUNTRY',
    'RIDER_POINTS',
    'UPDATE_TIMESTAMP'
])

# Parse HTML-data and save to data frame row by row
soup = BeautifulSoup(driver.page_source, "html.parser")
table = soup.find_all("table")[0]
debug_output("Soup made, table found!")

for row in table.tbody.find_all("tr"):
    columns = row.find_all("td")
    if len(columns) == 4:
        try:
            rider_name = columns[1].text.strip()
        except:
            rider_name = ''
        try:
            rider_country = BeautifulSoup(str(columns[2].img), 'html.parser').find('img').attrs['title'].strip()
        except:
            rider_country = ''
        try:
            rider_points = int(columns[3].text.strip())
        except:
            rider_points = 0
        if rider_country != '':
            riders_points = pd.concat([riders_points, pd.DataFrame.from_records([{
                'RIDER_NAME': rider_name,
                'RIDER_COUNTRY': rider_country,
                'RIDER_POINTS': rider_points,
                'UPDATE_TIMESTAMP': str(datetime.now())[0:19]
            }])])

# Close the driver
driver.close()

# Upload results to Google Sheets / SQLiteDB
gc = pygsheets.authorize()
sh = gc.open_by_key('1QwYUyU-ApdO-_jjHwhwO2coh9z7m0LWWvCjNOCKowKg')
wks_write = sh.worksheet_by_title('riders_points_2023')
wks_write.clear('B1', None, '*')
wks_write.set_dataframe(riders_points, (1, 2), encoding = 'utf-8', fit=True)

# Save results to text file to track points over time
riders_points.to_csv(r'/home/ubuntu/riders_points.csv', header=None, index=None, sep=',', quoting=csv.QUOTE_ALL, mode='a')

# Print results
#print()
#print("The output is:")
#print(riders_points)
#print()
debug_output("The program ended!")
print()
