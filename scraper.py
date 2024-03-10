'''
Code is based on: https://brightdata.com/blog/how-tos/how-to-scrape-job-postings
'''

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import traceback
import sys
import random
import time
import csv

def find_elements_with_retry(driver, by, selector, max_retry=100):
    retries = 0
    while retries < max_retry:
        try:
            elements = driver.find_elements(by, selector)
            return elements
        except StaleElementReferenceException:
            retries += 1
    return []

if __name__ == '__main__':    
    # Get args from command line
    discard_non_pay = True
    if len(sys.argv) < 4:
        print(f"Missing {4-len(sys.argv)} arguments")
        print("scraper.py url pages_to_scrape csv_file_path [discard_non_pay]")
        sys.exit()
    else:
        url = str(sys.argv[1])
        pages_to_scrape = int(sys.argv[2])
        csv_file_path = str(sys.argv[3])
        discard_non_pay = bool(sys.argv[4])
    
    # set up a controllable Chrome instance
    # in headless mode
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(service=Service(), options=options)
    
    # open the target page  in the browser
    driver.get(url)
    # set the window size to make sure pages will not be rendered in responsive mode
    driver.set_window_size(1366, 768)
    
    # a data structure where to store the job openings scraped from the page
    jobs = []
    pages_scraped = 0
    
    try:
        while pages_scraped < pages_to_scrape:
            print(f"Scraping page {pages_scraped} - ", end=" ")
            
            # select the job posting cards on the page
            job_cards = find_elements_with_retry(driver, By.CSS_SELECTOR, ".cardOutline")

            for job_card in job_cards:
                try:
                    # initialize a dictionary to store the scraped job data
                    job = {}
                
                    # initialize the job attributes to scrape
                    title = None
                    company_name = None
                    location = None
                    pay = None
                    job_type = None
                    description = None
                
                    # close the anti-scraping modal
                    if pages_scraped == 0:
                        try:
                            dialog_element = driver.find_element(By.CSS_SELECTOR, "[role=dialog]")[0]
                            close_button = dialog_element.find_element(By.CSS_SELECTOR, ".icl-CloseButton")[0]
                            close_button.click()
                        except NoSuchElementException:
                            pass

                            # close the cookie dialog
                        try:
                            cookie_dialog = driver.find_element(By.CSS_SELECTOR, "#CookiePrivacyNotice")[0]
                            close_button = cookie_dialog.find_element(By.CSS_SELECTOR, ".gnav-CookiePrivacyNoticeButton")[0]
                            close_button.click()
                        except NoSuchElementException:
                            pass
                        
                    # load the job details card
                    job_card.click()
                
                    # wait for the job details section to load after the click
                    try:
                        title_element = WebDriverWait(driver, 5) \
                        .until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobsearch-JobInfoHeader-title")))
                        title = title_element.text.replace("\n- job post", "")
                    except NoSuchElementException:
                        continue

                    # extract the job details
                    job_details_element = find_elements_with_retry(driver, By.CSS_SELECTOR, ".jobsearch-RightPane")[0]
                
                    # Comapny name
                    try:
                        company_link_element = find_elements_with_retry(job_details_element, By.CSS_SELECTOR, "div[data-company-name='true'] a")[0]
                        company_name = company_link_element.text
                    except IndexError:
                        pass

                    # Company location
                    try:
                        company_location_element = find_elements_with_retry(job_details_element, By.CSS_SELECTOR, "[data-testid='inlineHeader-companyLocation']")[0]
                        company_location_element_text = company_location_element.text
                        location = company_location_element_text
                        if "•" in company_location_element_text:
                            company_location_element_text_array = company_location_element_text.split("•")
                            location = company_location_element_text_array[0]
                            location_type = company_location_element_text_array[1]
                    except IndexError:
                        pass

                    # Pay and job type
                    for div in find_elements_with_retry(job_details_element, By.CSS_SELECTOR, "#jobDetailsSection"):
                        div_text = div.text
                        job_details_section = div_text.split('\n')
                            
                        if 'Sueldo' in job_details_section:
                            idx = job_details_section.index('Sueldo')
                            pay = job_details_section[idx+1]
                                
                        if 'Tipo de empleo' in job_details_section:
                            idx = job_details_section.index('Tipo de empleo')
                            job_type = job_details_section[idx+1]


                    # Try another option for pay
                    if pay is None:
                        aux_salary_elements = find_elements_with_retry(job_details_element, By.ID, "salaryInfoAndJobType")
                        for aux_salary_element in aux_salary_elements:
                            salary_spans = aux_salary_element.find_elements(By.TAG_NAME, "span")
                            for span in salary_spans:
                                if "$" in span.text:
                                    pay = span.text
                                    break

                    # Job description
                    try:
                        description_element = find_elements_with_retry(job_details_element, By.ID, "jobDescriptionText")[0]
                        description = description_element.text
                    except NoSuchElementException:
                        pass
                
                    # store the scraped data
                    if job_type is None:
                        job_type = 'not specified'
                            
                    job["title"] = title
                    job["company_name"] = company_name
                    job["location"] = location
                    job["pay"] = pay
                    job["job_type"] = job_type
                    job["description"] = description

                    if (discard_non_pay and job["pay"]!=None) or not discard_non_pay: # Discard no pay if needed
                        jobs.append(job)
                
                    # wait for a random number of seconds from 1 to 5 to avoid rate limiting blocks
                    time.sleep(random.uniform(1, 5))

                except StaleElementReferenceException:
                    # wait for a random number of seconds from 1 to 5 to avoid rate limiting blocks
                    time.sleep(random.uniform(1, 5))
                    continue

                except TimeoutException:
                    for _ in range(5):
                        driver.refresh()
                        time.sleep(5)
                    continue
            
            # Increment the scraping counter
            pages_scraped += 1
            print("Finished", end="\n")
            
            # If this is not the last page, go to the next page otherwise, break the while loop
            try:
                next_page_element = find_elements_with_retry(driver, By.CSS_SELECTOR, "a[data-testid=pagination-page-next]")[0]
                next_page_element.click()
            except NoSuchElementException:
                break

    except Exception: # Manage unexpected exception
        driver.quit()
        fieldnames = ["title", "company_name", "location", "pay", "job_type", "description"]
            
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for job in jobs:
                writer.writerow(job)
                        
            file.close()
        
        print("Scraping interrupted due to exception...")
        traceback.print_exc()
        print("\nJobs data has been saved to:", csv_file_path)
        print(f"Number of jobs scraped: {len(jobs)}")
        sys.exit()

    # Close the browser and free up the resources
    driver.quit()
        
    # Output
    fieldnames = ["title", "company_name", "location", "pay", "job_type", "description"]
        
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for job in jobs:
            writer.writerow(job)
                    
        file.close()
     
    print("Scraping complete...")
    print("\nJobs data has been saved to:", csv_file_path)
    print(f"Number of jobs scraped: {len(jobs)}")