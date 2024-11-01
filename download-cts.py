from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import os
import time

# Set up options for Chrome
chrome_options = Options()
# Commenting out headless mode for debugging
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")

# Set up the download directory to be the current directory
current_dir = os.getcwd()

chrome_prefs = {
    "download.default_directory": current_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "profile.default_content_settings.popups": 0,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", chrome_prefs)

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

# Enable file downloads in headless mode (if needed)
params = {'behavior': 'allow', 'downloadPath': current_dir}
driver.execute_cdp_cmd('Page.setDownloadBehavior', params)

try:
    wait = WebDriverWait(driver, 60)
    
    # Step 1: Open the URL
    driver.get("https://trialsearch.who.int/AdvSearch.aspx")
    
    # Step 2: Focus on the input field
    condition_input = wait.until(EC.element_to_be_clickable(
        (By.ID, "ctl00_ContentPlaceHolder1_txtCondition")))
    
    # Step 3: Write "Multiple Sclerosis" in the input field
    condition_input.send_keys("Multiple Sclerosis")
    
    # Step 4: Set the recruiting status to "ALL"
    status_select = Select(driver.find_element(
        By.ID, "ctl00_ContentPlaceHolder1_ddlRecruitingStatus"))
    status_select.select_by_visible_text("ALL")
    
    # Step 6: Click the search button
    search_button = driver.find_element(
        By.ID, "ctl00_ContentPlaceHolder1_btnSearch")
    search_button.click()
    
    # Wait for the next page to load
    wait.until(EC.presence_of_element_located(
        (By.ID, "ctl00_ContentPlaceHolder1_btnLaunchDialogTerms")))
    
    # Step 7: Click the "Launch Terms" button
    launch_terms_button = driver.find_element(
        By.ID, "ctl00_ContentPlaceHolder1_btnLaunchDialogTerms")
    launch_terms_button.click()
    
    # Step 8: Click the "Export" button
    export_button = wait.until(EC.element_to_be_clickable(
        (By.ID, "ctl00_ContentPlaceHolder1_btnExport")))
    export_button.click()
    
    # Step 9: Click to download all trials
    export_all_button = wait.until(EC.element_to_be_clickable(
        (By.ID, "ctl00_ContentPlaceHolder1_ucExportDefault_butExportAllTrials")))
    
    # Start the download
    export_all_button.click()
    
    # Step 10: Wait for the download to complete
    download_timeout = 300  # Increase timeout as needed
    download_start_time = time.time()
    download_complete = False

    while not download_complete:
        time.sleep(1)  # Wait a bit before checking
        # Check for any .crdownload files in the directory
        downloading_files = [filename for filename in os.listdir(current_dir)
                             if filename.endswith('.crdownload')]
        if downloading_files:
            print("Download in progress...")
        else:
            download_complete = True
            print("Download finished successfully.")
            # Optionally, get the name of the downloaded file
            downloaded_files = [filename for filename in os.listdir(current_dir)
                                if filename.endswith('.zip') or filename.endswith('.csv') or filename.endswith('.xlsx')]
            if downloaded_files:
                downloaded_file = downloaded_files[0]
                print(f"Downloaded file: {downloaded_file}")
            else:
                print("No downloaded file found.")
            break

        # Check for timeout
        if (time.time() - download_start_time) > download_timeout:
            print("Download did not complete within the timeout period.")
            break

finally:
    # Close the browser
    driver.quit()