#!/usr/bin/env python3

import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import tempfile
import shutil

# Import the upload_file function
from upload_cts import upload_file  # Ensure the filename is upload_cts.py

def wait_for_all_downloads_to_complete(download_dir, timeout=600):
    """
    Waits for all downloads to complete by monitoring the download directory.
    Returns a list of downloaded file names.
    """
    start_time = time.time()
    while True:
        time.sleep(1)
        # Get list of files in download directory
        files_in_download = set(f for f in os.listdir(download_dir) if not f.startswith('.'))
        # Check for any temp files indicating downloads are in progress
        temp_files = [f for f in files_in_download if f.endswith('.crdownload') or f.endswith('.part')]
        if not temp_files and files_in_download:
            # Downloads are complete
            return list(files_in_download)
        if time.time() - start_time > timeout:
            print("Downloads did not complete within the timeout period.")
            return []

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Download and upload clinical trial data.')
    parser.add_argument('--source-id', required=True, help='Source ID for the upload process')
    parser.add_argument('--condition', required=True, help='Condition to search for')

    args = parser.parse_args()

    source_id = args.source_id
    condition = args.condition

    # Set up options for Chrome
    chrome_options = Options()
    # Uncomment to run in headless mode if needed
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")

    # Create a temporary directory for downloads
    download_dir = tempfile.mkdtemp()

    chrome_prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": False,  # Disable Safe Browsing to avoid download issues
        "safebrowsing.disable_download_protection": True
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)

    # Initialize the driver with webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Increase page load timeout
    driver.set_page_load_timeout(120)

    # Set download behavior
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': download_dir
    })

    try:
        wait = WebDriverWait(driver, 60)

        # Step 1: Open the URL
        driver.get("https://trialsearch.who.int/AdvSearch.aspx")

        # Step 2: Focus on the input field
        condition_input = wait.until(EC.element_to_be_clickable(
            (By.ID, "ctl00_ContentPlaceHolder1_txtCondition")))

        # Step 3: Write the condition in the input field
        condition_input.send_keys(condition)

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

        # Start the download(s)
        export_all_button = wait.until(EC.element_to_be_clickable(
            (By.ID, "ctl00_ContentPlaceHolder1_ucExportDefault_butExportAllTrials")))
        export_all_button.click()

        # Wait for all downloads to complete
        downloaded_files = wait_for_all_downloads_to_complete(download_dir, timeout=600)

        if downloaded_files:
            print("All downloads finished successfully.")
            print(f"Downloaded files: {downloaded_files}")

            # Identify the XML file
            xml_file = None
            for filename in downloaded_files:
                if filename.endswith('.xml'):
                    xml_file = os.path.join(download_dir, filename)
                    break

            if xml_file:
                # Call the upload_file function directly
                try:
                    upload_file(xml_file, source_id)
                    print("Upload completed successfully.")
                except Exception as e:
                    print(f"An error occurred during the upload process: {e}")
            else:
                print("No XML file found among the downloaded files.")

        else:
            print("No downloads were completed.")

    finally:
        # Close the browser
        driver.quit()
        # Optionally move downloaded files to a permanent location
        destination_dir = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(destination_dir, exist_ok=True)
        for filename in os.listdir(download_dir):
            shutil.move(os.path.join(download_dir, filename), os.path.join(destination_dir, filename))
        # Clean up the temporary download directory
        shutil.rmtree(download_dir)

if __name__ == '__main__':
    main()