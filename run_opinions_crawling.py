import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import datetime
import time
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def main():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    # Get today's date and format it as a string (e.g., "2024-09-20")
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    # Define the directory path where the file will be saved
    opinion_base_dir = os.path.join('C:\\news' if os.name == 'nt' else '/', 'opinions')
    opinion_directory = os.path.join(opinion_base_dir, year, month)

    # Create the directory if it doesn't exist
    os.makedirs(opinion_directory, exist_ok=True)

    # Define the file path
    opinion_file_path = os.path.join(opinion_directory, f'{today}_사설 모음.txt')

    # Initialize variables to ensure they are defined
    editorial_urls = []

    # Define the list of press names to filter by
    target_press_names = ['한국경제', '서울경제', '파이낸셜뉴스', '디지털타임스', '코리아중앙데일리']

    # Opinions Crawling
    try:
        # Open the Naver Editorial Opinions page
        driver.get('https://news.naver.com/opinion/editorial')

        # Step 1: Scroll and Collect URLs of editorials from target press names
        previous_length = 0

        while True:
            # Ensure the editorial list section is visible and fetch all items
            editorial_list = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CLASS_NAME, "opinion_editorial_list"))
            )
            editorial_items = editorial_list.find_elements(By.CLASS_NAME, "opinion_editorial_item")
            current_length = len(editorial_items)

            # Break the loop if no new items are loaded after scrolling
            if current_length == previous_length:
                break
            previous_length = current_length

            # Scroll down to load more items
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the new items to load

        # Loop through each editorial item to collect URLs
        for index, item in enumerate(editorial_items):
            try:
                # Extract the press name
                press_name = item.find_element(By.CLASS_NAME, "press_name").text

                # Check if the press name is in the target list
                if press_name in target_press_names:
                    # Extract the href link for the editorial
                    editorial_link = item.find_element(By.TAG_NAME, "a").get_attribute("href")

                    # Add the URL and corresponding press name to the list
                    editorial_urls.append((editorial_link, press_name))

            except NoSuchElementException:
                continue

    except WebDriverException as e:
        print(f"An error occurred with the WebDriver during the opinions crawling: {e}")

    # Process each collected URL to extract content and save it to a file
    if opinion_file_path and editorial_urls:
        with open(opinion_file_path, 'w', encoding='utf-8') as file:
            file.write(f"=== {today} 사설 모음 ===\n\n\n")

            for index, (url, press_name) in enumerate(editorial_urls):
                try:
                    # Navigate to the editorial page
                    driver.get(url)

                    # Wait for the article page to load
                    editorial_title = WebDriverWait(driver, 10).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "media_end_head_headline"))
                    ).text

                    # Find the publication and modification dates
                    date_elements = driver.find_elements(By.CLASS_NAME, "media_end_head_info_datestamp_time")
                    if len(date_elements) == 2:
                        published_date = date_elements[0].text.strip()
                        modified_date = driver.find_element(By.CLASS_NAME, "_ARTICLE_MODIFY_DATE_TIME").text.strip()
                    else:
                        published_date = date_elements[0].text.strip()
                        modified_date = None

                    article_body = WebDriverWait(driver, 10).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "_article_body"))
                    ).text

                    # Write the press name, editorial title, dates, and content to the file
                    file.write(f"언론사: {press_name}\n사설 제목: {editorial_title}\n")
                    file.write(f"작성일: {published_date}\n")
                    if modified_date:
                        file.write(f"수정일: {modified_date}\n")
                    file.write(f"링크: {url}\n\n")
                    file.write(f"내용:\n{article_body}\n\n")
                    file.write("=" * 50 + "\n\n")

                    # Pause for 2 seconds after processing each URL
                    time.sleep(2)

                except TimeoutException:
                    file.write(f"Timeout occurred while retrieving the editorial: {url}\n\n")
                except NoSuchElementException:
                    file.write(f"Could not retrieve elements for the editorial: {url}\n\n")

    # Close the browser
    driver.quit()

    # Confirm the file has been saved
    if opinion_file_path:
        print(f"Opinion file saved at: {opinion_file_path}")


if __name__ == "__main__":
    main()
