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

# All managers and their team-links
manager_teamlinks = {
    "Chrelle": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=81189&ref=4863",
    "Holgersen": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=82335&ref=4863",
    "Jappo": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=81949&ref=4863",
    "Jarma": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=81089&ref=4863",
    "Kenk": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=81622&ref=4863",
    "Knak": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=81979&ref=4863",
    "Malle": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=81549&ref=4863",
    "Matti": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=81413&ref=4863",
    "Okholm": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=81067&ref=4863",
    "Skeel": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=82274&ref=4863",
    "Thomas": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=81027&ref=4863",
    "Visti": "https://www.feltet.dk/manager/saesonspil_2023_med_kaptajn/team/?id=81018&ref=4863"
}

# Create data frame to save data to
cykelvenner_kaptajner = pd.DataFrame(columns=[
    'MANAGER',
    'LØB',
    'KAPTAJN',
    'UPDATE_TIMESTAMP'
])

# For every manager, get the list of captains:
for val in manager_teamlinks:

    # Get the response
    url = manager_teamlinks[val]
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

    # Parse HTML-table
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find_all("table")[2]
    debug_output("Soup made!")

    for row in table.tbody.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) > 0:
            cykelvenner_kaptajner = pd.concat([cykelvenner_kaptajner, pd.DataFrame.from_records([{
                'MANAGER': val,
                'LØB': columns[0].text.strip()[13:],
                'KAPTAJN': columns[1].text.strip(),
                'UPDATE_TIMESTAMP': str(datetime.now())[0:19]
            }])])

    debug_output("Table made!")

# Close the driver
driver.close()

# Save results to text file to track points over time
cykelvenner_kaptajner.to_csv(r'/var/www/html/cykelvenner.dk/public_html/cykelvenner_kaptajner.csv', header=None, index=None, sep=',', quoting=csv.QUOTE_ALL, mode='w')

debug_output("Results saved to csv!")

debug_output("The program ended!")
print()
