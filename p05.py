'''
Ryan Barnhart

Resources: https://www.digitalocean.com/community/tutorials/python-time-sleep
        https://stackoverflow.com/questions
        https://www.w3schools.com/python/python_try_except.asp

I deserve an A because I used a wait to pause until the search page has loaded.
I then used selenium to enter text into the search area to input the current date and time
as well as the date and time of 48 hours ago.
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import json

def main():
    # datetime object containing current date and time
    date = datetime.now()
    date_minus_48 = datetime.now() + timedelta(days= -2)

    # dd/mm/YYYY H:M
    end_date = date.strftime("%m-%d-%Y %H:%M")
    start_date = date_minus_48.strftime("%m-%d-%Y %H:%M")

    # open the driver
    options = webdriver.ChromeOptions()
    options.headless = True
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get("https://dwslivescan.co.wake.nc.us/mug/MugshotSearch.aspx")
    print("Scraping in progress...")

    # click agree button CSS selector: "#btnAgree"
    page = driver.find_element(By.CSS_SELECTOR, "#btnAgree")
    page.click()

    # wait until page loads
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "frmMugshotSearch")))

    # swtich to search box frame
    iframe = driver.find_element(By.ID, "frameForm")
    driver.switch_to.frame(iframe)

    # send date of 48 hours ago to text box
    text_box = driver.find_element(By.CSS_SELECTOR, "#dwpForm input[name='NCCriminal_ArrestDateTimeStartXXX']")
    text_box.clear()
    text_box.send_keys(start_date)

    # send current date to text box
    text_box = driver.find_element(By.CSS_SELECTOR, "#dwpForm input[name='NCCriminal_ArrestDateTimeEndXXX']")
    text_box.clear()
    text_box.send_keys(end_date)

    # Switch back to the default content from the frame
    driver.switch_to.default_content()

    # search
    page = driver.find_element(By.ID, "btnSearch")
    page.click()

    # time.sleep until loaded
    time.sleep(2)

    # get the list of 8 elements on the page
    anchor_tags = driver.find_elements(By.CSS_SELECTOR, "#tblImages a")
    url_list = []
    for tag in anchor_tags:
        url_list.append(tag.get_attribute("href"))

    # collection of all attribute data from pages
    collection = []

    # go through each page while it still has a next
    same_page = 0
    while (same_page == 0):
        check = url_list[1]

        # Extract the URLs from the anchor tags and navigate to each URL
        for url in url_list:
            driver.get(url)
        
            # Switch to the frame the data is on
            iframe = driver.find_element(By.ID, "framePrint")
            driver.switch_to.frame(iframe)

            # Get the charges
            charges = []
            charges_elements = driver.find_elements(By.CSS_SELECTOR, "span.dwpGenHTMLValue")
            for index, charge in enumerate(charges_elements):
                if (index + 1) % 3 == 0:
                    charges.append(charge.text)

            # collect all other attributes
            attributes = {
            "first name": driver.find_element(By.XPATH, "//span[@columnname='FirstName']").text,
            "last name": driver.find_element(By.XPATH, "/html/body/table/tbody/tr[1]/td[2]/table/tbody/tr[1]/td/span[1]").text,
            "age": driver.find_element(By.XPATH, "/html/body/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[2]/span").text,
            "sex": driver.find_element(By.XPATH, "/html/body/table/tbody/tr[1]/td[2]/table/tbody/tr[3]/td[2]/span").text,
            "residence address": driver.find_element(By.XPATH, "/html/body/table/tbody/tr[2]/td/span[2]").text,
            "arrest location": driver.find_element(By.XPATH, "/html/body/table/tbody/tr[3]/td/span[2]").text,
            "arresting officer": driver.find_element(By.XPATH, "/html/body/table/tbody/tr[4]/td/span[2]").text,
            "charges": charges,
            "image address": driver.find_element(By.XPATH, "/html/body/table/tbody/tr[1]/td[1]/table/tbody/tr/td/img").get_attribute("src")
            }

            # Grab elements from the page and put them in the collection
            collection.append(attributes)

            # Switch back to the default content from the frame
            driver.switch_to.default_content()

            # Go back to the original page to load the next URL
            driver.back()

        # click the next page button
        next = driver.find_element(By.XPATH, '//*[@id="btnNext"]')
        next.click()

        # save the new anchor_tags
        anchor_tags = driver.find_elements(By.CSS_SELECTOR, "#tblImages a")

        # make a new url_list based
        url_list = []
        for tag in anchor_tags:
            url_list.append(tag.get_attribute("href"))
        
        # check if the first element of the new page is the same as the last page
        try:
            new_check = url_list[1]
            if (check == new_check):
                same_page = 1
        except:
            same_page = 1
            break

    # put the collection of data into the JSON file
    with open('bookings.jsonl','w') as fp: 
        for entry in collection:
            fp.write(json.dumps(entry) + '\n')

    print("Scraping finished, output data to bookings.jsonl")
    driver.quit()
    
if __name__ == '__main__': 
    main()
