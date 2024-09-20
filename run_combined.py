import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Specify the path to your WebDriver
service = Service('./chromedriver.exe')

# Initialize the WebDriver using the Service object
driver = webdriver.Chrome(service=service)

# Get today's date and format it as a string (e.g., "2024-09-20")
today = datetime.datetime.today().strftime('%Y-%m-%d')
year = datetime.datetime.today().strftime('%Y')
month = datetime.datetime.today().strftime('%m')

# Headline Crawling

# Open the Naver News website
driver.get('https://news.naver.com/')

# List of tabs to click based on the image provided (Korean labels)
tabs = ["경제", "IT/과학", "세계", "정치", "사회", "생활/문화"]

# Define the base directory depending on the operating system
base_dir = os.path.join('C:\\news', 'headlines')

# Define the directory path where the file will be saved
directory = os.path.join(base_dir, year, month)

# Create the directory if it doesn't exist
os.makedirs(directory, exist_ok=True)

# Define the file path
headline_file_path = os.path.join(directory, f'{today}_헤드라인 모음.txt')

# Open the text file in the specified directory with today's date as the file name
with open(headline_file_path, 'w', encoding='utf-8') as file:
    file.write(f"=== {today} 헤드라인 모음 ===\n\n\n")

    # Loop through each tab and click
    for tab in tabs:
        try:
            # Find the tab element by its text and click it
            tab_element = driver.find_element(By.LINK_TEXT, tab)
            tab_element.click()

            # After clicking the tab, find and click "헤드라인 더보기" (Headline More)
            try:
                more_button = driver.find_element(By.LINK_TEXT, "헤드라인 더보기")
                more_button.click()

                # Wait for the page to load after clicking
                time.sleep(2)

                # Find the section with class "section_component as_section_headline"
                headlines_section = driver.find_element(By.CLASS_NAME, "section_component.as_section_headline")

                # Find all headline titles, press names, summaries, and URLs within this section
                headlines = headlines_section.find_elements(By.CLASS_NAME, "sa_text_strong")
                presses = headlines_section.find_elements(By.CLASS_NAME, "sa_text_press")
                titles = headlines_section.find_elements(By.CLASS_NAME, "sa_text_title")
                summaries = headlines_section.find_elements(By.CLASS_NAME, "sa_text_lede")

                # Write the tab name as a section header in the file
                file.write(f"=== {tab} ===\n")

                # Write out each headline, its corresponding press name, and summary into the file
                for headline, press, title, summary in zip(headlines, presses, titles, summaries):
                    news_url = title.get_attribute('data-imp-url')
                    summary_text = summary.text.strip()

                    # Truncate the summary to 50 characters and add "..." if necessary
                    if len(summary_text) > 50:
                        summary_text = summary_text[:50] + "..."

                    file.write(f"제목: {headline.text}\n내용: {summary_text}\n언론사: {press.text}\n링크: {news_url}\n\n")

                # Add a separator between sections
                file.write("\n" + "=" * 50 + "\n\n")

            except Exception as e:
                file.write(f"Could not retrieve data for {tab} section.\n\n")

        except Exception as e:
            file.write(f"Could not access {tab} section.\n\n")

# Save and close the headline file
print(f"Headline file saved at: {headline_file_path}")

# Opinions Crawling

# Open the Naver Editorial Opinions page
driver.get('https://news.naver.com/opinion/editorial')

# Define the directory path where the editorial file will be saved
opinion_base_dir = os.path.join('C:\\news' if os.name == 'nt' else '/', 'opinions')
opinion_directory = os.path.join(opinion_base_dir, year, month)

# Create the directory if it doesn't exist
os.makedirs(opinion_directory, exist_ok=True)

# Define the file path
opinion_file_path = os.path.join(opinion_directory, f'{today}_사설 모음.txt')

# Define the list of press names to filter by
target_press_names = ['한국경제', '서울경제', '파이낸셜뉴스', '디지털타임스', '코리아중앙데일리']

# Step 1: Scroll and Collect URLs of editorials from target press names
editorial_urls = []

try:
    previous_length = 0

    while True:
        # Ensure the editorial list section is visible and fetch all items
        editorial_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "opinion_editorial_list"))
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

        except Exception as e:
            continue

except Exception as e:
    pass

# Step 2: Process each collected URL to extract content and save it to a file

with open(opinion_file_path, 'w', encoding='utf-8') as file:
    file.write(f"=== {today} 사설 모음 ===\n\n\n")

    for index, (url, press_name) in enumerate(editorial_urls):

        try:
            # Navigate to the editorial page
            driver.get(url)

            # Wait for the article page to load
            editorial_title = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "media_end_head_headline"))
            ).text

            article_body = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "_article_body"))
            ).text

            # Write the press name, editorial title, and content to the file
            file.write(f"언론사: {press_name}\n사설 제목: {editorial_title}\n링크: {url}\n내용:\n{article_body}\n\n")
            file.write("=" * 50 + "\n\n")

            # Pause for 2 seconds after processing each URL
            time.sleep(2)

        except Exception as e:
            continue

# Close the browser
driver.quit()

# Confirm the files have been saved
print(f"Opinion file saved at: {opinion_file_path}")
